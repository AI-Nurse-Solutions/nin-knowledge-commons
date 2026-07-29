# Contributing

> **Contribution intake for Knowledge Packs is not operational yet.** Do not submit patient information, private contributor records, school records, employer records, confidential policies, credentials, secrets, or unpublished institutional material through issues or pull requests.

## What may be proposed now

- corrections to the doctrine, playbook, governance, safety, or public site;
- accessibility and localization improvements to repository documentation;
- schema and validator proposals that remain clearly marked as proposals;
- public D0 synthetic fixtures created specifically for testing;
- security findings through the private route in [SECURITY.md](SECURITY.md).

## What may not be submitted now

- PHI or reconstructable patient narratives;
- D1–D4 personal, institutional, regulated, credential, or secret material;
- copyrighted material without documented reuse rights;
- real learner, employee, or patient records;
- institution-branded material implying a partnership or approval that has not been documented;
- clinically consequential or patient-specific tools;
- active content that executes code, macros, network requests, or embedded instructions;
- a Knowledge Pack presented as accepted, reviewed, approved, certified, or institutionally authorized.

## Proposal boundaries

A pull request is a proposal, not publication approval. Automated checks are not human review. Repository inclusion is not endorsement, clinical validation, certification, accreditation, institutional authorization, or permission to change practice.

Contributors retain copyright in their contributions. Code contributions accepted into this repository are provided under Apache-2.0; documentation contributions are provided under CC-BY-4.0 unless an artifact-specific notice states otherwise. Knowledge Pack contribution and licensing terms will be established separately before pack intake opens.

Public attribution must use a display name and contact route the contributor explicitly approves for public use. Private contact or eligibility information must never enter commits, issues, manifests, catalogs, indexes, graphs, or analytics.

## Before opening a pull request

Run:

```bash
python3 scripts/verify_repository.py
python3 -m unittest discover -s tests -v
```

Report the exact commit tested, checks run, unresolved limitations, and whether public behavior or authority claims changed.
