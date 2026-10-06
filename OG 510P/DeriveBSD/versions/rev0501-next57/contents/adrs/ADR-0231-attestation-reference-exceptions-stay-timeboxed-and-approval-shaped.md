# ADR-0231: Attestation reference exceptions stay timeboxed and approval-shaped

Status: Accepted  
Date: 2026-03-21r371

## Context

`ADR-0230` already fixed the first expensive measured-boot boundary:
routine `attestation.reference` authoring stays `scope.kind = cohort` and
`boot.variance.mode = manifest-replay-first`.

That still left one painful implementation gap open in practice:

- how do deployment- or host-shaped references get approved,
- how do mixed or strict-PCR exception postures stay visible,
- and how do we prevent verifier-side named-policy databases from becoming the *real* exception ledger?

If the archive leaves that review path informal, the anti-snowflake rule decays quickly.
Operators will still create exception references, but the real authority will move into tickets,
verifier tables, or local folklore instead of typed archive artifacts.

## Decision

**Any attestation reference that leaves the ordinary cohort baseline must carry a typed, timeboxed exception record inside the reference artifact itself.**

1. **Baseline stays small and ordinary.**
   - Ordinary reference authoring remains `scope.kind = cohort` plus `boot.variance.mode = manifest-replay-first`.
   - The canonical example stays on that baseline and does not carry exception metadata.

2. **Non-baseline references must carry `exception`.**
   - `attestation.reference.exception` is now required when:
     - `scope.kind = deployment`, or
     - `scope.kind = host`, or
     - `boot.variance.mode = mixed`, or
     - `boot.variance.mode = strict-pcr-only`.

3. **Exceptions are timeboxed and approval-shaped.**
   - `exception.reason`, `exception.justification`, `exception.expires_at`, and `exception.approvals` are required.
   - Optional `change_id` / `ticket` fields keep the reference joined to rollout, incident, or review context.
   - Renewal means a fresh reviewed reference artifact, not silent extension inside verifier state.

4. **Strict PCR pinning cannot hide under the ordinary baseline.**
   - `boot.strict_pcr_values` is forbidden when `boot.variance.mode = manifest-replay-first`.
   - `boot.variance.mode = strict-pcr-only` requires `boot.strict_pcr_values`.
   - `mixed` remains the explicit lane for replay-first references that still need a reviewed strict-PCR side condition during transition or containment.

## Consequences

- The archive now has a typed answer for deployment/host exception approval without inventing a new verifier subsystem.
- A/D can keep stronger attestation gates without normalizing perpetual verifier-side snowflake state.
- B/C keep attestation opt-in and reviewable when used, instead of inheriting a hidden per-host reference database.
- Renewal/review pressure is explicit: long-lived exception posture must survive fresh review, not ticket archaeology.

## Rejected alternatives

- **Keep exception approval out-of-band.** Rejected: that turns verifier DB rows and ticket notes into the real authority.
- **Invent a separate exception service now.** Rejected for v0: too large; the reference artifact itself can carry the minimum review surface.
- **Allow strict PCR pinning under `manifest-replay-first`.** Rejected: that blurs ordinary replay-first posture with hidden strict allowlists.

## Wiring

Accepted and wired through `spec/attestation.reference.schema.json`, the measured-boot/attestation docs,
`docs/266-open-questions-and-risk-register.md`, and `tools/check_attestation_reference_exception_contract.py`.
