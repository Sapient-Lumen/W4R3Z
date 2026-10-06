# Attestation reference renewals stay digest-linked and successor-shaped

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md` already made non-baseline `attestation.reference` artifacts carry `exception` with explicit expiry and approvals.

This doc makes the next hard decision explicit:

**what keeps a renewed exception from becoming an implied backend row update instead of a reviewed successor artifact?**

The answer is intentionally small.
DeriveBSD does not need a separate renewal service here.
It needs the renewed reference artifact itself to say whether it starts a fresh exception story or supersedes a prior exception digest.

See also:
- ADR: `adrs/ADR-0232-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`
- baseline scope/variance boundary: `docs/640-attestation-reference-scope-and-variance-boundary.md`
- exception boundary: `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`
- measured-boot lane: `docs/176-measured-boot-attestation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- replay ergonomics: `docs/313-boot-manifests-and-eventlog-replay.md`

## Why this needs a hard decision

Timeboxed exceptions are good, but they still leave room for drift if renewal stays implicit.
That happens when operators or verifiers infer continuity from:

- “same selector, so it must be the replacement”,
- “same `reference_id`, so we just extended it”,
- newest `created_at` wins,
- or ticket notes that say “approved for one more week”.

Once that happens, the archive again loses the authority boundary because the real truth lives in verifier-side ordering rules instead of the signed artifact.

## Accepted boundary

### 1) Renewals mint a fresh artifact

A renewed exception does not extend an old `attestation.reference` in place.
It produces a **new artifact** with a new digest, fresh `created_at`, fresh approvals, and a fresh `exception.expires_at`.

### 2) Every exception says what kind of renewal story it is

`attestation.reference.exception.renewal_posture` is required.
It may be:

- `fresh-exception`
- `supersedes-prior-exception`

That keeps the renewal story typed instead of inferred.

### 3) Successor renewals must name the exact prior exception digest

If `exception.renewal_posture = supersedes-prior-exception`, then `exception.supersedes_reference_digest` is required.

That field names the exact earlier `attestation.reference` whose exception authority is being replaced.
The archive does not rely on reused IDs, timestamps, or scope overlap to discover that lineage.

### 4) Fresh exceptions stay explicit too

If `exception.renewal_posture = fresh-exception`, the reference starts a new exception story.
It does not silently inherit continuity just because it looks similar to some earlier exception.

### 5) The ordinary baseline stays boring

Routine `scope.kind = cohort` plus `boot.variance.mode = manifest-replay-first` references still carry no `exception`.
The renewal boundary only exists for non-baseline reviewed exception artifacts.

## Why this is good for A/B/C/D

### A / secure fleet host

Fleet rollout or containment exceptions can renew when needed, but each successor stays digest-linked and reviewable instead of depending on verifier row ordering.

### B / secure workstation

Sensitive workstation attestation can still use explicit exceptions without teaching support that “the latest weird host row” is the real policy.

### C / general-purpose OS

General-purpose installs keep attestation optional, but any environment that opts in gets a portable renewal trail instead of a control-plane-only story.

### D / appliance factory / regulatory

Regulatory pins and tightly bounded rollout windows can renew cleanly while preserving exact review history, which matters for audit and incident replay.

## Guardrail

`tools/check_attestation_reference_renewal_contract.py`

The guardrail checks that:

- non-baseline exception metadata requires `exception.renewal_posture`,
- successor renewals require `exception.supersedes_reference_digest`,
- a canonical non-baseline example demonstrates the successor shape,
- and the measured-boot docs keep teaching the same digest-linked renewal boundary.

## What remains open

Still open:

- exact reviewer/quorum topology for different exception classes,
- future reference-assignment/catalog ergonomics, while keeping selection exact-digest-pinned and not selector-overlap-shaped,
- attester-key lifecycle and motherboard replacement ceremonies,
- and durable-attestation retention budgets.

Those are real questions, but they no longer block the renewal lineage boundary.

Last updated: 2026-03-21r373
