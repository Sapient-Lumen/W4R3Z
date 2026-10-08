# AnonSync rev0896 revision notes

## Mission increment

Rev0896 follows the rev0895 product spine by making the executable able to state
its own durable condition. The heart of AnonSync remains exact authorized
history under live, owned capability boundaries. This revision adds an
operator-facing `status` command that derives its report from the same durable
owners that claim, send, receive, publish effects, and anchor membership. Status
is therefore a subordinate observation of evidence and cutpoints, not a second
source of truth.

## C++ implementation

`src/anonsync_replica.cpp` now exposes:

- `status --replica-db ... --folder ... --local-device ... --local-epoch ...`
- optional `--payload-root` for retained durable payload inventory;
- paired `--effect-db --files-root` for receiver effect state; and
- paired `--membership-db --anchor-db` for anchored TLS membership state.

The implementation restores the causal replica model from the SQLite owner,
counts evidence/active/pending/quarantined/visible operations, reports causal
heads and missing predecessors, summarizes outbox lease states at the durable
outbox high-water epoch, reports the outbox clock health/anomaly/generations,
and emits operation/evidence/visible/cutpoint digests. Optional sections report
payload store entry/byte totals and digest, effect staged/published counts and
cutpoint, and membership generation/policy/entry/anchor agreement.

## Audit/refactor

The CLI now has small local helpers for JSON booleans, outbox clock health
names, outbox status summaries, effect status summaries, and paired option
validation. The important refactor is not cosmetic: the executable no longer has
only verbs that mutate or transfer. It has one bounded condition surface that
uses reviewed owners rather than open-coded SQL. The process test forces that
surface to observe the product before and after the network cutpoint.

The queued sender status deliberately treats a zero outbox high-water epoch as
not claimable while still counting the unclaimed intent. That avoids asking the
lease policy to certify liveness at an impossible epoch zero and makes the
status report conservative before any durable clock observation.

## Process proof expansion

`tools/test_anonsync_replica_cli.py` now validates status in three states:

1. after enqueue, the sender has one active operation, one outbox intent, and one
   retained payload;
2. after `send-one` receives the exact terminal receipt, the sender outbox is
   empty and the payload remains retained; and
3. after `serve-one`, the receiver has one published file effect, retained effect
   payload bytes equal to the source bytes, and anchored membership generation,
   policy, entry count, and anchor agreement.

## Build and audit observations

The full GCC Debug build required several resumed invocations because the
cloudtainer command window interrupted long compilations. A final `ninja: no
work to do.` closure was reached, and the complete registered CTest suite passed
214/214 afterward. This confirms the earlier waste diagnosis: target and
translation-unit fragmentation still make a small CLI change traverse a large
build graph. The corrective direction is consolidation and product-spine-first
integration, not weakened tests.

`clang-format` was not installed in this cloudtainer, so no formatting tool run
is claimed. The focused structural audits for outbox clock authority, bounded
regular file reads, SQLite busy handler ownership, and release path policy
passed.

## Dependency note

SQLite 3.53.4 remains the current upstream release observed during this session,
with official 3.53.4 source and amalgamation hashes recorded in the revision
research note. The tree still vendors 3.53.3. Rev0896 does not claim an SQLite
upgrade.

## Explicit nonclaims

Rev0896 does not provide a daemon, continuous scheduling, discovery, NAT
traversal, causal directory creation, tombstones, rename/symlink convergence,
chunking/resume, reachability, garbage collection, indexed performance,
automatic clock recovery, exactly-once network delivery, cross-resource
atomicity, at-rest encryption, capability-private sync, anonymity,
unlinkability, endpoint hiding, traffic-analysis resistance, hostile same-UID or
privileged-writer defense, universal network-filesystem semantics, Windows
runtime coverage, external signed build provenance, or formal proof.

## Next milestone

Turn the one-shot product spine into a bounded durable loop with status-aware
shutdown/recovery and explicit clock recovery, then model causal directories,
tombstones, and reachability/GC. In parallel, perform exact SQLite 3.53.4
acquisition and hash-pinned migration.
