#!/usr/bin/env python3
"""Fail-closed local lexical search over an authorized Pack index.

Draft candidates are excluded unless the caller explicitly supplies the exact
namespace/version and opts into review-candidate inspection. Results are
citations for inspection, not clinical or institutional answers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

DENIED_STATES = {"quarantined", "superseded", "retired", "recalled", "withdrawn"}
TOKEN = re.compile(r"[\w-]+", re.UNICODE)


def abstain(message: str) -> int:
    print(f"ABSTAIN: {message}", file=sys.stderr)
    return 3


def safe_fts_query(query: str) -> str:
    if len(query) > 1000:
        raise ValueError("query exceeds the 1000-character review-search ceiling")
    terms = TOKEN.findall(query.lower())
    if not terms:
        raise ValueError("query contains no searchable terms")
    return " AND ".join('"' + term.replace('"', '""') + '"' for term in terms[:20])


def load_json_object(path: Path, label: str) -> tuple[dict[str, object], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is unavailable or invalid: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("query")
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--candidate-digest")
    parser.add_argument("--allow-review-candidate", action="store_true")
    parser.add_argument("--governance-record", type=Path)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.limit < 1 or args.limit > 20:
        return abstain("limit must be between 1 and 20")
    if not args.allow_review_candidate:
        return abstain(
            "this local tool does not derive publication authority from Pack metadata; "
            "explicit review-candidate access is required"
        )
    if args.governance_record is None or args.candidate_digest is None:
        return abstain("review-candidate access requires an external governance record and exact digest")

    try:
        governance, governance_bytes = load_json_object(
            args.governance_record.resolve(), "governance record"
        )
        governed_pack = governance.get("pack")
        review_access = governance.get("review_access")
        if not isinstance(governed_pack, dict) or not isinstance(review_access, dict):
            raise ValueError("governance record lacks pack or review_access metadata")
        if governance.get("status") != "independent-review-requested":
            raise ValueError("governance record is not an active independent-review request")
        if not isinstance(governance.get("registry_epoch"), int):
            raise ValueError("governance record lacks a numeric registry epoch")
        if governance.get("deny_override") != "none":
            return abstain(f"governance deny override is active: {governance.get('deny_override')}")
        if governance.get("effective_lifecycle") in DENIED_STATES:
            return abstain(
                f"effective lifecycle is excluded: {governance.get('effective_lifecycle')}"
            )
        if review_access.get("authorized") is not True or review_access.get("mode") != "local-exact-digest-review":
            raise ValueError("governance record does not authorize bounded local review access")
        expected_identity = (
            governed_pack.get("namespace", governed_pack.get("pack_id")),
            governed_pack.get("pack_version"),
            governed_pack.get("candidate_digest"),
        )
        requested_identity = (args.namespace, args.version, args.candidate_digest)
        if expected_identity != requested_identity:
            raise ValueError("requested namespace/version/digest does not match governance record")

        lock_path = args.index.with_suffix(args.index.suffix + ".lock.json")
        lock, _ = load_json_object(lock_path.resolve(), "Pack shard lock")
        lock_identity = (
            lock.get("namespace"),
            lock.get("pack_version"),
            lock.get("candidate_digest"),
        )
        if lock_identity != requested_identity:
            raise ValueError("Pack shard lock does not match authorized namespace/version/digest")
        if lock.get("status") != "review-candidate-shard":
            raise ValueError("Pack shard lock is not a review-candidate shard")
        if not args.index.is_file():
            raise ValueError(f"authorized Pack shard does not exist: {args.index}")

        match_query = safe_fts_query(args.query)
        connection = sqlite3.connect(f"file:{args.index.resolve()}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        pack_rows = connection.execute(
            """
            SELECT * FROM pack_versions
            WHERE namespace = ? AND version = ?
              AND (? IS NULL OR candidate_digest = ?)
            """,
            (args.namespace, args.version, args.candidate_digest, args.candidate_digest),
        ).fetchall()
        if len(pack_rows) != 1:
            connection.close()
            return abstain("authorized namespace/version/digest does not resolve to exactly one Pack")
        pack = pack_rows[0]
        if pack["state"] in DENIED_STATES:
            connection.close()
            return abstain(f"Pack lifecycle state is excluded: {pack['state']}")
        if pack["state"] == "published":
            connection.close()
            return abstain("published retrieval requires a separate trusted publication-decision path")
        if pack["data_class"] != "D0" or pack["risk_tier"] not in {"Green", "Yellow"}:
            connection.close()
            return abstain("Pack data/risk classification is outside this public lexical-search boundary")
        authority = json.loads(pack["authority_json"])
        if any(value != "none" for value in authority.values()):
            connection.close()
            return abstain("authority metadata is not compatible with this non-authoritative search surface")

        rows = connection.execute(
            """
            SELECT
                c.chunk_id,
                c.content_unit_id,
                c.pack_id,
                c.version,
                c.candidate_digest,
                c.artifact_id,
                c.artifact_path,
                c.artifact_digest,
                c.citation_locator,
                c.unit_text_digest,
                c.chunk_digest,
                c.section_path_json,
                c.text,
                c.source_refs_json,
                bm25(chunks_fts) AS score
            FROM chunks_fts
            JOIN chunks AS c ON c.chunk_id = chunks_fts.chunk_id
            WHERE chunks_fts MATCH ?
              AND c.namespace = ?
              AND c.version = ?
              AND c.candidate_digest = ?
              AND c.lifecycle_state NOT IN ('quarantined', 'superseded', 'retired', 'recalled', 'withdrawn')
              AND c.data_class = 'D0'
              AND c.risk_tier IN ('Green', 'Yellow')
            ORDER BY score, c.chunk_id
            LIMIT ?
            """,
            (match_query, args.namespace, args.version, pack["candidate_digest"], args.limit),
        ).fetchall()
        connection.close()
        current_governance_bytes = args.governance_record.resolve().read_bytes()
        if hashlib.sha256(current_governance_bytes).digest() != hashlib.sha256(governance_bytes).digest():
            return abstain("governance registry epoch changed during retrieval; evidence discarded")
    except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        return abstain(f"search could not be completed safely: {exc}")

    payload = {
        "status": "review-candidate-results",
        "authority": "Evidence for human inspection only; no clinical or institutional authority.",
        "effective_lifecycle": governance["effective_lifecycle"],
        "registry_epoch": governance["registry_epoch"],
        "namespace": args.namespace,
        "version": args.version,
        "candidate_digest": pack["candidate_digest"],
        "query": args.query,
        "results": [
            {
                "rank": index,
                "chunk_id": row["chunk_id"],
                "content_unit_id": row["content_unit_id"],
                "citation": {
                    "pack_id": row["pack_id"],
                    "pack_version": row["version"],
                    "candidate_digest": row["candidate_digest"],
                    "artifact_id": row["artifact_id"],
                    "artifact_path": row["artifact_path"],
                    "artifact_digest": row["artifact_digest"],
                    "content_unit_id": row["content_unit_id"],
                    "citation_locator": row["citation_locator"],
                    "unit_text_digest": row["unit_text_digest"],
                    "chunk_digest": row["chunk_digest"],
                    "section_path": json.loads(row["section_path_json"]),
                    "source_refs": json.loads(row["source_refs_json"]),
                },
                "text": row["text"],
            }
            for index, row in enumerate(rows, start=1)
        ],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
