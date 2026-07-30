---
title: "KC-RC-0001: Founder preflight for independent human review"
status: "Proceed to independent human review"
version: "1.0"
recorded_at: "2026-07-30T05:22:14Z"
candidate_digest: "sha256:5f423157c79cd41b21a3b6b88a4dc6ec52b894b2de1c8da717352bfeb9329573"
review_zip_digest: "sha256:fbdd7425d8214e54687b97dc402cab0365a994ae6e52cf6a41da1d40f4018b7c"
---

# KC-RC-0001 founder preflight

## Disposition

**Proceed to a review-only commit and pull request for independent human review.**

This disposition applies only to the exact candidate digest above. It does not accept the Pack, adopt a schema, complete independent review, approve publication, populate the public catalog, authorize translation, grant clinical or institutional authority, authorize merge, or authorize deployment.

It does not authorize merge. It does not authorize deployment.

## Human authorization and review roles

- **Review sponsor and accountable founder:** Robert Domondon.
- **Authorization evidence:** Robert explicitly instructed Hermes on 2026-07-29 to conduct the founder review and authorize a review-only commit/PR for independent human review.
- **Preflight performer:** Hermes, serving as Robert's AI Chief of Staff.
- **Independence:** Hermes is not independent of the authoring process and cannot serve as the required independent human reviewer.
- **Human judgment preserved:** Robert's instruction authorizes exposure for review only. A qualified human must still review each required scope and a separate founder decision is required before publication.

## Scope reviewed

| Scope | Evidence reviewed | Founder-preflight outcome |
|---|---|---|
| Identity and lifecycle | Manifest, checksum ledger, candidate record, review brief, governance decision | Pass for review exposure; lifecycle remains draft/under-review |
| EDENA and authority | D0, Green, Learn, Observe/Draft, prohibited uses, authority fields, stop conditions | Pass for review exposure; clinical, institutional, and certification authority remain `none` |
| Privacy and safety | All 11 content artifacts, synthetic exercises, semantic validator, adversarial PHI fixture, secret/identifier scans | Pass for review exposure; no PHI-like identifiers, credentials, or operational clinical instructions found |
| Rights and provenance | Nine source records, Pack license, third-party notices, source bindings, citation-only postures | Pass for review exposure; independent rights/source-currency review remains required |
| Educational quality | Learning sequence, objectives, knowledge checks, glossary, uncertainty and human-judgment lessons | Pass for review exposure; independent nursing, educational, accessibility, and plain-language review remains required |
| Technical integrity | Ten schema proposals, validator, deterministic builder, ZIP, SQLite/FTS5 shard, pre-open governance checks, registry projection | Pass for review exposure; schemas remain proposals and retrieval remains local review-only |
| Public claims | Repository and Pack status copy, empty public catalog, live production catalog | Pass; no Pack is presented as published, certified, validated, or institutionally authorized |

## Findings and disposition

### Remediated before authorization

1. **P2 — fragile Markdown hard-break whitespace.** The complete staged-byte gate found six trailing-space line breaks in two knowledge checks. They were replaced with blank-line-separated choices. This superseded `sha256:4af348948303c5d473bb245bdb11ee1c9097eda587108546468375046cde9278` and produced the prior `sha256:fbe354b2a420f4de737cbfc3eb0e9c8d96e3bb4c7b280356b79cc23c1118927d` candidate.
2. **P2 — actual candidate absent from explicit CI reproduction.** Pull-request CI previously relied on repository checks and fixture-based pipeline tests. CI now regenerates schema proposals, checks schema drift, frozen-validates the actual Pack, and runs an exact-candidate two-directory reproduction test.
3. **P2 — isolated tests could escape through literal `python3`.** Pipeline tests now use `sys.executable`, so subprocess validation and builds remain inside the interpreter running the suite.
4. **P3 — review ZIP digest formatting differed across records.** The review brief now uses the same canonical `sha256:<hex>` form as the candidate record.
5. **P2 — review-candidate prose blurred draft lifecycle boundaries.** The citation example is now explicitly a pre-freeze template, and glossary definitions use declared/governed rather than authoritative content language.
6. **P2 — derivative builds silently replaced the frozen checksum ledger.** Builders now verify existing ledgers by default and require explicit `--freeze` authority to create or replace one; drift fails without mutating the Pack.
7. **P2 — leading body prose could be omitted from derivatives.** Non-empty content before the first Markdown heading now fails closed and has adversarial regression coverage.
8. **P2 — candidate search accepted `pack_id` as an implicit namespace.** External governance must now declare the authorized namespace explicitly; pack-ID-only records abstain before SQLite opens.
9. **P2 — JSON Schema format checks depended on unpinned optional validators.** RFC 3339 and RFC 3986 validators are pinned, and regression tests prove malformed date-time and URI values are rejected.
10. **P3 — repository verification had checksum and governance-binding gaps.** Blank checksum lines and symlinks now follow the Pack validator contract; review ZIP declarations are cross-bound; empty approval-state evidence is rejected.
11. **P3 — namespace risk-ceiling vocabulary was hand-copied.** The schema now derives ceiling-eligible tiers from the shared vocabulary while explicitly preserving the EDENA prohibition on `Red-P`.

### Open limitations carried to independent review

- Source currency, claim support, and rights interpretation require qualified human judgment. This preflight is not legal advice.
- Educational quality, nursing relevance, accessibility, and plain-language suitability require independent human review.
- The external candidate governance record is a local draft review-control artifact, not a signed publication authority or institutional trust registry.
- HHS blocks raw automated `curl` requests with HTTP 403, but the canonical page was successfully confirmed through the browser stack with the expected title and summary limitation language.
- No independent review decision, findings disposition, schema adoption, or publication decision exists.

## Verification evidence

- Frozen validator: **PASS**, exact candidate `sha256:5f423157c79cd41b21a3b6b88a4dc6ec52b894b2de1c8da717352bfeb9329573`.
- Isolated dependency environment: **PASS**; imports resolved inside `/tmp/nin-kc-isolated-verify-venv` with inherited `PYTHONPATH` removed.
- Full regression suite: **24/24 PASS**.
- Schema proposals: **10 generated and meta-valid**; not adopted.
- Cross-directory deterministic comparison: **PASS** for build manifest, catalog entry, chunks, entities, relations, review ZIP, and shard lock.
- Review ZIP: **19 safe regular-file members**, fixed ZIP timestamp, no absolute/traversal paths or symlinks.
- Local search: default unpublished query abstained; exact-digest authorized review returned bounded citations; recalled-state regression abstained before ranking.
- Repository verifier, Python compilation, workflow YAML parsing, staged-byte whitespace check, and sensitive-pattern scans: **PASS**.
- Production: HTTP 200; live catalog byte-equal to local catalog; published Pack count remains **0**.

## Conditions of the review-only PR

1. The PR title and body must identify the exact candidate and state that it is for independent human review only.
2. All schema, acceptance, publication, catalog, translation, merge, and deployment approval fields remain false.
3. Generated local SQLite and review ZIP artifacts remain outside Git history.
4. Any Pack-byte change supersedes this preflight, requires a new candidate digest, and requires renewed exact-byte review.
5. The PR must not be merged until required human review scopes, findings disposition, exact-head CI, formal reviews, and a separate human merge decision are complete.

---

*Agents propose. Humans judge. Nurses steward.*
