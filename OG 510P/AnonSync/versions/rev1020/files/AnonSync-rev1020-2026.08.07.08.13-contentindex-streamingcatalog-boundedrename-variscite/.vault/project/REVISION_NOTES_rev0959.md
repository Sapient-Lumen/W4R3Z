# Revision notes — rev0959

## Mission

AnonSync remains one C++ product intended to replace Resilio Sync for a named
real folder workflow. Rev0959 closes an unsafe old-reader composition in the
retained payload store and refactors identity-generation handling. It does not
add a parallel service, scanner, database, or synchronization algorithm.

## Primary C++ correction

- Raised the minimum payload-store reader generation through new standalone and
  product identity/lease-anchor basenames while preserving the established v2
  and v3 identity payload bytes.
- A writable owner encountering one exact legacy marker must first acquire an
  exclusive lease on that exact inode and complete a rooted full payload scan
  with process-cache and durable-checkpoint byte reuse mechanically disabled.
- Only after that current-byte proof succeeds does the owner atomically rename
  the exact locked inode with Linux `RENAME_NOREPLACE`, synchronize the inode and
  parent directory, prove the old name absent and new name exact, and rebind the
  live lease to the post-rename observation.
- A successful migration hands its cold verified generation to the immediately
  following ordinary snapshot, avoiding a duplicate payload-byte pass.
- The pre-rename verification checkpoint is forced to refresh because its store
  identity observation cannot authorize the renamed marker.
- If that cold migration sees a present unusable scrub record, it replaces the
  record with canonical `Idle` state bound to the renamed identity before the
  ordinary snapshot consumes the cold process generation. This avoids an
  immediate second namespace rehash without treating damaged state as proof.

## Fail-closed state machine

- Exact current plus absent legacy proceeds.
- Exact legacy plus absent current enters the exclusive cold migration.
- Coexisting current and legacy markers, conflicting marker bytes/types, or any
  other known identity generation fail without cleanup.
- `ExistingOnly` never bootstraps an unbound root.
- `CreateIfMissing` publishes only the current marker after the existing clean
  complete-namespace preflight.
- `ReadOnlyInspect` never renames or migrates; a legacy-only root is reported as
  lacking the current identity marker.

## Damaged write-ahead intent remains a restart fence

- A present checksum-invalid scrub-state file is no longer equivalent to clean
  absence. It may be torn or damaged `Prepared`/`Progress` intent.
- Because an unusable record cannot safely identify its active digest, the
  complete authority-producing scan disables both process-cache and durable-index
  acceleration for every digest-named payload and hashes current bytes.
- Failed current-byte reproof preserves the damaged record as forensic evidence.
  After repair, the complete scan re-proves all bytes before the ordinary
  exclusive scrub transition rebuilds canonical bounded state.
- Configuring both bounded scrub limits to zero disables payload-byte scrub
  work, not restart-fence repair. A good complete scan still replaces damaged
  or non-idle intent with canonical metadata-only state; the next fresh owner
  may then use the rebound verification checkpoint instead of rehashing the
  complete namespace forever. This zero-read repair does not consume the
  process-local scrub throttle, and any failed cutpoint or publication attempt
  preserves the conservative restart fence.
- The focused regression forges metadata-exact restart acceleration over
  same-size corrupt bytes and limits the optional scrub to one byte, proving the
  mismatch is detected by the complete scan rather than an immediate scrub.

## Adjacent current-byte handoff correction

- A fresh complete scan that hashes and proves the exact active
  `Prepared`/`Progress` payload now supersedes the older partial resumable-SHA
  checkpoint.
- The optional exclusive scrub transition re-proves the state file, root
  directory, active digest, and payload metadata, then durably advances the fair
  cursor and clears active state with zero duplicate payload reads.
- This prevents a stale corrupt-prefix checkpoint from producing a false alarm
  after metadata-hidden in-place repair.
- `SyncReplicaFilePayloadStoreScrubReport` distinguishes
  `reverified_active_completed` from `reverified_failure_cleared`.
