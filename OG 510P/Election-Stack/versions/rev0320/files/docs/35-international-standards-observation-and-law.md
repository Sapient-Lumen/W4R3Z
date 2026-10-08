# International standards, observation, and law (artifacts that matter)

**Track:** A (Deployable core)


Crypto is not enough: legitimacy depends on whether independent stakeholders can **observe, challenge, and validate** the election process.

This document collects legal/standards artifacts that should shape system requirements.

## Key sources to align with

### OSCE/ODIHR observation expectations
ODIHR handbooks emphasize that new voting technologies must meet the same democratic-election principles as paper processes and must be observable in a meaningful way.

Artifacts we SHOULD produce to support observation:
- public system description + threat model,
- public test and certification evidence,
- a complete "election evidence package" (see `32-governance-trusteeship-and-legal-evidence.md`),
- observation interfaces for the PBB, witnesses, and verification tools.

### Estonia internet voting legal opinion (2025)
The OSCE ODIHR legal opinion on Estonia’s internet voting regulation highlights the importance of clear legislative oversight, procedural safeguards, and transparency.

Even if you are not Estonia, it provides a useful checklist for:
- governance clarity,
- oversight and auditability,
- dispute resolution.

### Council of Europe e-voting recommendation (CM/Rec(2017)5)
The Council of Europe’s recommendation is widely referenced as an international legal standard for e-voting and stresses that e-voting must respect democratic principles, including secret suffrage.

### EU compendium of e-voting and ICT practices
Useful as a survey of implementation patterns and governance approaches (especially accessibility and inclusion tradeoffs).

## Spec-level implications
- **Observability** is a requirement: witnesses/monitors are not optional.
- **Transparency** must be designed so it does not become surveillance.
- The system MUST support **credible dispute resolution**:
  - clear evidence hierarchy,
  - deterministic reproduction of results,
  - documented incident response.

## Required artifacts (MUST)
1. Public election evidence manifest (hashes + signatures).
2. Public observer guide (what can be checked, how, by whom).
3. Public incident playbook and communication plan.
4. Public policy on disclosure granularity and privacy.