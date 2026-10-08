# Hidden override surfacing page — risky defaults, shadow rules, and disablement interface spec

## Purpose

Surface the deep rules that materially change behavior but are easy to miss from ordinary controls.
This page exists to stop the product from letting support-only or power-user-only knowledge silently outrun the UI.

## Inputs

- current subject / seat
- visible controls relevant to the subject
- detected deep overrides and hidden defaults
- severity class for each deep override
- editability from current surface
- effect class (`scope narrowing`, `deletion behavior`, `retention limit`, `transport/auth shift`, `detection lag`, `conflict handling`, `other`)
- whether the deep rule is merely documented, locally observed, or directly imported from config
- suggested safe inspection / mutation ladder

## Layout

### A. Hidden override summary strip

Fields:

- count of deep rules affecting current behavior
- highest severity override
- whether current surface can edit any of them
- next safest action

### B. Override table

Columns:

- rule name / human label
- effect class
- current effective value
- visible surface mismatch
- authority surface
- severity

Example rows:

- `LAN rate limit override`
- `placeholder removal recreation rule`
- `archive size / ttl limit`
- `bind interface hard requirement`
- `file notification disabled`
- `conflict-path handling override`

### C. Why the visible UI would mislead card

For each flagged override, state:

- what the ordinary UI suggests
- what actually happens
- what sentence must be substituted instead

### D. Safe ladder card

Ordered steps:

1. inspect
2. confirm winning rule
3. route to authoritative surface
4. review mutation
5. apply and receipt

## Required interactions

- `Inspect policy provenance`
- `Review override mutation`
- `Route to authority surface`
- `Export receipt`

## Guardrails

- Never hide a deep override because it lacks a first-class ordinary toggle.
- Never present a support-article-only rule as if it were outside product responsibility.
- Never let `advanced` mean `non-semantic`; many advanced rules materially change ordinary outcomes.
- Never fuse hidden defaults with live overrides; state whether each rule is passive default, active winner, or shadow residue.

## Output

A surfaced list of deep rules that materially alter current behavior and a safe route from observation to authoritative change.
