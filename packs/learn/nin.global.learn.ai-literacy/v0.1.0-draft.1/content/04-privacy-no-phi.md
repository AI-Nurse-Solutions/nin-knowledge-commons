---
schema_version: 0.1-draft
artifact_id: artifact.ai-literacy.privacy
content_unit_id: unit.ai-literacy.privacy
title: Privacy and the no-PHI boundary
artifact_type: lesson
language: en
audiences:
  - student-nurse
  - staff-nurse
  - nurse-educator
  - nurse-leader
  - nurse-informaticist
learning_objectives:
  - Apply the Pack's public no-PHI boundary before using an AI tool.
  - Distinguish removing a name from establishing formal deidentification.
  - Replace sensitive scenarios with clearly synthetic educational inputs or stop.
source_refs:
  - source.hhs.hipaa-privacy-summary
  - source.naio.commons-doctrine
  - source.naio.commons-playbook
keywords:
  - privacy
  - PHI
  - no-PHI
  - deidentification
  - confidentiality
limitations:
  - Not legal advice or a determination of HIPAA, privacy-law, contract, or policy applicability.
---

# Privacy and the no-PHI boundary

## Learning objectives

You should be able to stop sensitive information from entering an unapproved workflow and explain why deleting a name does not automatically make information safe.

## The rule for this Pack

This public Pack is D0. Use only public, synthetic, or formally approved deidentified information with documented rights. Do not enter protected health information, identifiable stories, private learner records, employment records, confidential procedures, credentials, or secrets.

This rule is stricter than asking whether a single field is legally defined as PHI. It protects people and institutions when the user does not have enough information to evaluate the tool, contract, retention, location, access, training use, or downstream disclosure.

## Removing a name is not enough

Information may remain identifiable through combinations of details, unusual events, dates, locations, roles, images, metadata, or narrative context. Formal deidentification is a governed process, not a casual editing technique.

Do not assume that changing a name, age, or date makes a real story appropriate for a public AI service.

## Use synthetic replacements

For learning exercises, create fictional material that is not derived from a real person or private record. Keep the exercise clearly generic and avoid rare combinations that could point back to someone.

Safe educational example:

> A fictional learner has three public articles about teamwork and wants help comparing their stated purposes.

Unsafe direction:

> Paste information from a real chart, private message, incident report, assignment record, or employee file into an unapproved AI service.

## Ask before using any system

When sensitive information may be involved, determine through the accountable local process:

- whether the system is approved for that data and purpose;
- what agreement and policy govern use;
- where information is processed and retained;
- who can access prompts, files, outputs, and logs;
- whether information is used for model improvement;
- what deletion, incident, and audit controls exist;
- who has authority to approve the task.

This Pack cannot answer those questions for a vendor or institution.

## If information was entered by mistake

Stop using the workflow. Do not repeat or spread the information. Follow the applicable organizational privacy, security, and incident-reporting process. This Pack does not provide incident-specific legal advice.

## Knowledge check

A learner removes a person's name from a detailed real event and plans to paste the narrative into a public chatbot. Is that automatically safe?

**No.** The narrative may remain identifiable, confidential, or restricted. Use a truly synthetic exercise or an approved institutional pathway.

## Sources and limitations

The HHS Privacy Rule summary describes U.S. HIPAA concepts and explicitly does not replace the governing rule or legal advice. The Commons Doctrine and Playbook establish a public no-PHI boundary that may be more restrictive than a user's informal legal assumptions.
