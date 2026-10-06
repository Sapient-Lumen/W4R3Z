# Parallel frame encoder audit

rev0023 adds compatible parallel BZ3v1 frame compression without changing the
block codec or the byte order of a valid frame. The implementation is a
retained, fixed-block-size encoder rather than a per-call collection of detached
jobs.

## Execution and ownership model

`ParallelFrameEncoder` owns one `Workspace` for the participating caller and one
workspace plus one persistent thread for each retained background lane. The worker
lifecycle and checked pool-shape calculation are shared with the rev0024 decoder;
encoding retains only its operation-specific scheduling and publication logic. The
constructor validates the block size, computes the checked per-lane memory
bound, charges every retained workspace against `max_workspace_bytes`, and only
then creates worker threads. A hard limit of 256 retained background workers
prevents an untrusted configuration from turning into an unbounded thread
request.

The existing floor-grain `ActivationPlan` selects the productive lanes for each
frame. For every bounded batch, each active lane receives at most one logical
block. Background work is dispatched first, the caller performs lane zero when
enabled, and every notified background worker is acknowledged before any block
is published. Completed payloads remain in their lane-owned workspaces and are
sent to the sink in original block order; there is no intermediate encoded
payload copy.

For active-only one-shot execution, the helper applies block count,
maximum-lane, and floor-grain policy before charging workspaces or starting
threads. The `all_retained` control instead preserves its configured inactive
wake-control population, subject to the same 256-worker and memory limits,
rather than silently rewriting the experiment into active-only behavior.
Empty one-shot frames emit the canonical 13-byte header without constructing a
codec workspace or thread pool. Reusing a `ParallelFrameEncoder` keeps thread
and codec/BWT workspace setup out of later non-empty calls.

## Range-reader contract

By default, active lanes may invoke the supplied `RangeReader` concurrently on
disjoint exact ranges. `serialize_range_reads` wraps the reader with a mutex for
sources that provide stable random access but are not concurrency-safe. The
filesystem CLI uses descriptor-pinned positional reads, so it can use the
concurrent path while preserving the existing post-read source fingerprint
check and atomic output publication. Sink spans are borrowed only for the
callback duration; reader and sink callbacks must not re-enter the same
encoder.

## Failure and lifetime audit

The audit established the following ordering rules:

- synchronization and result fields exist before a background thread starts;
- result bookkeeping is allocated before any worker borrows the call-local
  reader wrapper;
- a partially dispatched worker prefix is drained if a later dispatch throws;
- reader and codec exceptions are captured per lane and rethrown only after all
  notified workers acknowledge the batch;
- sink callbacks start only after the whole batch is drained;
- a reader, codec, or sink failure cannot leave a worker using call-local state;
- the retained encoder remains reusable after ordinary callback or codec
  failures.

As with the scalar streaming API, the sink can receive a valid frame prefix
before a later error. Filesystem publication therefore remains behind
`AtomicFileWriter` and occurs only after complete codec success and input
revalidation.

The retained-workspace budget charges codec state plus scratch storage for every
retained lane before thread creation. It does not claim to bound thread stacks,
synchronization objects, allocator metadata, page cache, or bytes retained by a
sink. The batch barrier is deliberate: it bounds live encoded results and makes
ordered zero-copy publication simple, but a slow block can delay faster blocks
in that batch. More dynamic scheduling remains a measured follow-up, not an
implicit claim of optimality.

## Compatibility and measured evidence

The strict `parallel_frame_encoder` group covers scalar/parallel byte identity,
pool reuse, floor-grain activation, active-only and all-retained wake behavior,
one-shot control-population preservation, serialized reads, reader and sink
failures, background-only execution, memory-budget rejection, worker caps, and
empty input without hidden workspace allocation.

Across the 18 external regular-datacube ZIP specimens, 98,376,644 input bytes
were encoded as 104 logical blocks under a requested one-MiB policy. One-lane
and up-to-four-lane frame bytes were identical for every archive, and every
parallel frame decoded to the exact
source bytes.

On one 17,616,777-byte representative archive, five alternating process runs
had median elapsed times of 1.80 seconds for scalar compression and 0.66 seconds
with four lanes. Median peak RSS increased from 14,604 KiB to 42,528 KiB, while
the four-lane encoder reported 30,462,536 charged retained-workspace bytes. The
3,028,312-byte frame and SHA-256 were identical in every run. This is a focused
single-host concurrency witness, not a universal throughput or memory claim.
rev0023 did not include parallel decoding; rev0024 adds the companion retained
decoder documented in `PARALLEL_FRAME_DECODER_AUDIT.md` and consolidates their
worker lifecycle in `RETAINED_LANE_CORE_AUDIT.md`.
