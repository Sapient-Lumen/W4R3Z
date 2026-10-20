# IoTox verified synchronization integration plan

Status: active implementation and qualification record, updated 2026-09-01.

The planned user-facing verbs are frozen in `future-cli-contract.md`; two-node proof uses
`sandwurm-two-node-lab.md`.

## Decision

Adopt the preserved toxsync 0.7.0 engine as IoTox's candidate synchronization core. Do not import the
historical IoToxsync daemon embedding wholesale: it targeted IoTox rev0010–rev0012 and predates the
current identity, authority-ledger v2, durable command, Ratox scheduling, and runtime contracts.
Forward-port the policy deliberately around the already qualified transport-neutral library.

Ordinary finite-file transfer remains the byte carrier and operator primitive. Synchronization adds
revision identity, delta/content reuse, restart convergence, multi-source scheduling, retention, and
atomic activation. Receiving bytes never grants activation authority.

## Assets worth keeping

- Signed mutable HEAD records over immutable revisions, with parent linkage and rollback/fork checks.
- Deterministic `treepack` directory artifacts with bounded external sorting.
- Range-v1 delta planning for a receiver that already has a related complete basis.
- Flat and paged content-v2 manifests, content-addressed storage, exact/sparse availability, and
  bounded rarest-first multi-source scheduling.
- Publication that commits immutable content before its HEAD, and verified activation into an
  immutable revision directory before an atomic `current` switch.
- Bounded reconstruction windows, cancellation points, retry/backoff seams, pin journaling, and
  conservative garbage collection.
- Fixed reconnect summary/query/receipt records suitable for bounded anti-entropy.

The first product slice should use only the minimum needed mechanisms. Range-v1 is appropriate for a
single complete source and related revisions; content-v2 becomes active only when measurements show
that complementary sources, storage deduplication, or range overhead justify it.

## Security and authority contract to freeze first

1. A namespace is a stable local policy object, not a filename and not a Tox friend number.
2. Each namespace names exact accepted writer keys and separately authorized subscribers. Friendship,
   owner status, and Ratox terminal authority imply none of these rights.
3. HEAD acceptance verifies the writer, namespace, immutable artifact identity, parent relation,
   monotonic revision policy, bounded sizes, and selected engine before durable mutation.
4. A received revision lands in a private staging/content store. Activation is a distinct local
   capability and policy decision; it never follows merely from transfer completion.
5. Paths are selected by local configuration. Remote names and tree entries cannot escape the
   namespace root, introduce symlinks, overwrite unrelated revisions, or choose executable authority.
6. Storage, manifest, object, peer, lane, outstanding-request, retry, and retained-revision bounds are
   mandatory. Exhaustion pauses or rejects work without discarding the last accepted revision.
7. Persistent state must survive power loss with file and directory synchronization, atomic replace,
   strict reread, and deterministic recovery. Runtime projections remain derived and content-minimal.

The local namespace policy/load contract is recorded in
`research/toxsync-namespace-policy-rev0040.md`. Message types 20–23 and feature bit 18 are frozen by
`protocol-sync-wire-v1.md`. ADR 0136 extends that contract with message types 24–25 and feature bit 26
for bounded range reconstruction; bit 26 requires bit 18. The Agent advertises both only under the
explicit default-off `--enable-sync` construction gate.

## Implementation sequence

### S0 — keep the component independently green

- Retain a pinned standalone Nix environment and the portable builtin-SHA/scalar lane.
- [x] Add toxsync to the official source matrix without linking it into `iotox`.
- [x] Add fuzzing for HEAD, range, manifest, inventory, treepack, pin-journal, and reconnect decoders.
  The wire, metadata, and files fuzzers cover mutable HEAD anti-entropy, range records, exact
  inventory, reconnect capabilities, signed index records, conservative availability, flat and paged
  manifests, treepack, index files, and pin journals.
- [x] Measure test and benchmark memory so later product limits are evidence-based. The current
  evidence is retained in `research/toxsync-s0-qualification-2026-08-20.md`.

### S1 — reconcile policy types without transport

