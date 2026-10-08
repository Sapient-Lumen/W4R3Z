# Companion case page — public summary, private packet, and audience split interface spec

## Purpose

Give the operator one durable page that answers:

- whether this case currently has a public-facing summary, a private evidence packet, or both
- which audience each artifact is for
- how the two sides are linked
- what details were intentionally withheld from the broader audience
- where continuation should happen next

This page exists so `forum post + logs sent` becomes one typed case object instead of two loosely related acts.

## Inputs

- incident identifier
- escalation-lane decision and destination confirmation
- public-summary draft if any
- evidence manifest or private packet summary if any
- sensitivity findings and redaction results
- companion references already issued (`thread`, `request`, `summary-id`, `packet-id`, `local draft`)
- current continuation state

## Primary questions this page must answer

1. Does this case currently have a public artifact, a private artifact, or both?
2. What audience is each artifact shaped for?
3. How are the artifacts linked without leaking private detail into the wrong lane?
4. What is intentionally omitted from the public side?
5. Where should the case continue next?

## Layout

### A. Companion strip

Fields:

- incident headline
- companion state (`summary-only`, `private-only`, `dual-lane`, `not-issued`)
- current recommended continuation lane
- linkage confidence
- privacy posture

### B. Artifact siblings card

Show rows for:

- public summary
- private packet
- local-only notes if any

Per row show:

- existence state
- audience class
- purpose
- last updated time
- current fit verdict

### C. Audience split card

Show:

- what the public/community side may safely say
- what must stay private
- what can be referenced abstractly in both lanes
- whether the current split is too weak or too vague

### D. Linkage card

Show:

- companion reference key
- public-to-private link mechanism (`ticket-id`, `thread-url`, `companion-id`, `none-yet`)
- whether the link is operator-entered, system-issued, or missing
- contradiction or ambiguity warnings

### E. Continuation card

Show:

- next expected act (`post summary`, `upload packet`, `reply publicly`, `reply privately`, `hold local`, `close companion set`)
- why that act is next
- what would force a new split or a merge review

## Required interactions

- `Create public summary`
- `Review public summary`
- `Attach or create private packet`
- `Open private companion linkage`
- `Issue companion receipt`
- `Keep case private only`
- `Keep case local only`

## Guardrails

- Never treat a public summary and private packet as interchangeable artifacts.
- Never show `linked` without showing the linkage mechanism.
- Never hide withheld details once a public artifact exists.
- Never imply that public posting alone delivered private evidence.
- Never let the companion object silently disappear into separate lane receipts.

## Output

A reviewed companion-case object that preserves public/private artifact existence, audience split, linkage method, withheld-detail boundary, and continuation state.

