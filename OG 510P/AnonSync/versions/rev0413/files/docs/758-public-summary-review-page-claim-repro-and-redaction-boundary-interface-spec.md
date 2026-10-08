# Public summary review page — claim, repro, and redaction boundary interface spec

## Purpose

Force one explicit review before a case statement becomes visible to a broader audience.
This page should answer:

- what minimum useful claim can be stated publicly
- which reproduction or observation details are safe to include
- what sensitive details must be removed or generalized
- whether the resulting summary is still useful after redaction
- what stronger sentence the product must forbid

This page exists so `post on forum` becomes a reviewed public-safe act instead of raw case leakage or vague folklore.

## Inputs

- incident brief
- symptom bookmark and repro summary if any
- sensitivity findings
- evidence manifest summary
- chosen public-facing lane if any
- desired public ask (`troubleshooting`, `confirmation`, `pattern-match`, `billing-question`, `other`)

## Primary questions this page must answer

1. What public-safe claim is actually useful here?
2. Which repro/event details can survive public sharing?
3. What details must be abstracted, removed, or moved to the private companion packet?
4. Is the summary still actionable after redaction?
5. What sentence would overclaim beyond public-safe proof?

## Layout

### A. Review strip

Fields:

- public lane
- public ask type
- redaction posture
- usefulness verdict (`useful`, `too-vague`, `overshared`, `private-only-better`)

### B. Summary draft card

Show:

- current proposed headline
- current public-safe narrative
- visible repro or observation window
- allowed attachments or none

### C. Redaction boundary card

Rows such as:

- identifiers / paths / names
- timestamps / chronology precision
- peer roles / topology hints
- raw logs / dumps / screenshots
- licensing or account details

Per row show:

- keep
- generalize
- move-private
- remove entirely
- reason

### D. Utility card

Show:

- whether enough detail remains for a helper to respond usefully
- whether the summary should ask a narrower question
- whether a private companion packet is required for real progress
- strongest safe sentence and stronger forbidden sentence

### E. Publication decision card

Actions:

- publish summary as reviewed
- narrow further
- route private only
- create companion packet first
- save as local draft

## Required interactions

- `Approve public summary`
- `Generalize more`
- `Move detail to private packet`
- `Hold as private only`
- `Open companion case`
- `Issue companion receipt`

## Guardrails

- Never treat redaction as a purely cosmetic step.
- Never let raw artifacts ride along with a public summary without an explicit decision.
- Never allow a public claim stronger than the surviving public proof.
- Never hide when redaction made the summary too vague to be useful.
- Never merge public-help and private-escalation language into one statement.

## Output

A reviewed public-summary object that preserves public-safe narrative, redaction decisions, utility verdict, and claim ceiling.