- [x] Introduce IoTox-owned namespace configuration, writer/subscriber bindings, storage quota,
  activation mode, and engine selection as a local canonical policy/load primitive.
- [x] Add local accepted-HEAD state and durable reload rules. The first store accepts genesis and
  linked advances, treats exact records as duplicates, refuses rollback/stale records, same-generation
  forks, parent mismatches, unauthorized writers, wrong namespaces, engine mismatch, quota violations,
  and generation jumps, and persists accepted records through IoTox atomic state replacement.
- [x] Add a local artifact-install job seam behind accepted HEAD state. It evaluates the candidate
  before mutation, verifies source size and injected digest, stages bytes through a private temporary
  object, publishes by no-clobber hard link with file and directory synchronization, rehashes existing
  objects before reuse, commits the accepted HEAD last, and never activates the revision.
- [x] Add an explicit local activation transaction. Manual activation names the exact accepted HEAD,
  rechecks the immutable artifact and manifest type, size, and digest plus their range-v1 semantic
  binding, rejects disabled policy, stale intent, rollback, forks, missing/corrupt objects, and
  corrupt prior state, and atomically persists a canonical activation pointer. Install and HEAD
  acceptance still never activate content.
- [x] Complete the synchronization capability allocation review without widening the frozen v2
  contract. ADR 0091 reserves bits 8 through 11 for `sync.admin`, `sync.publish`, `sync.subscribe`, and
  `sync.activate` in a future signed, non-widening authority format; v1/v2 authorize none of them.
- [x] Implement authority-ledger v3 with a signed, replayable, non-widening v2 transition, independent
  record/digest/proof domains, rollback-guard coverage, feature negotiation, exact-head online proof,
  remote delegation, RecallRoot CLI ceremonies, and explicit later owner activation of sync rights.
- [x] Freeze one reusable sync admission decision that requires a negotiated exact-head v3 proof,
  the operation's independent capability, the stable proven principal's writer/subscriber membership,
  and manual host policy for activation. V1/v2, stale proofs, capability substitution, invalid policy,
  wrong membership, and disabled activation fail before admission. ADR 0092 records the mapping and
  nonclaims.
- [x] Require that decision at both protocol entrances. The default-off bounded publisher now
  gates HEAD discovery and exact-FileId object offers on current v3 subscribe authority and local
  subscriber membership, with exact epoch replay and authority-head fencing. The subscriber gates a
  signed writer HEAD on exact v3 publish authority, local writer membership, transition policy, and
  quotas before creating durable object attempts. Namespace administration, local publication, and
  activation entrances remain S3 work.
- [x] Freeze a 296-byte canonical signed HEAD and local publisher transaction using the stable IoTox
  device identity. Creation derives the exact linked generation/parent, verification precedes
  accepted-candidate conversion, the private fixed-size store commits last, exact retries are
  duplicates, and one live store serializes concurrent publishers. ADR 0093 and
  `protocol-sync-head-v1.md` freeze the contract without allocating transport.
- [x] Commit and reverify both digest-named immutable objects before local signed-HEAD publication.
  Artifact and manifest have independent and combined bounds, private no-clobber object commits,
  exact final size/digest verification, cancellation-before-HEAD ordering, and safe retry reuse. ADR
  0094 records the boundary and retained whole-store/remote nonclaims.
- [x] Serialize signed-HEAD predecessor/load/replace across local processes with a private persistent
  advisory lock. Strictly inventory the flat digest-named object store and enforce configured
  byte/object ceilings before sequential publication or install growth. ADR 0095 retains the
  cooperative-lock, cross-job, reachability, pin, and GC nonclaims.
- [x] Freeze bounded explicit retained-revision state before collection. Canonical owner-private
  snapshots pin exact policy-valid accepted records, reject forks/capacity/corruption, survive restart,
  and serialize mutation across processes. ADR 0096 forbids deletion until pin authentication and one
  complete live-root transaction lock exist.
- [x] Authenticate retained-revision state with the stable device identity. The v2 record is
  domain-separated, rejects unsigned v1 and foreign devices, and commits each predecessor under a
  monotonic mutation counter. ADR 0097 preserves the whole-record replay nonclaim.
