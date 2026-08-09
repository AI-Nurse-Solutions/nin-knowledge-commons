#!/usr/bin/env python3
"""Fail-closed validator for draft NIN Knowledge Packs.

A PASS proves only the declared structural, referential, integrity, and screening
contracts. It is not publication approval, clinical validation, rights clearance,
or institutional authorization.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, NoReturn

from packlib import (
    PackError,
    load_yaml,
    parse_markdown_front_matter,
    read_jsonl,
    resolve_inside,
    sha256_bytes,
    sha256_file,
    validate_schema,
)

DENIED_SUFFIXES = {
    ".app",
    ".bat",
    ".cmd",
    ".com",
    ".dll",
    ".dmg",
    ".exe",
    ".jar",
    ".js",
    ".msi",
    ".ps1",
    ".py",
    ".scr",
    ".sh",
    ".so",
    ".vbs",
}
TEXT_SUFFIXES = {"", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
SENSITIVE_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "generic secret key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "US Social Security number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "PHI-like or patient-specific marker": re.compile(
        r"(?im)^\s*(?:patient name|medical record number|mrn|date of birth|dob)\s*:\s*\S+"
    ),
}
DATA_RANK = {"D0": 0, "D1": 1, "D2": 2, "D3": 3, "D4": 4}
RISK_RANK = {"Green": 0, "Yellow": 1, "Orange": 2, "Red-E": 3}


def fail(message: str) -> NoReturn:
    raise PackError(message)


def check_tree(pack: Path) -> list[Path]:
    if not pack.is_dir():
        fail(f"Pack directory does not exist: {pack}")
    files: list[Path] = []
    for path in sorted(pack.rglob("*")):
        if path.is_symlink():
            fail(f"symbolic links are prohibited in Packs: {path.relative_to(pack)}")
        if not path.is_file():
            continue
        relative = path.relative_to(pack)
        if path.suffix.lower() in DENIED_SUFFIXES:
            fail(f"active or executable content is prohibited: {relative}")
        if any(part.startswith(".") for part in relative.parts):
            fail(f"hidden Pack content is prohibited: {relative}")
        files.append(path)
    return files


def scan_sensitive(pack: Path, files: list[Path]) -> int:
    scanned = 0
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            fail(f"text file is not valid UTF-8: {path.relative_to(pack)}: {exc}")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                fail(f"possible {label} found in {path.relative_to(pack)}")
        scanned += 1
    return scanned


def validate_namespace(pack: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    namespace_path = pack / "namespace.yaml"
    if not namespace_path.is_file():
        fail("namespace.yaml is required in a draft Pack candidate")
    namespace = load_yaml(namespace_path)
    validate_schema(namespace, "namespace.schema.json", "namespace")
    if namespace["namespace_id"] != manifest["namespace"]:
        fail("manifest namespace does not match namespace.yaml")
    if manifest["lane"] not in namespace["eligible_lanes"]:
        fail("Pack lane exceeds namespace eligibility")
    if DATA_RANK[manifest["data_class"]] > DATA_RANK[namespace["data_ceiling"]]:
        fail("Pack data class exceeds namespace ceiling")
    if manifest["risk_tier"] not in RISK_RANK:
        fail("prohibited or exceptional risk tier cannot enter this public draft namespace")
    if RISK_RANK[manifest["risk_tier"]] > RISK_RANK[namespace["risk_ceiling"]]:
        fail("Pack risk tier exceeds namespace ceiling")
    return namespace


def validate_sources(pack: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    path = resolve_inside(pack, manifest["sources_path"])
    if not path.is_file():
        fail(f"source ledger is missing: {manifest['sources_path']}")
    sources: dict[str, dict[str, Any]] = {}
    for record in read_jsonl(path):
        validate_schema(record, "source-record.schema.json", "source record")
        source_id = record["source_id"]
        if source_id in sources:
            fail(f"duplicate source_id: {source_id}")
        if record["reuse_status"] == "rights-unclear":
            fail(f"source rights are unclear: {source_id}")
        sources[source_id] = record
    if not sources:
        fail("source ledger must contain at least one record")
    return sources


def validate_artifacts(
    pack: Path, manifest: dict[str, Any], sources: dict[str, dict[str, Any]]
) -> tuple[list[tuple[dict[str, Any], str, Path]], set[str]]:
    declared_paths: set[str] = set()
    artifact_ids: set[str] = set()
    content_unit_ids: set[str] = set()
    parsed: list[tuple[dict[str, Any], str, Path]] = []
    referenced_sources: set[str] = set()

    for summary in manifest["artifacts"]:
        relative = summary["path"]
        if relative in declared_paths:
            fail(f"duplicate artifact path: {relative}")
        declared_paths.add(relative)
        if summary["artifact_id"] in artifact_ids:
            fail(f"duplicate artifact_id: {summary['artifact_id']}")
        artifact_ids.add(summary["artifact_id"])
        if summary["content_unit_id"] in content_unit_ids:
            fail(f"duplicate content_unit_id: {summary['content_unit_id']}")
        content_unit_ids.add(summary["content_unit_id"])

        path = resolve_inside(pack, relative)
        if not path.is_file():
            fail(f"declared artifact is missing: {relative}")
        front_matter, body = parse_markdown_front_matter(path)
        validate_schema(front_matter, "artifact.schema.json", f"artifact {relative}")
        for field in ("artifact_id", "content_unit_id", "title", "artifact_type", "language"):
            if front_matter[field] != summary[field]:
                fail(f"artifact summary mismatch for {relative}: {field}")
        if front_matter["language"] != manifest["language"]:
            fail(f"artifact language does not match Pack language: {relative}")
        if not body.strip():
            fail(f"artifact body is empty: {relative}")
        if not re.search(r"(?m)^#\s+\S", body):
            fail(f"artifact must contain one visible H1: {relative}")
        for source_id in front_matter["source_refs"]:
            if source_id not in sources:
                fail(f"unknown source reference in {relative}: {source_id}")
            referenced_sources.add(source_id)
        parsed.append((front_matter, body, path))

    actual_paths = {
        path.relative_to(pack).as_posix()
        for path in sorted((pack / "content").glob("*.md"))
        if path.is_file()
    }
    if actual_paths != declared_paths:
        missing = sorted(declared_paths - actual_paths)
        undeclared = sorted(actual_paths - declared_paths)
        fail(f"artifact inventory mismatch; missing={missing}, undeclared={undeclared}")
    return parsed, referenced_sources


def validate_reviews(pack: Path, manifest: dict[str, Any]) -> int:
    count = 0
    for relative in manifest["review_records"]:
        path = resolve_inside(pack, relative)
        if not path.is_file():
            fail(f"declared review record is missing: {relative}")
        review = load_yaml(path)
        validate_schema(review, "review-record.schema.json", f"review {relative}")
        if review["pack_id"] != manifest["pack_id"] or review["pack_version"] != manifest["version"]:
            fail(f"review record identity mismatch: {relative}")
        count += 1
    if manifest["review_status"] == "reviewed-for-stated-scope" and count == 0:
        fail("reviewed-for-stated-scope requires at least one review record")
    return count


def validate_manifest_semantics(pack: Path, manifest: dict[str, Any]) -> None:
    license_path = resolve_inside(pack, manifest["license"]["path"])
    if not license_path.is_file():
        fail(f"Pack license file is missing: {manifest['license']['path']}")
    if manifest["state"] == "published":
        fail("this draft validator does not authorize or perform publication")
    if manifest["publisher"]["status"] == "published":
        fail("an unpublished draft cannot claim published publisher status")
    if manifest["lifecycle"]["published_at"] is not None:
        fail("an unpublished draft must have published_at: null")
    if manifest["language"] != "en" and not manifest["relationships"]["translations"]:
        fail("non-English editions require an exact translation source relationship")
    if manifest["pack_id"] == "nin.global.learn.ai-literacy":
        expected = {
            "title": "AI Literacy Foundations for Nurses",
            "lane": "Learn",
            "language": "en",
            "data_class": "D0",
            "risk_tier": "Green",
            "role": "reference-pack",
        }
        for field, value in expected.items():
            if manifest[field] != value:
                fail(f"approved first Pack scope drift: {field} must be {value!r}")
        if manifest["relationships"]["translations"]:
            fail("Tagalog and other translations remain held for the first English draft")


def canonical_files(pack: Path) -> list[Path]:
    excluded = {"CHECKSUMS.sha256"}
    return [
        path
        for path in sorted(pack.rglob("*"))
        if path.is_file()
        and not path.is_symlink()
        and path.relative_to(pack).as_posix() not in excluded
    ]


def validate_checksums(pack: Path) -> str:
    ledger_path = pack / "CHECKSUMS.sha256"
    if not ledger_path.is_file():
        fail("CHECKSUMS.sha256 is required in --frozen mode")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            fail(f"malformed checksum entry at CHECKSUMS.sha256:{line_number}")
        digest, relative = match.groups()
        path = resolve_inside(pack, relative)
        if relative == "CHECKSUMS.sha256":
            fail("checksum ledger must not include itself")
        if relative in entries:
            fail(f"duplicate checksum path: {relative}")
        if not path.is_file():
            fail(f"checksummed file is missing: {relative}")
        if sha256_file(path) != digest:
            fail(f"checksum mismatch: {relative}")
        entries[relative] = digest

    expected = {path.relative_to(pack).as_posix() for path in canonical_files(pack)}
    actual = set(entries)
    if expected != actual:
        fail(
            "checksum inventory mismatch; "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    return "sha256:" + sha256_bytes(ledger_path.read_bytes())


def validate(pack: Path, frozen: bool) -> dict[str, Any]:
    files = check_tree(pack)
    scanned = scan_sensitive(pack, files)
    manifest_path = pack / "manifest.yaml"
    if not manifest_path.is_file():
        fail("manifest.yaml is required")
    manifest = load_yaml(manifest_path)
    validate_schema(manifest, "knowledge-pack.schema.json", "manifest")
    validate_manifest_semantics(pack, manifest)
    validate_namespace(pack, manifest)
    sources = validate_sources(pack, manifest)
    artifacts, referenced_sources = validate_artifacts(pack, manifest, sources)
    reviews = validate_reviews(pack, manifest)
    unused_sources = sorted(set(sources) - referenced_sources)
    if unused_sources:
        fail(f"source ledger contains unreferenced records: {unused_sources}")
    candidate_digest = validate_checksums(pack) if frozen else None
    return {
        "pack_id": manifest["pack_id"],
        "version": manifest["version"],
        "files": len(files),
        "artifacts": len(artifacts),
        "sources": len(sources),
        "reviews": reviews,
        "text_files_scanned": scanned,
        "candidate_digest": candidate_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--frozen", action="store_true", help="require and verify the exact checksum ledger")
    args = parser.parse_args()
    try:
        result = validate(args.pack.resolve(), args.frozen)
    except PackError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    digest = f", candidate={result['candidate_digest']}" if result["candidate_digest"] else ""
    print(
        "PASS: "
        f"{result['pack_id']}@{result['version']}, "
        f"{result['artifacts']} artifacts, {result['sources']} sources, "
        f"{result['reviews']} review records, {result['text_files_scanned']} text files scanned"
        f"{digest}; structural validation is not publication approval"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
