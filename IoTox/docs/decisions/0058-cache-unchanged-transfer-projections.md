# ADR 0058: Cache unchanged live-transfer projections

Status: accepted, 2026-08-15.

## Context

The 8/16/32/64-stream laboratory exposed a second-order cost after ADR 0057 removed per-chunk
projection amplification. Every file admission and terminal event still passed the complete live
transfer set to both the global and per-peer runtime publishers. Each publisher atomically replaced
every record, including records whose exact `FileTransferRecord` had not changed.

At 64 files on one route, this made a 1 MiB shakedown take 71.018 seconds: 39.218 seconds creating
offers and 30.075 seconds admitting destinations. The transfer payload was not the limit. Rewriting
the growing record set on every addition and rewriting the shrinking set on every completion made
the projection path quadratic in concurrent files. A burst of local clients could also exceed the
ordinary five-second control response deadline while queued behind those rewrites.

## Decision

`RuntimeTree` retains an in-memory cache of the last successfully published global and per-peer
`FileTransferRecord` for each live projection key. While holding the existing surface mutex, a
publisher skips an exact unchanged record only when its expected path still exists as a real
directory. New or changed records still use the complete private temporary-directory plus atomic
rename transaction. Records absent from the current live set are still withdrawn immediately, and
their cache entries are erased. `prepare()` clears both the disposable filesystem projection and
its cache.

The concurrency harness also separates end-to-end time from its data window and admits no more
than one short-lived control client per route at once. This prevents the Unix socket queue from
becoming an accidental variable while still admitting every file before the bulk of a 16 MiB phase
is transferred.

## Consequences

- Unchanged transfer directories keep their inode and are not rewritten merely because another
  transfer changed.
- A missing cached directory is rebuilt on the next publication; changed and terminal truth remain
  atomic and immediate.
- The cache is bounded by the already bounded live transfer population and contains metadata only,
  never file payload bytes.
- The runtime tree remains a same-user, disposable observation surface rather than authority. An
  owner deliberately editing a scalar inside an otherwise intact cached directory is outside its
  integrity contract; a structured query still obtains exact manager truth.
- In the post-change 64-stream UDP shakedown, one-route end-to-end time fell from 71.018 to 6.184
  seconds and aggregate process CPU from 9,719 to 549 ticks. The retained 16 MiB UDP and TCP sweeps
  then completed all 48 phases byte-identically with zero dropped events.

## Evidence

- `tests/test_runtime_tree.cpp` proves unchanged projections retain their directory, missing cached
  directories are rebuilt, and empty live sets withdraw them.
- `docs/evidence/2026-08-15-stream-sweep-udp.tsv`
- `docs/evidence/2026-08-15-stream-sweep-tcp.tsv`
- `docs/research/c-toxcore-0.2.23-stream-concurrency-lab-rev0015.md`