- [x] Freeze a non-destructive complete-local-root planner. Exact object inventory records are merged
  against published, accepted, activated, and retained roots with source masks and separate
  missing/mismatch/unreferenced evidence. ADR 0098 forbids treating candidates as collectible.
- [x] Unify implemented local state transitions and stable reachability reads under one namespace
  transaction. Thread-bound nested-operation tokens avoid recursive flock, and a process oracle proves
  publication plus retention cannot cross a held transaction. ADR 0099 keeps deletion disabled.
- [x] Authenticate accepted-HEAD persistence with the stable device identity. The domain-separated
  envelope rejects unsigned legacy state, foreign keys, and tampering before install, activation, or
  stored reachability. ADR 0100 leaves activation authentication and restart anti-rollback open.
- [x] Authenticate activation persistence with a distinct stable-device signature domain. Restart,
  duplicate detection, and stored reachability reject unsigned legacy, foreign, or altered pointers.
  ADR 0101 leaves only independent anti-rollback before destructive collection.
- [x] Freeze the local four-root rollback-guard primitive. Its signed fixed-size committed/pending
  state reconciles both exact crash sides and rejects missing, divergent, foreign, tampered, or weak
  state under the namespace transaction. ADR 0102 leaves mutation-path wiring and coordinated replay
  resistance open.
- [x] Wrap publication, accepted-HEAD advance, activation, retention pin, and retention unpin in that
  begin/replace/finish protocol. Stored reachability checks the exact guard without mutating it, and a
  fresh-process oracle rejects isolated rollback of either publication state or guard. ADR 0103 keeps
  coordinated replay and destructive collection explicitly open.
- [x] Inject root-commit failure before replacement and after a landed replacement. Exact duplicate
  publication, acceptance, activation, pin, and already-applied unpin retries reconcile pending guard
  state before returning. ADR 0104 freezes the idempotent recovery rule.
- [x] Define the VM-independent destructive-test boundary and quarantine-first sequence in
  `sync-gc-containment-plan.md`. Disposable local roots cover deterministic refusal, while Sandwurm
  KVM guests own destructive acceptance and outside-root sentinel evidence.
- [x] Implement the quarantine-only boundary through local-control v1.32. Dry-run freezes exact
  descriptor identities; quarantine recomputes guarded reachability under one pinned transaction,
  uses Linux beneath/no-link/no-mount and no-replace rename constraints, never unlinks, and reports
  exact moved/durable prefixes. Unit refusal cells and the dual-guest Sandwurm mount/sentinel fixture
  pass (ADR 0149). Permanent purge remains a separate witness-dependent decision.
- Wrap publication, HEAD evaluation, content installation, reconstruction, activation, and retention
  behind injected filesystem/clock/crypto seams.
- Prove atomic persistence, corrupt/truncated state refusal, restart recovery, fork/rollback rejection,
  quota failure, cancellation, no-clobber activation, and idempotent receipts without toxcore.

### S2 — freeze a default-off synchronization protocol

- [x] Allocate one negotiated feature and versioned custom-packet control family for small bounded
  HEAD and object request/result records without advertising it.
- [x] Carry bulk immutable bytes through c-toxcore file transfer; the request-selected explicit
  FileId joins the control record to the offer, and chunks never enter chat messages.
- [x] Freeze how every message is interpreted only inside the confirmed peer session, current stable
  principal, namespace authority, connection epoch, exact signed-HEAD identity, and bounded request
  identifier. Both transport-neutral dispatchers and the Agent's pre-effect context reconstruction
  enforce this contract.
- [x] Reuse the preserved toxsync SHA-256 object identity through a production descriptor-based
  streaming hasher that rejects symlinks and detects replacement or mutation. IoTox metadata keeps
  its independent domain-separated BLAKE2b contracts.
- [x] Retain publisher request/result replay before file-offer effects, reject conflicting message
  IDs, fence cached responses when authority changes, and clear exact epoch state on disconnect.
- [x] Keep the toxcore owner callback nonblocking for the first complete-object slice. Blocking HEAD
  and object verification and terminal commit execute in one bounded worker with a distinct bounded
  priority terminal queue; overload refuses new ordinary work without losing already-reserved
  terminal truth.
