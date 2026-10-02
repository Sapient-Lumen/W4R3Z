# Open questions — after rev0051

These are unresolved product decisions, not permission to blur current contracts. Accepted ADRs stay
in force until a later ADR explicitly supersedes them.

## Significant architectural additions

- What is the one-paragraph human story for the proposed addition, and can it
  be understood without first knowing an implementation shortcut?
- Which exact layer owns the new behavior: CLI porch, local control, Agent
  logic, stable identity/authority, sync, routes, Ratox, update lifecycle,
  diagnostics, tooling, or research?
- Does the addition require a new capability bit, role, route class, durable
  file family, support artifact, terminal profile field, or witness lane?
- Which hostile refusal proves the boundary: wrong principal, revoked
  capability, stale generation, route fallback, corrupt state, unsupported
  host prerequisite, or remote-selected path/argv/sudo?
- Which docs become inaccurate if the addition lands, and which maturity label
  in `docs/governance/claim-maturity.md` is actually earned?

Use `docs/architectural-change-intake.md` before answering these as code.

## Ordinary local surface

- Should successful self-profile mutations gain a durable private audit record, or is savedata plus
  disposable runtime projection the correct privacy boundary?
- Should the root outgoing-request lane gain a companion structured binary record for request
  messages containing LF, or is the existing typed SOCK_SEQPACKET operation sufficient?
- Should `friend-events` remain one bounded operational journal, or should consumers receive a
  cursor-bearing local event stream with explicit gap detection?
- How should runtime surface compatibility be versioned without making the filesystem itself a
  second wire protocol?

## Outgoing friendship durability

- Should IoTox offer a durable outgoing request outbox, and if so what are its message identity,
  expiry, cancellation, duplicate, retry, and route-policy semantics?
- How does a durable request distinguish local `tox_friend_add` admission from actual remote
  observation or acceptance?
- What is the correct behavior when a request is queued for one complete Tox address but the remote
  changes its nospam value before delivery?
- Should repeated requests to an already-known key update an application-level invitation record,
  or remain only provider errors?

## Incoming friendship policy

- Is a durable incoming-request archive useful, given that c-toxcore exposes callbacks rather than a
  persistent pending-request object? What replay and spam risks would such an archive create?
- Where do block, rate-limit, and operator-notification policies live without confusing them with
  provider friendship or application authorization?
- Should acceptance be allowed only after a signed IoTox claim/authority ceremony, or can transport
  friendship remain deliberately earlier and broader?

## Durable command engine

- Which representative low-consequence physical desired-state operation should follow the qualified
  presentation-state mutation, without weakening effect identity or power-loss truth?
- What exact terminal result cache and deduplication horizon are needed for physical effects?
- Should operators be able to raise or lower immutable admission priority by creating a superseding
  command, or is cancellation plus new admission the safer interface?

## Command-store durability and privacy

- When should the current whole-file atomic replacement become an append/checkpoint design?
- Which ADR 0302 witness backend should each target class use when a hardware monotonic counter is
  unavailable, and what authenticated independent service is acceptable?
- Which custodian integrations should provision/rotate the random fscrypt data key after the frozen
  rule that it never comes from RecallRoot, argv, environment, config, or a peer?
- Which authenticated rate and alert policy should complement the implemented total, per-peer, and
  canonical-byte quotas?

## Authority, RecallRoot, and re-entry

- Define phrase-generation strength classes and user-facing refusal rules. Offline guessing is an
  intentional consequence of permanent deterministic re-entry; weak phrases cannot be cosmetically
  accepted.
- Decide whether one remembered root governs every device or derives site/device-specific roots that
  reduce correlation and blast radius.
- Define destructive physical reclaim separately from remembered-owner re-entry.
- Qualify ADRs 0305 and 0313 on a genuinely separate administration/storage/failure domain. Exercise
  separately retained checkpoint floors or rollback-resistant persistence under real service
  backup/restore and administrator-loss procedures, and freeze replacement/re-anchor policy without
  introducing mandatory vendor infrastructure.
