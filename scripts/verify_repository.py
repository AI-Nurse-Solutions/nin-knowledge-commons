#!/usr/bin/env python3
"""Fail-closed checks for the NIN Knowledge Commons repository baseline."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NoReturn
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    ".nojekyll",
    "CNAME",
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
    "governance/decisions/KC-DEC-0001-first-reference-pack.md",
    "governance/review-candidates/KC-RC-0001/FOUNDER-PREFLIGHT.md",
    "governance/review-candidates/KC-RC-0001/REVIEW-BRIEF.md",
    "governance/review-candidates/KC-RC-0001/candidate.json",
    "index.html",
    "namespaces/nin.global.learn.ai-literacy.yaml",
    "packs/README.md",
    "packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1/CHECKSUMS.sha256",
    "packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1/manifest.yaml",
    "requirements-dev.txt",
    "schemas/README.md",
    "schemas/artifact.schema.json",
    "schemas/catalog-entry.schema.json",
    "schemas/chunk.schema.json",
    "schemas/entity.schema.json",
    "schemas/knowledge-pack.schema.json",
    "schemas/namespace.schema.json",
    "schemas/publication-decision.schema.json",
    "schemas/relation.schema.json",
    "schemas/review-record.schema.json",
    "schemas/source-record.schema.json",
    "tests/test_pack_pipeline.py",
    "tools/build_pack.py",
    "tools/build_schemas.py",
    "tools/packlib.py",
    "tools/search_index.py",
    "tools/validate_pack.py",
)

FIRST_PACK = Path("packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1")

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


def fail(message: str) -> NoReturn:
    raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check_required_files() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {missing}")


def check_cname() -> None:
    if read("CNAME").strip() != "commons.nurse-ai-os.org":
        fail("CNAME must contain exactly commons.nurse-ai-os.org")


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


def check_first_pack_decision() -> None:
    decision = read("governance/decisions/KC-DEC-0001-first-reference-pack.md")
    required_phrases = (
        "Approved scope decision",
        "AI Literacy Foundations for Nurses",
        "| Language | English |",
        "| Data class | D0 |",
        "| EDENA risk tier | Green |",
        "| Library lane | Learn |",
        "stabilized and reviewed before any Tagalog edition is created",
        "does **not**",
        "Publication decision: not granted",
        "Tagalog edition: held",
    )
    for phrase in required_phrases:
        if phrase.lower() not in decision.lower():
            fail(f"first Pack decision missing required boundary: {phrase}")


def check_first_pack_candidate() -> None:
    manifest = read((FIRST_PACK / "manifest.yaml").as_posix())
    required_markers = (
        "pack_id: nin.global.learn.ai-literacy",
        "title: AI Literacy Foundations for Nurses",
        "version: 0.1.0-draft.1",
        "state: draft",
        "data_class: D0",
        "risk_tier: Green",
        "review_status: not-reviewed",
        "status: candidate-only",
        "clinical: none",
        "institutional: none",
        "certification: none",
        "translations: []",
    )
    for marker in required_markers:
        if marker not in manifest:
            fail(f"first Pack candidate missing fail-closed marker: {marker}")

    expected_manifest = ROOT / FIRST_PACK / "manifest.yaml"
    manifests = sorted((ROOT / "packs").rglob("manifest.yaml"))
    if manifests != [expected_manifest]:
        fail("Tagalog or another Pack manifest exists before the English candidate is reviewed")


def check_first_pack_checksums() -> None:
    pack = ROOT / FIRST_PACK
    ledger_path = pack / "CHECKSUMS.sha256"
    entries: dict[str, str] = {}
    for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            fail(f"malformed first Pack checksum at line {line_number}")
        digest, relative = match.groups()
        path = (pack / relative).resolve()
        if not path.is_relative_to(pack.resolve()) or not path.is_file():
            fail(f"invalid first Pack checksum path: {relative}")
        if relative == "CHECKSUMS.sha256" or relative in entries:
            fail(f"invalid or duplicate first Pack checksum entry: {relative}")
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest != digest:
            fail(f"first Pack checksum mismatch: {relative}")
        entries[relative] = digest

    expected = {
        path.relative_to(pack).as_posix()
        for path in pack.rglob("*")
        if path.is_file() and path.name != "CHECKSUMS.sha256"
    }
    if set(entries) != expected:
        fail(
            "first Pack checksum inventory mismatch; "
            f"missing={sorted(expected - set(entries))}, extra={sorted(set(entries) - expected)}"
        )


def check_founder_preflight() -> None:
    candidate = json.loads(read("governance/review-candidates/KC-RC-0001/candidate.json"))
    preflight = read("governance/review-candidates/KC-RC-0001/FOUNDER-PREFLIGHT.md")
    review_brief = read("governance/review-candidates/KC-RC-0001/REVIEW-BRIEF.md")
    ledger = (ROOT / FIRST_PACK / "CHECKSUMS.sha256").read_bytes()
    digest = "sha256:" + hashlib.sha256(ledger).hexdigest()

    if candidate.get("pack", {}).get("candidate_digest") != digest:
        fail("founder-preflight candidate digest does not match the frozen Pack")
    if candidate.get("pack", {}).get("content_digest") != digest:
        fail("founder-preflight content digest does not match the frozen Pack")
    founder = candidate.get("founder_preflight")
    if not isinstance(founder, dict):
        fail("candidate record lacks a founder-preflight disposition")
    expected = {
        "status": "proceed-to-independent-human-review",
        "record": "governance/review-candidates/KC-RC-0001/FOUNDER-PREFLIGHT.md",
        "review_sponsor": "Robert Domondon",
        "performed_by": "Hermes, AI-assisted founder preflight",
        "independent_human_review": False,
        "review_only_pr_authorized": True,
    }
    for key, value in expected.items():
        if founder.get(key) != value:
            fail(f"founder-preflight candidate field mismatch: {key}")

    approval_state = candidate.get("approval_state")
    if not isinstance(approval_state, dict) or any(value is not False for value in approval_state.values()):
        fail("review-only authorization must leave every approval state false")

    required_phrases = (
        digest,
        "Proceed to a review-only commit and pull request for independent human review.",
        "Hermes is not independent of the authoring process",
        "does not accept the Pack",
        "does not authorize merge",
        "does not authorize deployment",
        "published Pack count remains **0**",
    )
    for phrase in required_phrases:
        if phrase not in preflight:
            fail(f"founder preflight missing required boundary: {phrase}")
    if digest not in review_brief:
        fail("independent review brief is not bound to the founder-preflight digest")


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
        check_cname()
        check_catalog()
        links = check_links()
        check_governance_contract()
        check_first_pack_decision()
        check_first_pack_candidate()
        check_first_pack_checksums()
        check_founder_preflight()
        check_public_page()
        scanned = check_sensitive_patterns()
    except (AssertionError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"PASS: required files, empty catalog, governance contract, public page, {links} local links, {scanned} text files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
