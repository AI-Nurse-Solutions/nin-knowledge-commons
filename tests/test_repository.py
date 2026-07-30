#!/usr/bin/env python3
"""Regression contracts for the NIN Knowledge Commons repository baseline."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KnowledgeCommonsRepositoryTests(unittest.TestCase):
    def test_repository_verifier_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/verify_repository.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout)

    def test_catalog_is_explicitly_empty_and_d0(self) -> None:
        catalog = json.loads((ROOT / "catalog/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["status"], "empty-preview")
        self.assertEqual(catalog["packs"], [])
        self.assertEqual(catalog["publication_scope"]["data_class"], ["D0"])
        self.assertEqual(catalog["publication_scope"]["orange_publication"], "held")

    def test_domain_declaration_is_exact(self) -> None:
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8").strip(), "commons.nurse-ai-os.org")

    def test_doctrine_preserves_package_and_authority_maxims(self) -> None:
        doctrine = (ROOT / "DOCTRINE.md").read_text(encoding="utf-8")
        self.assertIn("Content packages are the source of truth", doctrine)
        self.assertIn("Contributors propose. Reviewers verify. Institutions authorize. Nurses steward.", doctrine)
        self.assertIn("Unauthorized content must never become a semantic-ranking candidate.", doctrine)
        self.assertIn("Red-P remains prohibited", doctrine)

    def test_public_page_is_honest_and_script_free(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("Current catalog: 0 packs", html)
        self.assertIn("No packs are published yet", html)
        self.assertNotIn("<script", html.lower())
        self.assertIn("min-width: 44px", html)
        self.assertIn("min-height: 44px", html)

    def test_private_and_active_content_boundaries_are_present(self) -> None:
        contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        safety = (ROOT / "SAFETY.md").read_text(encoding="utf-8")
        self.assertIn("must never enter commits, issues, manifests, catalogs, indexes, graphs, or analytics", contributing)
        self.assertIn("will not install, authorize, or activate", safety)
        self.assertIn("approved sandbox", safety)

    def test_first_pack_scope_is_approved_without_publication_or_translation(self) -> None:
        decision = (ROOT / "governance/decisions/KC-DEC-0001-first-reference-pack.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("AI Literacy Foundations for Nurses", decision)
        self.assertIn("| Language | English |", decision)
        self.assertIn("| Data class | D0 |", decision)
        self.assertIn("| EDENA risk tier | Green |", decision)
        self.assertIn("| Library lane | Learn |", decision)
        self.assertIn("Publication decision: not granted", decision)
        self.assertIn("Tagalog edition: held", decision)
        self.assertIn("stabilized and reviewed before any Tagalog edition is created", decision)

    def test_founder_preflight_authorizes_only_independent_review_exposure(self) -> None:
        preflight = (
            ROOT / "governance/review-candidates/KC-RC-0001/FOUNDER-PREFLIGHT.md"
        ).read_text(encoding="utf-8")
        candidate = json.loads(
            (ROOT / "governance/review-candidates/KC-RC-0001/candidate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("Proceed to a review-only commit and pull request", preflight)
        self.assertIn("Hermes is not independent of the authoring process", preflight)
        self.assertTrue(candidate["founder_preflight"]["review_only_pr_authorized"])
        self.assertFalse(candidate["founder_preflight"]["independent_human_review"])
        approval_state = candidate["approval_state"]
        self.assertTrue(approval_state)
        self.assertTrue(all(value is False for value in approval_state.values()))


if __name__ == "__main__":
    unittest.main()