- After ADRs 0306--0314's application/Ratox/route/terminal-policy/command-effect/sync-policy,
  update-lifecycle, single-writer four-root, and tree-v2 semantic-state lanes, choose witness
  replacement/re-anchor semantics and the remaining broader namespace transaction boundaries.
  Attempts, object/quarantine inventories, content, projection/current pointers, and health remain
  deliberately outside the current witness commitments.
- Define a witnessed effect-history compaction/checkpoint protocol before relaxing ADR 0309's
  deliberate lifetime record ceiling.

## Self mode and multidevice

`--mode self` now gives IoTox a product place to say “these are my machines” without depending on
Tox multidevice. ADR 0383 answers the first membership slice: the self roster is a separate
owner-signed, owner-local coordination artifact; it is not a second constitutional authority ledger.
`iotox self-swarm` now creates, joins, retires, inspects, verifies, plans, applies narrow grants, and
revokes retired members with RecallRoot supplied only on stdin.

Resolved in v1:

- self-join proves the owner key by signing a canonical roster generation;
- member records bind alias, stable principal, Tox route key, role, capabilities, and active/retired
  status;
- reciprocal grants are explicit reviewed commands, not automatic friendship side effects;
- `interactive.terminal` can be rostered as the first self capability, while sudo remains a
  profile/host-policy decision;
- retirement advances the signed generation and blocks future grant apply for that member; and
- tests cover wrong owner/signature, wrong stable principal, stale minimum generation, wrong route
  key, duplicate member identity, tamper, and retired-member grant exclusion.
- local high-water floors, explicit roster fan-out, and optional live alias-route proof are now
  implemented by ADR 0384; and
- public person delivery cards plus bounded signed person-message fanout are now implemented by
  ADR 0385.
- person-signed device sender delegations, contact-side card floors, local seen stores, signed group
  descriptors/messages, and review-only group fanout plans are now implemented by ADR 0386.
- local contact books, transcripts, delegated device receipts, and reviewed durable outbox plans are
  now implemented by ADR 0387.

Still open:

- When should a local self-swarm floor be backed by an independent remote witness, and how should
  that custody be shown without leaking the private roster?
- Do we need a cryptographic route transcript beyond ADR 0384's live alias-route proof, or is the
  alias/peer proof sufficient for reviewed grant/fanout planning?
- Which route privacy policies are inherited across the self domain, and how is silent Tor/I2P to
  native fallback refused?
- Which support-bundle, overview, and diagnostics fields should ingest ADR 0384's redacted
  `self-swarm readiness` output without leaking the private roster?
- Should fanout ever become background automation, or should it remain an explicit reviewed
  `fanout-plan` / `fanout` workflow until external freshness and route privacy are solved?
- Which integrated tests should prove missing profile, missing `interactive.terminal`, and revoked
  authority fail at Ratox admission after a valid self roster names the peer?
- How should contacts refresh public person cards in the background without learning private
  self-machine names, silently accepting stale/forked cards, or turning card refresh into a vendor
  directory?
- When should person/delegation/group freshness floors be backed by an independent witness, and what
  custody ceremony is acceptable for ordinary users?
- After ADR 0414, service reality evidence is a content-free
  `iotox.service-reality.v1` receipt over explicit operator-observed
  active/enabled-or-managed/log-reviewed/health-passed/upgrade-passed state.
  The remaining question is whether any future deployment family needs a
  stronger external attestation format; IoTox itself still must not become the
  service manager.
- Are remote human-read receipts ever worth adding above local `person
  read-mark`/`read-status`, and if so how can they avoid pretending that every
  device maps to a person reading the message?
- What conversation-order model is needed above stable message IDs and
  `person transcript-convergence` set/digest checks before groupchat can be
  called daily-driver complete?
- Which Tox group/conference APIs are useful as carriers once IoTox person/group signatures, not Tox
  group peer identities, remain authoritative?

## Content replication and recovery

