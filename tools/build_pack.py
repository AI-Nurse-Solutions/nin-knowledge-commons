#!/usr/bin/env python3
"""Build deterministic review-only derivatives from a validated Knowledge Pack.

The Pack remains authoritative. JSON/JSONL projections and SQLite/FTS5 are
rebuildable derivatives. This tool does not publish or approve a Pack.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import sys
import zipfile
from pathlib import Path
from typing import Any

from packlib import (
    PackError,
    canonical_json,
    load_yaml,
    parse_markdown_front_matter,
    read_jsonl,
    sha256_bytes,
    sha256_file,
    validate_schema,
)
from validate_pack import canonical_files, validate

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
NON_ID = re.compile(r"[^a-z0-9]+")
LIFECYCLE_DENY = {"quarantined", "superseded", "retired", "recalled", "withdrawn"}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [canonical_json(value) for value in values]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def slug(value: str) -> str:
    normalized = NON_ID.sub("-", value.lower()).strip("-")
    return normalized or "section"


def split_sections(body: str) -> list[tuple[list[str], str]]:
    """Return heading-path/content pairs using direct content per heading."""
    sections: list[tuple[list[str], str]] = []
    stack: list[str] = []
    current_path: list[str] | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_path is None:
            return
        content = "\n".join(current_lines).strip()
        if content:
            heading = "#" * len(current_path) + " " + current_path[-1]
            sections.append((list(current_path), heading + "\n\n" + content + "\n"))

    for line in body.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        match = HEADING.match(line)
        if not match:
            current_lines.append(line)
            continue
        flush()
        level = len(match.group(1))
        title = match.group(2).strip()
        stack = stack[: level - 1]
        while len(stack) < level - 1:
            stack.append("Untitled parent")
        stack.append(title)
        current_path = list(stack)
        current_lines = []
    flush()
    return sections


def create_checksum_ledger(pack: Path) -> str:
    lines = [
        f"{sha256_file(path)}  {path.relative_to(pack).as_posix()}"
        for path in canonical_files(pack)
    ]
    ledger = "\n".join(lines) + "\n"
    (pack / "CHECKSUMS.sha256").write_text(ledger, encoding="utf-8")
    return "sha256:" + sha256_bytes(ledger.encode("utf-8"))


def build_chunks(pack: Path, manifest: dict[str, Any], candidate_digest: str) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    seen_units: set[str] = set()
    for unit_source_order, summary in enumerate(manifest["artifacts"]):
        path = pack / summary["path"]
        front_matter, body = parse_markdown_front_matter(path)
        content_unit_id = front_matter["content_unit_id"]
        if content_unit_id in seen_units:
            raise PackError(f"duplicate declared content_unit_id: {content_unit_id}")
        seen_units.add(content_unit_id)
        artifact_digest = "sha256:" + sha256_file(path)
        unit_text_digest = "sha256:" + sha256_bytes(body.encode("utf-8"))
        citation_locator = (
            f"ninpack:{manifest['pack_id']}@{manifest['version']}/"
            f"{front_matter['artifact_id']}#{content_unit_id}"
        )
        for part_index, (section_path, text) in enumerate(split_sections(body)):
            if len(text) > 1600:
                raise PackError(
                    "content unit part exceeds structural-scalar-1600-v1 ceiling: "
                    f"{content_unit_id} part {part_index} has {len(text)} Unicode scalars"
                )
            text_digest = sha256_bytes(text.encode("utf-8"))
            chunk_key = canonical_json(
                [
                    "kc:chunk:v1",
                    manifest["pack_id"],
                    manifest["version"],
                    candidate_digest,
                    front_matter["artifact_id"],
                    content_unit_id,
                    part_index,
                    "structural-scalar-1600-v1",
                    text_digest,
                ]
            )
            chunk = {
                "schema_version": "0.1-draft",
                "chunk_id": "chunk." + sha256_bytes(chunk_key.encode("utf-8"))[:32],
                "content_unit_id": content_unit_id,
                "pack_id": manifest["pack_id"],
                "pack_version": manifest["version"],
                "candidate_digest": candidate_digest,
                "parser_contract": "markdown-front-matter-sections-v1",
                "chunker_version": "structural-scalar-1600-v1",
                "namespace": manifest["namespace"],
                "artifact_id": front_matter["artifact_id"],
                "artifact_path": summary["path"],
                "artifact_digest": artifact_digest,
                "section_path": section_path,
                "unit_source_order": unit_source_order,
                "part_index": part_index,
                "citation_locator": citation_locator,
                "unit_text_digest": unit_text_digest,
                "text": text,
                "language": manifest["language"],
                "lane": manifest["lane"],
                "data_class": manifest["data_class"],
                "risk_tier": manifest["risk_tier"],
                "action_modes": manifest["action_modes"],
                "review_status": manifest["review_status"],
                "lifecycle_state": manifest["state"],
                "license": manifest["license"]["spdx_id"],
                "permitted_uses": manifest["permitted_uses"],
                "prohibited_uses": manifest["prohibited_uses"],
                "authority": manifest["authority"],
                "source_refs": front_matter["source_refs"],
                "chunk_digest": "sha256:" + text_digest,
            }
            validate_schema(chunk, "chunk.schema.json", f"chunk {content_unit_id}")
            chunks.append(chunk)
    if not chunks:
        raise PackError("no indexable content units were generated")
    return chunks


def entity(
    entity_id: str,
    entity_type: str,
    label: str,
    manifest: dict[str, Any],
    candidate_digest: str,
) -> dict[str, Any]:
    value = {
        "schema_version": "0.1-draft",
        "entity_id": entity_id,
        "entity_type": entity_type,
        "label": label,
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["version"],
        "candidate_digest": candidate_digest,
        "lifecycle_state": manifest["state"],
    }
    validate_schema(value, "entity.schema.json", f"entity {entity_id}")
    return value


def relation(
    source: str,
    predicate: str,
    target: str,
    provenance: str,
    manifest: dict[str, Any],
    candidate_digest: str,
) -> dict[str, Any]:
    relation_key = canonical_json([source, predicate, target, provenance])
    value = {
        "schema_version": "0.1-draft",
        "relation_id": "relation." + sha256_bytes(relation_key.encode("utf-8"))[:20],
        "source_entity_id": source,
        "predicate": predicate,
        "target_entity_id": target,
        "pack_id": manifest["pack_id"],
        "pack_version": manifest["version"],
        "candidate_digest": candidate_digest,
        "provenance": provenance,
        "review_status": manifest["review_status"],
    }
    validate_schema(value, "relation.schema.json", f"relation {value['relation_id']}")
    return value


def build_graph(
    manifest: dict[str, Any], sources: list[dict[str, Any]], candidate_digest: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pack_entity = f"entity.pack.{manifest['pack_id']}"
    version_entity = f"entity.version.{manifest['pack_id']}.{manifest['version']}"
    namespace_entity = f"entity.namespace.{manifest['namespace']}"
    creator_entity = "entity.creator." + slug(manifest["creator"]["display_name"])
    license_entity = "entity.license." + slug(manifest["license"]["spdx_id"])
    language_entity = "entity.language." + slug(manifest["language"])

    entities = [
        entity(pack_entity, "pack", manifest["title"], manifest, candidate_digest),
        entity(version_entity, "version", f"{manifest['title']} {manifest['version']}", manifest, candidate_digest),
        entity(namespace_entity, "namespace", manifest["namespace"], manifest, candidate_digest),
        entity(creator_entity, "creator", manifest["creator"]["display_name"], manifest, candidate_digest),
        entity(license_entity, "license", manifest["license"]["spdx_id"], manifest, candidate_digest),
        entity(language_entity, "language", manifest["language"], manifest, candidate_digest),
    ]
    relations = [
        relation(pack_entity, "HAS_VERSION", version_entity, "manifest", manifest, candidate_digest),
        relation(version_entity, "IN_NAMESPACE", namespace_entity, "manifest", manifest, candidate_digest),
        relation(version_entity, "CREATED_BY", creator_entity, "manifest", manifest, candidate_digest),
        relation(version_entity, "LICENSED_UNDER", license_entity, "manifest", manifest, candidate_digest),
        relation(version_entity, "IN_LANGUAGE", language_entity, "manifest", manifest, candidate_digest),
    ]

    unit_entity_by_artifact_id: dict[str, str] = {}
    for artifact in manifest["artifacts"]:
        entity_id = f"entity.artifact.{artifact['artifact_id']}"
        entities.append(entity(entity_id, "artifact", artifact["title"], manifest, candidate_digest))
        relations.append(
            relation(version_entity, "CONTAINS_ARTIFACT", entity_id, "manifest", manifest, candidate_digest)
        )
        front_matter, _ = parse_markdown_front_matter(Path(manifest["_pack_path"]) / artifact["path"])
        unit_entity_id = f"entity.unit.{front_matter['content_unit_id']}"
        unit_entity_by_artifact_id[artifact["artifact_id"]] = unit_entity_id
        entities.append(
            entity(unit_entity_id, "source-unit", front_matter["title"], manifest, candidate_digest)
        )
        relations.append(
            relation(
                entity_id,
                "CONTAINS_UNIT",
                unit_entity_id,
                "artifact-front-matter",
                manifest,
                candidate_digest,
            )
        )

    source_entity_by_id: dict[str, str] = {}
    for source_record in sources:
        entity_id = f"entity.source.{source_record['source_id']}"
        source_entity_by_id[source_record["source_id"]] = entity_id
        entities.append(entity(entity_id, "source", source_record["title"], manifest, candidate_digest))

    for artifact in manifest["artifacts"]:
        front_matter, _ = parse_markdown_front_matter(Path(manifest["_pack_path"]) / artifact["path"])
        for source_id in front_matter["source_refs"]:
            relations.append(
                relation(
                    unit_entity_by_artifact_id[artifact["artifact_id"]],
                    "CITES",
                    source_entity_by_id[source_id],
                    "artifact-front-matter",
                    manifest,
                    candidate_digest,
                )
            )

    entities.sort(key=lambda value: value["entity_id"])
    relations.sort(key=lambda value: value["relation_id"])
    entity_ids = {value["entity_id"] for value in entities}
    if len(entity_ids) != len(entities):
        raise PackError("duplicate graph entity IDs")
    for value in relations:
        if value["source_entity_id"] not in entity_ids or value["target_entity_id"] not in entity_ids:
            raise PackError(f"graph relation has missing endpoint: {value['relation_id']}")
    return entities, relations


def build_catalog(
    manifest: dict[str, Any], source_count: int, candidate_digest: str
) -> dict[str, Any]:
    value = {
        "schema_version": "0.1-draft",
        "projection_status": "review-candidate",
        "pack_id": manifest["pack_id"],
        "version": manifest["version"],
        "candidate_digest": candidate_digest,
        "namespace": manifest["namespace"],
        "title": manifest["title"],
        "description": manifest["description"],
        "lane": manifest["lane"],
        "language": manifest["language"],
        "data_class": manifest["data_class"],
        "risk_tier": manifest["risk_tier"],
        "state": manifest["state"],
        "review_status": manifest["review_status"],
        "license": manifest["license"]["spdx_id"],
        "rights_status": manifest["rights_status"],
        "publisher_status": manifest["publisher"]["status"],
        "action_modes": manifest["action_modes"],
        "permitted_uses": manifest["permitted_uses"],
        "prohibited_uses": manifest["prohibited_uses"],
        "authority": manifest["authority"],
        "intended_audiences": manifest["intended_audiences"],
        "limitations": manifest["limitations"],
        "source_count": source_count,
        "artifact_count": len(manifest["artifacts"]),
    }
    validate_schema(value, "catalog-entry.schema.json", "candidate catalog entry")
    return value


def build_sqlite(path: Path, catalog: dict[str, Any], chunks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            PRAGMA journal_mode=DELETE;
            PRAGMA synchronous=FULL;
            CREATE TABLE pack_versions (
                pack_id TEXT NOT NULL,
                version TEXT NOT NULL,
                candidate_digest TEXT NOT NULL,
                namespace TEXT NOT NULL,
                state TEXT NOT NULL,
                review_status TEXT NOT NULL,
                rights_status TEXT NOT NULL,
                publisher_status TEXT NOT NULL,
                data_class TEXT NOT NULL,
                risk_tier TEXT NOT NULL,
                license TEXT NOT NULL,
                authority_json TEXT NOT NULL,
                permitted_uses_json TEXT NOT NULL,
                prohibited_uses_json TEXT NOT NULL,
                PRIMARY KEY (pack_id, version, candidate_digest)
            );
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                content_unit_id TEXT NOT NULL,
                pack_id TEXT NOT NULL,
                version TEXT NOT NULL,
                candidate_digest TEXT NOT NULL,
                namespace TEXT NOT NULL,
                parser_contract TEXT NOT NULL,
                chunker_version TEXT NOT NULL,
                artifact_id TEXT NOT NULL,
                artifact_path TEXT NOT NULL,
                artifact_digest TEXT NOT NULL,
                section_path_json TEXT NOT NULL,
                unit_source_order INTEGER NOT NULL,
                part_index INTEGER NOT NULL,
                citation_locator TEXT NOT NULL,
                unit_text_digest TEXT NOT NULL,
                text TEXT NOT NULL,
                chunk_digest TEXT NOT NULL,
                source_refs_json TEXT NOT NULL,
                data_class TEXT NOT NULL,
                risk_tier TEXT NOT NULL,
                review_status TEXT NOT NULL,
                lifecycle_state TEXT NOT NULL,
                license TEXT NOT NULL,
                authority_json TEXT NOT NULL,
                permitted_uses_json TEXT NOT NULL,
                prohibited_uses_json TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE chunks_fts USING fts5(
                chunk_id UNINDEXED,
                content_unit_id UNINDEXED,
                artifact_id UNINDEXED,
                section_path,
                text,
                tokenize='unicode61 remove_diacritics 2'
            );
            """
        )
        connection.execute(
            "INSERT INTO pack_versions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                catalog["pack_id"],
                catalog["version"],
                catalog["candidate_digest"],
                catalog["namespace"],
                catalog["state"],
                catalog["review_status"],
                catalog["rights_status"],
                catalog["publisher_status"],
                catalog["data_class"],
                catalog["risk_tier"],
                catalog["license"],
                canonical_json(catalog["authority"]),
                canonical_json(catalog["permitted_uses"]),
                canonical_json(catalog["prohibited_uses"]),
            ),
        )
        for chunk in chunks:
            connection.execute(
                "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    chunk["chunk_id"],
                    chunk["content_unit_id"],
                    chunk["pack_id"],
                    chunk["pack_version"],
                    chunk["candidate_digest"],
                    chunk["namespace"],
                    chunk["parser_contract"],
                    chunk["chunker_version"],
                    chunk["artifact_id"],
                    chunk["artifact_path"],
                    chunk["artifact_digest"],
                    canonical_json(chunk["section_path"]),
                    chunk["unit_source_order"],
                    chunk["part_index"],
                    chunk["citation_locator"],
                    chunk["unit_text_digest"],
                    chunk["text"],
                    chunk["chunk_digest"],
                    canonical_json(chunk["source_refs"]),
                    chunk["data_class"],
                    chunk["risk_tier"],
                    chunk["review_status"],
                    chunk["lifecycle_state"],
                    chunk["license"],
                    canonical_json(chunk["authority"]),
                    canonical_json(chunk["permitted_uses"]),
                    canonical_json(chunk["prohibited_uses"]),
                ),
            )
            connection.execute(
                "INSERT INTO chunks_fts VALUES (?, ?, ?, ?, ?)",
                (
                    chunk["chunk_id"],
                    chunk["content_unit_id"],
                    chunk["artifact_id"],
                    " > ".join(chunk["section_path"]),
                    chunk["text"],
                ),
            )
        connection.commit()
        connection.execute("PRAGMA optimize")
        connection.execute("VACUUM")
    finally:
        connection.close()

    logical_export = canonical_json({"catalog": catalog, "chunks": chunks})
    lock = {
        "schema_version": "0.1-draft",
        "status": "review-candidate-shard",
        "database_filename": path.name,
        "pack_id": catalog["pack_id"],
        "pack_version": catalog["version"],
        "candidate_digest": catalog["candidate_digest"],
        "namespace": catalog["namespace"],
        "declared_state": catalog["state"],
        "review_status": catalog["review_status"],
        "rights_status": catalog["rights_status"],
        "data_class": catalog["data_class"],
        "risk_tier": catalog["risk_tier"],
        "parser_contract": "markdown-front-matter-sections-v1",
        "chunker_version": "structural-scalar-1600-v1",
        "tokenizer": "unicode61 remove_diacritics 2",
        "sqlite_version": sqlite3.sqlite_version,
        "row_count": len(chunks),
        "logical_export_digest": "sha256:" + sha256_bytes(logical_export.encode("utf-8")),
    }
    write_json(path.with_suffix(path.suffix + ".lock.json"), lock)


