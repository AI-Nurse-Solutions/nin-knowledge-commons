#!/usr/bin/env python3
"""Deterministically build draft Knowledge Commons JSON Schemas.

These schemas are proposals. Building or validating them does not adopt them.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "schemas"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
ID = r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$"
VERSION = r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$"
DIGEST = r"^sha256:[0-9a-f]{64}$"
LANGUAGE = r"^[a-z]{2,3}(?:-[A-Z]{2})?$"
SAFE_PATH = r"^(?!/)(?!.*\.\.)[^\\]+$"
LANES = ["Learn", "Practice", "Lead", "Build"]
DATA_CLASSES = ["D0", "D1", "D2", "D3", "D4"]
RISK_TIERS = ["Green", "Yellow", "Orange", "Red-P", "Red-E"]
# Red-P is prohibited and therefore cannot be a namespace risk ceiling.
NAMESPACE_RISK_CEILINGS = [tier for tier in RISK_TIERS if tier != "Red-P"]
ACTION_MODES = [
    "Observe",
    "Draft",
    "Recommend",
    "Prepare Action",
    "Act With Approval",
    "Constrained Autonomy",
]
AUDIENCES = [
    "student-nurse",
    "staff-nurse",
    "nurse-educator",
    "nurse-leader",
    "nurse-informaticist",
]
ARTIFACT_TYPES = ["orientation", "lesson", "practice-exercise", "glossary", "assessment"]


def base(schema_id: str, title: str, required: list[str], properties: dict) -> dict:
    return {
        "$schema": DIALECT,
        "$id": f"https://commons.nurse-ai-os.org/schemas/{schema_id}",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


def nonempty_string() -> dict:
    return {"type": "string", "minLength": 1}


def string_list(*, min_items: int = 0, unique: bool = False) -> dict:
    value = {"type": "array", "items": nonempty_string()}
    if min_items:
        value["minItems"] = min_items
    if unique:
        value["uniqueItems"] = True
    return value


def enum_list(values: list[str], *, min_items: int = 1) -> dict:
    return {
        "type": "array",
        "minItems": min_items,
        "uniqueItems": True,
        "items": {"enum": values},
    }


def schemas() -> dict[str, dict]:
    namespace = base(
        "namespace.schema.json",
        "NIN Knowledge Commons namespace record",
        [
            "schema_version",
            "namespace_id",
            "title",
            "visibility",
            "steward",
            "eligible_lanes",
            "data_ceiling",
            "risk_ceiling",
            "status",
            "limitations",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "namespace_id": {"type": "string", "pattern": ID},
            "title": nonempty_string(),
            "visibility": {"enum": ["public", "partner", "private", "commercial"]},
            "steward": {
                "type": "object",
                "additionalProperties": False,
                "required": ["display_name", "role"],
                "properties": {"display_name": nonempty_string(), "role": nonempty_string()},
            },
            "locality": nonempty_string(),
            "jurisdiction": nonempty_string(),
            "eligible_lanes": enum_list(LANES),
            "data_ceiling": {"enum": DATA_CLASSES},
            "risk_ceiling": {"enum": NAMESPACE_RISK_CEILINGS},
            "status": {"enum": ["proposed", "approved", "suspended", "retired"]},
            "limitations": string_list(min_items=1),
        },
    )

    source = base(
        "source-record.schema.json",
        "Knowledge Pack source record",
        [
            "schema_version",
            "source_id",
            "title",
            "creator",
            "publisher",
            "publication_date",
            "url",
            "source_type",
            "reuse_status",
            "use_in_pack",
            "verified_at",
            "claims_supported",
            "limitations",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "source_id": {"type": "string", "pattern": ID},
            "title": nonempty_string(),
            "creator": nonempty_string(),
            "publisher": nonempty_string(),
            "publication_date": {
                "type": ["string", "null"],
                "pattern": r"^\d{4}(?:-\d{2}-\d{2})?$",
            },
            "url": {"type": "string", "format": "uri", "pattern": "^https://"},
            "source_type": {
                "enum": [
                    "framework",
                    "guidance",
                    "regulation-summary",
                    "professional-guidance",
                    "position-statement",
                    "project-doctrine",
                    "project-playbook",
                    "research",
                    "web-page",
                ]
            },
            "identifier": {"type": ["string", "null"]},
            "license": {"type": ["string", "null"]},
            "reuse_status": {
                "enum": [
                    "original-project-source",
                    "public-domain-or-government-work",
                    "open-license",
                    "citation-only",
                    "rights-unclear",
                ]
            },
            "use_in_pack": {
                "enum": [
                    "original-synthesis-and-citation",
                    "citation-only",
                    "adaptation-with-attribution",
                ]
            },
            "verified_at": {"type": "string", "format": "date-time"},
            "claims_supported": string_list(min_items=1),
            "limitations": string_list(),
        },
    )

    artifact = base(
        "artifact.schema.json",
        "Knowledge Pack Markdown artifact front matter",
        [
            "schema_version",
            "artifact_id",
            "content_unit_id",
            "title",
            "artifact_type",
            "language",
            "audiences",
            "learning_objectives",
            "source_refs",
            "limitations",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "artifact_id": {"type": "string", "pattern": ID},
            "content_unit_id": {"type": "string", "pattern": ID},
            "title": nonempty_string(),
            "artifact_type": {"enum": ARTIFACT_TYPES},
            "language": {"type": "string", "pattern": LANGUAGE},
            "audiences": enum_list(AUDIENCES),
            "learning_objectives": string_list(min_items=1),
            "source_refs": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": ID},
            },
            "keywords": string_list(unique=True),
            "limitations": string_list(min_items=1),
        },
    )

    review = base(
        "review-record.schema.json",
        "Knowledge Pack review record",
        [
            "schema_version",
            "review_id",
            "pack_id",
            "pack_version",
            "candidate_digest",
            "review_type",
            "reviewer",
            "scope",
            "materials_inspected",
            "findings",
            "limitations",
            "decision",
            "reviewed_at",
            "re_review_required",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "review_id": {"type": "string", "pattern": ID},
            "pack_id": {"type": "string", "pattern": ID},
            "pack_version": {"type": "string", "pattern": VERSION},
            "candidate_digest": {"type": "string", "pattern": DIGEST},
            "review_type": {
                "enum": [
                    "rights-provenance",
                    "edena-data-action",
                    "educational-quality",
                    "accessibility",
                    "technical-integrity",
                    "localization",
                    "publication",
                ]
            },
            "reviewer": {
                "type": "object",
                "additionalProperties": False,
                "required": ["display_name", "role", "declared_competence", "independent_of_author"],
                "properties": {
                    "display_name": nonempty_string(),
                    "role": nonempty_string(),
                    "declared_competence": nonempty_string(),
                    "independent_of_author": {"type": "boolean"},
                },
            },
            "scope": nonempty_string(),
            "materials_inspected": string_list(min_items=1),
            "findings": string_list(),
            "limitations": string_list(min_items=1),
            "decision": {"enum": ["approve", "revise", "reject", "defer"]},
            "reviewed_at": {"type": "string", "format": "date-time"},
            "review_due": {"type": ["string", "null"], "format": "date"},
            "re_review_required": {"type": "boolean"},
        },
    )

    publication_decision = base(
        "publication-decision.schema.json",
        "External human Knowledge Pack publication decision",
        [
            "schema_version",
            "decision_id",
            "pack_id",
            "pack_version",
            "content_digest",
            "distribution_digest",
            "decision_maker",
            "authority_scope",
            "decision",
            "limitations",
            "unresolved_findings",
            "decided_at",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "decision_id": {"type": "string", "pattern": ID},
            "pack_id": {"type": "string", "pattern": ID},
            "pack_version": {"type": "string", "pattern": VERSION},
            "content_digest": {"type": "string", "pattern": DIGEST},
            "distribution_digest": {"type": "string", "pattern": DIGEST},
            "decision_maker": {
                "type": "object",
                "additionalProperties": False,
                "required": ["display_name", "role", "authority_basis"],
                "properties": {
                    "display_name": nonempty_string(),
                    "role": nonempty_string(),
                    "authority_basis": nonempty_string(),
                },
            },
            "authority_scope": string_list(min_items=1),
            "decision": {"enum": ["approve", "reject", "defer"]},
            "limitations": string_list(),
            "unresolved_findings": string_list(),
            "decided_at": {"type": "string", "format": "date-time"},
        },
    )

    manifest = base(
        "knowledge-pack.schema.json",
        "NIN Knowledge Pack manifest",
        [
            "schema_version",
            "pack_id",
            "namespace",
            "title",
            "version",
            "state",
            "lane",
            "role",
            "language",
            "data_class",
            "risk_tier",
            "action_modes",
            "description",
            "intended_audiences",
            "permitted_uses",
            "prohibited_uses",
            "authority",
            "creator",
            "publisher",
            "license",
            "rights_status",
            "artifacts",
            "sources_path",
            "review_status",
            "review_records",
            "ai_disclosure",
            "limitations",
            "lifecycle",
            "relationships",
            "integrity",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "pack_id": {"type": "string", "pattern": ID},
            "namespace": {"type": "string", "pattern": ID},
            "title": nonempty_string(),
            "version": {"type": "string", "pattern": VERSION},
            "state": {
                "enum": [
                    "draft",
                    "submitted",
                    "quarantined",
                    "under_review",
                    "changes_requested",
                    "accepted_for_scope",
                    "published",
                    "superseded",
                    "retired",
                    "recalled",
                    "withdrawn",
                ]
            },
            "lane": {"enum": LANES},
            "role": {"enum": ["reference-pack", "community-pack", "institutional-pack"]},
            "language": {"type": "string", "pattern": LANGUAGE},
            "data_class": {"enum": DATA_CLASSES},
            "risk_tier": {"enum": RISK_TIERS},
            "action_modes": enum_list(ACTION_MODES),
            "description": nonempty_string(),
            "intended_audiences": string_list(min_items=1, unique=True),
            "permitted_uses": string_list(min_items=1),
            "prohibited_uses": string_list(min_items=1),
            "authority": {
                "type": "object",
                "additionalProperties": False,
                "required": ["clinical", "institutional", "certification"],
                "properties": {
                    "clinical": {"const": "none"},
                    "institutional": {"const": "none"},
                    "certification": {"const": "none"},
                },
            },
            "locality": nonempty_string(),
            "jurisdiction": nonempty_string(),
            "creator": {
                "type": "object",
                "additionalProperties": False,
                "required": ["display_name", "role", "rights_holder"],
                "properties": {
                    "display_name": nonempty_string(),
                    "role": nonempty_string(),
                    "rights_holder": nonempty_string(),
                },
            },
            "publisher": {
                "type": "object",
                "additionalProperties": False,
                "required": ["display_name", "status"],
                "properties": {
                    "display_name": nonempty_string(),
                    "status": {"enum": ["not-published", "candidate-only", "published"]},
                },
            },
            "license": {
                "type": "object",
                "additionalProperties": False,
                "required": ["spdx_id", "path"],
                "properties": {
                    "spdx_id": nonempty_string(),
                    "path": {"type": "string", "pattern": SAFE_PATH},
                },
            },
            "rights_status": {"enum": ["draft-rights-review-pending", "rights-reviewed"]},
            "artifacts": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "artifact_id",
                        "content_unit_id",
                        "path",
                        "title",
                        "artifact_type",
                        "language",
                    ],
                    "properties": {
                        "artifact_id": {"type": "string", "pattern": ID},
                        "content_unit_id": {"type": "string", "pattern": ID},
                        "path": {"type": "string", "pattern": r"^content/(?!.*\.\.)[^\\]+\.md$"},
                        "title": nonempty_string(),
                        "artifact_type": {"enum": ARTIFACT_TYPES},
                        "language": {"type": "string", "pattern": LANGUAGE},
                    },
                },
            },
            "sources_path": {"const": "sources/sources.jsonl"},
            "review_status": {
                "enum": [
                    "not-reviewed",
                    "review-requested",
                    "changes-requested",
                    "reviewed-for-stated-scope",
                ]
            },
            "review_records": {
                "type": "array",
                "uniqueItems": True,
                "items": {"type": "string", "pattern": r"^reviews/(?!.*\.\.)[^\\]+\.ya?ml$"},
            },
            "ai_disclosure": {
                "type": "object",
                "additionalProperties": False,
                "required": ["used", "purposes", "human_verification_status"],
                "properties": {
                    "used": {"type": "boolean"},
                    "purposes": string_list(),
                    "human_verification_status": {"enum": ["pending", "partial", "complete"]},
                },
            },
            "limitations": string_list(min_items=1),
            "lifecycle": {
                "type": "object",
                "additionalProperties": False,
                "required": ["created_at", "published_at", "supersedes", "retirement_notice", "recall_notice"],
                "properties": {
                    "created_at": {"type": "string", "format": "date-time"},
                    "published_at": {"type": ["string", "null"], "format": "date-time"},
                    "supersedes": {"type": ["string", "null"]},
                    "retirement_notice": {"type": ["string", "null"]},
                    "recall_notice": {"type": ["string", "null"]},
                },
            },
            "relationships": {
                "type": "object",
                "additionalProperties": False,
                "required": ["translations", "derived_from", "prerequisites", "related_packs"],
                "properties": {
                    "translations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["pack_id", "version", "source_digest"],
                            "properties": {
                                "pack_id": {"type": "string", "pattern": ID},
                                "version": {"type": "string", "pattern": VERSION},
                                "source_digest": {"type": "string", "pattern": DIGEST},
                            },
                        },
                    },
                    "derived_from": {"type": "array", "items": {"type": "string", "pattern": ID}},
                    "prerequisites": {"type": "array", "items": {"type": "string", "pattern": ID}},
                    "related_packs": {"type": "array", "items": {"type": "string", "pattern": ID}},
                },
            },
            "integrity": {
                "type": "object",
                "additionalProperties": False,
                "required": ["algorithm", "checksums_path", "candidate_digest"],
                "properties": {
                    "algorithm": {"const": "sha256"},
                    "checksums_path": {"const": "CHECKSUMS.sha256"},
                    "candidate_digest": {"type": ["string", "null"], "pattern": DIGEST},
                },
            },
        },
    )
    manifest["allOf"] = [
        {
            "if": {"properties": {"state": {"const": "published"}}},
            "then": {
                "properties": {
                    "publisher": {"properties": {"status": {"const": "published"}}},
                    "review_status": {"const": "reviewed-for-stated-scope"},
                    "review_records": {"minItems": 1},
                    "rights_status": {"const": "rights-reviewed"},
                    "lifecycle": {"properties": {"published_at": {"type": "string"}}},
                    "integrity": {
                        "properties": {
                            "candidate_digest": {"type": "string", "pattern": DIGEST}
                        }
                    },
                }
            },
        },
        {
            "if": {"properties": {"data_class": {"const": "D0"}}},
            "then": {"properties": {"risk_tier": {"enum": ["Green", "Yellow"]}}},
        },
        {
            "if": {
                "properties": {
                    "state": {"enum": ["draft", "submitted", "under_review", "changes_requested"]}
                }
            },
            "then": {
                "properties": {
                    "publisher": {
                        "properties": {"status": {"enum": ["not-published", "candidate-only"]}}
                    }
                }
            },
        },
    ]

    chunk = base(
        "chunk.schema.json",
        "Deterministic Knowledge Pack chunk",
        [
            "schema_version",
            "chunk_id",
            "content_unit_id",
            "pack_id",
            "pack_version",
            "candidate_digest",
            "parser_contract",
            "chunker_version",
            "namespace",
            "artifact_id",
            "artifact_path",
            "artifact_digest",
            "section_path",
            "unit_source_order",
            "part_index",
            "citation_locator",
            "unit_text_digest",
            "text",
            "language",
            "lane",
            "data_class",
            "risk_tier",
            "action_modes",
            "review_status",
            "lifecycle_state",
            "license",
            "permitted_uses",
            "prohibited_uses",
            "authority",
            "source_refs",
            "chunk_digest",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "chunk_id": {"type": "string", "pattern": ID},
            "content_unit_id": {"type": "string", "pattern": ID},
            "pack_id": {"type": "string", "pattern": ID},
            "pack_version": {"type": "string", "pattern": VERSION},
            "candidate_digest": {"type": "string", "pattern": DIGEST},
            "parser_contract": {"const": "markdown-front-matter-sections-v1"},
            "chunker_version": {"const": "structural-scalar-1600-v1"},
            "namespace": {"type": "string", "pattern": ID},
            "artifact_id": {"type": "string", "pattern": ID},
            "artifact_path": nonempty_string(),
            "artifact_digest": {"type": "string", "pattern": DIGEST},
            "section_path": string_list(min_items=1),
            "unit_source_order": {"type": "integer", "minimum": 0},
            "part_index": {"type": "integer", "minimum": 0},
            "citation_locator": {
                "type": "string",
                "pattern": r"^ninpack:[A-Za-z0-9][A-Za-z0-9._-]*@[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*#[A-Za-z0-9][A-Za-z0-9._-]*$",
            },
            "unit_text_digest": {"type": "string", "pattern": DIGEST},
            "text": {"type": "string", "minLength": 1, "maxLength": 1600},
            "language": nonempty_string(),
            "lane": {"enum": LANES},
            "data_class": {"enum": DATA_CLASSES},
            "risk_tier": {"enum": RISK_TIERS},
            "action_modes": enum_list(ACTION_MODES),
            "review_status": nonempty_string(),
            "lifecycle_state": nonempty_string(),
            "license": nonempty_string(),
            "permitted_uses": string_list(min_items=1),
            "prohibited_uses": string_list(min_items=1),
            "authority": {
                "type": "object",
                "additionalProperties": False,
                "required": ["clinical", "institutional", "certification"],
                "properties": {
                    "clinical": {"const": "none"},
                    "institutional": {"const": "none"},
                    "certification": {"const": "none"},
                },
            },
            "source_refs": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {"type": "string", "pattern": ID},
            },
            "chunk_digest": {"type": "string", "pattern": DIGEST},
        },
    )

    catalog = base(
        "catalog-entry.schema.json",
        "Knowledge Pack catalog projection",
        [
            "schema_version",
            "projection_status",
            "pack_id",
            "version",
            "candidate_digest",
            "namespace",
            "title",
            "description",
            "lane",
            "language",
            "data_class",
            "risk_tier",
            "state",
            "review_status",
            "license",
            "rights_status",
            "publisher_status",
            "action_modes",
            "permitted_uses",
            "prohibited_uses",
            "authority",
            "intended_audiences",
            "limitations",
            "source_count",
            "artifact_count",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "projection_status": {"enum": ["review-candidate", "published"]},
            "pack_id": {"type": "string", "pattern": ID},
            "version": {"type": "string", "pattern": VERSION},
            "candidate_digest": {"type": "string", "pattern": DIGEST},
            "namespace": {"type": "string", "pattern": ID},
            "title": nonempty_string(),
            "description": nonempty_string(),
            "lane": {"enum": LANES},
            "language": nonempty_string(),
            "data_class": {"enum": DATA_CLASSES},
            "risk_tier": {"enum": RISK_TIERS},
            "state": nonempty_string(),
            "review_status": nonempty_string(),
            "license": nonempty_string(),
            "rights_status": nonempty_string(),
            "publisher_status": nonempty_string(),
            "action_modes": enum_list(ACTION_MODES),
            "permitted_uses": string_list(min_items=1),
            "prohibited_uses": string_list(min_items=1),
            "authority": {
                "type": "object",
                "additionalProperties": False,
                "required": ["clinical", "institutional", "certification"],
                "properties": {
                    "clinical": {"const": "none"},
                    "institutional": {"const": "none"},
                    "certification": {"const": "none"},
                },
            },
            "intended_audiences": string_list(min_items=1),
            "limitations": string_list(min_items=1),
            "source_count": {"type": "integer", "minimum": 1},
            "artifact_count": {"type": "integer", "minimum": 1},
        },
    )

    entity = base(
        "entity.schema.json",
        "Registry graph entity",
        [
            "schema_version",
            "entity_id",
            "entity_type",
            "label",
            "pack_id",
            "pack_version",
            "candidate_digest",
            "lifecycle_state",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "entity_id": {"type": "string", "pattern": ID},
            "entity_type": {
                "enum": [
                    "pack",
                    "version",
                    "artifact",
                    "source-unit",
                    "source",
                    "creator",
                    "review",
                    "license",
                    "subject",
                    "language",
                    "namespace",
                ]
            },
            "label": nonempty_string(),
            "pack_id": {"type": "string", "pattern": ID},
            "pack_version": {"type": "string", "pattern": VERSION},
            "candidate_digest": {"type": "string", "pattern": DIGEST},
            "lifecycle_state": nonempty_string(),
        },
    )

    relation = base(
        "relation.schema.json",
        "Registry graph relation",
        [
            "schema_version",
            "relation_id",
            "source_entity_id",
            "predicate",
            "target_entity_id",
            "pack_id",
            "pack_version",
            "candidate_digest",
            "provenance",
            "review_status",
        ],
        {
            "schema_version": {"const": "0.1-draft"},
            "relation_id": {"type": "string", "pattern": ID},
            "source_entity_id": {"type": "string", "pattern": ID},
            "predicate": {
                "enum": [
                    "HAS_VERSION",
                    "CONTAINS_ARTIFACT",
                    "CONTAINS_UNIT",
                    "CITES",
                    "CREATED_BY",
                    "REVIEWED_BY",
                    "LICENSED_UNDER",
                    "TRANSLATION_OF",
                    "DERIVED_FROM",
                    "SUPERSEDES",
                    "IN_NAMESPACE",
                    "IN_LANGUAGE",
                ]
            },
            "target_entity_id": {"type": "string", "pattern": ID},
            "pack_id": {"type": "string", "pattern": ID},
            "pack_version": {"type": "string", "pattern": VERSION},
            "candidate_digest": {"type": "string", "pattern": DIGEST},
            "provenance": {
                "enum": [
                    "manifest",
                    "artifact-front-matter",
                    "source-ledger",
                    "review-record",
                    "human-curated",
                ]
            },
            "review_status": nonempty_string(),
        },
    )

    return {
        "namespace.schema.json": namespace,
        "source-record.schema.json": source,
        "artifact.schema.json": artifact,
        "review-record.schema.json": review,
        "publication-decision.schema.json": publication_decision,
        "knowledge-pack.schema.json": manifest,
        "chunk.schema.json": chunk,
        "catalog-entry.schema.json": catalog,
        "entity.schema.json": entity,
        "relation.schema.json": relation,
    }


def build() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for name, data in sorted(schemas().items()):
        path = OUT / name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    files = build()
    print(f"Built {len(files)} draft schemas")