- ADRs 0335--0336 answer both sides of immutable manifest installation,
  immutable branch-record installation, and mutable branch-pointer
  replacement with exact target commitments plus external ptrace syscall-entry
  fences. ADR 0337 selects all five live namespace-local signed metadata
  families together and requires refusal plus byte-exact external restoration.
  ADR 0339 now directly covers valid-old replay of the mutable semantic roots
  under a current external witness and constructs the co-resident-corruption
  v2 gate. ADR 0338 preserves bounded held-descriptor writes both before and
  immediately after exchange in deterministic tests.
  What operator-facing authenticated restore ceremony should select a trusted
  generation? ADR 0340 next needs a real post-exchange descriptor/remount
  campaign; after that, which other durable families—policy, automation,
  attempt, health, or projection markers—lead? What equally semantic observer
  should cut witnessed publication without adding a product crash hook?

- Would a future durable CAS index materially outperform ADR 0331's pull-private inventory after
  native source watching and object bundling, and what authenticated rollback/rebuild contract would
  prevent that index from becoming storage authority?

- What canonical owner-private record admits a signed HEAD as an authenticated replica without
  placing it in the locally authored `published-heads` tree?
- Which principal and rollback witness authorize that replica across cold start, and how is replica
  retirement distinguished from rollback or selective deletion?
- Should source discovery remain entirely owner-local, or may an authoritative HEAD name bounded
  eligible mirrors without granting them HEAD or activation authority?
- Can transparent same-job source replacement be proved without weakening the current source-bound
  FileId/CTA1 fence, or should selected-source loss permanently require an explicit new job?

## Ratox interactive service

R1 through the first R6 contract are now constructed behind explicit default-off gates. R2 is
frozen by ADR 0063, R3 by ADR 0064, the live host boundary by ADR 0065, the private controller stream
by ADR 0066, bounded controller admission by ADR 0067, and the signed restart fence by ADR 0068. The
host reserves a signed lifetime-locked incarnation before networking, terminates PTYs on Agent
restart, returns `not found` for lost local session state, and never implies child survival. rev0022
freezes the R7 instrument, v2 raw-evidence, balanced-schedule, exact-span, auxiliary-digest, and
two-capture-signature contract through ADRs 0069 through 0071, and freezes profile v2 confinement plus the first
capability/confinement boundary through ADR 0072. rev0023 closes reviewed terminal/namespace/lifecycle
escape paths, proves high-descriptor closure, and adds pidfd-revalidated session-wide teardown through
ADR 0073. rev0024 pins procfs member identities, requires repeated quiescent inventories, denies
payload process-handle interfaces, and seals the enabled host's dump/core policy through ADR 0074.
rev0025 adds opt-in delegated cgroup-v2 session ownership, helper-before-manifest attachment,
`cgroup.kill`, and recursive `populated=0` completion through ADR 0075. rev0026 binds every local
control and terminal request/response record to kernel sender credentials, optionally pidfds, rejects
ancillary capability injection, follows terminal-owner process lifetime, and bounds administrative
silent requests/socket inode ownership through ADR 0076. rev0027 multiplexes bounded administrative
pending clients and active-terminal contenders with independent leases, global/per-process quotas,
accept-refill limits, finite per-cycle record work, and active-stream-first service through ADR 0077.
ADR 0078 additionally pins pending control peers, administrative server waits, and the active terminal
connection to exact connection-process lifetimes with optional `SO_PEERPIDFD` handles.
rev0029 retains boot/exact-daemon incarnation recovery and adds pre-network, pre-attachment process,
memory, swap, and CPU controller policy. It serializes startup recovery under the signed host lease,
and reclaims only proven-stale versioned leaves through ADR 0079. rev0030 advances canonical profiles
to v3, composes profile-scoped budgets beneath the host ceiling, preflights distinct identity/effective-
policy pairs, and recomputes composition at spawn through ADR 0081. rev0031 adds exact aggregate
process, memory, and swap reservation admission, pre-mutation atomic charging, RAII rollback, complete-
teardown ownership, fail-closed charge stranding when teardown proof is unavailable, and private
current/peak/rejection/stranding evidence through ADR 0082. rev0032 extends that vector to exact
average CPU bandwidth at one administrator-selected accounting period, rejecting every ratio that
would require rounding, through ADR 0083. rev0033 adds monotone `memory.high` plus cumulative
teardown-time PID/memory/CPU outcomes through ADR 0084. rev0034 adds one exact-device read/write BPS
and IOPS envelope plus cumulative `io.stat` totals through ADR 0085. rev0035 adds zero-baseline
completed-session CPU, memory, and I/O PSI totals plus explicit capability counts through ADR 0086.
rev0036 adds zero-baseline PID, memory, and swap lifetime peaks plus quota-independent complete CPU
work/bandwidth/burst tuples through ADR 0087. rev0037 adds memory fault/reclaim/swap work, swap
high/max/fail events, local freezer duration, and optional IRQ-full pressure through ADR 0088. rev0038
adds descriptor-pinned delegated-root PSI admission with exact basis-point hysteresis through ADR 0089.
rev0039 adds dedicated per-resource PSI trigger descriptors, one bounded poll/eventfd monitor, minimum-
window holds, fail-closed monitor health, and bounded owner-private trigger evidence through ADR 0090.
The controller remains constructed under the signed host lease before recovery or network mutation,
samples before aggregate reservation or spawn mutation, and fails closed. Isolated process oracles retain the positive kernel branches available on the
construction host, while its kernel exposes no per-cgroup PSI and the read-only host cgroup mount
prevents positive live controller-policy runs. It has not run the physical matrix, qualified that path
under a named production service manager and fleet, qualified live PSI admission and positive trigger delivery on a supported host,
adaptive threshold tuning, live peak/fault/reclaim/freeze policy,
positive IRQ-pressure qualification, or parent CPU policy, or qualified every controller and
confinement tier on a named production host.
Remaining questions concern physical experiment execution, supported-host
qualification, independent review, operations, and optional future protocol versions:

