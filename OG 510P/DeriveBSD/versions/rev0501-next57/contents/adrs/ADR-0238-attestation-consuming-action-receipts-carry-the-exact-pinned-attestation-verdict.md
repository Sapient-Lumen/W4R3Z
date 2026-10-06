# ADR-0238: Attestation-consuming action receipts carry the exact pinned attestation verdict and may not reinterpret it

- Status: Accepted
- Date: 2026-03-22
- Deciders: DeriveBSD archive maintainers

## Context

Recent archive cuts already fixed several expensive ambiguities on the attestation lane:

- `attestation.receipt` is evidence-only,
- authoritative consuming receipts pin the exact requirement/receipt/policy digest tuple,
- degraded admission is only allowed when the consumed requirement already says so,
- and ordinary authority stays fail-closed on rejected posture.

That still leaves one quieter loophole:
**a consuming receipt can pin the exact `attestation.receipt` digest, but still summarize a different semantic story than the pinned receipt actually said.**

Without a narrow rule here, implementations drift toward one or more hidden behaviors:

- an authority receipt that says `decision = accepted` while the pinned verifier receipt actually said `degraded`,
- a support/export service that rewrites `fail` into `rejected-but-basically-ok` in its own local state,
- or a verifier/database/dashboard that becomes the real place operators must inspect to learn what the original attestation verdict actually was.

That is the same backend-state folklore this archive has been removing one cut at a time.

## Decision

**In v0, decisive attestation-consuming authority receipts must carry the exact verdict from the pinned `attestation.receipt`, and the action-side summary must follow a fixed projection.**

That means:

1. For decisive consuming outcomes, `attestation_verification` must carry `attestation_receipt_verdict`.
2. `attestation_receipt_verdict` is the exact verdict already present in the pinned `attestation.receipt`: `pass`, `degraded`, or `fail`.
3. The action-side summary is a compact projection, not a reinterpretation:
   - `accepted` → `pass`
   - `degraded` → `degraded`
   - `rejected` → `fail`
4. Consuming receipts do **not** invent new semantics like “accepted-with-fail underneath”, “degraded-because-verifier-was-weird”, or “rejected-but-overridden-locally”. If a different authority story is needed, it must be expressed in explicit requirement/policy/emergency-lane artifacts, not by rewriting the pinned verdict.

## Consequences

### Positive

- The exact verifier outcome remains portable in the authoritative receipt that consumed it.
- Export/support/admission flows no longer need side lookups to prove whether the pinned attestation verdict was `pass`, `degraded`, or `fail`.
- A/B/C/D stay coherent because action receipts can explain both the compact authority decision and the exact pinned verifier outcome without verifier-specific archaeology.

### Negative / limits

- This duplicates one compact field from `attestation.receipt` into the consuming receipt.
- It does **not** define every future higher-level policy consequence of each verdict.
- It does **not** add a new attestation catalog or resolver subsystem.

## Why this is the right small hard decision now

The archive already pinned the exact receipt digest, but that alone still left room for hidden semantic drift between the evidence object and the authority object that consumed it.
This cut removes that loophole without inventing a large new subsystem.
It keeps the archive converging toward implementable truth:
**a consuming receipt may summarize, but it may not reinterpret, the exact attestation verdict it pinned.**
