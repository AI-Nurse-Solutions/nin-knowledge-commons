#!/usr/bin/env python3
"""Regression contracts for the NIN Knowledge Commons repository baseline."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KnowledgeCommonsRepositoryTests(unittest.TestCase):
    def test_repository_verifier_passes(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/verify_repository.py"],
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
        self.assertEqual((ROOT / "CNAME").read_text(encoding="utf-8"), "commons.nurse-ai-os.org\n")

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


if __name__ == "__main__":
    unittest.main()
