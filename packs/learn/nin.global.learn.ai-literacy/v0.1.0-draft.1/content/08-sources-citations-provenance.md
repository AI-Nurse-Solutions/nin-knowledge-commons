---
schema_version: 0.1-draft
artifact_id: artifact.ai-literacy.sources
content_unit_id: unit.ai-literacy.sources
title: Sources, citations, and provenance
artifact_type: lesson
language: en
audiences:
  - student-nurse
  - staff-nurse
  - nurse-educator
  - nurse-leader
  - nurse-informaticist
learning_objectives:
  - Distinguish a claim, a citation, evidence, and provenance.
  - Evaluate whether a source supports a specific material claim.
  - Cite the exact Pack, version, artifact, section, and source when using Commons evidence.
source_refs:
  - source.nist.ai-rmf-1-0
  - source.naio.commons-doctrine
  - source.naio.commons-playbook
keywords:
  - evidence
  - claims
  - citations
  - provenance
  - source evaluation
limitations:
  - Introductory source-evaluation method; does not replace formal evidence appraisal for clinical questions.
---

# Sources, citations, and provenance

## Learning objectives

You should be able to separate claims from proof, inspect whether a source supports a statement, and trace Commons content to an exact version and location.

## Four different things

A **claim** is a statement that can be assessed, such as a definition, date, relationship, or reported effect.

A **citation** points to a source. A citation can be accurate, inaccurate, incomplete, or fabricated.

**Evidence** is information that actually supports or challenges the claim when interpreted within an appropriate method and context.

**Provenance** records where content came from, who created or transformed it, which version was used, what rights apply, and what review occurred.

A citation is not automatically evidence, and evidence without provenance is difficult to inspect or update.

## Evaluate claim support

For a material claim, ask:

1. Does the source exist and open successfully?
2. Is the author or issuing body identifiable?
3. Is it the original or authoritative source rather than a summary of a summary?
4. What date and version apply?
5. Does the source state the claim, or only something adjacent?
6. What population, setting, method, language, and limitations apply?
7. Are important qualifications missing from the AI-generated wording?
8. Is the use permitted by the source's license or rights statement?
9. Do other credible sources conflict?
10. What level of authority does the source actually carry?

## Claim versus proof table

| Output statement | What must be inspected |
| --- | --- |
| “A framework recommends X.” | Exact framework, version, section, wording, scope, and whether it is mandatory or voluntary. |
| “Research proves X.” | Original study, method, population, outcome, uncertainty, limitations, and whether “proves” overstates the evidence. |
| “Policy requires X.” | Current authoritative policy for the relevant institution and jurisdiction. |
| “The AI found no issue.” | What was tested, what was not tested, model/tool limits, and qualified human review. |

## Cite Commons content exactly

A governed Commons citation should resolve to:

```text
pack_id
pack_version
artifact_id
section path or content-unit identifier
candidate or release digest
source record identifiers
```

The following is a pre-freeze citation template, not the binding for this review candidate:

```text
nin.global.learn.ai-literacy@0.1.0-draft.1
artifact.ai-literacy.sources
Sources, citations, and provenance > Evaluate claim support
candidate digest: <copy the bound sha256 digest from the candidate record>
```

Do not cite a moving branch as though it were an immutable release.

## Surface conflict and uncertainty

If credible sources disagree, report the disagreement. Do not flatten it into a single confident answer merely for convenience.

If a source is unavailable, outdated, outside the relevant locality, or not rights-clear, say so. Abstention is more trustworthy than a fabricated citation.

## A synthetic example

An AI response says that a fictional professional framework “requires” a specific checklist. The linked document actually describes the checklist as optional guidance.

The citation exists, but the claim overstates its authority. Correct the wording and record the source's actual status.

## Knowledge check

What does provenance add beyond a hyperlink?

**It records identity, version, transformation, rights, review, and lifecycle context so the material can be inspected, rebuilt, corrected, or recalled.**

## Sources and limitations

This lesson applies the Commons source-of-truth and lifecycle doctrine and uses the NIST AI RMF as an example of a versioned public framework. It is not a clinical evidence-appraisal curriculum.