- [x] Define and implement exact retry, duplicate, stale-epoch, unavailable-object, corrupt-object,
  peer-loss, and shutdown behavior for HEAD plus whole immutable objects and one negotiated bounded
  range bundle. Multi-source reassignment remains a later gate. Explicit operator cancellation has one
  process-local job ID and a fail-closed terminal implementation. Cancellation and bilateral
  disconnect now have genuine-provider dual-carrier evidence. A pre-offer publisher `unavailable`
  result now receives at most eight fresh message/FileId attempts by default while preserving the
  scheduler attempt; exhaustion, denial, absence, stale generation, and post-offer unavailability
  remain terminal. ADR 0180 qualifies the retry beside four-job route loss without changing wire v1.

### S3 — ship one complete vertical slice

- [x] Add owner-only one-binary namespace create/configure, publish, subscribe, status, cancel, and
  activate operations plus a private runtime projection. Canonical `sync-namespace-template` and
  `sync-namespace-template-tree` plus `sync-namespace-lint` are effect-free;
  `sync-namespace-install` atomically creates and live-reloads
  one no-clobber policy through local control v1.27. `sync-namespaces`, `sync-publish`, `sync-pull`,
  exact-token `sync-activate`, content-free `sync-status`, and process-local `sync-cancel` use the same
  typed socket (v1.28 after cancellation). Local control v1.29 adds quiescence-gated replacement of
  activation and writer/subscriber membership plus policy-only removal; root, engine, quotas,
  content, and signed namespace state are never implicitly migrated or deleted. Persistent automatic
  subscription scheduling remains separate future work.
- [x] Support one signed writer, one subscriber, one immutable file or deterministic directory
  revision, one complete source, and range-v1 resume/reuse. One-source whole-object and successor
  range-reuse paths have full Agent proofs and genuine direct-UDP/forced-TCP provider evidence;
  missing/corrupt accepted-basis fallback now has deterministic and genuine direct-UDP/forced-TCP
  proof. One fully cleared same-epoch range-plan retry also has deterministic and genuine
  direct-UDP/forced-TCP proof, and exact-prefix range continuation across native available-policy
  carrier loss now passes on both carriers under fresh attempt/FileId identities; two sequential
  native carrier losses also pass with exact cumulative prefix accounting, and one distinct loss
  after 15/16 receives only the final suffix under fresh identities (ADRs 0231–0233). Signed
  treepack-v1 now has bounded deterministic publication,
  post-commit atomic projection, exact retry/recovery, and genuine direct-UDP/forced-TCP evidence.
- [x] Prove duplicate/reordered control records and the bounded single-source sync failures. Exact
  request replays, conflicting message identifiers, corrupt basis, publisher-source recovery,
  subscriber-destination refusal/selective retry, full-disk, and real read-only-storage directory
  cells pass on both carriers. ADR 0132 freezes disconnect as terminal old-epoch fencing followed by
  explicit higher-epoch whole-object retry; ADR 0147 freezes same-epoch exact replay without repeated
  file-offer effects.
- [x] Prove file-transfer pause/resume without retiring or rebinding the subscriber job. The genuine
  direct-UDP and forced-TCP cells retain one exact FileId and partial position through a two-second
  local pause, then resume and complete through accepted-HEAD-last ordering and explicit activation.
- [x] Prove bilateral live-link loss after positive progress over direct UDP and forced TCP. Both
  roles observe offline, advance to one stable confirmed/authorized epoch, and admit only an
  explicit fresh whole-object pull after the old job and staging are terminally cleared.
- [x] Prove explicit job cancellation after positive provider progress and admitted receives over
  direct UDP and forced TCP, with no accepted or activated HEAD.
- [x] Prove one genuine unclean receiver-process restart after positive transport progress over both
  direct UDP and forced TCP. Startup fences lost handles, removes only exact signed-attempt-scoped
  private transport temporaries, retains identity, and converges the exact revision after retry.
  Destination corruption and residual control failures remain open.