- Operator status advances to `anonsync.peer-service.status.v6`; configured
  service and native-I2P process tests require the new Boolean evidence fields,
  cooperative-lease scheduling evidence, and explicit ambiguous-network-outcome
  accounting. The version is not left at the earlier rev0959 v5 shape after
  those later fields are added.

## Hard regression

The focused C++ test models a rev0958 store containing a valid `Prepared` record
and a forged metadata-exact verification index over same-size corrupt payload
bytes. It proves that:

- a child-held shared legacy lock blocks migration;
- corruption is found by the mandatory pre-rename byte proof;
- failure leaves the legacy basename and inode untouched;
- repair migrates the exact `(st_dev, st_ino)`;
- the immediate snapshot performs zero duplicate hashes and one process-cache
  reuse from the migration proof;
- a fresh owner obtains exact durable reuse only after checkpoint rebound;
- product-bound v3 migration preserves its inode;
- coexisting exact marker generations are rejected without deleting evidence;
  and
- the optimized remote-only exact-name lane rejects a coexisting unsupported
  v1 identity before publishing bytes or catalog state.

The CLI process test now expects the reader-fenced product identity basename.

## Bounded stale-observation recovery

- A non-cooperating same-UID writer can invalidate one otherwise complete
  descriptor-rooted payload observation while the cooperative identity lease
  itself remains exact.
- Exact observation drift now has a private typed classification across payload
  read/fstat, namespace-open, final pathname, sidecar traversal, staged-prefix,
  and root-directory cutpoints.
- The complete scanner discards one stale attempt, re-proves the exact live lock
  inode, and restarts from a fresh independent directory cursor before any
  verification generation, checkpoint observation, or snapshot authority is
  published.
- The retry count is fixed at one. A second drift remains terminal and bounded
  rather than turning private-root churn into an unbounded liveness loop.
- A Linux inotify regression changes and restores the first payload byte after
  the scanner begins reading a 32 MiB object, then proves one fresh full hash and
  exact final bytes. The deliberate service-corruption oracle still takes the
  cooperative exclusive lease because that test must exercise stable integrity
  recovery, not observation churn.

## Retained cooperative lease deferral and turn fence

- A legitimate same-host writer holding the exact identity-anchor exclusive
  `flock` now produces `PayloadStoreLeaseBusyDeferred` rather than terminating
  the shipping peer-service process.
- The retained step preserves the authenticated listener, owner-only control
  socket, ingress state, failure counters, and any active integrity alarm. It
  records separate newly observed conflict and clock-only backoff counters,
  exposes the exact bounded retry delay, and does not recategorize local
  maintenance as a peer or network failure.
- One service-owned retry cutpoint now gates every further local lease attempt.
  Initial repair and integrity recovery remain fail-closed. An established
  healthy owner may accept inbound work until the cutpoint instead of letting an
  overdue repair probe `flock` on every scheduler turn.
- The same cutpoint becomes the next ordinary repair deadline even when the old
  periodic deadline was distant. This guarantees bounded re-observation of
  separately idempotent progress that an interrupted inbound or outbound
  session may have committed before reaching the contended store.
- Payload-authority exceptions are caught at six explicit owner phases rather
  than by one global catch. Local repair preserves the network role. A network
  phase with no returned session result publishes `network_outcome_known=false`;
  outbound ambiguity yields to inbound for the full successful-handoff horizon,
  while inbound ambiguity remains inbound. This prevents a duplicate outbound
  turn without inventing a completed handoff.
- The failed nonblocking acquisition itself consumes no payload-store
  authority. An enclosing convergence or network turn may already have
  committed separately idempotent progress before reaching the store, so the
  next authority operation retries from fresh observation; rev0959 does not
  claim pass-wide rollback.
- The configured-service process regression keeps the exact product lease held
  while querying live status. It proves same-PID survival, retained healthy
  readiness during transient contention, exact conflict/outcome fields, valid
  inbound-versus-outbound fencing, release-driven continuation, and subsequent
  stable typed corruption recovery.
## Adjacent audit/refactor

