# ADR 0330: Batch tree-v2 file-object commits

- Status: accepted and implemented; subscriber inventory schedule refined by ADR 0331
- Date: 2026-09-03

## Context

ADR 0329 made exact tree-v2 object transfer concurrent without changing the frozen wire protocol.
The retained 3,500-file Sandwurm series showed that increasing the lane cap from 4 through 16
helped, but caps 32 and 64 regressed severely. Inspection then found a local amplification boundary
behind the transport: every completed file lane called the general tree-v2 CAS importer separately.
That importer correctly inventories and digest-verifies the complete existing immutable store before
prospective quota admission. Repeating that full inventory once per 16-KiB object made large
small-file pulls effectively quadratic.

The first batching experiment also exposed an independent transport race. A pull can be cancelled
after an exact object response is received but before the corresponding Tox file-offer callback is
delivered. Once the lane was gone, that late offer was no longer recognized by tree-v2 and could
fall through to the generic incoming-file surface in a paused state, consuming sender transfer
slots.

## Decision

Keep tree-v2 framing, authority, FileId binding, manifests, signed branches, and projection semantics
unchanged. Change only the subscriber's local commit schedule:

1. A successfully completed file transport remains in its owner-private `.receive-*.part` staging
   path while other file lanes in the current bounded window finish.
2. Once every lane in that window is a completed file object, pass the complete window to the
   existing CAS importer under one namespace transaction. The effective batch size can never exceed
   the lowest of the process lane cap, signed namespace lane cap, and signed outstanding-request
   cap.
3. The importer still performs a complete strict-store inventory, prospective quota admission,
   exact per-file SHA-256 and size verification, no-replace installation, and per-object durability.
   Signed branch acceptance and atomic workspace projection still occur only after the required
   object closure exists.
4. A cancelled, failed, or disconnected lane whose Tox offer has not arrived leaves an exact
   friend/epoch/stable-principal/carrier/FileId retirement record. A later matching offer is claimed
   and immediately cancelled. The process retains at most 4,096 such records; current retained
   count, successful late cancellations, and evictions are owner-visible.

`sync-status` now reports aggregate `tree-file-commit-batches`,
`tree-file-objects-committed`, `tree-largest-file-commit-batch`,
`tree-late-offers-cancelled`, `tree-retired-offer-ids`, and
`tree-retired-offer-evictions`. Each retained tree job reports `staged-file-objects`,
`file-commit-batches`, and `largest-file-commit-batch`. The three-writer receipt and verifier bind
the terminal batch sizes and require zero retained FileIds and zero retirement evictions at accepted
capacity convergence.

## Consequences

At cap 16, a full file window now pays for one complete CAS inventory instead of as many as sixteen.
The direct source-linked 3,500-file retry completed capacity catch-up in 387.085 seconds and the full
conflict/resolution gate in 478.624 seconds. Its two followers each committed 3,500 file objects in
219 batches with a largest batch of 16.

The exact networkless Sandwurm cap-16 repeat on committed revision
`defd492e00162e5a59bdcc8982c97b0c085f3d0f` then passed the same 3,500-file, 2-vCPU/2-GiB gate.
Capacity catch-up fell from 1,059.715 to 654.214 seconds, a 405.501-second or 38.3% reduction. Full
elapsed time fell from 1,138.904 to 788.317 seconds, a 350.587-second or 30.8% reduction. Each
follower again committed 3,500 files in 219 batches with a largest batch of 16. The live fence
cancelled 7 and 8 late offers; all nodes ended with zero retired IDs and zero retirement evictions.
Compact proof `.sandwurm/exports/three-writer/run.WoveT4SE` verifies independently.

This batch is namespace-serialized, bounded, and effect-safe; it is not an ACID multi-object
transaction. An interrupted batch may leave additional valid immutable CAS objects, but no new
signed branch or projected workspace becomes visible from those orphan objects. A corrupt staging
source can similarly fail after an earlier valid object was installed; ordinary reachability and GC
rules treat the extra object as unreferenced immutable data.

This ADR's implementation originally revalidated the full object store once per batch, leaving the
residual algorithm approximately quadratic in object count divided by effective batch width. ADR
0331 now replaces that subscriber schedule with a pull-private verified inventory and a strict final
effect fence; the general importer remains strict for standalone callers. Native filesystem watching,
incremental source scans, and a separately negotiated tree-v2 bundle/range extension are still open. The default
tree lane cap remains four; this result does not authorize raising it globally or claim precious-data,
power-cut, dishonest-storage, physical-machine, or long-soak qualification. ADR 0353 later
remeasures the cap-4/cap-8/cap-16 sweet spot after additional source-watch and scan work; that
current constrained-VM series favors cap 8 and keeps cap 16 as negative scaling evidence.
