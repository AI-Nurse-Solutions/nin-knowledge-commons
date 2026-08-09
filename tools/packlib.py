#!/usr/bin/env python3
"""Shared deterministic helpers for Knowledge Pack tooling."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


class PackError(ValueError):
    """A fail-closed Pack validation error."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PackError(f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PackError(f"YAML document must be an object: {path}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS / name
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackError(f"cannot read schema {name}: {exc}") from exc
    Draft202012Validator.check_schema(value)
    return value


def validate_schema(value: Any, schema_name: str, label: str) -> None:
    validator = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise PackError(f"{label} schema error at {location}: {error.message}")


def parse_markdown_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise PackError(f"cannot read Markdown {path}: {exc}") from exc
    if not text.startswith("---\n"):
        raise PackError(f"Markdown front matter is required: {path}")
    try:
        raw_front_matter, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise PackError(f"Markdown front matter is not closed: {path}") from exc
    try:
        front_matter = yaml.safe_load(raw_front_matter)
    except yaml.YAMLError as exc:
        raise PackError(f"invalid Markdown front matter in {path}: {exc}") from exc
    if not isinstance(front_matter, dict):
        raise PackError(f"Markdown front matter must be an object: {path}")
    return front_matter, body.lstrip("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise PackError(f"cannot read JSONL {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PackError(f"invalid JSONL {path}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise PackError(f"JSONL record must be an object: {path}:{line_number}")
        records.append(value)
    return records


def resolve_inside(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    resolved_root = root.resolve()
    if not candidate.is_relative_to(resolved_root):
        raise PackError(f"path escapes Pack root: {relative}")
    return candidate