- [x] Qualify ADR 0234's whole-object suffix continuation over direct UDP and forced TCP. The new
  process must retain only strict canonical positive prefixes, restore no old handles or jobs, and
  require exact interrupted = restart-retained = restart-resumed byte accounting under a fresh
  authorized signed-HEAD pull. Compact proofs `pair.f20ma62y` and `pair.lj0pdz6a` pass.
- [x] Bind a range-bundle prefix to its exact locally derived plan across daemon restart. ADR 0239
  spends one reserved ATM1 byte to distinguish historical route/worker records from plan-bound
  records, commits the complete plan digest plus bundle length, and permits reuse only after a fresh
  authorized pull independently derives the same plan. Legacy/mismatch/complete-bundle bytes fence;
  deterministic persistence and full-subscriber convergence pass.
- [x] Qualify ADR 0239's range-bundle restart continuation over direct UDP and forced TCP with exact
  interrupted/retained/resumed accounting, suffix-only receive under fresh identities, complete
  target verification, HEAD-last acceptance, and explicit activation. Compact proofs
  `pair.xg41pthc` and `pair.00992erw` pass after a two-sided authority barrier and independently
  strict replay (`evidence/2026-08-29-sandwurm-sync-range-restart-resume.md`).
- [x] Prove one controlled publisher-guest restart from its persisted disk after positive transport
  progress over both direct UDP and forced TCP. The stable subscriber retires its old job and staging;
  the successor preserves the exact publisher identity, policy, source, objects, and signed HEAD; and
  a higher stable authorized epoch plus explicit whole-object pull precedes convergence and activation.
- [x] Prove publisher worker-queue saturation without transport-pump starvation over direct UDP and
  forced TCP. A queue bound of one retains active and queued work, refuses one additional namespace
  job, exposes nonblocking status, and converges both retained namespaces by exact retry after the
  held transaction is released (ADR 0141).
- [x] Prove whole-store byte-quota saturation over both carriers. With both candidate objects larger
  than the exact remaining budget, admission fails independent of completion order, cleans staging,
  and preserves the accepted HEAD, activation, old object inventory, and visible predecessor tree.
- [x] Prove whole-store object-count saturation over both carriers without byte pressure. Four valid
  filler objects plus generation 1 reach the six-object/tree-entry ceiling; either successor object
  is refused with zero commits and all predecessor truth is preserved (ADR 0142).
- [x] Prove real read-only-storage refusal and exact retry over both carriers. A loop-backed ext4
  namespace fails pull transaction setup before object requests and fails activation without moving
  accepted, activated, or visible truth; explicit retries after read-write remount complete the exact
  successor (ADR 0143).
- [x] Measure process-lifetime resident high-water for a maximum-entry directory successor over both
  carriers. Publisher and subscriber phase observations remain below a 65,536 KiB construction
  ceiling and bind exact post-generation-1 deltas without presenting the threshold as enforcement
  (ADR 0144).
- [x] Demonstrate byte-identical convergence and atomic revision switch across two source-linked IoTox
  Sandwurm guests before declaring the slice complete.

### S4 — enable the content fabric only with evidence

- [x] Freeze source eligibility before adding content-v2 frames. One already-verified signed HEAD
  remains authoritative; every additional immutable-object source must separately prove the exact
  current authority-ledger v3 head, `sync.publish`, writer membership, and the identical HEAD record
  digest. ADR 0242 deliberately allocates no transport or activation authority.
- [x] Freeze initially dark feature bit 29 and canonical object request/result types 28/29. The request binds
  namespace, frozen signed-HEAD record, page/chunk digest, logical index, byte size, and exact FileId;
  the result is correlated and replay-bounded. ADR 0251 later activates it only after complete Agent
  construction.
- [x] Embed the bounded flat/paged content coordinator and source publisher entrance. Deterministic
  tests prove exact CAS resolution, two authorized simultaneous complete sources, in-flight source
  disappearance, stale completion refusal, survivor reconstruction, subscriber authority, and
  replay without duplicate offer (ADR 0244).
- [x] Add a strict transaction-bound physical CAS inventory and count flat plus CAS objects against
  one namespace object/byte quota. Reject algorithm/path aliases, permission drift, links, mount
  crossings, and optionally digest corruption (ADR 0246).
