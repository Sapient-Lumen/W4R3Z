# Rev0946 mission, capacity, scale, and waste audit

## Heart of the mission

AnonSync exists to let a person remove Resilio Sync from a named real workflow
and keep that workflow working with an open C++ product. Direct TCP, Tor, and I2P
are routes to the same authenticated folder semantics. Proof systems, historical
ledgers, exact authority types, and packaging are valuable only when they make
that replacement safer or faster to ship.

The retained shipping spine is coherent: `anonsync_sync` owns setup and service
lifecycle; the linked peer service owns watch/full-scan wakeup and reconnect;
the folder process composes catalog, replica, and payload stores; reconciliation
runs over authenticated TLS; direct, Tor SOCKS, and I2P SAM connectors feed the
same protocol; rooted atomic publication fences filesystem effects.

## Severe production defect corrected

The default folder catalog and convergence pass each admitted 100,000 current
paths. The production payload store was created by a helper that changed only
its byte ceilings and silently retained `SyncReplicaFilePayloadStoreLimits`'
4,096-entry generic default. The payload namespace is append-only and owns no
collector, so a valid tree of more than 4,096 distinct payloads was structurally
unsynchronizable despite being accepted by the folder contract.

Rev0946 makes the production owner explicit:

- `kSyncReplicaFilePayloadStoreProductionMaxEntries` is 100,000;
- the production helper assigns it instead of inheriting the test default;
- the content-inventory hard limit is raised to the same value;
- the default folder/catalog/pass composition is compile-time checked;
- every pass checks its requested local and remote path counts against the
  actual catalog and payload-store owners before mutation;
- the service configuration validator rejects values above the production
  durable boundary; and
- process-level tests prove the real `check-config` error path.

Simply reserving the new ceiling on every scan would have converted correctness
into routine memory waste. Namespace scans therefore reserve at most 4,096
entries initially and retain the 100,000-entry bound only as a growth ceiling.

## What remains dangerously incomplete

### 1. No durable payload metadata index

Every cold payload snapshot and every new mutation segment still enumerates,
opens, and stats the complete private payload namespace. A cold process hashes
all retained payload bytes. The rev0944/rev0945 warm cache helps only within one
process lifetime. The correct next slice is a crash-consistent SQLite metadata
index keyed by digest, with exact filesystem observations, a monotonic change
sequence, recovery/rebuild from the complete scanner, and a bounded rotating
byte scrub. The scanner must remain the oracle; the index must not become an
unverifiable source of truth.

### 2. Prefix starvation under the aggregate scan budget

`sync_replica_folder_observer.cpp` reads each directory into bytewise-sorted
components and performs a deterministic depth-first traversal from the root.
Every classified regular file is charged before the callback. The default pass
aggregate is 256 MiB (or at least one configured maximum file). Exceeding it
throws after earlier callbacks may have made durable progress. The next pass
starts at the root again.

For a stable tree whose sorted prefix itself fills the budget, later paths may
never be visited. Unchanged files still consume classification bytes. Deletion
inference is intentionally available only after a complete traversal, so such a
tree can also prevent absence repair forever. This is a release-blocking scale
semantics problem, not merely a performance tuning issue.

The durable fix should introduce a scan epoch and continuation cursor. Work may
commit path-by-path, but absence may commit only after the cursor wraps and the
whole epoch is complete. Namespace mutation during an epoch needs explicit
restart/merge rules. Raising the byte budget may be an operator escape hatch,
not the design.

### 3. Append-only payload retention

The current idle fast path explicitly depends on payloads never being deleted.
A collector therefore cannot be bolted on. It needs reachability from current
catalog entries, retained operation/version policy, durable in-flight transfer
prefixes, and active snapshot/batch pins. Collection should be mark/plan,
quarantine, revalidate, then unlink; an epoch or lease must prevent a snapshot
from reopening a digest after collection begins.

Matching the 100,000 current-path ceiling is only initial capacity truth. At the
ceiling, one changed file can need a new digest while the superseded digest is
still retained, so there is no guaranteed churn headroom. Retention/GC and user
recovery policy must be designed together.

### 4. Whole-file retransmission

The wire path can resume a file in bounded ranges, but a one-byte edit still
produces a new whole-file digest and can transfer the entire file. A fixed-block
SHA-256 manifest is the lowest-risk first production delta slice because the
existing range transport and content verification can remain. Local block reuse
should precede network fetch. Rolling-checksum or content-defined chunking is a
later optimization only if the named workflow proves fixed blocks inadequate.

### 5. Product surface gaps

The first Resilio uninstall workload is still unnamed. Rename identity,
directories, portable naming, timestamps/permissions, ordinary conflict copies,
deleted-version restore, selective synchronization/placeholders, explicit
Owner/Read-Write/Read-Only policy, encrypted untrusted storage, multi-share
multi-peer device ownership, ENOSPC/quota recovery, long soak, large-tree
qualification, and desktop/mobile/NAS surfaces are incomplete.

Tor stream isolation in the current connector uses the modern `<torS0X>0`
format with an application-provided isolation token and route locking remains
fail-closed. The next privacy work is live qualification—DNS/address leak tests,
router outage, circuit isolation observation, throughput, and traffic-shape
measurement—not a speculative connector rewrite. I2P deserves the same live
qualification and no anonymity guarantee should exceed measured behavior.

## Severe or wasteful process structure

The unpacked wrapper is roughly 108 MB across 6,544 files. The hidden project is
about 87 MB; `REVISION_EVIDENCE` alone is about 55 MB and 5,683 files. The active
implementation projection is only about 24 MB. A nested rev0907 parent archive
adds about 18.8 MB even though current lineage is rev0945. This is expensive to
copy, hash, unzip, inspect, and republish every turn.

The C++/header/test corpus is about 237,000 lines across 432 files. The older
`sync_domain.cpp` is about 15,167 lines and its selftests about 9,601 lines. They
remain donor/oracle material and are not linked into the shipping
`anonsync_sync`, yet the default all-target graph compiles them. The repository
already has an `anonsync_product_lane`; ordinary work should use it by default,
with the inherited complete graph reserved for scheduled and release assurance.

Recommended gradual correction:

1. Keep one compact current source tree plus content-addressed provenance
   digests. Store historical bulky evidence once, not copied into every ZIP.
2. Periodically squash old revision evidence into a signed/indexed checkpoint
   while retaining verifiable hashes and the selected donor archives.
3. Generate repeated narrative/release views from one structured current-state
   record to reduce BOOTSTRAP/README/notes/gate drift.
4. Split giant files only along tested shipping ownership boundaries; do not
   perform broad aesthetic refactors before the named uninstall workflow.
5. Treat product-lane build/test as the edit loop and the 254-test inherited
   corpus as a release/nightly lane.

## Recommended order of work

1. Name the first uninstall workflow and record path count, bytes, largest file,
   churn pattern, routes, platforms, and acceptable catch-up/recovery times.
2. Add durable fair traversal continuation plus completed scan epochs.
3. Add the durable payload metadata index with rotating scrub and scanner
   rebuild.
4. Add reachability/retention/GC with recovery UX and snapshot pins.
5. Add fixed-block changed-file reuse.
6. Consolidate many shares and peers under one device owner.
7. Finish rename/directory/metadata/conflict/version UX, then cross-platform and
   selective-sync surfaces required by the named workflow.
