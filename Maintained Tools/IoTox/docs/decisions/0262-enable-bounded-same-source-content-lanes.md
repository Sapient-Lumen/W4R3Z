# ADR 0262: Enable bounded same-source content lanes

Status: accepted, 2026-08-30

## Context

Content-v2 deliberately shipped with one active object receive per pull. That made source loss,
FileId attribution, durable CTA1 recovery, and HEAD-last acceptance easy to audit, but it also left
the scheduler unable to test whether independent immutable objects can usefully overlap on one
authenticated Tox session. The existing namespace record already signs `maximum-lanes` and
`maximum-outstanding-requests`; treating those fields as decorative would waste an authority-bound
resource control.

Object concurrency must not quietly become arbitrary concurrency. The root manifest discovers the
graph, the signed HEAD remains the sole revision authority, and one lane failure must not let sibling
work accept a partial revision. Multiple active objects also make the old single `active-file`
projection ambiguous.

## Decision

Add the Agent run option `--max-sync-content-lanes N`, bounded to `1..64`, with default `1`. The
effective per-source ceiling is the minimum of:

- the process option;
- the signed namespace `maximum-lanes` quota;
- the signed namespace `maximum-outstanding-requests` quota; and
- the protocol's bounded lane representation.

Keep the root-manifest request serial. After verified root/page discovery, permit only immutable
manifest-page and artifact-chunk requests to overlap. Keep signed-HEAD acceptance and activation
serial and last. Each lane owns an exact source ID, request message ID, FileId, optional toxcore file
number, object kind/index/size, carrier identity, staging path, and durable CTA1 attempt. A terminal
for one lane settles only that lane before refilling the free slot. Any permanent lane, source,
authority, commit, or job failure attempts to cancel and durably fence every sibling before
failing the whole pull; if the storage transaction itself is unavailable, conservative recovery
retains the residue for the existing durable-attempt recovery path instead of claiming cleanup.

`sync-status` reports `content-lane-cap=N`, `active-lanes=N`, and one owner-private
`content-lane-job=` row per live binding. The compatibility `active-file` fields remain populated
only when zero or one lane makes them unambiguous; a multi-lane job exposes `active-file=none` and
the exact lane rows instead.

Do not change content-v2 peer framing, feature bit 29, local-control framing, signed HEADs, CTA1
encoding, source authority, carrier binding, or activation semantics.

## Evidence

The 666-check owned registry includes a real paged-content test with a two-lane process and namespace
cap. It requires two simultaneous requests to one source with distinct request IDs and FileIds,
completes the second lane before the first, observes immediate single-slot refill, and converges with
HEAD accepted last. A second job fails one of two live lanes and requires whole-job failure, sibling
transport cancellation, zero live lanes, and an empty durable active-attempt journal.

Two genuine source-linked Sandwurm pairs run the dedicated
`sync-content-same-source-lanes` scenario:

- direct UDP compact proof `pair.895m5lwy`;
- forced TCP compact proof `pair.bcecui0l`.

Both use the same product binary SHA-256
`8296219d64ece148355610a04a7b83a04c509fbaf61eabf4b16312a631f4b3a7`. The subscriber receipt in
each proof records process cap 2, two simultaneously admitted non-root lanes, one source, two
distinct request IDs, two distinct FileIds, convergence, and explicit activation. The standalone
verifier rejects missing, publisher-side, aliased, root-lane, or non-admitted claims. See
`../evidence/2026-08-30-sandwurm-sync-content-same-source-lanes.md`.

## Consequences

IoTox can now overlap independently verifiable content objects on one authenticated source without
relaxing its conservative default or HEAD-last atomicity. Signed policy can reduce the process
setting but cannot be bypassed by it. Exact per-lane status makes later scheduling and bottleneck
science observable without exporting content or paths.

This is not byte striping inside an object, multiple Tox friendships, auxiliary-route distribution,
physical-path diversity, or a measured throughput improvement. The dedicated VM gate uses one
source and one Tox session in each route mode. Lane-count A/B performance, fairness under competing
traffic, same-source distribution across independently authenticated auxiliary carriers, and
daemon-restart recovery with multiple active lanes remain separate gates.