- [x] Route construction-level content writes through canonical private roots, exact single-link
  staging, full SHA-256 copy verification, no-replace publication, and prospective combined quota
  checks. Coordinator quota refusal retains exact staging for explicit retry (ADR 0247).
- [x] Freeze a separate stable-device-signed content attempt journal. It burns IDs before assignment,
  binds HEAD/object/FileId/carrier/source before transport effect, commits only exact complete staging
  on startup, fences partial/absent work, and retains ambiguous truth (ADR 0248).
- [x] Publish a real local flat or paged content fabric through the product command. Whole-set
  scratch/combined-quota admission precedes verified CAS commits, HEAD is signed last, and startup
  removes only exact abandoned local-publication workspaces (ADR 0249).
- [x] Bootstrap root kind 3 and join signed HEAD, object requests/results, early file offers, terminal
  events, and CTA1 in a bounded transport-neutral one-source subscriber. Reconstruct and commit the
  whole artifact before accepting HEAD; cancellation cannot revive delayed events (ADR 0250).
- [x] Construct and dispatch that service in the Agent, integrate explicit activation and accepted
  reachability/repair/quarantine, and advertise bit 29 only after startup validates the complete
  persisted live graph (ADR 0251).
- [x] Qualify the one-source primary-carrier path through independent source-linked Sandwurm guests.
  The same paged 4 MiB generation-1 revision converges in one pull with zero failure, accepts HEAD
  last, and explicitly activates over direct UDP and forced TCP (ADR 0252).
- [x] Consume exact sparse availability from explicit independently authorized primary peers in the
  product subscriber. `sync-source-add JOB_ID FRIEND` cannot change the original frozen HEAD or
  activation state; deterministic complementary stores both contribute real availability and
  objects before exact reconstruction (ADR 0254).
- [x] Freeze an exact bounded sparse-availability exchange before claiming complementary partial
  stores. Types 30/31 bind kind, first index, count, namespace, and frozen HEAD; the source
  verifies every set bit and the receiver accepts only its exact current window. Deterministic
  even/odd complementary stores reconstruct the exact artifact (ADR 0245).
- Run representative unchanged, shifted, renamed, sparse, and complementary-source corpora.
- Compare bytes fetched, verified goodput, CPU, peak memory, store amplification, fsync cost, and
  completion latency between full transfer, range-v1, and content-v2.
- Enable paged content-v2 and multiple logical lanes only where those measurements beat the simpler
  path. Local corrupt-object repair and unreachable-object quarantine are implemented as explicit
  `sync-repair` and `sync-gc ... quarantine` actions with deterministic Agent evidence; genuine
  one-source content-v2 evidence now covers both native carrier forms. Add an
  independent monotonic witness and separately reviewed purge protocol before enabling
  deletion-heavy content-v2 paths.
- Direct-UDP product multi-source convergence now passes genuine c-toxcore with two complementary
  authorized stores (ADR 0255). ADR 0256 adds atomic initial source admission and qualifies explicit
  fail-closed recovery after selected-source disappearance over direct UDP: the old job is fenced,
  and a distinct job starts only after higher-epoch recovery. Qualify forced TCP independently of
  future bonded Tox-route experiments. Thirteen bounded forced constructions separated relay count,
  admission order, pending requests, known-key pre-provision, address rendezvous, and A/B placement.
  The strongest briefly confirmed the secondary, then lost it before v3 authority or object work; a
  future route-identity design must preserve the frozen HEAD and source-bound FileId/CTA1 chain rather
  than treating sockets or transient confirmation as usable sessions. ADR 0257 now supplies the
  separate authenticated replica-head store: one owner-local
  import verifies the foreign signature and complete manifest graph, enforces a same-writer linked
  chain, adds a device custody signature, and roots only present replica bytes for GC. The partial
  source cold-starts and serves the exact frozen record while local publication remains absent.
  Forced-TCP topology and transparent continuation remain separate gates.

The preserved rev0010 live fabric embedding is a forward-port map, not an authority-compatible
implementation. Retain its bounded inventory/scheduling, O(jobs) intent, immutable-store rescan,
deadline, disappearance, and goodput ideas. Rebind them to current v3 proof, signed-HEAD/rollback,
FileId/attempt, HEAD-last, explicit activation, and route-class rules before any live effect.

