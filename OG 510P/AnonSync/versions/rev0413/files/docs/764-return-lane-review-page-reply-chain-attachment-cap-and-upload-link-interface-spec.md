# Return lane review page — reply chain, attachment cap, and upload-link interface spec

## Purpose

Decide how the current ask should be returned and whether the chosen lane can actually carry the reviewed packet.

This page exists so `reply to the ticket`, `use the portal`, `mention the forum link`, and `ask for a larger upload link` become one explicit routing decision.

## Inputs

- recipient ask object
- ask fulfillment review
- chosen packet or narrowed packet
- known binding token
- known lane constraints and size limits
- current surface capabilities

## Primary questions this page must answer

1. Must this return travel in an existing reply chain or may it start a fresh private packet?
2. Does the lane have known size, format, or attachment constraints?
3. Is an upload-link request or other preparatory act required first?
4. Can the current surface complete the return, or is a different surface/device required?
5. What proof will later show that the chosen lane matched the ask?

## Layout

### A. Lane strip

Fields:

- chosen return lane
- binding token
- lane viability (`ready`, `needs-prestep`, `blocked`, `ambiguous`)
- current-surface fit

### B. Chain and binding card

Show:

- reply-chain requirement
- portal / thread / ticket binding
- whether the lane preserves companion-case continuity
- missing token warnings

### C. Payload fit card

Show:

- packet size class
- attachment cap if known
- format constraints if known
- whether the packet fits now, needs narrowing, or needs alternate transfer

### D. Surface feasibility card

Show:

- whether the current device/surface can complete the return
- whether a portal, mail client, NAS WebUI, or another machine is required
- what evidence may need export before the actual return act

### E. Receipt preview card

Show the exact proof fields that the later receipt will preserve:

- ask version
- lane used
- binding token used
- packet version or manifest version
- residual unsatisfied clauses

## Required interactions

- `Approve current lane`
- `Request upload link / alternate lane`
- `Narrow packet to fit lane`
- `Change return surface`
- `Issue fulfillment receipt`

## Guardrails

- Never present a lane as ready without binding-token truth.
- Never ignore known size limits.
- Never let a new lane silently replace a required reply chain.
- Never pretend the current surface can send what it can only export.

## Output

A reviewed return-lane decision preserving binding method, payload fit, current-surface feasibility, and lane-specific next steps.