- Does remote apply/restart ever justify a separately versioned authority protocol, or should
  `linux-service-v1` preserve owner-local apply and one-use confirmation permanently?
- Which first physical Linux target and whole-cgroup service manager can qualify the frozen
  `linux-service-v1` adapter with operator recovery media, flash-wear bounds, secure-boot policy, and
  power cuts injected at every durable boundary?
- Which external monotonic witness is available on the first target class to detect rollback of the
  complete owner-local update policy and lifecycle state, and when may independently witnessed
  quarantine custody gain a separately reviewed purge procedure?
- What supervisor, authenticated durable journal, and crash-safe input-commit protocol would be
  sufficient to preserve a PTY across daemon failure without replaying uncertain input?
- Which external monotonic witness, if any, should detect coordinated rollback of both the signed
  incarnation state and its surrounding device state?
- How should more than one local terminal be admitted: fixed small cardinality, per-principal quotas,
  explicit operator selection, or a separate multiplexing protocol version?
- Which callbacks should move off the local admission loops so a handler that blocks after admission
  cannot delay unrelated ready clients, and what bounded cancellation/result protocol preserves exact
  request ordering?
- Should hostile same-UID multi-process coalitions be constrained by a daemon-wide token bucket,
  cgroup attribution, a stable local-principal protocol, or an operating-system service boundary?
- What long-duration multi-process/fleet stress matrix is sufficient to qualify the finite local
  admission budgets without pretending they prove starvation freedom?
- Which operations, if any, require authorization finer than the current owner-private same-UID local
  boundary, and what stable local principal could supply it without inventing ambient secrets?
- Which Linux distributions, kernel configurations, architectures, and outer sandbox policies form
  the support matrix for baseline and strict, and what retained boot/runtime inventory proves it?
- Should canonical `compatibility` remain indefinitely for migrated v1 profiles, require an explicit
  operator rewrite, or be prohibited by selected deployments after a staged migration window?
- Should a future strict tier also restrict filesystem read/execute access, and how can executable,
  dynamic-loader, locale, terminfo, library, and profile dependencies be described without granting
  broad ambient trees?