## Required release evidence

- Exact compiler, sanitizer, static-analysis, fuzz, restart, fault-injection, and filesystem matrix.
- A retained two-process genuine-provider transcript with immutable input/output digests and signed
  namespace/HEAD evidence.
- Bounded resident memory and durable-state growth for maximum configured artifact, manifest, peer,
  lane, and retained-revision counts.
- Power-loss simulations at every durable transaction boundary and named real-filesystem checks.
- Negative authority evidence: friend-only, stale principal, revoked writer/subscriber, wrong
  namespace, forked HEAD, rollback, and activation-without-local-capability all fail before effect.
- Clear nonclaims for confidential content, metadata completeness, distributed consensus, automatic
  conflict merging, realtime propagation, and unattended OTA safety.

## Current evidence and nonclaims

The preserved 0.7.0 engine now registers 125 native checks. The 2026-09-01 deep pass requalifies GCC
Debug/Release, dependency-minimum builtin-SHA/scalar Release, Clang Debug, ASan/UBSan, TSan, the Nix
package, and a direct Clang static-analysis pass. Three CTest routes cover the native registry,
version, and a backend-aware command transaction; the portable route still reconstructs raw content
and range artifacts without pretending Ed25519 exists. Three sanitizer fuzzers completed 30,000
aggregate final post-change runs in the current campaign. The founding S0 bounds remain in
`research/toxsync-s0-qualification-2026-08-20.md`; current deltas and exact commands are in
`evidence/2026-09-01-toxsync-deep-audit.md`.

IoTox now has local namespace policy/load and administration, accepted-HEAD, artifact-install, explicit activation,
exact-head sync authorization, stable-device-signed publication, ordered immutable-object primitives,
canonical remote codecs, explicit-FileId sender/receiver joins, and deterministic directory
projection. The complete current owned registry has 711 direct checks plus dedicated publication,
retention, shared-transaction, rollback, and directory-projection process oracles.
With `--enable-sync`, the Agent strictly constructs both dispatchers, recovers durable attempt state,
advertises `state-sync-v1` plus `state-sync-ranges-v1`, moves blocking work off the toxcore owner
callback, and exposes
`sync-namespaces`, `sync-namespace-install`, `sync-namespace-update`, `sync-namespace-remove`,
`sync-publish`, `sync-pull`, `sync-cancel`, `sync-activate`, and `sync-status`. Publication builds
a genuine bounded toxsync range-v1 index for regular files or canonical treepacks and advances its signed HEAD only after artifact/index
semantic validation. A full Agent/mock-provider check exercises real
lossless frames, request-selected Tox FileIds, paused incoming offers, ordinary finite-file callbacks,
two SHA-256 object commits, accepted-HEAD-last ordering without implicit activation, and exact-token
manual activation after complete pair revalidation. A second process-boundary gate starts from an
accepted 16 KiB basis, negotiates the range extension, fetches one 4 KiB bundle, reuses 12 KiB, and
accepts the exact linked generation-2 HEAD last.

