# Restart-Discoverable Quarantine Inventory Audit — rev0963

## Heart of the mission

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
application. Diagnostic corruption handling matters only when an owner can use
it safely during normal service operation. Rev0961 could preserve one exact
corrupt image, and rev0962 could release an exact image, but the owner still had
to know both digests from the most recent incident. After restart, or after more
than one retained image, older evidence was effectively hidden behind private
filenames. A bounded store that cannot disclose its bounded occupants is not an
operable product boundary.

## Product boundary

Rev0963 exposes the complete retained diagnostic quarantine set inside ordinary
owner status. Each entry contains only:

- the expected payload SHA-256;
- the observed corrupt-byte SHA-256; and
- the observed private-file size.

Those exact digest pairs are sufficient selectors for the already-shipping
`quarantine-release` operation. No new socket command, daemon, queue, scheduler
knob, or mutation engine is added. Status does not restore bytes, authenticate
the quarantined image, infer a user path, or turn diagnostic evidence into a
file-version archive.

## The operability defect

Before this revision, status retained only the last requested quarantine action
and its last result. That is action history, not retained-set truth. The private
quarantine namespace may contain up to sixteen images and may outlive the
process that created them, while the release CLI requires the exact expected and
observed digests. An older pair could therefore consume bounded capacity forever
without any supported way to rediscover its selector.

A draft repair added a separate `quarantine-list` request and a fresh rooted
traversal for every query. The audit rejected that shape. It would have widened
the local protocol, duplicated an existing complete namespace observer, acquired
filesystem and lease authority in a read-oriented status path, and made repeated
status polling spend directory work. The corrected design reuses already-paid
observations from ordinary store work.

## One bounded projection, not a second traversal

The payload store already completely observes canonical quarantine entries in
two places:

1. an ordinary complete writable payload-store scan; and
2. the narrow exclusive-lease observer used by exact preserve and release.

Rev0963 projects those observations into one fixed process-local structure:

- at most `kSyncReplicaFilePayloadStoreMaxQuarantineEntries` entries (sixteen);
- two fixed 64-byte lowercase digest arrays and one `uint64_t` size per entry;
- exact entry count and overflow-checked byte total; and
- canonical expected/observed digest ordering.

The internal projection is fixed-width and trivially copyable. No path string or
basename is retained. The public `std::vector` is materialized only when the
owner asks to render status. Thus the long-lived cache remains bounded and the
status view cannot accidentally become another filesystem owner.

## Complete-scan publication cutpoint

A complete writable scan still performs the existing work: reader-fenced shared
lease acquisition, exact identity proof, complete lexical namespace traversal,
private regular-file validation, count and byte frontier enforcement, payload
metadata/byte verification, scrub-state handling, retained-root proof, and final
lease proof.

The quarantine projection is prepared before the terminal authority cutpoint.
It publishes only after verification-generation, checkpoint, scrub, and
integrity-fault state have all reached their existing final state. Allocation or
validation failure therefore leaves the preceding observation intact; a new
observation cannot become visible before the scan that supports it completes.
Quarantined bytes are not hashed merely to render status. Their sizes are
metadata evidence, while their digest-bearing filenames remain selectors rather
than authenticity proof.

## Preserve and release mutation cutpoints

The exact preserve/release observer now returns the same fixed projection as the
complete scanner.

For a non-mutating typed result, the projection publishes only after the lease,
reopened root, and retained root are re-proved. For a mutating result, the
successor projection is prepared before mutation. The prior cached observation
is forgotten immediately before the no-replace rename or exact unlink. Only
after directory synchronization, pathname transition proof, final lease proof,
and both rooted-authority proofs does the exact successor publish.

This ordering matters under exceptions. A failure after namespace mutation can
leave status **unknown**, but cannot leave a known stale list claiming that an
old image still exists or a new one does not. Exact absence also republishes the
complete retained observation, so an idempotent release repairs discoverability
without another full payload scan.

## Restart semantics and age semantics

The inventory is process-local presentation state, not a new durable database.
A fresh process begins with `observation_known=false`. Its first ordinary
complete writable scan rediscovers every retained canonical image under the
normal identity and lease boundary and then publishes the exact sorted set. A
ready retained service has already completed its initial repair, so ordinary
owner status exposes the resulting empty or populated observation.

`last_observation_age_milliseconds` is monotonic process age since the most
recent complete leased observation. It is not a persisted creation timestamp,
retention age, last-access time, or proof that no same-UID actor has changed the
namespace since that cutpoint. The adjacent refactor centralizes this monotonic
age calculation with scrub status instead of keeping two subtly different
implementations.

The raw store API preserves honest process-cold semantics. The service adds a
stronger product contract: its initial repair always obtains one complete
writable payload-store snapshot and moves that exact owner-bound snapshot into
the existing convergence algorithm. The service does not become ready unless
the bounded inventory witness remains known. Four counters expose the handoff,
entry cardinality, any accidental second snapshot observation, and mutation
full scans. The empty-folder process oracle requires one handoff and zero second
observations. This avoids hidden duplicate work while acknowledging that
startup readiness now pays one namespace traversal.

## Status contract

Status advances to `anonsync.peer-service.status.v10`. The existing
`payload_quarantine` object gains an `inventory` object containing:

- `observation_known`;
- nullable `last_observation_age_milliseconds`;
- `entry_limit` and `byte_limit`;
- `entry_count` and `total_bytes`; and
- a canonical sorted `entries` array of exact expected digest, observed digest,
  and size.

The view is filesystem-cold and exact-owner-thread-affine. It opens no file,
acquires no payload-store lease, hashes no byte, and advances no request or
effect generation. Live and terminal status use the same canonical renderer.
Action history remains separate: the last preserve/release result is not
misrepresented as the complete retained set.

