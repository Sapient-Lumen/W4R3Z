# ADR-0093: No separate telemetry product-profile key

- Status: Accepted
- Date: 2026-03-08

## Context

`adrs/ADR-0091-product-profile-default-vocabulary-boundary.md` fixed the rule that
product-profile default keys are intentionally expensive and must stay small.

One overlap still remained in the allowlisted vocabulary: `telemetry`.
In practice, the archive already had three better-shaped surfaces for the same design space:

- `evidence` decides what diagnostic/evidence collection posture is normal,
- `evidence_exports` decides how evidence leaves the machine or org boundary,
- `network_egress` decides whether off-box transport is brokered, interactive, offline, or absent.

Keeping a separate `telemetry` key creates the wrong kind of freedom:

1. one product shape can quietly grow a fifth observability posture axis that other profiles do not carry,
2. reviewers must guess whether a change belongs in `telemetry`, `evidence`, `evidence_exports`, or `network_egress`,
3. and product profiles drift back toward a bag of overlapping semi-policy folklore.

The archive already uses the word *telemetry* in prose and interoperability notes.
The problem is narrower: it should not be a first-class product-profile default key.

## Decision

1. Remove `telemetry` from the allowlisted `product.profiles.defaults` vocabulary.

2. Treat telemetry / off-box diagnostics posture as a composition of existing surfaces:
   - `evidence` for what is collected and retained locally,
   - `evidence_exports` for sharing / support-handoff posture,
   - `network_egress` for transport authority,
   - plus explicit observability/export lanes when richer behavior is needed.

3. Keep the prohibition on ambient production telemetry as an invariant / forbidden-by-default rule where appropriate,
   especially for `appliance_factory`.

4. Keep the word *telemetry* available in prose, docs, event classes, and adapter discussions,
   but not as a separate A/B/C/D default knob.

## Consequences

- The product-profile artifact gets smaller and less ambiguous.
- `docs/478-evidence-collection-posture-by-profile.md` and `docs/466-export-boundary-posture-by-profile.md`
  remain the canonical product-shape posture docs for this space.
- D still forbids ambient live production diagnostic streaming by default,
  but that promise now lives where it belongs: evidence/export posture and forbidden lanes.
- Future richer telemetry/export ideas must either fit an existing key or justify a dedicated schema/lane,
  not smuggle themselves in as another overlapping profile knob.

## Why this is narrow enough

This ADR does not redesign observability, exporters, OpenTelemetry interoperability,
or trace grants.
It only removes one overlapping vocabulary key so the archive keeps one coherent product-profile surface.
