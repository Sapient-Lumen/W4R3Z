# Attestation reference exceptions stay timeboxed and approval-shaped

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/640-attestation-reference-scope-and-variance-boundary.md` already fixed the baseline:
routine measured-boot reference authoring stays cohort-shaped and manifest-replay-first.

This doc makes the next hard decision explicit:

**what keeps deployment / host / strict-PCR exception references from becoming a hidden verifier-side database?**

The answer is intentionally small.
DeriveBSD does not need a new exception service here.
It needs the reference artifact itself to say when it is exceptional, why, who approved it, and when that approval expires.

See also:
- ADR: `adrs/ADR-0231-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`
- baseline scope/variance boundary: `docs/640-attestation-reference-scope-and-variance-boundary.md`
- measured-boot lane: `docs/176-measured-boot-attestation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- replay ergonomics: `docs/313-boot-manifests-and-eventlog-replay.md`
- practical ecosystem lessons: `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`

## Why this needs a hard decision

A design can say “host-shaped references are exceptional” and still quietly normalize them.
That happens when the typed artifact stops carrying the review context and the real truth moves into:

- verifier-side named policy tables,
- ticket systems,
- temporary chat instructions,
- or “we all know this machine is weird” folklore.

Once that happens, the archive has lost the anti-snowflake fight even if the schema still says `cohort` is preferred.

## Accepted boundary

### 1) Ordinary references stay boring

The ordinary measured-boot reference remains:

- `scope.kind = cohort`
- `boot.variance.mode = manifest-replay-first`
- no `boot.strict_pcr_values`
- no `exception`

That is the baseline that should be easy to author, easy to review, and easy to share.

### 2) Non-baseline references must carry `exception`

`attestation.reference.exception` is required whenever a reference leaves that baseline.
Today that means any reference with:

- `scope.kind = deployment`
- `scope.kind = host`
- `boot.variance.mode = mixed`
- `boot.variance.mode = strict-pcr-only`

The exception object is not verifier-private metadata.
It is part of the reviewed reference artifact.

### 3) Exceptions are timeboxed

`exception.expires_at` is required.
That means deployment windows, host containment, firmware drift handling, and regulatory strict-PCR pins must all come back for review instead of living forever because “nobody removed the override”.

The point is not bureaucracy.
The point is to keep renewal visible and typed.

### 4) Exceptions are approval-shaped

`exception.reason`, `exception.justification`, and `exception.approvals` are required.
Optional `change_id` / `ticket` fields keep the reference joined to rollout, incident, or audit context.

This is the minimum review surface needed to answer:

- why is this reference exceptional,
- who accepted that exception,
- and when does it stop being acceptable without fresh review?

### 4a) Renewals are now typed too

`exception.renewal_posture` is now required, so the artifact has to say whether it is a `fresh-exception` or a reviewed successor.
If renewal happens, `exception.supersedes_reference_digest` names the exact prior exception digest.
That keeps renewed exception references on a new artifact path instead of treating expiry extension as an in-place row update.

### 5) Strict PCR pinning cannot hide inside the ordinary lane

`strict_pcr_values` may not appear with `boot.variance.mode = manifest-replay-first`.
If strict PCR pinning is present, the reference must say so explicitly by using either:

- `boot.variance.mode = mixed`, or
- `boot.variance.mode = strict-pcr-only`

`strict-pcr-only` also requires `boot.strict_pcr_values`.
That keeps “replay-first with explicit temporary strict pins” distinct from “this platform is entirely strict-PCR-driven”.

## Why this is good for A/B/C/D

### A / secure fleet host

Fleet hosts can still stage rollout windows and temporary host containment, but those exceptions stay reviewable and expiring instead of becoming a permanent verifier sidecar database.

### B / secure workstation

Workstations keep measured posture usable for sensitive operations without teaching support to accumulate ad-hoc host-specific allowlists.

### C / general-purpose OS

General-purpose installs keep attestation optional, but any deployment that turns it on inherits a reviewable exception story instead of an invisible verifier dependency.

### D / appliance factory / regulatory

Regulated deployments can still choose stronger strict-PCR or host-shaped reference posture, but those choices stay explicit, approved, and renewable rather than becoming timeless hidden config.

## Guardrail

`tools/check_attestation_reference_exception_contract.py`

The guardrail checks that:

- non-baseline attestation references require `exception`,
- the exception object is timeboxed and approval-shaped,
- strict PCR pinning cannot hide under `manifest-replay-first`,
- and the measured-boot docs keep teaching the same renewal-first boundary.

## What remains open

Still open:

- exact reviewer/quorum topology for different deployment classes,
- future reference-assignment/catalog ergonomics, while keeping evaluation exact-digest-pinned and not selector-precedence-shaped,
- automatic renewal UX for long-running regulated exceptions,
- attester-key lifecycle and motherboard replacement ceremonies,
- and durable-attestation retention budgets.

Those are real questions, but they no longer block the core implementation boundary.

Last updated: 2026-03-21r373
