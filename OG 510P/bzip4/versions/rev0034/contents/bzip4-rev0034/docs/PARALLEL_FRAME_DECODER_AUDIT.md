# Parallel frame decoder audit

rev0024 adds compatible parallel BZ3v1 frame decoding without changing the
block codec, frame grammar, decoded byte order, or scalar APIs. The decoder is a
retained fixed-block-size pool: codec state and BWT scratch survive between
calls, while each call retains only a bounded batch of block descriptors and
workspace-owned decoded spans.

## Execution and ownership model

`ParallelFrameDecoder` owns one `Workspace` for the caller lane when caller
participation is enabled and one workspace plus one persistent thread for each
retained background lane. The worker lifecycle and checked pool-shape calculation
are shared with the encoder; decoding retains only its descriptor scheduling and
ordered decoded publication logic. Construction validates the fixed block size, computes
the checked per-lane codec-state plus scratch bound, charges every retained lane
against `max_workspace_bytes`, and enforces the 256-background-worker hard
limit before any worker is created.

The complete frame envelope is scanned before a decoded sink callback. The
shared `FrameBlockCursor` then rereads descriptors into a vector sized only to
the retained lane count. Each bounded batch assigns at most one block to each
active lane. Background work is dispatched first, the caller decodes lane zero
when enabled, every notified worker is acknowledged, and only then are decoded
workspace views published in exact block order. No complete output vector or
per-block decoded copy is required by the streaming path.

The same floor-grain `ActivationPlan` used by the encoder selects productive
decode lanes from block count and total logical bytes. `active_only` notifies
only workers with a block. `all_retained` remains an explicit broadcast control
whose inactive wakeups are counted. The first batch gives every active lane one
block, so the reported productive-lane count is witnessed rather than inferred
from a worker population that never ran.

For a one-shot `active_only` call, the helper scans the envelope first and trims
the retained population to the actual activation plan before charging codec
workspaces or starting threads. An empty one-shot frame allocates no codec state
or worker and remains valid under a zero workspace budget. Reusable decoder
objects deliberately retain their configured pool, including when a particular
frame activates fewer lanes.

## Source and callback contract

A range source must fill every requested span or throw and must expose stable
bytes for the complete call. Active lanes may issue disjoint payload reads
concurrently. `serialize_range_reads` wraps the callback with a mutex for stable
random-access sources that are not concurrency-safe; block decode remains
parallel after the serialized reads complete.

The generic callback is not an authenticated snapshot. A hostile callback that
changes bytes between the envelope scan and payload reads violates the API
contract. Descriptor-pinned filesystem callers provide a stronger publication
boundary: positional reads use one retained descriptor, source identity and
metadata are rechecked after codec completion, and output is committed from a
same-directory private temporary only after that check.

Sink spans alias lane-owned workspace and are valid only for the callback.
Callbacks must copy or consume synchronously and must not re-enter the same
decoder. A later block checksum/transform error or sink exception can leave a
valid decoded prefix in a non-transactional sink, so all-or-nothing callers
must stage publication.

## Failure and lifetime audit

The retained pool follows these ordering rules:

- all scheduling vectors and synchronization fields exist before dispatch;
- each worker task borrows only a call-local reader that remains alive until all
  notified workers acknowledge the generation;
- a partial dispatch prefix is drained if a later dispatch fails;
- reader and codec exceptions are captured per lane and rethrown only after the
  complete notified set has been joined at the batch barrier;
- sink callbacks begin only after the batch has no running worker;
- a sink exception therefore cannot strand a worker on call-local state;
- failed calls do not advance into another batch and the retained pool is
  reusable on the next call;
- calls on one decoder serialize around the shared arenas and generation
  counters.

The retained-workspace budget covers the codec state and scratch arena reported
by `workspace_memory_bound()` for every retained lane. It does not include
thread stacks, synchronization objects, allocator bookkeeping, page cache, the
source, or bytes copied by a sink.

The encoder and decoder now share the worker-generation, exception-drain,
inactive-wake, pool-shape, serialized-reader, and joined-shutdown machinery.
The audit and allocation-order rationale are recorded in
`RETAINED_LANE_CORE_AUDIT.md`.

## Executable evidence

The strict `parallel_frame_decoder` group covers exact reconstruction and
publication order, retained reuse, concurrent-call serialization, true floor
grain, active-only and broadcast accounting, concurrent and serialized source
reads, background-only operation, reader/codec/sink failure drainage, post-
failure reuse, one-shot worker trimming, empty zero-allocation behavior,
pre-callback output and trailing-byte rejection, changed descriptors, fixed
block-size enforcement, workspace and worker limits, and null callbacks.

Across 18 external regular-datacube ZIP specimens, the final refactored
four-lane encoder remained byte-identical to the prior compatible frames and
four-lane decoding rebuilt 98,376,644 bytes exactly from 104 independent
one-MiB blocks. Seven balanced-order scalar/four-lane process pairs on two
external specimens measured median decode times of 3.61/1.45 seconds and
1.83/0.72 seconds. Corresponding median peak RSS was 14,880/44,572 KiB and
14,648/44,208 KiB. The parallel pool charged 30,462,536 bytes of retained codec
workspace. These are focused single-host witnesses, not universal speed or
memory claims.

## rev0027 compact retained workspaces

One-shot parallel decode now constructs lane workspaces from the exact validated
frame plan rather than the declared upper bound. The retained decoder adds an
explicit compact constructor accepting both the declaration and retained state
size. Complete preflight still occurs before dispatch; a frame requiring a
larger state is rejected before any sink callback. The original constructor
continues to retain declaration-sized lanes for callers that need one pool able
to accept every legal frame under that declaration.
