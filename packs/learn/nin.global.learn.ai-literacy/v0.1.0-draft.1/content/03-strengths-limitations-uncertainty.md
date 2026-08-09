---
schema_version: 0.1-draft
artifact_id: artifact.ai-literacy.uncertainty
content_unit_id: unit.ai-literacy.uncertainty
title: Strengths, limitations, and uncertainty
artifact_type: lesson
language: en
audiences:
  - student-nurse
  - staff-nurse
  - nurse-educator
  - nurse-leader
  - nurse-informaticist
learning_objectives:
  - Match low-consequence AI strengths to appropriate educational tasks.
  - Recognize hallucination, automation bias, outdated knowledge, and hidden uncertainty.
  - Apply a verification ladder before relying on a material claim.
source_refs:
  - source.nist.ai-rmf-1-0
  - source.nist.genai-profile
  - source.who.lmm-guidance
keywords:
  - hallucination
  - uncertainty
  - automation bias
  - verification
  - limitations
limitations:
  - General educational framing; actual system performance must be evaluated in context.
---

# Strengths, limitations, and uncertainty

## Learning objectives

You should be able to identify useful low-consequence tasks, name common failure modes, and escalate verification as consequences increase.

## Common strengths

Depending on the system and task, AI may help a person:

- generate alternate wording;
- organize public notes into headings;
- compare two user-provided passages;
- create questions for self-study;
- produce a first draft from explicit inputs;
- identify terms that need clarification;
- translate a general idea into a checklist for human review.

These are candidate-generation tasks. Their value depends on the quality of the inputs and the review that follows.

## Common limitations

### Confident false content

Generative systems can produce invented facts, citations, quotations, links, or explanations. This is often called hallucination or confabulation. Confidence of tone does not reliably indicate correctness.

### Incomplete or outdated information

A model may not have current information. Even when retrieval is available, the retrieved material may be incomplete, stale, or outside the relevant jurisdiction.

### Hidden assumptions

A response may silently assume an audience, setting, definition, policy, or goal. Ask what assumptions the answer depends on.

### Sensitivity to wording

Small prompt changes can produce materially different answers. This can expose ambiguity rather than resolve it.

### Uneven performance

Performance can vary across languages, specialties, populations, formats, and uncommon situations. Average benchmark performance does not prove reliability for your task.

### Automation bias

People may give excessive weight to a machine-generated recommendation, especially when it is fast, polished, or presented as objective. Human review must be substantive, not ceremonial.

## A verification ladder

Increase verification as uncertainty or consequence increases:

1. **Inspect the task.** Is it within the permitted educational scope?
2. **Inspect the inputs.** Are they public, appropriate, complete, and rights-clear?
3. **Inspect the output.** What claims, assumptions, omissions, and uncertainties appear?
4. **Inspect the sources.** Do original sources exist and support the material claims?
5. **Inspect the context.** Does the content apply to the language, locality, date, audience, and purpose?
6. **Inspect authority.** Who is qualified and authorized to decide?
7. **Stop or abstain.** If evidence or authority is missing, do not manufacture certainty.

## A synthetic example

An AI system creates five study questions from a public paragraph supplied by a learner. This is a bounded Draft task. The learner should still check whether each question matches the paragraph and whether the answer key is correct.

If the same system is asked what action should be taken for a real person, the task has changed. This Pack does not authorize that use.

## Knowledge check

True or false: A response that includes several citations is lower risk even when none of the citations has been opened.

**False.** Unverified citations can create an appearance of evidence without evidence.

## Sources and limitations

This lesson synthesizes general risk themes from NIST AI RMF 1.0, the NIST Generative AI Profile, and WHO guidance on large multi-modal models in health. The WHO publication is cited only. This lesson does not measure any particular model or establish fitness for a healthcare task.
