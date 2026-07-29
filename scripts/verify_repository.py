#!/usr/bin/env python3
"""Fail-closed checks for the NIN Knowledge Commons repository baseline."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    ".nojekyll",
    "CONTRIBUTING.md",
    "DOCTRINE.md",
    "GOVERNANCE.md",
    "LICENSE",
    "LICENSE-DOCUMENTATION.md",
    "NOTICE",
    "PLAYBOOK.md",
    "README.md",
    "SAFETY.md",
    "SECURITY.md",
    "catalog/catalog.json",
    "catalog/entities.jsonl",
    "catalog/relations.jsonl",
    "governance/README.md",
    "index.html",
    "packs/README.md",
    "schemas/README.md",
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HTML_LINK = re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "generic secret key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "US Social Security number": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}
TEXT_SUFFIXES = {"", ".html", ".json", ".jsonl", ".md", ".py", ".txt", ".yml", ".yaml"}


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check_required_files() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {missing}")


def check_custom_domain_gate() -> None:
    if (ROOT / "CNAME").exists():
        fail("CNAME must remain absent until the custom-domain gate")


def check_catalog() -> None:
    catalog = json.loads(read("catalog/catalog.json"))
    if catalog.get("schema_version") != "0.1":
        fail("catalog schema_version must be 0.1")
    if catalog.get("status") != "empty-preview":
        fail("initial catalog status must be empty-preview")
    if catalog.get("packs") != []:
        fail("initial repository must not claim published packs")
    if catalog.get("publication_scope", {}).get("data_class") != ["D0"]:
        fail("initial catalog public data ceiling must be D0")

    for relative in ("catalog/entities.jsonl", "catalog/relations.jsonl"):
        for line_number, line in enumerate(read(relative).splitlines(), start=1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    fail(f"invalid JSONL in {relative}:{line_number}: {exc}")


def link_targets(path: Path, text: str) -> list[str]:
    if path.suffix.lower() == ".md":
        return MARKDOWN_LINK.findall(text)
    if path.suffix.lower() == ".html":
        return HTML_LINK.findall(text)
    return []


def check_links() -> int:
    checked = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in {".md", ".html"}:
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in link_targets(path, text):
            target = raw_target.strip().split()[0].strip("<>\"")
            parsed = urlsplit(target)
            if parsed.scheme in {"http", "https", "mailto", "tel"} or target.startswith("#"):
                continue
            if parsed.scheme or parsed.netloc or target.startswith("/"):
                fail(f"unsupported absolute/local target in {path.relative_to(ROOT)}: {target}")
            relative_target = unquote(parsed.path)
            if not relative_target:
                continue
            resolved = (path.parent / relative_target).resolve()
            if not resolved.is_relative_to(ROOT):
                fail(f"repository-escaping link in {path.relative_to(ROOT)}: {target}")
            if not resolved.exists():
                fail(f"broken link in {path.relative_to(ROOT)}: {target}")
            checked += 1
    return checked


def check_governance_contract() -> None:
    combined = "\n".join(read(path) for path in ("README.md", "DOCTRINE.md", "PLAYBOOK.md", "SAFETY.md"))
    required_phrases = (
        "Content packages are the source of truth",
        "Contributors propose. Reviewers verify. Institutions authorize. Nurses steward.",
        "Unauthorized content must never become a semantic-ranking candidate.",
        "Orange content remains held.",
        "No Knowledge Packs are published",
        "No PHI",
    )
    for phrase in required_phrases:
        if phrase.lower() not in combined.lower():
            fail(f"missing governance contract phrase: {phrase}")

    stale_claims = (
        "no separate Commons repository or hosted catalog has been created",
        "Create a separate repository when implementation begins",
    )
    for phrase in stale_claims:
        if phrase.lower() in combined.lower():
            fail(f"stale incubator claim remains: {phrase}")


def check_public_page() -> None:
    html = read("index.html")
    required = (
        "Repository scaffold",
        "Current catalog: 0 packs",
        "No packs are published yet",
        "min-width: 44px",
        "min-height: 44px",
        "Skip to main content",
    )
    for phrase in required:
        if phrase not in html:
            fail(f"index.html missing required accessibility/status phrase: {phrase}")
    if re.search(r"<script\b", html, re.IGNORECASE):
        fail("baseline public page must remain script-free")


def check_sensitive_patterns() -> int:
    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                fail(f"possible {label} found in {path.relative_to(ROOT)}")
        scanned += 1
    return scanned


def main() -> int:
    try:
        check_required_files()
        check_custom_domain_gate()
        check_catalog()
        links = check_links()
        check_governance_contract()
        check_public_page()
        scanned = check_sensitive_patterns()
    except (AssertionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: required files, empty catalog, governance contract, public page, {links} local links, {scanned} text files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
