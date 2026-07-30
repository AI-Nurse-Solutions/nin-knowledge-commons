---
schema_version: 0.1-draft
artifact_id: artifact.ai-literacy.glossary
content_unit_id: unit.ai-literacy.glossary
title: Plain-language glossary
artifact_type: glossary
language: en
audiences:
  - student-nurse
  - staff-nurse
  - nurse-educator
  - nurse-leader
  - nurse-informaticist
learning_objectives:
  - Define foundational AI-literacy and Knowledge Commons terms in plain language.
  - Distinguish retrieval, generation, review, authorization, and publication.
  - Use stable Pack identifiers when discussing evidence.
source_refs:
  - source.nist.ai-rmf-1-0
  - source.nist.genai-profile
  - source.naio.commons-doctrine
  - source.naio.commons-playbook
keywords:
  - glossary
  - definitions
  - Knowledge Pack
  - retrieval
  - governance
limitations:
  - Working plain-language definitions for this Pack; formal definitions may differ by source, law, or institution.
---

# Plain-language glossary

## Learning objectives

Use these working definitions to discuss AI and Commons evidence precisely. When a formal source defines a term, cite that source and version.

## Terms

### Abstention

A deliberate decision not to answer, recommend, or act when evidence, authority, privacy, safety, or scope requirements are not satisfied.

### Action mode

The kind of assistance a governed system is permitted to provide. This Pack permits **Observe** and **Draft** only. It does not authorize external action or clinical decisions.

### Artificial intelligence

An umbrella term for computational systems designed to perform tasks such as recognizing patterns, classifying information, generating content, or supporting predictions.

### Artifact

A declared content file inside a Knowledge Pack, such as a lesson, exercise, glossary, or assessment.

### Automation bias

A tendency to give excessive weight to an automated output or recommendation, sometimes despite conflicting evidence.

### Candidate digest

A cryptographic SHA-256 identifier that binds a review candidate to an exact checksum ledger. Any content change creates a different digest and requires renewed review.

### Citation

A pointer to a source. A citation must be checked before it is treated as evidence.

### Content unit

A stable, indexable section of a declared artifact. A content unit retains the Pack ID, version, artifact ID, section path, source references, and digest needed for citation.

### D0

The Commons data class for public, synthetic, or formally approved deidentified material with documented reuse rights. D0 does not mean that any public-looking information is automatically appropriate.

### Derivative index

A rebuildable search or graph artifact—such as chunks, an FTS5 database, or registry edges—generated from accepted Pack files. It is not the source of truth.

### EDENA risk tier

A governance classification describing the harm context and controls required. This Pack is **Green** and does not authorize Yellow, Orange, Red-P, or Red-E use.

### Evidence

Information that supports or challenges a claim when interpreted within an appropriate method, scope, and context.

### Generative AI

AI that produces new content, such as text, images, audio, or code, based on learned patterns and the context available at generation time.

### Hallucination

Generated content that is false, invented, or unsupported but may appear plausible or confident.

### Human review

Substantive inspection by a person with suitable competence, context, time, and authority to correct, reject, stop, or decide. Merely clicking approval is not sufficient.

### Knowledge Pack

A portable, versioned package containing governed content, metadata, rights, provenance, lifecycle information, and review records. Search indexes are derived from it.

### Language model

A model that estimates patterns in language and generates or evaluates text based on those patterns and supplied context.

### Namespace

A governed boundary that identifies who stewards a collection and constrains eligible lane, visibility, data class, risk, locality, and lifecycle state.

### PHI

Protected health information under applicable U.S. HIPAA rules. This Pack uses a broader public no-PHI boundary and does not make legal determinations about particular data.

### Prompt

Input or instructions supplied to an AI system. A prompt may include context, examples, boundaries, output requirements, and stop conditions.

### Prompt injection

Untrusted text that attempts to redirect an AI system, override authorized instructions, disclose information, or trigger actions. Source content does not gain user authority by containing commands.

### Provenance

Information about origin, authorship, version, transformation, rights, review, and lifecycle that lets a reader inspect and trace content.

### Publication

A separate governed act that makes an exact Pack version available within a declared scope. Drafting, validation, repository presence, or review requests do not equal publication.

### Retrieval

The process of selecting potentially relevant content from an authorized collection. Retrieval does not prove that a passage is correct or applicable.

### Review candidate

An exact, checksummed draft submitted for independent inspection. A review candidate is not published or approved.

### Source of truth

The authoritative record from which derivatives are rebuilt. In the Commons, the versioned Knowledge Pack—not its search index—is the source of truth.

### Synthetic information

Fictional information created for learning or testing that is not derived from a real person's private record or identifiable event.

### Stewardship

Ongoing human responsibility for safe scope, evidence, equity, dignity, environmental impact, nursing relevance, agency, correction, and accountability.

## Sources and limitations

These are original plain-language working definitions informed by NIST resources and the Commons Doctrine and Playbook. They do not override formal definitions in law, regulation, standards, policy, or source publications.
