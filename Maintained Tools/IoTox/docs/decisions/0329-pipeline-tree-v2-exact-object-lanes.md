# ADR 0329: Pipeline tree-v2 exact object lanes

- Status: accepted and implemented
- Date: 2026-09-03

## Context

The rejected near-ceiling tree-v2 diagnostic exposed a concrete scale limit: after branches and
manifests were already authenticated, followers still fetched thousands of 16 KiB file objects
mostly one at a time. The subscriber had a single `ActiveLane` per pull job even though namespace
policy already carried `maximum-lanes` and `maximum-outstanding-requests`.

That made the small-file case latency-bound. It also left operator status unable to prove whether a
tree-v2 pull was actually using a bounded object window.

## Decision

Keep the frozen tree-v2 wire protocol and change only local subscriber scheduling. A tree-v2 pull may
now keep a bounded vector of active exact-object lanes. The effective lane cap is:

1. the process-local `--max-sync-tree-lanes` value;
2. the signed namespace `maximum-lanes`; and
3. the signed namespace `maximum-outstanding-requests`.

The smallest of those values wins. Each lane still has its own request ID, FileId, source, staging
file, object kind, expected byte length, offer, and terminal transfer proof. Branch records and
manifests still verify before graph expansion. File objects still commit to CAS before branch
metadata and current-workspace effects. Cancellation, peer-offline handling, and failure cleanup now
settle every active lane explicitly.

`sync-status` exposes the process cap as `tree-lane-cap`, each pull's `active-lanes`, and one
owner-private `tree-lane-job=` row per exact active receive. The old `active-file` and
`active-file-number` fields remain as compatibility projections only when a tree-v2 pull has exactly
one active lane.

## Consequences

Tree-v2 can now attack thousands-of-small-file head-of-line blocking without changing peer framing,
authority semantics, signed branch identity, or object attribution. The default Agent cap is four
lanes, matching the default namespace quota; operators can lower or raise it within `1..64`, but a
namespace policy can only tighten the effective window.

This is not object striping inside one file, range reconstruction for tree-v2, auxiliary route
distribution, power-cut qualification, or proof that near-ceiling sync is production-ready. It is the
first bounded local prerequisite for making the near-ceiling three-writer gate finish inside the
existing time budget.
