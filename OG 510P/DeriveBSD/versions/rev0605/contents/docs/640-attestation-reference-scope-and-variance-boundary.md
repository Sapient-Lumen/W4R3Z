# Attestation reference scope and variance stay explicit

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already chose explainable measured boot over raw PCR folklore.
This doc makes the next small but expensive decision explicit:

**how do we keep `attestation.reference` shareable and operable without turning measured boot into a per-host allowlist database?**

The answer is deliberately narrow.
It is not a new verifier subsystem and not a giant DSL for every firmware quirk.
It is the minimum boundary needed to make measured posture viable across A/B/C/D without forks.

See also:
- ADR: `adrs/ADR-0230-attestation-reference-scope-and-variance-boundary.md`
- follow-on exception workflow: `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`
- measured-boot lane: `docs/176-measured-boot-attestation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- boot-manifest replay: `docs/313-boot-manifests-and-eventlog-replay.md`
- attestation-in-practice lessons: `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`
- profile default: `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`

## Why this needs a hard decision

Every measured-boot design eventually gets cornered by variance.
Real machines change firmware, drivers, and optional boot components.
If the archive does not say how that variance is authored, one of two bad things happens:

- operators keep a silent per-host golden-PCR database, or
- they weaken attestation until it becomes theater.

Neither outcome is compatible with DeriveBSD’s goals.
A coherent archive needs a small explicit answer for scope shape and variance posture.

## Accepted boundary

### 1) Reference scope kind is explicit

`scope.kind` is required on `attestation.reference`, and `attestation.reference.scope.kind` may be:

`scope.selector` may still carry useful discovery hints, but it is not a newest-match or overlap-precedence resolver key. Exact evaluation stays pinned to a reviewed reference digest.

- `cohort` — the normal shape for shared fleet / pool / hardware-class policy
- `deployment` — a staged rollout or release-window reference
- `host` — an exceptional single-host reference

Routine references should be `cohort`-scoped.
That keeps reference authoring reviewable and reusable instead of collapsing into host-by-host snowflakes.

### 2) Variance mode is explicit too

`boot.variance.mode` is required on `attestation.reference`, and `attestation.reference.boot.variance.mode` may be:

- `manifest-replay-first`
- `mixed`
- `strict-pcr-only`

The archive’s design bias is clear: **manifest replay first**.
Use the event log plus accepted `boot.manifest` digests as the normal way to explain and authorize measured posture.
`mixed` and especially `strict-pcr-only` exist for tighter lanes, but they do not become the silent baseline.

### 3) Strict PCR pinning stays exceptional

`boot.strict_pcr_values` still exists, but now it must live under an explicit variance posture.
This is the key cut: strict PCR pinning is no longer allowed to hide behind verifier implementation detail.
If a deployment wants it, the reference has to say so.

### 4) Allowed degraded reasons are named by the reference

A reference may also list `boot.variance.allowed_degraded_reason_codes`.
That means the archive now has one typed place to say:

- which deviations are acceptable as `degraded`, and
- which deviations must fail closed.

This stays coarse on purpose.
The goal is to keep “allowed variance” reviewable without inventing a giant exception language.

## Follow-on decision: exceptions are now timeboxed and approval-shaped

`attestation.reference.exception` now carries the minimum review metadata for non-baseline references.
That means deployment/host scope and mixed/strict-PCR posture can still exist, but they must say why they exist, who approved them, and when they expire.
See `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md` and `docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`.

## Practical meaning by product shape

### A / secure fleet host

Fleet references stay cohort-shaped by default, so secret release and rollout gates can remain strong without a per-host PCR database becoming the real control plane.

### B / secure workstation

Workstation posture can stay visible/exportable and sensitive-operation-gated without making support flows depend on raw PCR archaeology or opaque verifier folklore.

### C / general-purpose OS

General-purpose installs keep attestation optional, but when the lane is used it stays explicit and reviewable instead of hiding a surprise host-specific verifier dependency.

### D / appliance / factory / regulatory

Factory and regulatory lanes can still choose stricter policy, including exceptional host or strict-PCR references, but those choices are now explicit artifacts rather than informal verifier configuration.

## Guardrail

- `tools/check_attestation_reference_variance_contract.py`

The guardrail checks that `attestation.reference` keeps scope kind and variance posture explicit, keeps `scope.selector` discovery-only rather than precedence-shaped, that the canonical example stays cohort-shaped and manifest-replay-first, and that the measured-boot docs keep teaching the same anti-snowflake boundary.

## What remains open

This doc does **not** fix:

- the final canonical event-log representation for every platform,
- the exact long-term reason-code registry for every verifier,
- the full attester key lifecycle model,
- or durable-attestation retention budgets.

The expensive decision here is smaller and more useful:
DeriveBSD no longer gets to say “avoid golden PCRs” in prose while leaving reference scope and variance mode implicit.

Last updated: 2026-03-21r373
