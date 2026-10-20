# ADR 0242: Separate content sources from signed-HEAD authority

Status: accepted prerequisite; live content-v2 protocol and genuine-provider qualification remain
open, 2026-08-29.

## Context

M5B still requires one-source and multiple-source convergence on the genuine provider. The current
Agent subscriber is deliberately a one-complete-source range-v1/treepack-v1 service. The preserved
toxsync 0.7.0 component already has a bounded rarest-first `ContentFabricSession`, but attaching it
directly would leave an authority ambiguity: a peer that can supply a digest-named chunk is not
necessarily the peer whose signature selected the revision.

The `IoToxsync-rev0010` capsule in `DR0Pbox` contains a useful older live fabric coordinator,
inventory service, bounded range client, durable O(jobs) intent, immutable-store rescan, and lane
observation logic. It also predates current authority-ledger v3 exact-head proof, IoTox signed HEAD
and rollback guards, explicit FileId attempts, HEAD-last acceptance, route-class constraints, and
the frozen sync-v1 request shapes. Its mechanics are reference material, not code that can regain
product authority unchanged.

## Decision

Freeze a pure `evaluate_sync_content_source` decision before allocating a content-v2 wire format.
The subscriber must first verify and freeze one accepted content-v2 HEAD. An additional source is
eligible only when all of these independently hold:

1. its current session has an authorized exact-head authority-ledger v3 proof;
2. its proven principal has `sync.publish` and appears in the namespace's sorted writer set;
3. the frozen expected HEAD remains valid under the local namespace policy; and
4. the source advertises the exact digest of that already-verified signed HEAD record.

The source need not be the principal that signed the frozen HEAD. This permits writer A to select the
revision and authorized writer B to serve immutable objects for that exact revision. It does not
permit B to replace, advance, fork, or roll back A's HEAD. Every object still needs a request bound
to the frozen HEAD and complete digest verification before immutable-store admission. Source-side
read admission independently continues to require the requester's `sync.subscribe` capability and
subscriber membership.

Reuse the existing writer membership instead of adding an ambiguous third principal list. A writer
already has the stronger local permission to assert revision truth; using that same explicit set as
the eligible immutable-source ceiling does not widen it. Friendship, route membership, transport
availability, possession of a chunk, or an old authority proof never makes a source eligible.

The decision maps every failure to stable content-free truth: invalid policy, wrong engine, invalid
expected HEAD, pre-v3 authority, stale exact-head proof, missing capability, source outside the
writer set, or mismatched HEAD digest. It allocates no feature bit, message type, filesystem effect,
job, transfer, or activation right.

## Qualification

At this prerequisite's acceptance, the owned registry had 620 checks. New deterministic cells prove that a second authorized writer
can serve the exact frozen HEAD even when it did not sign that HEAD, and that wrong digest, wrong
engine, invalid HEAD, missing capability, and non-writer source fail closed. The complete
`iotox.unit-and-integration` CTest route passes in the pinned Nix development environment.

## Consequences

- The authority prerequisite for the multi-source coordinator is closed without weakening the
  existing one-source service or pretending that multiple routes are multiple sources.
- ADR 0244 closes the next construction prerequisite with separately negotiated dark content-v2
  object framing, an authority-gated coordinator, and a replay-safe publisher entrance. Exact sparse
  inventory exchange, live Agent lifecycle, and genuine-provider evidence remain open. Heavy manifest
  and inventory work stays off the toxcore owner callback.
- The older rev0010 coordinator is mined selectively for bounded scheduling, deadlines, source
  disappearance, immutable-store rediscovery, and telemetry. Its old trust, message, and HEAD
  layers are not imported.
- M5B remains open until one-source and complementary multiple-source jobs cross real c-toxcore
  sessions in Sandwurm, survive one selected source disappearing, reconstruct the exact artifact,
  accept the HEAD last, and activate only through the existing explicit token.
