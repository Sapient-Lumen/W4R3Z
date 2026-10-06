# ADR-0071: Support-bundle contract and timeline-first handoff

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has most of the pieces required for humane incident handoff:
`docs/216-incident-snapshots-and-support-bundles.md`,
`docs/419-incident-timelines-as-derived-artifacts.md`, and
`docs/253-bundle-plans-and-deterministic-exports.md`
define typed incident metadata, a human-scale timeline view, deterministic selection/redaction plans,
payload manifests, and build receipts.

What the archive still lacked was the **official support handoff contract**.
Without that contract, the same bundle vocabulary drifts into contradictory practice:

- operators still fall back to mystery tarballs or one-off scripts,
- a useful incident timeline exists in theory but is omitted from the bundle people actually share,
- exported bytes are hard to relate back to the selection/redaction plan that produced them,
- and compatibility formats (`zip`) threaten to silently become the canonical bundle story instead of an adapter.

## Decision

DeriveBSD will treat the **official support handoff** as a small typed contract, not an implementation detail.

The canonical support handoff is:

1. `incident.timeline` — the default one-page human orientation surface.
2. `incident.bundle` — the metadata envelope describing trigger, scope, included evidence, and payload.
3. `bundle.plan` — the deterministic selection + transform plan.
4. `bundle.payload.manifest` — the stable member listing for the produced payload bytes.
5. `bundle.build.receipt` — the plan→bytes binding for the built payload.

When the bundle leaves the machine or crosses a trust boundary, the handoff is extended with the existing export lane:

6. `export.receipt` — what was actually shared, under which policy.
7. optional `consent.receipt`, `transport.receipt`, and `export.transparency.entry` digests when the lane provides them.

Additional hard decisions:

- The canonical payload format for official support bundles is **`tar.zst`**.
- `zip` remains an explicit compatibility adapter, not the default support-bundle contract.
- Official support bundles should be **timeline-first**: include an `incident.timeline` by default and bind its digest into the bundle metadata and build receipt when present.
- Raw crash/core/kernel dumps remain **off by default** and require explicit policy/plan selection; metadata-first debugging is the baseline.

## Consequences

### Positive

- Human responders get a standard one-page orientation surface instead of reconstructing the story from raw logs.
- Support bundle bytes become explainable: plan, member list, timeline, and metadata are all typed and digest-bound.
- Export posture stays separate from collection posture: building a bundle and sharing a bundle remain distinct, receipted acts.
- The archive can converge on implementable bundle tooling without pretending every recipient supports the same container format.

### Negative / trade-offs

- This adds a little more ceremony around “just make a tarball”.
- Some recipients still require `zip`, so adapter paths remain necessary.
- Timeline generation now matters enough that poor summaries or missing references become visible product defects rather than background implementation debt.

## Non-goals

This ADR does **not** decide:

- the final UI for timeline rendering,
- the exact heuristics for selecting bundle-min inputs,
- the exact reproduction workflow after a bundle is collected,
- or the exact safe-open/sanitization UX for imported artifacts.

Those remain implementation work or follow-on design items.

## Why this shape

The coherence win is not “invent a bigger bundle system”.
It is deciding that the archive’s existing pieces form one small official handoff contract:

- timeline first for humans,
- metadata + manifest + build receipt for explainability,
- `tar.zst` as the default payload format,
- export receipts only when bytes actually leave the box,
- and raw dumps as explicit exceptions rather than ambient default behavior.

That is enough to guide future specs and implementation without freezing collector internals, UI shapes, or recipient transports.
