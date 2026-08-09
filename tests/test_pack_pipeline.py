#!/usr/bin/env python3
"""Adversarial contracts for draft Pack validation and schema generation."""

from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/packs/valid-draft"
ACTUAL_PACK = ROOT / "packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1"
ACTUAL_CANDIDATE = ROOT / "governance/review-candidates/KC-RC-0001/candidate.json"
ACTUAL_REVIEW_BRIEF = ROOT / "governance/review-candidates/KC-RC-0001/REVIEW-BRIEF.md"


class DraftPackPipelineTests(unittest.TestCase):
    def run_validator(self, pack: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "tools/validate_pack.py", str(pack), *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def copied_fixture(self, temporary: str) -> Path:
        destination = Path(temporary) / "pack"
        shutil.copytree(FIXTURE, destination)
        files = sorted(
            path for path in destination.rglob("*") if path.is_file() and path.name != "CHECKSUMS.sha256"
        )
        ledger = "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(destination).as_posix()}"
            for path in files
        )
        (destination / "CHECKSUMS.sha256").write_text(ledger + "\n", encoding="utf-8")
        return destination

    def governance_record(
        self, temporary: str, output: Path, *, deny_override: str = "none"
    ) -> tuple[Path, str]:
        build_manifest = json.loads(
            (output / "build-manifest.json").read_text(encoding="utf-8")
        )
        digest = build_manifest["candidate_digest"]
        record = {
            "schema_version": "0.1-draft",
            "candidate_id": "KC-RC-TEST",
            "status": "independent-review-requested",
            "registry_epoch": 1,
            "effective_lifecycle": "recalled" if deny_override == "recalled" else "under-review",
            "deny_override": deny_override,
            "review_access": {
                "authorized": True,
                "mode": "local-exact-digest-review",
            },
            "pack": {
                "pack_id": build_manifest["pack_id"],
                "namespace": build_manifest["pack_id"],
                "pack_version": build_manifest["pack_version"],
                "candidate_digest": digest,
            },
        }
        path = Path(temporary) / "governance-record.json"
        path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
        return path, digest

    def test_schema_builder_is_deterministic_and_schemas_compile(self) -> None:
        before = {
            path.name: path.read_bytes()
            for path in sorted((ROOT / "schemas").glob("*.schema.json"))
        }
        result = subprocess.run(
            [sys.executable, "tools/build_schemas.py"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {
            path.name: path.read_bytes()
            for path in sorted((ROOT / "schemas").glob("*.schema.json"))
        }
        self.assertEqual(before, after)
        for path in sorted((ROOT / "schemas").glob("*.schema.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

        namespace = json.loads((ROOT / "schemas/namespace.schema.json").read_text(encoding="utf-8"))
        risk_ceilings = namespace["properties"]["risk_ceiling"]["enum"]
        self.assertNotIn("Red-P", risk_ceilings)
        self.assertEqual(risk_ceilings, ["Green", "Yellow", "Orange", "Red-E"])

    def test_required_schema_formats_are_actively_checked(self) -> None:
        checker = FormatChecker()
        date_validator = Draft202012Validator(
            {"type": "string", "format": "date-time"}, format_checker=checker
        )
        uri_validator = Draft202012Validator(
            {"type": "string", "format": "uri"}, format_checker=checker
        )
        self.assertTrue(list(date_validator.iter_errors("not-a-date-time")))
        self.assertTrue(list(uri_validator.iter_errors("not a uri")))

    def test_valid_unpublished_draft_passes_source_validation(self) -> None:
        result = self.run_validator(FIXTURE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout)

    def test_unknown_manifest_field_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            manifest_path = pack / "manifest.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["unreviewed_authority_claim"] = "approved"
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Additional properties are not allowed", result.stderr)

    def test_missing_source_reference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            artifact = pack / "content/01-orientation.md"
            text = artifact.read_text(encoding="utf-8").replace(
                "source.test.project", "source.missing"
            )
            artifact.write_text(text, encoding="utf-8")
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown source reference", result.stderr)

    def test_content_unit_identity_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            artifact = pack / "content/01-orientation.md"
            artifact.write_text(
                artifact.read_text(encoding="utf-8").replace(
                    "unit.test.orientation", "unit.test.changed"
                ),
                encoding="utf-8",
            )
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("content_unit_id", result.stderr)

    def test_phi_like_example_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            artifact = pack / "content/01-orientation.md"
            artifact.write_text(
                artifact.read_text(encoding="utf-8") + "\nPatient name: Example Person\n",
                encoding="utf-8",
            )
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PHI-like or patient-specific marker", result.stderr)

    def test_path_traversal_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            manifest_path = pack / "manifest.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"][0]["path"] = "../outside.md"
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result = self.run_validator(pack)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match", result.stderr)

    def test_frozen_mode_requires_checksums(self) -> None:
        result = self.run_validator(FIXTURE, "--frozen")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CHECKSUMS.sha256 is required", result.stderr)

    def test_public_catalog_remains_empty_during_draft_build(self) -> None:
        catalog = json.loads((ROOT / "catalog/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["packs"], [])
        self.assertEqual(catalog["status"], "empty-preview")

    def test_derivative_build_is_deterministic_and_citations_are_exact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            output = Path(temporary) / "derivatives"
            index = Path(temporary) / "local-index/commons.sqlite"
            command = [
                sys.executable,
                "tools/build_pack.py",
                str(pack),
                "--output",
                str(output),
                "--sqlite",
                str(index),
            ]
            first = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            deterministic_names = [
                "build-manifest.json",
                "catalog-entry.json",
                "chunks.jsonl",
                "entities.jsonl",
                "nin.test.learn.ai-literacy-0.1.0-draft.1.zip",
                "relations.jsonl",
            ]
            before = {name: (output / name).read_bytes() for name in deterministic_names}
            second = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            after = {name: (output / name).read_bytes() for name in deterministic_names}
            self.assertEqual(before, after)
            lock_path = index.with_suffix(index.suffix + ".lock.json")
            first_lock = lock_path.read_bytes()
            third = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertEqual(third.returncode, 0, third.stdout + third.stderr)
            self.assertEqual(first_lock, lock_path.read_bytes())

            chunks = [
                json.loads(line)
                for line in (output / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertTrue(chunks)
            self.assertEqual(len(chunks), len({chunk["chunk_id"] for chunk in chunks}))
            self.assertEqual({chunk["content_unit_id"] for chunk in chunks}, {"unit.test.orientation"})
            self.assertEqual(
                {chunk["citation_locator"] for chunk in chunks},
                {
                    "ninpack:nin.test.learn.ai-literacy@0.1.0-draft.1/"
                    "artifact.test.orientation#unit.test.orientation"
                },
            )
            self.assertEqual(
                {chunk["chunker_version"] for chunk in chunks},
                {"structural-scalar-1600-v1"},
            )
            candidate_digests = {chunk["candidate_digest"] for chunk in chunks}
            self.assertEqual(len(candidate_digests), 1)
            self.assertTrue(next(iter(candidate_digests)).startswith("sha256:"))

            entities = [
                json.loads(line)
                for line in (output / "entities.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            relations = [
                json.loads(line)
                for line in (output / "relations.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            entity_ids = {entity["entity_id"] for entity in entities}
            for relation in relations:
                self.assertIn(relation["source_entity_id"], entity_ids)
                self.assertIn(relation["target_entity_id"], entity_ids)

    def test_derivative_build_rejects_body_text_before_first_heading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            artifact = pack / "content/01-orientation.md"
            text = artifact.read_text(encoding="utf-8")
            artifact.write_text(
                text.replace("\n---\n\n#", "\n---\n\nDiscarded preamble.\n\n#", 1),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/build_pack.py",
                    str(pack),
                    "--output",
                    str(Path(temporary) / "derivatives"),
                    "--sqlite",
                    str(Path(temporary) / "index/commons.sqlite"),
                    "--freeze",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("content before first Markdown heading", result.stderr)

    def test_default_derivative_build_never_rewrites_frozen_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            shutil.copytree(ACTUAL_PACK, pack)
            ledger = pack / "CHECKSUMS.sha256"
            before = ledger.read_bytes()
            artifact = pack / "content/01-orientation.md"
            artifact.write_text(
                artifact.read_text(encoding="utf-8") + "\nUnfrozen drift.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/build_pack.py",
                    str(pack),
                    "--output",
                    str(root / "derivatives"),
                    "--sqlite",
                    str(root / "index/commons.sqlite"),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(ledger.read_bytes(), before)

    def test_actual_review_candidate_is_exactly_bound_and_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            shutil.copytree(ACTUAL_PACK, pack)

            validated = self.run_validator(pack, "--frozen")
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

            deterministic_names = [
                "build-manifest.json",
                "catalog-entry.json",
                "chunks.jsonl",
                "entities.jsonl",
                "nin.global.learn.ai-literacy-0.1.0-draft.1.zip",
                "relations.jsonl",
            ]
            outputs: list[Path] = []
            locks: list[bytes] = []
            for label in ("a", "b"):
                output = root / f"derivatives-{label}"
                index = root / f"index-{label}/commons.sqlite"
                built = subprocess.run(
                    [
                        sys.executable,
                        "tools/build_pack.py",
                        str(pack),
                        "--output",
                        str(output),
                        "--sqlite",
                        str(index),
                    ],
                    cwd=ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
                outputs.append(output)
                locks.append(index.with_suffix(index.suffix + ".lock.json").read_bytes())

            for name in deterministic_names:
                with self.subTest(name=name):
                    self.assertEqual((outputs[0] / name).read_bytes(), (outputs[1] / name).read_bytes())
            self.assertEqual(locks[0], locks[1])

            manifest = json.loads((outputs[0] / "build-manifest.json").read_text(encoding="utf-8"))
            candidate = json.loads(ACTUAL_CANDIDATE.read_text(encoding="utf-8"))
            review_brief = ACTUAL_REVIEW_BRIEF.read_text(encoding="utf-8")
            digest = manifest["candidate_digest"]
            self.assertEqual(candidate["pack"]["candidate_digest"], digest)
            self.assertEqual(candidate["pack"]["content_digest"], digest)
            self.assertEqual(candidate["deterministic_derivatives"], manifest["derivative_digests"])
            self.assertIn(digest, review_brief)
            self.assertIn(
                manifest["derivative_digests"]["nin.global.learn.ai-literacy-0.1.0-draft.1.zip"],
                review_brief,
            )
            self.assertFalse(manifest["public_catalog_modified"])
            self.assertEqual(manifest["counts"]["content_units"], 11)
            self.assertEqual(manifest["counts"]["sources"], 9)
            self.assertTrue(candidate["approval_state"])
            self.assertTrue(all(value is False for value in candidate["approval_state"].values()))

    def test_search_fails_closed_without_candidate_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            output = Path(temporary) / "derivatives"
            index = Path(temporary) / "local-index/commons.sqlite"
            built = subprocess.run(
                [
                    sys.executable,
                    "tools/build_pack.py",
                    str(pack),
                    "--output",
                    str(output),
                    "--sqlite",
                    str(index),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            governance_record, digest = self.governance_record(temporary, output)
            base = [
                sys.executable,
                "tools/search_index.py",
                str(index),
                "synthetic paragraph",
                "--namespace",
                "nin.test.learn.ai-literacy",
                "--version",
                "0.1.0-draft.1",
                "--candidate-digest",
                digest,
                "--governance-record",
                str(governance_record),
            ]
            blocked = subprocess.run(base, cwd=ROOT, check=False, capture_output=True, text=True)
            self.assertEqual(blocked.returncode, 3)
            self.assertIn("explicit review-candidate access is required", blocked.stderr)

            allowed = subprocess.run(
                base + ["--allow-review-candidate"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
            payload = json.loads(allowed.stdout)
            self.assertEqual(payload["status"], "review-candidate-results")
            self.assertGreaterEqual(len(payload["results"]), 1)
            citation = payload["results"][0]["citation"]
            self.assertEqual(citation["pack_id"], "nin.test.learn.ai-literacy")
            self.assertEqual(citation["pack_version"], "0.1.0-draft.1")
            self.assertEqual(citation["candidate_digest"], payload["candidate_digest"])
            self.assertEqual(citation["content_unit_id"], "unit.test.orientation")
            self.assertTrue(citation["citation_locator"].endswith("#unit.test.orientation"))

            governance = json.loads(governance_record.read_text(encoding="utf-8"))
            del governance["pack"]["namespace"]
            governance_record.write_text(json.dumps(governance), encoding="utf-8")
            missing_namespace = subprocess.run(
                base + ["--allow-review-candidate"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(missing_namespace.returncode, 3)
            self.assertIn("does not declare an authorized namespace", missing_namespace.stderr)
            governance["pack"]["namespace"] = "nin.test.learn.ai-literacy"
            governance_record.write_text(json.dumps(governance), encoding="utf-8")

            wrong_namespace = subprocess.run(
                [part if part != "nin.test.learn.ai-literacy" else "nin.unauthorized" for part in base]
                + ["--allow-review-candidate"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(wrong_namespace.returncode, 3)
            self.assertIn("does not match governance record", wrong_namespace.stderr)

    def test_recalled_candidate_is_removed_before_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = self.copied_fixture(temporary)
            output = Path(temporary) / "derivatives"
            index = Path(temporary) / "local-index/commons.sqlite"
            built = subprocess.run(
                [
                    sys.executable,
                    "tools/build_pack.py",
                    str(pack),
                    "--output",
                    str(output),
                    "--sqlite",
                    str(index),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            governance_record, digest = self.governance_record(
                temporary, output, deny_override="recalled"
            )
            index.unlink()
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/search_index.py",
                    str(index),
                    "synthetic",
                    "--namespace",
                    "nin.test.learn.ai-literacy",
                    "--version",
                    "0.1.0-draft.1",
                    "--candidate-digest",
                    digest,
                    "--governance-record",
                    str(governance_record),
                    "--allow-review-candidate",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 3)
            self.assertIn("governance deny override is active: recalled", result.stderr)


if __name__ == "__main__":
    unittest.main()