- Split identity-name classification into four lease-capable v2/v3 anchors and
  five reserved known names including unsupported v1. Complete traversals retain
  their explicit v1 offline-migration diagnostic, while every targeted identity
  open/reproof now rejects all competing reserved names.
- Tightened internal migration wiring to the two directed same-family upgrade
  pairs; any standalone/product cross-pair now fails before lease or namespace
  mutation.
- Added an explicit `PayloadVerificationReusePolicy::RequireCurrentBytes` instead
  of relying on cache state to make migration cold.
- Separated "scrub bytes are enabled" from "a durable restart fence requires
  settlement." This removes an unbounded restart tax when an operator disables
  bounded scrubbing while a damaged, active, or failure record remains.
- Documented crash/retry and already-running old-reader boundaries using Linux
  `rename(2)`, open-file-description, `flock(2)`, and directory-`fsync` semantics.
- Corrected an overstrong implementation comment: post-rename exceptions abort
  and leave a reconcilable namespace; the code does not claim allocation-free
  completion after rename.
- Terminated a stale rev0958 Ninja build that was still consuming cloudtainer
  resources and excluded it from revision evidence.
- Corrected the configured-service corruption oracle so every deliberate
  payload mutation acquires and re-proves the exact reader-fenced product
  identity inode under the cooperative exclusive `flock`. This prevents a slow
  sanitizer build from racing a shared namespace scan and testing the wrong
  generic instability path.
- Audited the resulting lease-busy service boundary and removed an overstrong
  zero-effect claim: only the failed payload-store acquisition is authority-
  free; independently committed idempotent pass progress is retained and
  re-observed on the bounded retry.
- Kept the folder-owner CTest stall detector at 60 seconds for ordinary builds
  while selecting 120 seconds explicitly for ASan/UBSan builds, matching the
  instrumented workload without weakening production timeouts.

See `MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md`.

## Preserved boundaries

- Complete descriptor-rooted scanning remains namespace, capacity, and
  current-byte authority.
- `Prepared`, `Progress`, durable verification records, and the identity marker
  are never payload-content proof by themselves.
- Payloads remain immutable digest-named regular files under the existing rooted
  no-follow/no-mount-crossing resolver and cooperative writer lease.
- The peer-service degraded-recovery state machine, exact-owner snapshot handoff,
  folder convergence, authenticated transport, and atomic replica publication
  paths remain the shipping spine.

## Nonclaims

Rev0959 does not claim seamless mixed-version rolling upgrade, downgrade to an
old binary, universal power-loss behavior, hostile same-UID protection,
network-filesystem lock equivalence, quarantine, restore, bounded history,
garbage collection, rename identity, directory semantics, selective
synchronization, many-share ownership, cross-platform qualification, live public
Tor/I2P privacy qualification, or completion of the first Resilio uninstall
workflow.

## Validation

- Fresh GCC 14.2 Debug graph: **527/527 build edges** from an empty directory.
- Complete GCC registry: **258/258 tests** in 240.58 seconds.
- Independent GCC product lane: **39/39 tests** in 105.45 seconds.
- Focused GCC checks: **84 SHA**, **19 scrub-state**, **26 verification-index**, **515 payload-store**, **30/30 rooted POSIX**, **92 network-model plus 41 generated operations**, **296 SQLite-owner**, **360 folder-owner**, **110 sync-once**, **2043 TLS**, and **17 integrity-evidence**.
- Structural authority audit: **161/161 checks**.
- Fresh Clang 17 ASan/UBSan product graph: **238/238 build edges**.
- Clang ASan/UBSan product lane: **39/39 tests** in 317.19 seconds with leak detection and no retained diagnostic.
- Exact sealed rev0958 parent: SHA-256 matched and **41/41** wrapper-aware checks passed.
- Binary-aware source patch: **15/15** changed active files reconstructed byte-for-byte and by executable mode.
- Final publication is bound by `RELEASE_GATE.json` and additionally requires projection, manifest, directory/ZIP verification, CRC, path/no-symlink policy, and clean-extraction path/byte/type/mode equality.
