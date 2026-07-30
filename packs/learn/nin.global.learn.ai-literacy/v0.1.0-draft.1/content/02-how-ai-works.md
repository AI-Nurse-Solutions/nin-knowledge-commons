---
schema_version: 0.1-draft
artifact_id: artifact.ai-literacy.how-ai-works
content_unit_id: unit.ai-literacy.how-ai-works
title: How AI and generative AI work
artifact_type: lesson
language: en
audiences:
  - student-nurse
  - staff-nurse
  - nurse-educator
  - nurse-leader
  - nurse-informaticist
learning_objectives:
  - Distinguish artificial intelligence, machine learning, and generative AI at a foundational level.
  - Explain why a generated response is not automatically a verified fact.
  - Identify how prompts, training patterns, system design, and available context shape outputs.
source_refs:
  - source.nist.ai-rmf-1-0
  - source.nist.genai-profile
keywords:
  - artificial intelligence
  - machine learning
  - generative AI
  - inference
  - prompt
limitations:
  - Simplified conceptual explanation; not a technical implementation guide.
---

# How AI and generative AI work

## Learning objectives

You should be able to distinguish several common AI terms and explain why output generation is different from evidence verification.

## Artificial intelligence is an umbrella term

Artificial intelligence describes computational systems designed to perform tasks associated with capabilities such as recognizing patterns, classifying information, generating content, or supporting predictions. Different systems use different methods and operate under different constraints.

Machine learning is one approach in which a system learns statistical patterns from data rather than relying only on hand-written rules. A model's behavior depends on its training data, objective, architecture, evaluation, configuration, and use context.

## What generative AI does

Generative AI produces new content—such as text, images, audio, or code—by using patterns learned from data and context supplied at use time. A language model predicts a plausible continuation based on those patterns and the instructions and text available in its current context.

Plausibility is not the same as truth. A generated answer may be clear, specific, and confidently phrased while still being incomplete, outdated, unsupported, or false.

## Training and inference

**Training** is the process through which model parameters are adjusted using data and an objective. The details vary by system.

**Inference** is the process of using a trained model to produce an output from a new input. During inference, the system may receive a prompt, system instructions, retrieved documents, tool results, or other context.

A user usually cannot infer the exact training examples behind a particular sentence. When a system provides a citation, the citation must still be checked; the model's wording alone is not provenance.

## Inputs shape outputs

Outputs can change when any of the following change:

- wording or structure of the prompt;
- information included or omitted;
- model or model version;
- system instructions;
- retrieval sources;
- connected tools;
- randomness or sampling settings;
- vendor updates and safety controls.

This variability is one reason important work requires repeatable methods, documented sources, and human review.

## A synthetic example

Suppose a learner asks an AI system to summarize a fictional article about teamwork. The system can often produce a concise summary. But if the article is not provided and the system cannot retrieve it, the model may generate a plausible-sounding description of an article it has not actually inspected.

The responsible response is to provide the source or say that the source is unavailable—not to reward confident guessing.

## Practical distinction

Use this mental model:

```text
Prompt + available context + model behavior
                    ↓
             generated candidate
                    ↓
       source and consequence review
                    ↓
           human decision or abstention
```

## Knowledge check

A generated explanation includes a journal title and year. What should you do first?

**Inspect the original source and confirm that it exists, says what the output claims, and applies to the intended context.** A citation-shaped string is not evidence until verified.

## Sources and limitations

This lesson is an original educational synthesis informed by NIST AI RMF 1.0 and the NIST Generative AI Profile. Those frameworks address general AI risk management and do not authorize nursing or clinical use.