## Mechanical runtime oracles

The focused C++ payload-store regression proves:

- a new owner begins with an unknown observation;
- a complete empty scan publishes a known empty inventory;
- two retained images written in noncanonical creation order are rediscovered
  after restart and rendered in canonical digest-pair order;
- diagnostic images never enter authoritative payload inventory;
- exact release immediately publishes the one-entry successor without another
  complete scan;
- exact absence preserves the complete observation; and
- a second process again begins unknown and rediscovers the remaining image on
  its ordinary complete scan.

The real configured-service process oracle proves, through the shipping status
socket, that initial convergence reports a known empty observation, exact
preserve reports the one retained digest pair and size, exact release reports a
known empty successor, terminal status retains that empty truth, authoritative
payload bytes and inode remain unchanged by release, and the same service PID
remains healthy. The independent folder-wake process oracle covers the empty
startup path: readiness follows exactly one complete payload snapshot handoff,
the receiving convergence pass performs zero duplicate snapshot observations,
repeated status queries preserve the known observation without I/O, and restart
repeats the same bounded cutpoint before becoming ready.

## Audit/refactor findings

### Payload-store cardinality is not current-path cardinality

The restart process oracle originally expected one handed-off payload entry
because the catalog retained one current path. That was wrong: the store is
append-only, and a create followed by an edit retains two immutable payload
objects even though the catalog still exposes one current path. The corrected
oracle proves two payload entries, one snapshot handoff, zero duplicate snapshot
observations, and one current catalog entry. Status and capacity reasoning must
therefore treat payload namespace cardinality as its own quantity rather than
borrowing catalog cardinality.

1. **Last action was not retained-set truth.** A process could preserve several
   exact images while exposing only the newest action result. The complete set
   now has its own bounded status domain.
2. **A list command would have been wasteful duplication.** Existing complete
   observers already pay the rooted traversal. Status now borrows their result
   rather than creating a query-time authority path.
3. **Mutation can invalidate presentation state before it succeeds.** The old
   projection is explicitly forgotten before rename/unlink, and a prepared
   fixed successor publishes only after terminal reproof.
4. **Paths are unnecessary retained state.** Canonical digest pairs reconstruct
   the private basename and select exact release; storing path strings would add
   allocation and duplicate derived data.
5. **Observation age is not retention age.** A monotonic process timestamp is
   useful staleness context but cannot drive collection policy.
6. **Readiness must not outrun diagnostic discoverability.** The initial draft
   allowed an empty service to become ready while retained evidence remained
   unknown. That made restart discoverability depend on unrelated future file
   work. Initial repair now pays one complete payload-namespace observation and
   moves its exact snapshot into convergence. Runtime counters prove one handoff
   and zero duplicate observation. The live ready predicate checks the current
   allocation-free witness as well as the historical initial-repair bit, so a
   mutation that revokes stale presentation cannot leave readiness overstated.
   This is a deliberate startup metadata cost, not hidden free behavior.
7. **A stale-SAM test relied on cross-socket scheduler luck.** Closing the
   control TCP stream before replying on a separate data stream does not prove
   the connector observed that close first. The oracle now half-closes control
   and waits for Linux `TCP_INFO` to reach `TCP_FIN_WAIT2` before releasing the
   data marker, mechanically ordering the stale-session probe without widening
   production retry behavior.

## Research-informed product comparison

Resilio Sync's Archive is a user-visible recovery feature: remote replacements
or deletions move older copies into Archive, desktop retention defaults to 30
days, and restoration is manual. Syncthing separately exposes configurable
per-folder file versioning strategies with retention rules and a versions
namespace. These products make retained user versions discoverable because
recovery is an ordinary product obligation.

Sources reviewed:

- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files
- https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences
- https://docs.syncthing.net/users/versioning.html

Rev0963 deliberately does **not** label diagnostic corruption evidence as an
Archive or version. A future user-version owner needs path identity, causal
version identity, retention class, reachability pins, quota and age policy,
crash-safe collection, list/restore UX, and conflict semantics. Reusing this
quarantine namespace for that job would conflate untrusted corrupt bytes with
restorable user history.

## What this proves

Rev0963 proves a bounded vertical C++ status slice from complete rooted
observation through fixed process projection, exact mutation successor,
canonical live/terminal JSON, restart rediscovery, real service operation, and
release-package binding. It repairs a concrete owner-operability defect without
adding another command or spending another namespace traversal.

## What this does not prove

- The inventory is not a durable index. A raw fresh payload-store owner begins
  unknown, while the retained service performs one complete initial observation
  before claiming readiness.
- Ready status does imply a known inventory. `observation_known=false` remains a
  truthful process-cold or revoked state and does not itself assert corruption;
  the status path still performs no I/O.
- It is the last complete leased observation, not a continuously live view.
- Digest-bearing quarantine names are selectors, not authenticity proof; exact
  preserve remains the byte-proving operation.
- There is no automatic retention, TTL, quota eviction, reachability graph,
  archive browser, user-path mapping, restore, version history, or garbage
  collector.
- Diagnostic evidence remains bounded by sixteen entries and the active indexed
  byte budget; reporting the frontier does not choose what to release.
- The same-effective-user boundary is cooperative; hostile same-UID code is
  outside this protection boundary.
- Linux rooted descriptor, `flock`, Unix socket, and directory-sync behavior is
  not a universal network-filesystem or power-loss guarantee.
- Rename identity, directories, portable metadata, conflict UX, selective sync,
  changed-block transfer, many-share ownership, live Tor/I2P qualification, and
  a named measured Resilio uninstall workflow remain open.
