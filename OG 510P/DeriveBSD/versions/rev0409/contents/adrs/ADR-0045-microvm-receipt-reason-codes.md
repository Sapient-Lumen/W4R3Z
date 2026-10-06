# ADR-0045: MicroVM lifecycle receipts require reason codes on non-success outcomes

- Status: **accepted**
- Date: 2026-03-04

## Context

DeriveBSD treats runtime operations as evidence.
For microVM lifecycle actions (launch/stop), the *most common operational questions* are:

- **Why was this denied?**
- **Why did this fail?**
- **Why did it time out?**

If receipts only include a free-form message (or worse, only logs), then:

- fleet automation cannot reliably branch on outcomes,
- support bundles cannot deterministically answer “what happened?”,
- and different product shapes drift into different error vocabularies.

We want a small, implementable contract that improves operability without inventing a new subsystem.

## Decision

For microVM lifecycle receipts:

- `microvm.launch.receipt` MUST include a non-empty `reasons[]` list when `outcome` is `denied` or `failed`.
- `microvm.stop.receipt` MUST include a non-empty `reasons[]` list when `outcome` is `denied`, `failed`, or `timeout`.

Each `reasons[]` entry contains:

- `code`: a stable, machine-readable identifier (kebab-case; optional dot-separated namespace segments).
- `message`: a short human explanation.

The minimal, stable v0 microVM reason code vocabulary includes (non-exhaustive):

- `denied-by-policy`
- `instance-id-collision`
- `plan-digest-mismatch`
- `artifact-missing`
- `signature-invalid`
- `digest-mismatch`
- `backend-error`
- `timeout`

Notes:

- `message` is not a spec surface; `code` is.
- Receipts MAY include multiple reasons (e.g., “denied-by-policy” + a more specific subreason).
- Do not overload `code` with backend-specific paths; treat those as `message` or `notes`.

## Consequences

- Incidents become more deterministic: “why” is queryable without log archaeology.
- Fleet and workstation behavior stays aligned across A–D.
- Schema-level enforcement prevents drift back into log-only explanations.

See: `spec/microvm.launch.receipt.schema.json`, `spec/microvm.stop.receipt.schema.json`, `docs/455-microvm-launch-plans-and-receipts.md`.