The genuine single-file baseline now passes in two concurrent source-linked Sandwurm guests over
direct UDP and forced TCP. Both carriers produce the same 4 MiB artifact, range index, generation-1
signed HEAD, accepted-HEAD-last transition, and explicit activation token. This is not yet the S3
exit. A separate rate-shaped 8 MiB cell now passes an unclean receiver-daemon restart on both
carriers after positive transport progress. Its first scientific run exposed pre-rename
transport-temporary leakage; ADR 0129's exact attempt-scoped, shape-checked cleanup repaired it before
the accepted cells. ADR 0130 adds canonical offline template/lint plus atomic no-clobber live policy
creation. ADR 0133 adds serialized quiescent live update/removal, immutable identity/storage fields,
strict crash-temp recovery, policy-only retirement, exact retries, and fail-closed disk/live
reconciliation. ADR 0131 freezes process-local pull identity and cancellation-before-cleanup; its
rate-shaped genuine direct-UDP and forced-TCP cells pass after positive provider progress. ADR 0132
freezes old-epoch disconnect retirement; both genuine carriers now pass cleanup, bilateral epoch
advance, stabilized explicit retry, convergence, and activation. ADR 0135 freezes publisher-guest
restart as durable publication recovery plus old-epoch retirement; both genuine carriers pass across
a bounded initial reboot chain and a successor VMM using the exact persisted disk. ADR 0136 freezes
bounded manifest-first range reconstruction. Genuine two-guest direct-UDP and forced-TCP cells each
reconstruct an exact 4 MiB generation-2 successor by fetching one 128-byte range and reusing
4,194,176 verified bytes; both independently reverified compact proofs are retained. Corrupt-basis
recovery now falls back to a fresh complete-successor request after manifest verification, preserves
the unusable object, verifies the full target, and accepts HEAD last in the deterministic subscriber
gate. Genuine direct-UDP and forced-TCP cells also pass with the same generation-2 identities while
preserving the corrupt old basis. ADR 0138 now continues one partial range fault only after exact
staging, signed-attempt, and scheduler cleanup; the unchanged plan gets fresh durable and transport
identities, and genuine direct-UDP/forced-TCP cells prove convergence without prefix reuse. Local
`sync-repair NAMESPACE` now quarantines only verified digest-name mismatches in the final object
store. Genuine direct-UDP and forced-TCP cells fsync an exact target mismatch, preserve signed state,
recover the same authorized revision, retain quarantine evidence, and pass a clean second scan.
Signed treepack-v1 now rejects unsafe/unbounded source trees, commits activation truth before a
retryable derived projection, verifies unpacking by deterministic repack, atomically switches one
read-only current tree, recovers exact staging, and prunes superseded projections. Genuine
direct-UDP and forced-TCP cells converge the same three-directory/three-file 4 MiB tree. A second
dual-carrier cell advances through generation 2A, coherent stale generation 1, a distinct valid
generation-2 fork, and generation 3 across four publisher restarts. The subscriber refuses both
adversarial HEADs without changing accepted, activated, or visible generation-2 truth. On a dedicated
64 MiB ext4 namespace, generation-3 signed activation then commits under real ENOSPC while projection
leaves `current` unchanged; removing only the exact filler lets duplicate activation materialize the
same signed revision with one projection and no temporary residue. A separate queue-of-one
dual-carrier cell retains active and queued publisher work behind a real namespace lock, refuses one
additional namespace job without blocking the toxcore event pump, and converges both retained
namespaces after exact retry. A separate dual-carrier cell retains 4,981,169 generation-1 bytes under
a 5,242,880-byte subscriber store ceiling and refuses both possible first-arriving generation-2
objects without changing signed, object, staging, or visible truth. Another cell reaches the shared
six-object/tree-entry ceiling while retaining enough bytes for the complete successor, then refuses
either new object with zero commits and the same state preservation. The real ext4 read-only cell
refuses pull before object requests, separates accepted from activated successor truth after a second
refusal, and completes both exact retries only after read-write remount. A 128-entry, 7,616,908-byte
successor then peaks at 12,924 KiB over UDP and 13,132 KiB over forced TCP in the long-lived IoTox
processes, both below the 65,536 KiB construction threshold. A separate dual-carrier publisher-source
cell corrupts both generation-2 objects after durable
publication, proves request-time refusal with zero subscriber admission, explicitly quarantines both,
reconstructs the same signed revision through duplicate publication, and converges only after an
explicit retry (ADR 0145). A subscriber-destination cell now corrupts the paused artifact temporary,
rejects it at complete staged digest verification, preserves its valid committed manifest, and
selectively retries only the missing artifact before HEAD-last acceptance and explicit activation
(ADR 0146). The subsequent duplicate/reordered-control cell captures the original canonical HEAD and
object requests, replays object requests only after both FileId offers are admitted, and proves the
provider returns retained results without repeating file offers. A duplicate HEAD result after both
object results emits no further request; a same-ID/different-payload HEAD is refused without
poisoning the original pull. Both carriers pass with exact request/result and replay/conflict deltas
(ADR 0147).