def build_archive(pack: Path, destination: Path, pack_id: str, version: str) -> None:
    """Create a byte-reproducible review archive with normalized metadata."""
    archive_root = f"{pack_id}-{version}"
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for path in sorted(path for path in pack.rglob("*") if path.is_file()):
            relative = path.relative_to(pack).as_posix()
            info = zipfile.ZipInfo(f"{archive_root}/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits |= 0x800
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(pack: Path, output: Path, sqlite_path: Path) -> dict[str, Any]:
    validate(pack, frozen=False)
    candidate_digest = create_checksum_ledger(pack)
    frozen = validate(pack, frozen=True)
    if frozen["candidate_digest"] != candidate_digest:
        raise PackError("candidate digest changed between freeze and verification")

    manifest = load_yaml(pack / "manifest.yaml")
    manifest["_pack_path"] = str(pack)
    source_records = read_jsonl(pack / manifest["sources_path"])
    chunks = build_chunks(pack, manifest, candidate_digest)
    catalog = build_catalog(manifest, len(source_records), candidate_digest)
    entities, relations = build_graph(manifest, source_records, candidate_digest)
    del manifest["_pack_path"]

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    write_jsonl(output / "chunks.jsonl", chunks)
    write_json(output / "catalog-entry.json", catalog)
    write_jsonl(output / "entities.jsonl", entities)
    write_jsonl(output / "relations.jsonl", relations)
    archive_path = output / f"{catalog['pack_id']}-{catalog['version']}.zip"
    build_archive(pack, archive_path, catalog["pack_id"], catalog["version"])

    derivative_files = [
        archive_path,
        output / "catalog-entry.json",
        output / "chunks.jsonl",
        output / "entities.jsonl",
        output / "relations.jsonl",
    ]
    derivative_digests = {
        path.name: "sha256:" + sha256_file(path) for path in sorted(derivative_files)
    }
    build_sqlite(sqlite_path, catalog, chunks)
    build_manifest = {
        "schema_version": "0.1-draft",
        "status": "review-candidate-derivatives-not-public-catalog",
        "builder": "tools/build_pack.py",
        "builder_contract_version": "2",
        "parser_contract": "markdown-front-matter-sections-v1",
        "chunker_version": "structural-scalar-1600-v1",
        "digest_contract": "sha256-of-canonical-checksum-ledger-v1",
        "pack_id": catalog["pack_id"],
        "pack_version": catalog["version"],
        "candidate_digest": candidate_digest,
        "source_of_truth": "Knowledge Pack files bound by CHECKSUMS.sha256",
        "derivatives_are_disposable": True,
        "public_catalog_modified": False,
        "counts": {
            "artifacts": catalog["artifact_count"],
            "sources": catalog["source_count"],
            "content_units": len({chunk["content_unit_id"] for chunk in chunks}),
            "chunks": len(chunks),
            "entities": len(entities),
            "relations": len(relations),
        },
        "derivative_digests": derivative_digests,
        "sqlite_index": {
            "path": sqlite_path.name,
            "lock_path": sqlite_path.with_suffix(sqlite_path.suffix + ".lock.json").name,
            "tracked": False,
            "byte_determinism_claimed": False,
            "content_rebuildable_from": ["chunks.jsonl", "catalog-entry.json"],
        },
    }
    write_json(output / "build-manifest.json", build_manifest)
    return build_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sqlite", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build(args.pack.resolve(), args.output.resolve(), args.sqlite.resolve())
    except (PackError, OSError, sqlite3.Error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    counts = result["counts"]
    print(
        "PASS: review-only derivatives built for "
        f"{result['pack_id']}@{result['pack_version']} {result['candidate_digest']}; "
        f"{counts['chunks']} chunks, {counts['entities']} entities, {counts['relations']} relations; "
        "public catalog unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
