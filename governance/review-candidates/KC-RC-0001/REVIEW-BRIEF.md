# KC-RC-0001 — Independent review brief

## Decision requested

Review the exact English **AI Literacy Foundations for Nurses v0.1.0-draft.1** candidate and return one bounded decision for each declared review scope: **approve, revise, reject, or defer**.

This is a review request—not publication approval, schema adoption, certification, clinical validation, institutional authorization, or permission to translate.

## Exact candidate

```text
Pack ID:           nin.global.learn.ai-literacy
Version:           0.1.0-draft.1
Candidate digest:  sha256:5f423157c79cd41b21a3b6b88a4dc6ec52b894b2de1c8da717352bfeb9329573
Checksum ledger:   packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1/CHECKSUMS.sha256
Review ZIP digest: sha256:fbdd7425d8214e54687b97dc402cab0365a994ae6e52cf6a41da1d40f4018b7c
Data/risk/lane:    D0 / Green / Learn
Language:          English
Authority:         no clinical, institutional, or certification authority
```

The candidate contains 11 artifacts, 11 explicit durable source units, and 9 source records. Local rebuilds generate 135 disposable deterministic chunks, 37 registry entities, and 65 provenance relations.

## Integrity preflight

Run from the repository root in a clean environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-deps --requirement requirements-dev.txt
.venv/bin/python tools/build_schemas.py
.venv/bin/python tools/validate_pack.py \
  packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1 \
  --frozen
.venv/bin/python tools/build_pack.py \
  packs/learn/nin.global.learn.ai-literacy/v0.1.0-draft.1 \
  --output /tmp/nin-kc-review-build \
  --sqlite /tmp/nin-kc-review-index/commons.sqlite
.venv/bin/python -m unittest discover -s tests -v
```

The frozen validator must report the exact candidate digest above. If any byte differs, stop: the review is no longer bound to KC-RC-0001.

## Reviewer declaration

Each reviewer must record:

- public display name and role;
- declared competence for the review scope;
- whether the reviewer is independent of the author;
- conflicts of interest or limitations;
- exact candidate digest inspected;
- materials and methods inspected;
- findings with file and section references;
- decision: approve, revise, reject, or defer;
- whether re-review is required after changes.

An AI system may assist analysis but cannot serve as the required independent human reviewer or approve its own output.

## Required review scopes

### 1. Rights and provenance

- Verify all nine source records against current authoritative locations.
- Confirm titles, issuers, dates, identifiers, URLs, licenses, and use posture.
- Confirm the Pack contains original synthesis rather than unlicensed copied passages.
- Confirm CC BY 4.0 is compatible with the original Pack content and notices.
- Identify any claim whose rights or provenance are unclear.

### 2. EDENA classification and authority

- Confirm D0, Green, and Observe/Draft boundaries.
- Confirm examples contain no PHI, private learner data, employer-confidential material, credentials, or real identifiable narratives.
- Confirm the Pack does not drift into patient-specific advice, clinical decision support, institutional policy, grading, certification, or competency determination.
- Confirm clinical, institutional, and certification authority remain `none`.

### 3. Educational quality and nursing relevance

- Check conceptual accuracy, coherence, sequence, learning objectives, knowledge checks, and synthetic exercises.
- Identify overstatements, missing foundations, misleading simplifications, or unnecessary repetition.
- Confirm bedside usefulness without implying clinical authority.

### 4. Accessibility and plain language

- Check heading hierarchy, tables, code blocks, link text, reading load, jargon, and glossary support.
- Identify language that may exclude learners or obscure uncertainty.
- Recommend changes without flattening necessary governance boundaries.

### 5. Technical integrity and retrieval

- Rebuild schemas, checksum validation, chunks, candidate catalog, registry graph, and SQLite/FTS5 index.
- Confirm explicit durable source-unit IDs remain stable even when headings or chunk boundaries change.
- Confirm generated chunk IDs are disposable retrieval locators and are not treated as canonical citation targets.
- Confirm each derivative binds to the exact Pack ID, version, source location, and candidate digest.
- Confirm the external governance record and shard lock authorize the exact namespace/version/digest before SQLite is opened.
- Confirm wrong namespaces, unpublished candidates, and recalled states are excluded before ranking.
- Confirm the public `catalog/catalog.json` remains empty.

### 6. Source currency and claim support

- Check each material claim against its cited source.
- Identify claims not supported by the listed source, changes since verification, or missing qualifications.
- Confirm WHO, HHS, ANA, and ICN sources are used citation-only and that NIST material is original synthesis.
- Surface conflicts and uncertainty rather than resolving them by assertion.

## Review outcomes

- **Approve:** suitable for the stated review scope at this exact digest; does not authorize publication.
- **Revise:** findings require source changes; any changed byte creates a new digest and requires renewed review.
- **Reject:** unsuitable for the stated scope.
- **Defer:** reviewer lacks evidence, competence, independence, or time to decide.

Approval in one scope does not imply approval in another. All required scopes and a separate founder publication decision remain necessary.

## Translation hold

No Tagalog edition may be created from this draft. Localization may begin only after an exact stable English release is independently reviewed and separately approved as the translation source.

## Governing doctrine

> Contributors propose. Reviewers verify. Institutions authorize. Nurses steward.

> Agents propose. Humans judge. Nurses steward.
