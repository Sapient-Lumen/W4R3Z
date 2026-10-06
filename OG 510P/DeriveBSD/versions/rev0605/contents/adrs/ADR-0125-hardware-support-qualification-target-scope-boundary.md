# ADR-0125: hardware support qualification target-scope boundary

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0118-hardware-support-matrix-and-bundled-admission-boundary.md` fixed where support claims live: `hw.support.matrix` is the digest-bound catalog artifact.
`adrs/ADR-0119-hardware-support-promotion-and-qualification-boundary.md` fixed that positive entries must carry a typed `qualification` summary.
`adrs/ADR-0120-hardware-support-qualification-receipt-boundary.md`, `adrs/ADR-0121-hardware-support-qualification-profile-boundary.md`, `adrs/ADR-0122-hardware-support-qualification-freshness-boundary.md`, `adrs/ADR-0123-hardware-support-qualification-status-boundary.md`, and `adrs/ADR-0124-hardware-support-conditions-and-known-limitations-boundary.md` then made those claims proof-bound, standard-bound, freshness-bound, status-bound, and caveat-bound.

That still left one expensive ambiguity: the archive could say *what* proof backed a support claim and *why* the claim was conditional, but not *which target span that proof was allowed to cover*. Without that boundary, a receipt qualified on one `release_train` or boot-manifest lineage can quietly keep sounding current on another target.

Real ecosystems make compatibility claims target-specific. Android publishes a per-release CDD and expects CTS packages that match the device Android version. Ubuntu’s desktop/server certification guidance ties certification to the life cycle of the Ubuntu release against which the system was certified. Red Hat hardware certification is specific to a RHEL major version and architecture. Windows HLK official playlists must match the kit/target release version.

## Decision

Accept a typed boundary for support qualification target scope.

1. **Positive support claims must say how far their proof reaches.**
   `hw.support.matrix.entries[].qualification.target_binding` and `hw.support.qualification.receipt.qualification.target_binding` become the canonical publication/evidence answer for the target span a proof may cover.

2. **Release-train identity is first-class target context.**
   `hw.support.matrix`, `hw.support.qualification.profile`, `hw.support.qualification.receipt`, and `hw.compat.report` targets must carry `release_train` so the archive can tell when support evidence is being reused on the wrong train.

3. **Target-scope mismatch is a distinct preflight outcome.**
   `hw.compat.report` gains `qualification-target-mismatch`, plus `support_matrix.matched_target_binding` and `support_matrix.target_scope_state`, so “proof is out of scope for this target” stays distinct from `qualification-stale`, `qualification-superseded`, or `support-condition-triggered`.

4. **This remains a small publication boundary, not a giant certification service.**
   The archive does not need a universal compatibility graph. It only needs a typed answer for whether the matched proof applies to the report target.

## Consequences

Good:
- B/workstation trusted-UI claims can say when a laptop class was only qualified for the same release train and boot-manifest lineage instead of pretending older proof still counts after a release hop.
- A/fleet rollouts can deny or downgrade reuse of old qualification on newer trains without ticket folklore.
- D/factory bundles can carry a small offline answer for whether the included support proof actually applies to the shipped target.

Trade-offs:
- The support lane gains a small new vocabulary surface (`target_binding`, `qualification-target-mismatch`, `target_scope_state`).
- The archive still does not define a universal semver/range language for every future compatibility lane.

## Follow-up

This ADR does **not** decide:
- a general compatibility-range DSL across all DeriveBSD artifact types,
- automatic requalification orchestration,
- or the final UI wording for every `qualification-target-mismatch` case.

It only fixes the missing boundary so support proof cannot silently float across `release_train` or boot-manifest boundaries.
