# Retained lane-core audit and refactor

## Audit target

rev0023 introduced the retained parallel encoder and rev0024 adds the companion
retained parallel decoder. The first decoder implementation correctly mirrored
the encoder's generation, wake, drain, and shutdown protocol, but that left two
independent copies of the most concurrency-sensitive code in
`src/parallel_codec.cpp`.

That duplication was an avoidable maintenance hazard. A later fix to generation
ordering, inactive broadcast acknowledgement, callback lifetime, or worker
shutdown could have been applied to one direction but not the other while both
still compiled and passed ordinary round trips.

## Refactor

The encoder and decoder now share four internal components:

1. `RetainedCodecLane` owns one `Workspace`, one background thread, the
   generation handshake, optional inactive wake, result/error capture, and
   deterministic shutdown.
2. `RetainedPoolShape` is the single checked calculation for retained worker
   count, caller participation, per-lane workspace bound, aggregate workspace
   charge, the 256-background-worker cap, and the no-executor guard.
3. `RetainedLanePool` constructs the optional caller workspace and retained
   background lanes from that validated shape.
4. `run_retained_batch` owns task dispatch, partial-dispatch drainage, caller
   execution, the complete acknowledgement barrier, and post-barrier exception
   propagation for both directions.

A tagged internal task selects encode or decode work. It carries only block
shape plus a borrowed `RangeReader`; payload bytes remain in the lane's existing
workspace. The task representation allocates no per block and does not alter
BZ3v1 bytes or decoded output.

The optional serialized-reader adapter and typed task executor are also shared.
The adapter's lifetime remains owned by the coordinating call and every
notified worker is joined at the common batch barrier before it can be
destroyed.

## Allocation and start-order finding

The audit also found that the encoder created a fresh result vector for every
active batch. The decoder already retained its result slots. Both directions
now preallocate one result slot per retained background worker before the pool
starts any thread. Decoder descriptor slots are likewise allocated before pool
construction.

The initialization order is deliberate:

1. validate and charge the complete pool shape;
2. allocate coordinator result/descriptor metadata;
3. reserve the pool's background pointer array and allocate the caller
   workspace, when present;
4. start retained background lanes.

Thus a workspace-budget or scheduling-metadata allocation failure cannot leave
a started worker borrowing an incompletely constructed coordinator. Partial
thread construction remains RAII-safe: already-created lanes are stopped and
joined if a later thread creation throws.

## Preserved failure contract

The coordinator still advances one monotonically increasing generation per
batch. A lane now rejects redispatch while its prior generation is outstanding,
and `wait()` requires an exact match to the dispatched generation rather than
accepting a later result. The task is installed before the visible generation
advance, preserving protocol state even if task representation changes in a
future revision.

Dispatch failure drains the successfully notified prefix. Reader or codec
failures are captured through the same typed executor for caller and background
lanes and rethrown only after all notified lanes acknowledge. Even an internal
caller-workspace shape failure follows that barrier. Sink callbacks begin only
after the batch barrier, so a sink exception cannot strand a worker with a
borrowed callback. Inactive `all_retained` wakes use the same empty optional task
and acknowledgement path in both directions.

## Executable evidence

The encoder and decoder strict groups jointly cover active-only and all-retained
wakes, caller and background-only execution, serialized and concurrent range
reads, partial worker failures, sink failures, post-failure reuse, pool reuse,
concurrent-call serialization, worker caps, and aggregate workspace limits.
Both groups execute the same exact-generation and common-barrier implementation.
GCC and Clang warning-clean Release builds plus ASan/UBSan and ThreadSanitizer
runs are release gates.

This is an internal lifecycle and allocation refactor. It changes neither the
public API nor the BZ3v1 format, and it makes no universal throughput claim.
