# NIN Knowledge Commons

> **Status: public repository scaffold, proposed doctrine, and first English review candidate, version 0.1.** The public catalog is empty. No Knowledge Packs are published. Draft schemas and local validation/rebuild tools are not canonical adoption, independent review, hosted retrieval, institutional authorization, clinical validation, or a PHI-capable environment.

The **NIN Knowledge Commons** is the proposed public catalog for the **Nurse AI OS Knowledge Fabric**: one federated fabric distributed as portable, versioned Knowledge Packs and discovered through a thin shared registry.

## Governing maxims

> **Content packages are the source of truth. Search, vector, and graph indexes are disposable derivatives.**

> **Contributors propose. Reviewers verify. Institutions authorize. Nurses steward.**

> **Inclusion means available for governed use—not endorsement, certification, clinical validation, institutional authorization, or permission to change practice.**

## Documents

- [Doctrine](DOCTRINE.md) — constitutional principles, authority boundaries, scope, risk posture, ownership, retrieval, graph, hosting, and commerce rules.
- [Operational Playbook](PLAYBOOK.md) — contribution, review, publication, localization, retrieval, incident, pilot, and staged implementation procedures.
- [Governance](GOVERNANCE.md) — precedence, current activation state, and decision rights.
- [Safety](SAFETY.md) — public no-PHI, risk, active-content, and incident boundaries.
- [Contributing](CONTRIBUTING.md) — what may and may not be proposed at this stage.
- [Security](SECURITY.md) — responsible reporting instructions.

## Four governed lanes

```text
Learn     → student, subject, school, and locality libraries
Practice  → specialty, unit, department, and professional libraries
Lead      → leadership, management, educator, and wisdom libraries
Build     → dashboards, designs, simulations, and creator showcase
```

All four lanes use one package and governance standard. They are views over the same fabric, not separate incompatible databases.

## Current implementation state

Implemented in this first repository baseline:

- the repository boundary;
- doctrine and operational playbook;
- an accessible static catalog holding page;
- empty portable catalog, entity, and relation projections;
- public contribution, governance, safety, and security boundaries;
- deterministic repository verification and CI;
- ten draft JSON Schema proposals plus adversarial fixtures, including a separate external publication-decision contract;
- a fail-closed draft Pack validator and exact checksum freeze;
- a D0/Green English `AI Literacy Foundations for Nurses v0.1.0-draft.1` review candidate;
- deterministic local chunk, candidate-catalog, registry/provenance graph, and SQLite/FTS5 builds;
- fail-closed local candidate search requiring an exact namespace/version/digest, an external review-governance record, and a matching shard lock before SQLite is opened.

Not implemented or activated:

- canonical adoption of the draft schema proposals;
- accepted or published Knowledge Packs;
- independent rights, educational, accessibility, nursing, governance, and publication review of the English candidate;
- any Tagalog or other translation of the moving English draft;
- contributor intake or reviewer authority;
- package signing or release automation;
- hosted search, vector retrieval, graph traversal, or RAG;
- user accounts, school tenants, entitlements, payments, or marketplace functions;
- PHI, D2–D4, clinical decision support, competency scoring, or institutional integrations;
- MCP, connectors, cron, or autonomous actions.

Designed, documented, implemented, tested, committed, deployed, and live-verified are distinct states.

## Repository layout

```text
.
├── DOCTRINE.md
├── PLAYBOOK.md
├── GOVERNANCE.md
├── SAFETY.md
├── CONTRIBUTING.md
├── SECURITY.md
├── catalog/
│   ├── catalog.json
│   ├── entities.jsonl
│   └── relations.jsonl
├── governance/
├── namespaces/
├── packs/
├── schemas/
├── scripts/
├── tests/
├── tools/
├── requirements-dev.txt
└── index.html
```

The catalog and graph files are rebuildable projections. Future versioned Knowledge Packs—not these indexes—will remain authoritative.

## Local verification

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-deps --requirement requirements-dev.txt
.venv/bin/python scripts/verify_repository.py
.venv/bin/python -m unittest discover -s tests -v
```

The repository verifier checks required files, the exact custom-domain declaration, JSON/JSONL validity, repository-contained links, empty-catalog honesty, core governance language, and common secret/identifier patterns. Pack tooling additionally checks draft schemas, source references, public-safety patterns, exact checksums, explicit durable source-unit IDs, disposable chunk provenance, lifecycle exclusion, and exact-digest candidate-search authorization from an external governance record.

## Planned publication domains

```text
commons.nurse-ai-os.org       public catalog
packs.nurse-ai-os.org         future version-stable pack distribution
```

The `CNAME` file binds this Pages site to `commons.nurse-ai-os.org` after verification of the default GitHub Pages endpoint. Account-level domain verification, repository association, DNS binding, certificate issuance, and live verification remain separate controlled steps.

## Source lineage

The doctrine and playbook were incubated and reviewed in [`AI-Nurse-Solutions/ai-operating-system-heart-of-a-nurse`](https://github.com/AI-Nurse-Solutions/ai-operating-system-heart-of-a-nurse/tree/5f789035191603dfa5cf3dbf94a7f14bd51e5670/knowledge-commons) and transferred into this dedicated repository after the repository boundary was explicitly authorized.

## Licensing

- Source code and site implementation: [Apache License 2.0](LICENSE).
- Doctrine, playbook, governance text, and documentation: [CC BY 4.0](LICENSE-DOCUMENTATION.md).
- Trademarks and project identity are not granted by either license beyond reasonable factual reference.
- Future Knowledge Packs do **not** inherit one blanket repository license. Every pack and third-party component must declare its own artifact-specific license and rights record.

Copyright 2026 Robert Domondon. See [NOTICE](NOTICE).

---

*Agents propose. Humans judge. Nurses steward.*