- Should the current one-device BPS/IOPS policy grow to a bounded multi-device map, weights, latency
  controls, or aggregate bandwidth admission; which PSI/accounting thresholds, parent/burst CPU
  enforcement, dynamic policy-reload semantics, and cross-daemon coordination belong above the exact
  process/memory/swap/average-CPU reservation ledger without creating nondeterministic admission? Should
  `CLONE_INTO_CGROUP` replace helper migration on qualified kernels,
  how should deployment tooling surface a populated legacy leaf without unsafe automated cleanup, and
  what named service-manager/kernel matrix proves the complete lifecycle outside an isolated test
  hierarchy?
- Should `ratox-events` hash or redact session/principal identifiers, and what retention/export policy
  preserves useful lifecycle evidence without terminal-content leakage?
- What independent reviewer procedure, binary/host inventory, packet-route inspection, clock-quality
  evidence, load-generator audit, and custody record are sufficient to establish the physical facts
  that v2 digests and capture signatures intentionally do not prove?
- Which reconnect, CPU/RSS, context-switch, and power thresholds should complement the now-frozen R7
  latency and semantic gates?
- Which bounded excess-work scheduler should sit above ADR 0165's qualified 32-accepted-transfer
  ceiling, and can it prove 64 total queued objects on both route classes without weakening attempt
  identity, fairness, cancellation, or the still-failed frozen 64-live-transfer gates?
- What exact R8 review, independent audit, deployment ceremony, recovery runbook, and support boundary
  would justify production support beyond the new self-mode default-on product path?

## Real toxcore and route evidence

- Make the retained founding-machine Sandwurm genuine-peer and controlled-network laboratories a
  repeatable operator/CI runner without weakening their redaction or cleanup.
- Repeat both the accepted savedata/product-load gate and live mixed-provider Sandwurm route matrix
  for every future provider pin. Decide what additional public-network and fleet-orchestration
  evidence is required before calling any transition production-rolling-qualified.
- Measure savedata mutation timing, connection convergence, memory, traffic, and wakeups on target
  Linux hardware.
- Validate ADR 0198's separately keyed native/Tor identities over restart and on target hardware;
  the route set remains immutable for one Agent start and is never live-reconfigured.
- Extend ADR 0205's accepted exact Tor-process-loss/native-reassignment/carrier-return sample across
  long-duration operation, multiple reviewed relays/exits/time windows, and adversarial local-proxy
  behavior. Decide whether a separate exact-member retry policy is useful without weakening
  immutable-object integrity or allowing auxiliary evidence to mutate session epochs.
- Extend ADRs 0207/0208's accepted 120-sample actual-Tor Ratox circuit-churn proofs and ADR 0206's
  accepted process-loss cell across independently separated time windows, explicit Tor-path
  populations, and adversarial local
  proxies while retaining the frozen heartbeat, PTY-output, session, and byte-continuity proof.
  Decide whether any automatic
  resume policy can preserve explicit authenticated epochs and exact attachment identity without
  allowing auxiliary evidence to change carrier truth.
- Extend ADRs 0220–0222's enforced per-job failover and constructed-network class into a signed
  route-class grammar: which equivalent classes may replace a privacy-required member, how does the
  stable device authenticate that class without disclosing endpoints, and how is it kept distinct
  from local fixed/adaptive load placement?
- Extend ADR 0227's accepted bounded digest-bound auxiliary range transfer through an actual-I2P
  carrier interruption/resume, then repeat the exact-I2P payload gate across later records/time
  windows without turning one observed carrier epoch into a product MTU or availability claim.

## Product and safety boundary

- Which first hardware integration is harmless enough to exercise end-to-end semantics without
  implying lock, medical, fire, or industrial safety claims?
- What signature, anti-rollback, staging, health-confirmation, and recovery contract is required
  before any transferred object can become executable firmware?
- Which target classes can run toxcore directly, and which require an owner-controlled gateway?
- What upstream bootstrap/relay contribution can IoTox operate without becoming mandatory vendor
  infrastructure?
