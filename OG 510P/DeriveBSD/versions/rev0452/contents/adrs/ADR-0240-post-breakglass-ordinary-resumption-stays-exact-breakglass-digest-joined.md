# ADR-0240: Post-breakglass ordinary resumption stays exact-breakglass-digest joined

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

`ADR-0239` already made one important recovery boundary explicit:
ordinary attestation-gated authority does not silently reopen after breakglass.
Later ordinary secret or workload-identity lanes must consume a fresh `attestation.receipt` issued after the relevant breakglass receipt `created_at`.

That still left one quiet implementation choice open:
**which breakglass receipt is the relevant barrier?**

Without one more narrow cut, implementations drift toward folklore such as:

- using “latest breakglass session for this host” as an implicit lookup rule,
- asking dashboards, session history, or operators which emergency session mattered,
- or comparing timestamps against some helper-side row while the consuming authority receipt itself stays silent.

That would reintroduce hidden resolver behavior exactly where the archive has been removing it.

## Decision

**When breakglass materially gated or explained a later ordinary attestation-gated authority decision, the ordinary consuming receipt must carry the exact breakglass receipt digest.**

In v0 that means:

1. `secret-receipt.attestation_verification` and `workload-identity-issue-receipt.attestation_verification` now define `relevant_breakglass_receipt_digest`.
2. Carry that field whenever breakglass materially formed the ordinary resumption barrier or otherwise explains why the fresh attestation mattered.
3. The field names the exact `breakglass.receipt` whose `created_at` is the boundary for post-breakglass freshness.
4. Implementations may not rediscover the governing breakglass session from “latest session wins”, host history scans, dashboards, or operator memory.

## Consequences

### Positive

- Detached support/export tooling can explain **which** breakglass session mattered from portable receipt data.
- The archive removes another hidden resolver/database lookup from the ordinary authority lane.
- A/B/C/D stay coherent even when a host has multiple breakglass sessions over time.

### Negative / limits

- This still does not define a dedicated “ordinary lane attempted too early after breakglass” receipt shape.
- JSON Schema alone still cannot prove cross-object timestamp ordering; the exact digest join makes that ordering auditable rather than implicit.
- Ordinary receipts now carry one more exact context digest when breakglass materially matters.

## Why this is the right small hard decision now

The expensive ambiguity is no longer whether fresh post-breakglass attestation is required.
It is whether responders can tell which emergency session set that boundary without reopening backend state.
This cut answers that narrowly and usefully:
**post-breakglass ordinary resumption stays exact-breakglass-digest joined instead of latest-session folklore.**
