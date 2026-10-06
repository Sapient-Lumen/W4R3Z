# ADR-0230: Attestation reference scope and variance stay explicit

Date: 2026-03-21
Status: Accepted

## Context

DeriveBSD already decided that measured posture should be explainable, receipted, and reusable.
`boot.manifest`, `boot.attestation`, `attestation.reference`, and `attestation.receipt` already gave us the right nouns, but one expensive implementation choice was still too fuzzy in practice:

- are references written per host or per cohort,
- when is strict PCR pinning acceptable,
- and how does a verifier record “allowed variance” without quietly turning the product into a per-host allowlist database?

That ambiguity is dangerous across all four product shapes.
If references become per-host snowflakes, A/D fleet and regulatory stories collapse into fragile databases, B becomes painful to support, and C quietly inherits hidden attestation complexity that looks optional on paper but not in practice.

## Decision

**`attestation.reference` must make scope shape and variance model explicit.**

1. **Reference scope kind is required.**
   - `attestation.reference.scope.kind` is now required.
   - Allowed values are `cohort`, `deployment`, and `host`.
   - Routine references should be `cohort`-scoped so a verifier can share one reviewed reference across a role/pool/hardware class instead of inventing per-host snowflakes.
   - `deployment` scope is for staged rollouts or temporary release-train windows.
   - `host` scope is exceptional and should not become the normal product shape for A/B/C/D.

2. **Variance mode is required.**
   - `attestation.reference.boot.variance.mode` is now required.
   - Allowed values are `manifest-replay-first`, `mixed`, and `strict-pcr-only`.
   - The default design bias is `manifest-replay-first`: verify quote authenticity, replay the event log, and compare to accepted `boot.manifest` digests.
   - `mixed` exists for more tightly controlled lanes that still want replay/explainability plus selected strict-PCR anchors.
   - `strict-pcr-only` remains exceptional, not the archive’s ordinary recommendation.

3. **Strict PCR pinning stays exceptional.**
   - `boot.strict_pcr_values` remains available, but it is no longer allowed to masquerade as the unspoken baseline.
   - If a reference uses strict PCR pinning, the reference must say so through `boot.variance.mode` instead of leaving operators to infer it from verifier behavior.

4. **Allowed degraded reason codes are reference policy, not verifier folklore.**
   - `attestation.reference.boot.variance.allowed_degraded_reason_codes` may list the coarse verifier reasons that are still acceptable as `verdict = degraded` for that reference.
   - Anything outside that list should fail closed instead of becoming an undocumented verifier convenience.

## Consequences

- Measured-boot references become shareable and reviewable instead of drifting into per-host allowlist sprawl.
- A/D can keep stronger attestation gates without making rollout/reference evolution unmanageable.
- B keeps a real measured-posture lane without forcing workstation support to debug raw PCR folklore.
- C keeps attestation optional and explicit rather than quietly inheriting a hidden verifier database requirement.

## Alternatives considered

- **Leave scope and variance implicit.** Rejected: that is how “golden PCRs per machine” becomes the real product.
- **Allow only one universal variance mode.** Rejected: the archive needs one default bias, but still has to describe exceptional stricter lanes honestly.
- **Invent a new standalone variance-policy subsystem now.** Rejected for v0: the high-leverage move is to tighten `attestation.reference`, not to grow a second policy language.

## Status

Accepted and wired through the `attestation.reference` schema/example, the measured-boot and attestation docs, and a dedicated guardrail script.
