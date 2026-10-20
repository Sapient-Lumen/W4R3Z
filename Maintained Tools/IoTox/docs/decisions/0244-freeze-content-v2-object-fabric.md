# ADR 0244: Freeze the bounded content-v2 object fabric

Status: accepted construction prerequisite; live Agent and genuine-provider qualification remain
open, 2026-08-29.

## Context

ADR 0242 separated immutable content sources from signed-HEAD authority but intentionally allocated
no protocol. The preserved toxsync 0.7.0 component already contains verified flat and paged
manifests, a digest-named content store, bounded windows, exact/sparse availability, rarest-first
multi-source scheduling, source removal, and reconstruction. Importing that scheduler without a
current IoTox frame, authority, replay, FileId, and HEAD binding would recreate the ambiguity ADR
0242 removed.

## Decision

Allocate feature bit 29, `state-sync-content-v2`, dependent on state-sync-v1, and canonical message
types 28/29 for one immutable page/chunk request and its correlated result. Keep the bit out of the
implemented/default feature mask until the Agent owns the complete lifecycle. Freeze the byte
layouts and failure statuses in `protocol-sync-content-v2.md`.

Embed only the current toxsync content mechanics needed by the product core. Add a bounded,
transport-neutral coordinator that:

- freezes and independently verifies one accepted content-v2 HEAD and root manifest;
- admits each source only through the ADR 0242 exact-v3 decision plus negotiated bit 29;
- schedules immutable manifest pages and artifact chunks within namespace and workspace bounds;
- verifies every commit into the content-addressed store, reconstructs the exact artifact, and
  exposes content-free counters; and
- fences and returns every in-flight assignment when a source disappears so a future live owner can
  cancel the corresponding exact transport handles.

Add a source-side publisher service that requires current `sync.subscribe` authority and membership,
rehashes the local signed HEAD, derives object identity and path through the verified manifest,
rehashes the CAS object, retains bounded replay before offer, and never reoffers on exact replay.
The service accepts no remote pathname and treats a file result as separate from file completion.

The first coordinator entrance names only complete-window sources. ADR 0245 subsequently freezes the
preserved scheduler's exact sparse-availability entrance and types 30/31; this decision remains the
object-transfer prerequisite.

## Qualification

The owned registry now has 628 checks. Deterministic cells cover canonical and adversarial codecs,
feature dependency, current subscriber admission, replay without reoffer, replay conflict, wrong
HEAD, false membership, locally corrupt or missing objects, flat and paged reconstruction, two
independently authorized simultaneous sources, in-flight source disappearance, stale completion
refusal, survivor convergence, and bounded resident workspace. The complete owned CTest passes in
the pinned Nix environment.

## Consequences

- The content-v2 trust, framing, CAS resolver, publisher entrance, and scheduler seam are frozen
  without changing the live product surface.
- Message allocation does not imply support. The Agent must not advertise bit 29 until durable
  attempts, exact FileId/result joining, quota/reachability/GC, authority/epoch retirement, and
  restart behavior are integrated and tested.
- M5B remains open. Genuine one-source and multiple-source Sandwurm cells must cross c-toxcore,
  remove one selected source after positive progress, converge the exact artifact, accept HEAD last,
  and activate only via the existing explicit token.
- Representative performance corpora remain necessary before claiming complementary-source
  efficiency or preferring content-v2 over range-v1.
