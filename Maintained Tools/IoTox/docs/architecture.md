# IoTox rev0051 architecture

Significant architectural additions must pass the intake checklist in
`docs/architectural-change-intake.md` before they are treated as coherent
product architecture. In particular, no new subsystem may blur friendship,
authority, route class, durable storage, terminal execution, support export,
or backup boundaries merely because the implementation path is convenient.

## 1. Product shape

IoTox is one C++20 executable with two invocation roles:

```text
iotox run ...       foreground agent
iotox COMMAND ...   local operator/client
```

`iotox run --mode self` is the self-machine product shape: the Ratox terminal
host and same-user terminal controller are selected by default for machines the
owner admits to their own domain. That mode still routes every shell effect
through fixed profiles, principal bindings, `interactive.terminal`, and host
policy; it is not Tox multidevice and not friendship-as-authority. The
owner-signed self-swarm roster is the first native membership layer for that
domain: it names aliases, stable principals, route keys, narrow roles/caps, and
retired members, then feeds reviewed authority grants and revocations.
The public person delivery-card layer sits above that private roster: it
publishes only the owner/person key, roster generation/digest, and active Tox
route keys, then lets direct or device-delegated person-message envelopes fan
out over those routes without making the route key the human identity.
Contact-side card floors, local seen stores, signed group descriptors,
contact books, transcripts, delegated device receipts, aggregate receipt
stores, and reviewed outbox plans form the first messenger substrate above
delivery. Native `outbox-retry-plan`, `outbox-expire`,
`card-refresh-plan`, `background-plan`, and `background-run` now make
retry/freshness/expiration ordinary bounded work for service supervision.
Top-level `service plan|render|receipt|status-plan|status-receipt` now
projects the Agent/sync/Ratox service and person messenger worker into
reviewed systemd, NixOS, or MonsterNix-adapter shapes and records explicit
operator-observed service status for stable dossiers. Local
`read-mark`/`read-status`,
`transcript-convergence`, and `group-status` make human-read UX, transcript
set convergence, and signed group summaries native without converting them
into remote delivery proof, global total order, or Tox groupchat identity.
Delivery to never-online devices, independent person/group freshness custody,
and automatic Tox group/conference adapters remain outside the current claim.

The installed surface is one binary. The POSIX PTY adapter and sealed update-service pre-exec helper
re-enter that same executable through distinct exact hidden child arguments before public CLI
parsing; these are implementation boundaries, not public invocation roles. Internal libraries,
exact mocks, test-only fixtures, fuzzers, and
incubator programs are build/evidence components, not additional products.

The immediate product is a modern ratox successor:

```text
small headless agent
Tox connectivity
public-key-first peers
ordinary Unix control and observation
self-owned stable identity and authority
explicit self-machine mode for owner-controlled terminal reachability
durable machine operations beneath a simple surface
no mandatory vendor service
```

## 2. Layering

```text
operator / script / local integration
        |
        | Unix SOCK_SEQPACKET + private runtime files/FIFOs/journals
        v
one iotox agent process
        |
        +-- bounded local control decoder and correlated dispatcher
        +-- hardened friendship and per-peer FIFO services
        +-- stable device identity
        +-- signed authority ledger
        +-- owner-signed self-swarm roster tools
        +-- person delivery-card, delegated sender, seen-store, and group tools
        +-- transcript-bound authority sessions
        +-- signed durable command store
        +-- transport/storage-blind operation executor
        +-- finite-file manager
        +-- default-off file/tree synchronization publisher/subscriber and activation transaction
        +-- default-off signed-update verifier, health-gated slot lifecycle, and sealed Linux service adapter
        +-- Ratox coordinator, terminal profile registry, and PTY adapter
            (manual default-off; self-mode default-on)
        +-- bounded command/event queues
        +-- disposable runtime projection
        |
        v
one serialized Tox owner thread
        |
        +-- runtime provider for research/exact mock
        +-- source-linked provider for product
        v
c-toxcore
        |
        +-- Tox/native now
        +-- Tox/Tor strict construction route
        +-- Tox/I2P strict VM-qualified route
```

No business-logic module may call toxcore directly. The transport adapter owns C ABI conversion,
callback capture, iteration, savedata, custom-packet/file calls, and error mapping.

## 3. Identity classes

IoTox does not ask one key to do every job.

```text
RecallRoot-v1
    permanent generated phrase -> Argon2id root

owner principal
    deterministic Ed25519 key derived from RecallRoot-v1

stable device principal
    independent random Ed25519 key stored by the device

Tox route identity
    c-toxcore savedata identity for addressing/session transport

self-swarm roster v1
    owner-signed local membership artifact binding alias, stable principal,
    expected Tox route key, role, capabilities, generation, and retirement

person delivery card v1
    owner-signed public route artifact binding person key, self-swarm
    generation/digest, and active Tox route keys without private aliases

person message envelope v1
    sender-person-signed bounded message carrying from-person, to-person,
    nonce, message-id, and body independent of the route that delivered it

person sender delegation v1
    person-signed authorization for one stable device principal to sign daily
    person/group messages without RecallRoot on every send

person group descriptor/message v1
    creator-signed sorted person-key membership plus direct/delegated bounded
    group-message envelopes delivered through member person cards

person messenger stores v1
    owner-private contact book, contentful transcript, delegated device
    receipt, and reviewed outbox state for explicit per-route delivery plans
```

Properties:

```text
owner authority can be reconstructed from memory or print
device identity survives process and Tox route-key replacement
Tox friendship does not imply application authority
route-specific Tox identities bind to one device principal through signed route-set policy
self-swarm membership plans and applies authority but does not replace the authority ledger
person delivery says where a person can be reached, not what any route may do
group membership says which person keys may speak, not which Tox route is authoritative
command-store signatures remain stable when the Tox endpoint changes
```

rev0018 retains transcript-bound directional proof of a stable principal over the current Tox
session and binds authority-ledger format into v2 challenges, proofs, and confirmed sessions.
Route-set v1 signatures, strict pre-network loading, signed generation high-water state, and the
content-free operator projection are implemented. Live reciprocal worker binding and immutable
multi-route sync are also implemented for the qualified same-context construction. ADR 0198 keeps
native and privacy-routed Tox keys independently random by default and forbids treating v1's full
auxiliary roster exchange as private cross-context discovery.
The negotiated private construction allocates a primary-only full-inventory frame and a fixed
member-scoped auxiliary proof bound to the full artifact digest, exact primary authority epoch, and
auxiliary transcript. Its bounded send/receive registry, generation/fork high-water, worker handoff,
and authority-loss withdrawal are implemented behind `--enable-private-route-bindings`
(ADRs 0199/0200). Exact-key local worker network contexts and ordering-safe adoption of an early
reciprocal proof are implemented and two-guest generic-SOCKS qualified by ADR 0201. The ordinary
feature mask and v1 worker path remain unchanged.

## 4. Authority ledger

The authority ledger is the local application constitution. It is separate from:

```text
Tox friend list
confirmed IoTox session registry
signed command journal
runtime filesystem projection
```

It contains fixed-size signed records bound to one stable device principal. Deterministic replay
produces the active principal table.

```text
v1 bootstrap owner
    -> grant administrator/operator/viewer/automation/service/owner
    -> revoke active principal
    -> exact self-signed migration to v2 with no capability widening
    -> explicit v2 grant may add interactive.terminal
    -> exact self-signed migration to v3 with no capability widening
    -> explicit v3 owner self-grant may add synchronization rights
    -> grant successor owner with exact rights
    -> successor-signed next ownership epoch preserving those rights
    -> old principals no longer live
```

Policy invariants:

```text
issuer must be active
issuer must hold manage.principals
issuer cannot grant capabilities it lacks
role ceilings are fixed
only owner can create/revoke owner
active owner cannot be demoted by an overwrite grant
last active owner cannot be revoked
epoch transition must immediately follow a distinct successor-owner nomination
successor signs the transition, epoch advances once, and sequence resets to one
unknown actions/roles/capabilities fail closed
v1 `all` remains seven bits; `all-v2` remains eight bits; v2 terminal and v3 sync authority require explicit later grants
ledger format, record domain, challenge/proof domain, and session negotiation agree
```

Preparation produces exact bytes for an external signer. Append/replay independently rechecks all
policy because callers may construct records without preparation. A separate fixed-size rollback
guard records committed and pending exact heads around atomic complete-history replacement. It
rejects unrelated local rollback, deletion, and forks while making no claim against coordinated
replacement of both ledger and guard.

## 5. Local owner mutation ceremony

For RecallRoot commands, the local `iotox` client—not the agent—handles the permanent secret:

```text
phrase from stdin
    -> RecallRoot-v1 Argon2id
    -> owner seed domain
    -> Ed25519 keypair
    -> request canonical body from agent
    -> sign locally
    -> append signed record
```

The agent receives the public issuer in the prepare request and the final signed record. It does
not receive the phrase, root, seed, or owner secret key.

This reduces secret spread; it does not defeat a hostile equal-privilege local process.

## 6. Transport, session, authority, and operation state

The state model is deliberately layered:

```text
transport friend
    c-toxcore recognizes a Tox public key

online transport epoch
    friend is connected through Tox

compatible IoTox session
    HELLO negotiation succeeds

confirmed IoTox session
    both peers confirm one canonical transcript

challenged IoTox principal
    peer names verifier device, ownership epoch, transcript digest, and challenge

authorized IoTox principal
    valid Ed25519 proof binds an active ledger principal to that session

admitted operation
    proven principal holds the capability for the exact operation

durable operation
    canonical request and state transitions survive process restart
```

The stable device principal answers a peer challenge automatically; recalled-owner/controller
proof remains explicit. `device.describe` and `system.summary` require `read.telemetry` and cross
the same durable engine. They can be entered through the structured one-binary client or literal
per-peer command FIFO; both entrances converge before durable identity reservation.

## 7. Capability session

Every true online transition starts a new session epoch:

```text
fresh local 128-bit nonce
frozen local HELLO and message ID
first valid peer HELLO frozen
symmetric negotiation
frozen local confirmation and message ID
first valid peer confirmation frozen
application-frame gate opens only after exact mutual confirmation
```

The required friend-connection callback is the sole lifecycle authority for those transitions.
Friend-list refresh is an inventory and presentation snapshot only: it may ensure that a known
public key has an offline registry shell, but it may not call `peer_online`, call `peer_offline`,
create a nonce, send HELLO, or advance an epoch. A snapshot collected on the toxcore owner thread
can be stale by the time another worker applies it; treating it as an ordered event can manufacture
a reconnect and discard a frozen retry record. A continuous TCP/UDP presentation change updates the
current session without opening a new epoch. ADR 0044 freezes this separation.

Transient toxcore `SENDQ` or not-connected rejection retries the same frozen record. Once
c-toxcore accepts the lossless packet, IoTox does not invent blind retransmission above Tox.
Application receipts and durable command recovery are a separate layer.

### Owner scheduling and live interactive service

One `Tox*` still has exactly one owner thread. Its local command admission is separated into
interactive, control, and bulk queues with an 8:4:1 weighted schedule. At most 16 calls run before
the next `tox_iterate`, so neither a busy file source nor a stream of local commands can indefinitely
delay provider progress. A newly nonempty interactive queue receives one preemptive service without
rewinding the weighted cursor, preserving eventual control and bulk service. Peers cannot choose
these classes over the wire.

The owner sleeps for the smaller of c-toxcore's requested interval and the configured maximum,
20 ms by default. Runtime status exposes iteration count, requested/effective interval, pending
commands, executed counts, and maximum wait per class. This is a latency/power policy seam, not a
new network transport.

The Agent has a distinct threading boundary above that owner. One event consumer applies every
ordered friendship, protocol, finite-file, and projection event. Ratox host/controller cadence runs
on a separate condition-variable worker so it cannot make required-event draining wait for the
toxcore owner that is applying backpressure. Local terminal changes and Ratox transport events wake
that worker by generation; active attachments use the configured 5 ms defaults and idle Ratox uses
20 ms. The worker does not own or call `tox_iterate`; its sends still enter the sole owner's
interactive command class. ADRs 0156 and 0157 freeze this separation.

### Experimental multi-route coordination

The default product still owns one `Tox*`. With explicit route-worker construction enabled, it loads
a stable-device-signed inventory, checkpoints its generation before networking, and supervises an
independently keyed toxcore owner for each auxiliary member. Every route retains its own owner-thread
and savedata rules. A worker reaches ready only after reciprocal binding proof anchored in the exact
authority-authenticated primary session; this remains coordinated routes, not a transparent bonded
socket.

An exact auxiliary may override the primary's local network context. The Agent derives the complete
native or strict-Tor toxcore configuration for every signed key and validates the entire topology
before starting one worker. Proxy endpoints are deliberately host policy, not signed inventory.
Private-v2 context replacement cancels effects and regenerates local proof, while an inert early
remote proof is retained only for exact revalidation; stale proof bytes are discarded without
authority. This closes a genuine one-shot scheduling race without changing framing (ADR 0201).

```text
one authority and workload coordinator
        |
        +-- protected authenticated route: Ratox/control, bulk-free by default
        +-- authenticated bulk route: immutable sync objects
        +-- authenticated bulk route: immutable sync objects
        `-- explicit degraded/recovering/unavailable state
```

Ratox frames remain ordered on one protected route. The first transport-neutral scheduler now makes
immutable kind/digest/size records the only assignment unit, admits them only to exact ready bulk
workers, fences attempts before reassignment, rejects late completion, and commits a verified object
once. Toxcore file numbers never cross that identity boundary. Missing capacity fails closed rather
than overloading remaining routes. ADRs 0108 and 0110–0122 freeze the implemented direction. An
attempt now derives one private staging path, reserves its full bytes across all namespace routes,
and can transactionally commit verified bytes to the object store. Each authenticated auxiliary bulk
worker contains its own bounded file-transfer manager and file-number domain. An admitted receive
pre-reserves a non-evicting terminal slot; the namespace bridge binds that live handle to one attempt
and lets only strict object-store verification drive scheduler completion. The genuine two-guest
Gate 3 cell now fences one positively progressing carrier, reassigns only missing immutable objects,
rejects old-incarnation truth, restores the exact route identity under a fresh incarnation, and then
proves protected Ratox on direct UDP and forced TCP. `multi-route-plan.md` owns the remaining
fixed/adaptive performance/fairness and long-running policy qualification. The first genuine
fixed/adaptive topology A/B now passes both carriers: fixed reuses one eligible route and adaptive
places the later overlapping job on the idle route (ADR 0171). Before
receive, the stable-device-signed namespace attempt journal retains an ID high-water mark plus active
object/route incarnations. Restart recovery verifies final bytes or commits complete staging and
fences everything else without persisting or reviving Tox file numbers.
Available-policy bounded ranges now use the same attempt boundary. On auxiliary loss, an exact
strict positive range prefix may remain inert only after the old receive, FileId, signed attempt,
and scheduler reservation are retired. A distinct authenticated worker that negotiated range-v1
receives the unchanged HEAD/range plan under a fresh attempt and FileId, inherits the inode by
no-replace handoff, and seeks before receiving the suffix. Fail-closed loss still discards and
blocks; no route-class migration is inferred. The boundary is repeatable rather than a one-shot
exception: each subsequent loss must finish and fence its current attempt before another fresh
carrier can inherit the newly observed exact prefix (ADR 0231).
The number of processes is not frozen, but one product binary and one authority coordinator are.
This remains explicit experimental construction rather than a default bonded transport.

Route admission has two explicit policies. `adaptive` is the default bounded-load order. `fixed`
remains an explicit stable route-key diagnostic policy. `adaptive`
is a Gate 4 experiment that chooses the lowest exact admitted-work/signed-budget ratio, then fewer
restarts and the stable key, only for a new job or after an old carrier is already fenced. Neither
policy migrates a healthy pull or derives authority from load. ADR 0170 freezes the selector; live
topology comparison and counterbalanced policy phase order are accepted by ADR 0171. For auxiliary
pulls, local status joins process-private transfer FileIds to the exact worker incarnation and exposes
only aggregate active-receive count, position, and size. ADR 0172 uses that content-free seam to bind
positive progress to bounded cancellation and exact work release on both carrier classes. ADR 0176
also qualifies both exact corresponding auxiliary readiness orders with a post-authentication hold;
it does not rewrite route inventory or framing. Random startup/fault delays or startup under fault,
larger-load performance/fairness/resources, randomized loss/cancel timing, common-link QoS, and relay
diversity remain qualification work. ADR 0177 closes the opposite deterministic
cancellation→loss→recovery order with zero reassignment. ADR 0178 closes one shared-arm
cancellation/loss cell per carrier: both linearize as cancel-first, expose typed transport cleanup
unavailability, settle it by one exact retry, and recover route capacity without reviving the pull.
ADR 0179 makes fault lead from the same armed state without polling for reassignment; both carriers
perform exactly one fresh assignment and cancel that replacement on the first request. Both
authority linearizations are therefore live-qualified, though timing distributions remain open.
ADR 0174 closes the bounded
eight-job/four-withdrawal concurrent-cancellation row and records why a protected logical route does
not imply physical queue priority. ADR 0175 additionally closes one exact loss→reassignment→
replacement-progress→cancellation order and permits the explicit qualification restart only after
the affected pull is complete or cancelled. ADR 0180 closes one deterministic eight-job/four-
affected-carrier loss row. Replacement eligibility now requires the complete remaining job work;
transient pre-offer publisher `unavailable` results receive bounded fresh message/FileId retries;
and auxiliary carrier service runs independently from the sole ordered event consumer without
holding the supervisor snapshot mutex across toxcore owner waits. Random timing distributions,
startup during faults, larger-object common-link behavior, and production restart policy remain
open.
ADR 0181 closes the next degraded-admission distinction. Two jobs migrate from one stopped fixed
carrier, then two jobs created after loss both enter through the sole ready survivor before recovery;
all four activate and signed work drains exactly. Auxiliary shutdown now quiesces and joins
synchronous carrier service while ordered event draining remains alive, then stops the event
consumer and transports. This preserves the same no-required-event-loss rule during clean shutdown,
not only steady service. ADR 0182 then qualifies the complementary startup shape: after a clean
same-state Agent restart, one authenticated route is sufficient to admit two live 16 MiB jobs, and
the delayed route's later readiness does not migrate either healthy assignment. This is an
application-readiness hold inside an already-running guest, not physical path absence. Machine or
guest cold startup with a route absent, random timing distributions, larger-object throughput and
common-link behavior, and production restart policy remain open.

The `interactive` component now owns the complete transport-independent R1 model:

```text
attachment fence       session/incarnation/principal/nonce/generation
bounded byte replay    cumulative ACK, retained prefix, explicit history gap
input receiver         staged whole-frame commit, duplicate/overlap/gap classification
output history         independent sequence, ACK release, bounded eviction, explicit gap
message replay cache   pre-effect result reservation, exact duplicate replay, no ID eviction
interactive session    attachment/output ACK atomicity, lifecycle, replacement, bounded events
session directory      atomic two-per-principal and eight-per-device quotas
RTT estimator          monotonic SRTT/variation and bounded RTO
```

It also owns fixed 10-byte custom-lossless/custom-lossy diagnostic echo codecs. The Agent answers
them only for a transcript-confirmed peer. They are unadvertised carrier evidence and do not open a
PTY, carry terminal data, grant authority, or alter protocol 1.0 negotiation.

Always-on advertised implemented features:

```text
capability-session-v1
tox-text-lane
finite-file-transfer-v1
authorization-ledger-v1
authorization-ledger-v2
authorization-ledger-v3
durable-commands-v1
```

Runtime-conditional implemented feature:

```text
ratox-interactive-v1
```

Feature bits 24 and 25 advertise the implemented v2 and v3 authority/session formats. V3 proofs
require both bits for the exact confirmed epoch. Ratox terminal-service bit 23
is omitted in manual mode by default. It is added to the frozen local HELLO mask only when the
operator explicitly enables the service, or selects `--mode self`, and all profile-store,
process-factory, and bounded-service checks succeed before toxcore starts. An activation failure
therefore prevents network startup rather than exposing a partially configured feature.

### Live Ratox service boundary

Ratox packet ID `0xA2`, framing 1.0, the R1 session model, the R3 process boundary, and the R4 Agent
coordinator remain connected in rev0020. Transport callbacks still cannot create processes directly:

```text
custom-lossless callback for packet 0xA2
    -> current transcript-confirmed online epoch
    -> bilateral ratox-interactive-v1 negotiation
    -> authenticated remote stable principal
    -> exact current authority-ledger head with interactive.terminal
    -> strict frame decode and attachment/session validation
    -> replay-result reservation before any effect
    -> fixed local profile resolution
    -> bounded PTY controller and process backend
    -> retained outbound response queue
```

The Agent supplies a fresh route context for every packet. Friend number is only the current toxcore
routing handle; online epoch, stable principal, session ID, incarnation, attachment nonce, and
monotonic generation fence stale traffic. The coordinator prefixes every existing-session control
replay identity with a local domain plus that authenticated friend/epoch, and cancels a fresh replay
reservation when attachment-route validation fails. Byte-identical traffic on another route can
therefore neither inherit a result nor consume the owning route's replay slot. A v1 owner or any v2
principal without an explicit bit-7 grant is denied even after transcript confirmation and feature
negotiation; unauthorized absent ATTACH/RESUME requests receive a retained denial rather than
`NOT_FOUND`.

One Agent mutex orders local or remote signed authority-head mutation against Ratox receive,
bounded PTY progress, and outbound transport admission. The ledger and authority-session objects
retain their own internal locks; this outer lock exists only to make the exact-head decision and the
resulting Ratox effect one transaction from the Agent's point of view.

`RatoxService` owns cumulative input commitment, duplicate suppression, attachment generations,
incarnations, output history and gaps, bounded result replay, quotas, PTY lifecycle, and content-free
events. It stages one whole INPUT frame, permits only bounded nonblocking PTY writes, and advances the
input ACK only after complete sink commitment. A partial-write failure makes the incarnation terminal
so uncertain bytes are not replayed into a replacement process. Its service loop rotates among live
sessions under global read, write, and frame budgets so one busy PTY cannot indefinitely starve the
others.

Outbound packets remain byte-for-byte retained until toxcore accepts them. A retryable `SENDQ` or
not-connected result stops the cycle without dropping or regenerating the packet. A stale epoch or
non-retryable route failure detaches the route. Transport disconnect fences the attachment but leaves
the PTY eligible for a later valid attach/resume. Exact-head proof loss is reconciled against the
last successfully attached friend/epoch and closes only that route's sessions; rejected traffic cannot
retarget the recorded owner. A durable signed-ledger revocation is a separate principal-wide pass that
also reaches detached sessions and other epochs. Agent shutdown initiates HUP/TERM/KILL closure and
drains PTY state under a finite deadline.

The fixed outbound record carries a `terminal_authority_required` fence that survives exact admission
replay. Before sending an authority-bound record, the Agent reconstructs the current route context and
requires the same epoch, principal, negotiated feature, and exact-head terminal grant. Explicit
unauthorized admission denials clear only this authority dependency; they still require a current
confirmed negotiated route and disclose no attachment success or terminal content.

The local policy tree maps a nonzero stable principal to one fixed profile. Canonical owner-only
profile v7 records freeze argv, cwd, exact environment construction, terminal type, dimension clamps,
identity, privilege policy, rlimits, close graces, one local confinement tier, and an optional profile-scoped cgroup
budget including one exact block-device I/O policy. They may also pin the exact SHA-256 bytes of the
shell and rescue Toybox ELF; the already-open shell descriptor and the descriptor-pinned Toybox path
are rehashed immediately before spawn. Candidate replacement is validated and sorted
before atomically incrementing the registry generation. A resolved profile is copied with its
generation and remains immutable for one OPEN attempt. Missing, disabled, ambiguous, insecure, or
malformed policy denies creation. Existing canonical v1-v6 records remain readable; v1 maps explicitly
to `compatibility`, v1/v2 map to an empty profile budget, v3 maps to no `memory.high`, v1-v4 map to no
I/O policy, v1-v5 map to denied privilege escalation, and v1-v6 carry no payload pins. New profiles default to
`baseline`. V6's retained `account` identity freezes one non-root UID, primary GID, and sorted unique
supplementary-group vector instead of inheriting mutable daemon groups.

When the explicit host gate is enabled, the outer `run` entrance first seals the long-lived process:
`PR_SET_DUMPABLE` must read back as zero and the soft plus hard `RLIMIT_CORE` values must both read back
as zero before `Agent` is constructed. Controller-only and ordinary agent invocations do not acquire
that irreversible process policy.

The Linux backend opens helper, target, and cwd without following path symlinks, passes target and cwd
by descriptor, and uses `posix_spawn` to enter the same IoTox executable in a hidden child mode. High
source descriptors make ordered file actions collision-proof. The child receives a bounded canonical
manifest, PTY slave, status channel, executable descriptor, and cwd descriptor; creates a session and
controlling terminal; applies window, foreground group, limits, exact environment, runtime
capability-ceiling discovery, ambient and active capability clearing, exact identity, nondumpability,
`umask(077)`, and two-pass inventory-proved descriptor closure. `baseline` then installs an
architecture-checked hazardous-syscall seccomp filter that inspects reviewed terminal/console ioctl
requests and legacy clone namespace flags, returns `ENOSYS` for clone3, and freezes `setsid`,
controlling-terminal reassignment/detach, parent-death-signal mutation, and payload acquisition/use of
the reviewed pidfd/process-memory interfaces. `strict`
additionally requires MDWE and Landlock ABI 10, grants ordinary
mutation only below the already-open non-root cwd, grants no TCP/UDP port, and scopes pathname and
abstract Unix sockets plus external signals. It never downgrades those requirements. The child
announces readiness only after the selected tier is installed and then uses `fexecve`. Readiness plus
close-on-exec EOF is the success proof. A fixed stage/errno record reports setup or exec failure, and
startup timeout kills and reaps the child. Before PTY allocation, baseline/strict require pidfd open
and signaling plus a readable inventory whose filesystem type is genuine procfs; immediately after
spawn they require a retained close-on-exec leader pidfd. Compatibility retains the historical
process-group path.

By default every tier also sets and reads back `PR_SET_NO_NEW_PRIVS`, seals privileged securebits and
the capability bounding set, and therefore prevents set-ID or file-capability helpers from granting
new privilege. Profile v7 retains one deliberately separate v6 exception:
`allow-privilege-escalation=1` is valid only for `compatibility` plus a non-root account identity.
The child then proves that inherited `no_new_privs`, securebits, and capability bounding policy have
not already made elevation impossible, while still clearing all active, permitted, inheritable, and
ambient capabilities before the selected shell exec. This makes ordinary host-authorized `sudo`
possible without starting Ratox as root. It also truthfully gives up baseline seccomp, Landlock, and
delegated-cgroup containment: root obtained through sudo could escape all three. The remote peer
still selects no executable, argv, account, group, environment, or privilege flag.

ADR 0287 adds no runtime protocol component. The optional `iotox-rescue-toolbox` deployment payload
is a separate static oksh plus Toybox payload. Owner-local discovery canonicalizes its shell and
directory, applies the existing ELF/ownership/mode checks to the `toybox` multicall target, and emits
an ordinary disabled profile-v6 record with fixed `-i` and toolbox-first PATH. The package is neither
linked into the product nor selected automatically. Baseline remains the default; a rescue-admin
profile crosses the same explicit compatibility/sudo boundary above. The resolved profile and PTY
path therefore require no Ratox, authority, registry, local-socket, or profile-format change.

`TerminalController` bounds each I/O call, rejects input and resize once close begins, permits output
drain, observes exit before signaling, and escalates HUP, TERM, then KILL with fresh monotonic profile
windows. Native exit observation prefers `waitid(P_PIDFD, ..., WNOWAIT)` with a narrow direct-child wait
fallback. Baseline/strict inventory the fixed PTY session through one pinned `/proc` descriptor. Each
numeric member directory is opened without following links; reported PID, session, live state, and
field-22 start time are parsed and then re-read through the same directory after pidfd acquisition.
Only a matching identity is signaled through the pidfd. Without cgroup configuration, once SIGKILL
begins, any live member resets a quiescence counter and three consecutive complete empty inventories
are required before the waitable leader is reaped.

rev0025 adds a stronger optional KILL/completion path. `--ratox-cgroup-root` names one explicit
administrator-delegated cgroup-v2 manager root. The production factory rejects compatibility,
inherited/root/daemon-equal identities, retained supplementary groups, injected factories, unsafe
paths, wrong filesystem type, unsafe ownership/mode, missing controls, threaded leaves, or failed
migration. It creates one daemon-owned underscore-prefixed leaf, pins the pathname and opened inode,
attaches the still-waitable helper before sending its manifest, and leaks no control descriptor across
exec. Explicit KILL and natural-leader cleanup write the pinned `cgroup.kill`; exit remains unreported
until an event-driven `cgroup.events` wait says recursive `populated 0`; the exact leaf is removed
before leader reap.
HUP/TERM retain the pidfd/procfs session sweep because cgroup v2 has no equivalent subtree-wide
nonfatal signal. Empty configuration preserves the rev0024 path exactly.

rev0028 closes the ungraceful-daemon-restart gap. New leaves use
`_iotox_session_v2_<boot-id>_<pid>_<start-time>_<sequence>`, binding the delegated object to the
creating daemon's canonical Linux boot ID and `/proc/<pid>/stat` field-22 start time rather than a
reusable PID alone. The signed Ratox host-incarnation lease is acquired before recovery, serializing
legitimate daemon starts. Recovery then pins and validates the complete bounded reserved-name set
before mutation. Exact live owners are preserved; stale versioned owners receive recursive
`cgroup.kill`, bounded `populated=0` proof, and exact-inode removal. Empty legacy leaves are removed,
while populated PID-only legacy leaves and malformed reserved names fail startup because their
ownership cannot be proved reuse-safe. Recovery completes before the PTY factory or transport is
activated, and content-free counts are projected in runtime status.

rev0029 layers a host-owned controller envelope on that exact leaf. Optional process, memory, swap,
and CPU fields map to `pids.max`, `memory.max`, `memory.swap.max`, `memory.oom.group=1`, and
`cpu.max`. The delegated root must advertise and activate every requested controller. Real session
creation applies and exactly reads back all controls before the blocked helper enters the leaf. No
configured error silently falls back.

rev0030 added the same five fields to canonical local profile v3 and composed them beneath the host
ceiling. rev0033 emitted profile v4 with a sixth `memory.high` throttle field. rev0034 emits profile v5
with one exact `MAJOR:MINOR` plus read/write BPS and IOPS ceilings and matching host CLI policy. For
pids, memory high, hard memory, swap, and each I/O rate, the smaller configured maximum wins; an absent
side inherits the configured side. Cross-layer high is clamped to the effective hard maximum. CPU
selects the lower exact `quota/period` ratio, treating an absent period as 100,000 microseconds. The
implementation compares positive rationals through continued fractions, avoiding floating-point drift
and overflowing cross-products; equal ratios retain the host representation. I/O composition requires
exactly matching host/profile device identities, so a profile can tighten or add policy but cannot
weaken or redirect administrator policy.

After lease acquisition but before orphan recovery, Agent startup computes every enabled profile's
effective envelope and creates one disposable leaf per distinct `(payload identity, effective budget)`
pair. Only after all probes succeed may rev0028 recovery, production-factory construction, or transport
activation proceed. The production factory recomputes composition before cgroup filesystem or spawn
work and passes only the effective envelope to leaf creation. An enabled effective budget without an
explicit delegated root fails host activation and direct factory admission.

rev0031 adds one factory-owned aggregate admission controller above those effective leaves for
process, memory, and swap maxima. rev0032 adds exact rational CPU bandwidth to the same atomic vector.
The administrator selects one aggregate quota and accounting period; 100,000 microseconds is the
period default. Every enabled effective policy must carry finite matching maxima, fit once before
activation, and have a CPU ratio exactly representable as an integral quota at that accounting period.
Continued-fraction comparison and GCD-reduced normalization avoid floating point, overflowing cross-
products, and hidden rounding.

The controller checks and charges the complete vector under one mutex before helper-path, filesystem,
PTY, cgroup-leaf, or spawn work. Its move-only reservation token rolls back pre-spawn and proved-
cleanup early returns and remains attached to the PTY object until recursive cgroup quiescence/removal
and leader reap. If post-spawn cleanup cannot prove both leader reap and exact leaf removal, it strands
the complete charge rather than under-account possible live work. This is conservative configured-
maximum accounting, not physical allocation or parent-cgroup CPU enforcement.

rev0038 adds a second factory-owned admission controller over recent delegated-root PSI. This
controller is host-local and independent of profile serialization and the Ratox wire. During host
activation it verifies the same normalized daemon-owned cgroup-v2 root, pins `cgroup.pressure` and
each configured `cpu.pressure`, `memory.pressure`, or `io.pressure` file by descriptor, requires
enabled accounting, and parses one complete sample before listener/network exposure. PSI observation
does not itself require those resource controllers in `cgroup.subtree_control`; configured resource
ceilings retain their separate controller checks.

The policy carries exact basis-point maxima for CPU `some avg10`, memory `full avg10`, and I/O
`full avg10` plus one common hysteresis width. A request closes the gate only when an enabled value is
strictly above its maximum. Once closed, every enabled value must reach
`maximum-hysteresis` before the same sample reopens and admits. Any missing, disabled, unreadable,
malformed, or semantically incomplete sample rejects and latches closed. `cgroup.pressure=1` is checked
before and after the configured reads. One mutex joins descriptor reads, state transition, and
saturation-safe counters. A live sampling failure is classified as local `unavailable`; the private
snapshot retains last-sample validity and the original typed local error while preserving the last
valid complete observations.

Spawn ordering is now:

```text
resolve and validate effective profile/resource policy
    -> sample descriptor-pinned delegated-root PSI and transition the latch
    -> atomically reserve the complete aggregate vector
    -> validate helper/filesystem and create PTY/session cgroup/process state
    -> attach the blocked helper, verify policy, and release the manifest
```

A pressure rejection therefore consumes no aggregate charge and creates no leaf or child. A pressure
admission grants no shortcut around later aggregate, cgroup, confinement, attachment, or supervision
checks. A valid high-pressure sample does not abort Agent startup because it is live policy state; the
first real request applies the threshold.

rev0039 adds independently opened PSI trigger descriptors to the same controller. One optional
trigger may be paired with each configured CPU `some`, memory `full`, or I/O `full` metric. All triggers
share one validated 500-millisecond-to-10-second tracking window and each cumulative stall threshold
must be positive, no larger than that window, and paired with its metric's avg10 threshold. Startup
writes one exact trigger record per descriptor and refuses activation if registration or monitor
construction fails.

One finite monitor thread polls those descriptors and a private eventfd. A priority event publishes its
resource class atomically, then the admission mutex transfers pending events into saturation-safe totals,
closes the gate, and extends a hold through at least one complete tracking window. Hold expiry never
opens the gate by itself; a later complete avg10 sample must still satisfy every lower hysteresis boundary.
Poll error, invalidation, hangup, or unexpected monitor failure latches the controller unhealthy and all
later admissions unavailable. Destruction wakes the eventfd, joins the monitor, and only then releases
the descriptor-pinned registrations.

rev0033 opens one protected read-only outcome interface for every selected PID, memory, and CPU
controller before payload attachment. It prefers local-only `pids.events.local` and
`memory.events.local`, falls back to hierarchical variants only when the local kernel files are
unsupported, and opens controller-enabled `cpu.stat` for CPU bandwidth policy. rev0034 requests the
`io` controller when I/O policy exists, writes one complete `io.max` device line with explicit `max`
values, and semantically verifies the unordered nested-key readback before helper attachment. It also
opens protected `io.stat`. A new leaf must have zero known counters.

rev0035 also attempts to open protected `cpu.pressure`, `memory.pressure`, and `io.pressure` for every
session leaf, independent of which resource ceilings are configured. Interface absence is preserved
as an optional capability. When `cgroup.pressure` exists it must report exact enabled state. A bounded
nested-key parser requires canonical `some` PSI fields, accepts an optional `full` class, validates the
rolling percentages, and retains only absolute cumulative microseconds. Every observed total must be
zero before helper attachment.

After recursive `populated=0` and before exact-inode removal, bounded key-based parsers capture every
selected record. Unknown future well-formed keys are accepted, malformed or duplicate keys fail
parsing, `io.stat` totals every unique device line with saturation, and one session outcome may be
consumed only once. Complete PID, memory, CPU, read/write/discard I/O, and available CPU/memory/I/O
pressure outcomes are accumulated with saturating arithmetic in factory-owned state even when
aggregate ceilings are disabled. PSI `some` and `full` remain separate, and per-resource availability
counts distinguish absent support from an observed zero. Statistics failure adds one incomplete-
outcome counter and no partial totals without blocking proved-empty removal; unproved teardown
contributes no completed outcome.

rev0036 extends the same pinned-descriptor outcome boundary to independently optional `pids.peak`,
`memory.peak`, and `memory.swap.peak`. Every available peak must begin at zero in the fresh leaf and is
read after quiescence as an optional exact lifetime high-water mark. `cpu.stat` is now attempted for
every session, not only quota-limited sessions. Its mandatory usage/user/system work tuple and optional
all-or-none bandwidth and burst tuples retain controller-disabled and older-kernel compatibility while
rejecting partial evidence.

rev0037 extends that boundary to protected `memory.stat`, `memory.swap.events`,
`cgroup.stat.local`, and `irq.pressure`. Memory and swap policy make their corresponding accounting
interfaces mandatory; newer local-freeze and IRQ-PSI support remains independently optional. The
bounded parsers require the fault tuple, complete optional reclaim and swap-work tuples, all documented
swap-event fields, `frozen_usec`, and the current kernel's IRQ `full` class. Every retained counter must
begin at zero. The same pinned descriptors are read after recursive quiescence and before exact leaf
removal, and any failure makes the whole session outcome incomplete rather than publishing a partial
cross-controller record.


Snapshots retain policy generation, dimensions, close reason, I/O/signal counters, exact exit, and
typed failure. A fake backend covers deterministic race/error behavior; a separate test-only ELF
covers real PTY bytes and process state.

Runtime status exposes whether Ratox is enabled and configuration-valid plus bounded session,
process, replay, outbound, and event counters. rev0030 adds aggregate host/profile/preflight policy
counts. rev0032 exposes configured aggregate dimensions and maxima, the CPU accounting period,
current and peak active reservations, current and peak reserved process/memory/swap/normalized-CPU
totals, and saturating capacity-rejection and stranded-reservation counts. rev0033 adds cumulative
complete/incomplete session outcomes, PID-limit hits, memory high/max/OOM outcomes, CPU usage, and CPU
throttling. rev0034 adds cumulative read/write/discard bytes and operation totals from `io.stat`.
rev0035 adds cumulative CPU, memory, and I/O `some`/`full` PSI microseconds plus explicit observed-
interface counts. rev0036 adds peak-interface observed-session counts, saturation-safe sums and
maxima, CPU work/bandwidth/burst capability counts, and exact usage/user/system/throttle/burst totals.
rev0037 adds capability-aware page-fault, major-fault, scan, reclaim, swap-page, swap-event,
freeze-microsecond, and IRQ-full-microsecond totals. rev0038 adds pressure-policy configuration, exact
thresholds/hysteresis, latch state, saturation-safe check/admit/reject/sampling-failure/transition
counts, last-sample validity and typed local error class, and presence plus values for the last valid
configured `avg10` observations. rev0039 adds trigger configuration, monitor health, active/remaining
hold, typed monitor error, total/per-resource trigger counts, monitor-failure count, and trigger-caused
close transitions. These fields
remain unlabeled and content free; completed-session outcome PSI still retains only cumulative totals,
and neither surface stores memory addresses, interrupt sources, or per-session resource histories.
`ratox-events` is a private rotating lifecycle journal; it deliberately excludes terminal input/output,
argv, environment, cwd, profile identifiers, payload identities, paths, commands, and error strings.

This is a test-gated remote PTY service with named process-hygiene and kernel-confinement controls,
not production activation or complete confinement. Baseline seccomp is a deny floor rather than a
complete allowlist. Strict Landlock confines handled mutation/network/IPC rights but deliberately does
not restrict filesystem read or execute access. The optional cgroup path owns lifecycle and, when
explicitly configured, process/memory/swap/CPU ceilings plus one exact-device BPS/IOPS envelope inside
one valid delegated subtree. The host-local ledger additionally rejects configured process/memory/swap
and exact average-CPU aggregate overcommit inside one legitimate daemon incarnation. It does not create
a cgroup namespace, reserve aggregate I/O bandwidth, control storage latency or queue depth,
retain continuous PSI histories or resource peaks, select or adapt pressure thresholds,
make cross-resource samples atomic, preempt existing sessions from pressure, adapt policy from peaks,
`memory.high`, or I/O outcomes, synchronize CPU periods, enforce a parent CPU
ceiling, reserve physical resources, or defend against root or another same-UID writer
violating the single-writer contract. There are no created PID/user/mount/network namespaces, mount
isolation, or container/VM boundary. There is no PTY survival across daemon
restart, two-host complete-service qualification, target-fleet cgroup qualification, or final R8
production activation. The explicit runtime gate is intended for controlled construction and
evidence; normal configurations continue to advertise no Ratox feature.

### Private controller stream and local terminal plane

rev0019 added a second, independently gated role rather than overloading administrative
`control.sock` RPC or the host PTY coordinator. rev0020 bounded its first-OPEN lifecycle; rev0027
removes contender-induced fixed waits and adds bounded multiplexed admission:

```text
local iotox terminal process
    -> absolute owner-private <runtime>/terminal.sock
    -> canonical bounded ITTS/1.0 SOCK_SEQPACKET messages
    -> Agent-local exact peer/epoch/principal route resolution
    -> pure RatoxClient state and immutable outbound packet queue
    -> existing paced 0xA2 transport admission
    -> remote R4 host authority/profile/PTY boundary
```

`--enable-ratox-terminal-client` constructs the pure controller before transport startup but publishes
the local socket only after the normal private runtime is ready. It needs no profile registry or PTY
factory and creates no process. Host and controller roles can be enabled separately or together.

The pathname socket is Linux `AF_UNIX` `SOCK_SEQPACKET`, mode 0600 in a real owner-private parent.
Connection-time `SO_PEERCRED` is only the first identity witness. Every request and response also
requires one kernel-generated `SCM_CREDENTIALS` record and exact PID/UID/GID agreement; kernels that
support `SO_PASSPIDFD` additionally deliver and require the sender's `SCM_PIDFD`. A fixed ancillary
ceiling, `MSG_CMSG_CLOEXEC`, truncation/duplicate/malformed rejection, and exhaustive closure of
received `SCM_RIGHTS` descriptors make descriptor injection fail closed. Both clients verify server
records too, so fork inheritance of an accepted socket cannot transfer the accepting process's
identity.

The terminal listener binds the first valid record to its sender process and retains that process by
pidfd. Exit releases the controller slot even if another process still holds the file description.
The server otherwise uses nonblocking close-on-exec descriptors, one active controller, bounded
contender admission, first-OPEN enforcement, an `eventfd` wake, exact stale-inode reclamation, and
unlink ownership tied to the bound device/inode. The client rejects relative or embedded-NUL paths
and rechecks owner, mode, type, device, and inode after connection so pathname replacement cannot
silently retarget the stream.

On Linux 6.5+ with suitable headers, the accepted active connection is additionally pinned with
`SO_PEERPIDFD` before the first record. Connector exit therefore releases a silent pre-`OPEN` slot even
when another process retains the connected file description. The administrative server retains the
same exact connection-process handle for each bounded pending client, and the administrative client
polls a server connection pidfd beside response readiness. Socket readability has precedence over a
simultaneous pidfd exit so a complete record queued immediately before exit remains valid. Unsupported
kernels keep the finite lease and mandatory per-record credential path.

The first complete `OPEN` has a configurable 1 ms..60 s steady-clock lease (5 s default). A silent
accepted controller therefore times out before publication and does not trigger attachment cleanup.
While one controller is active, the listener, active stream, owner pidfd, wake descriptor, and a
bounded contender set are polled together. Contenders receive independent 20 ms leases by default,
with global and per-process pending quotas, a finite accept-refill budget and interval, and a finite
ready-record budget per cycle. Active controller work is serviced before contender work. A complete
already-queued contender packet may be authenticated and decoded only to preserve its stream ID; it
is never dispatched and the reply is nonblocking best effort. A pre-OPEN `ERROR` is connection-
scoped; every success/progress packet remains exact-stream-bound.

After local `DETACH` commits, the socket enters a 1 ms..5 s ACK-only drain (250 ms default). Final
`OUTPUT` and `DETACHED` records are sent while only cumulative `OUTPUT_ACK` may arrive; no other
post-detach operation can reach the controller state machine. Every packet-send wait consumes the
same absolute deadline. Only during this drain is the listener omitted from polling, so successors
wait in the kernel backlog and the server cannot spin on a readable listener or deny against a stream
that is already closing. Outside the drain, an active descriptor terminal event without readable data
releases the old controller before any same-cycle contender can be rejected.

A separate CTest crosses the actual CLI/process boundary: one controller wins, the loser receives the
busy reason, abrupt winner death detaches locally, a replacement resumes retained and final detach
output, commits the exact cumulative ACK only after rendering, and an empty restarted server returns
explicit `not_found`. The repaired gate also survives repeated real-CLI execution. This is one-host
local controller evidence, not complete remote R6 qualification or PTY survival across Agent restart.

Local protocol v1 freezes a 32-byte `ITTS` header, 16 KiB payload bound, one nonzero stream ID, strict
directions, cumulative byte positions, typed status, and canonical structured OPENED/GAP/EXIT fields.
The local link is reliable and message preserving; impossible duplicate or out-of-order local state
fails closed rather than inheriting Ratox network replay tolerance.

`RatoxClient` owns no toxcore, socket, terminal, authority store, or clock. It binds every operation to
the exact friend, online epoch, authenticated principal, session, nonce, incarnation, generation, and
message IDs; retains immutable packets until accepted; separately bounds unacknowledged input, output,
outbound packets/bytes, and events; validates output overlap byte-for-byte; coalesces cumulative ACK
and latest resize; and preserves only safely resumable state after route loss.

One exact PING identity is reused for the current attachment. Repeated samples therefore cross the
current remote Ratox route and exact-result replay service without allocating an unbounded series of
never-evicted host control records. The installed client samples once per second and, after three
missed deadlines, warns while retaining the session. Only authoritative lifecycle or an explicit
operation changes attachment state (ADR 0193).

ADR 0197 qualifies that authoritative boundary in two guests. Complete bilateral path loss first
misses the heartbeat while the route remains confirmed; c-toxcore peer-offline then returns typed
`unavailable` to the controller and detaches the exact host route without replacing its live PTY.
After the same peer reauthenticates on a higher online epoch, explicit resume must preserve session,
principal, process incarnation, and byte positions while advancing only attachment generation.
Automatic route migration is outside the current architecture.

The one installed executable implements `terminal` and `terminal-resume`, restores terminal modes and
signal handlers, propagates resize, writes output before ACK, detaches on stdin EOF, and handles local
beginning-of-line escapes. The remaining boundary is intentionally narrow: one local stream, no state
survival across Agent restart, no automatic route migration, and no production-default activation.

## 8. Durable command engine

### 8.1 Identity

A durable wire command is identified by:

```text
sender Tox public key
persistent nonzero sender epoch
sender-chosen nonzero message id
```

Direction is part of the local journal locator. Friend number and one online epoch are excluded
because they are process/session implementation details.

### 8.2 Store-before-observe order

Outgoing:

```text
freeze canonical request
commit request to signed store
commit send attempt
ask toxcore to enqueue exact bytes
commit remote receipt
commit terminal result
recover unfinished request on restart/reconnect
```

Incoming:

```text
validate canonical request and durable key
commit request and exact RECEIVED receipt
send receipt
commit authority admission and ledger head
commit STARTED
execute operation
commit exact terminal result
send result
replay frozen evidence for exact duplicates
```

This order gives each externally visible promise a preceding durable fact. `RECEIVED` is not
`STARTED`; toxcore enqueue is not remote receipt; terminal result is not inferred from connection
state.

### 8.3 Store format and policy

The v3 store is a private regular file signed by the stable device identity. It has a bounded
header, bounded records, exact canonical request/receipt/result frames, deterministic ordering,
strict transition validation, a signed clock high-water mark, and verified atomic v2 migration.

Default limits:

```text
records: 1,024
file:    8 MiB
unfinished total: 256
unfinished per peer/direction: 32
canonical bytes per peer/direction: 256 KiB
```

Only oldest fully delivered terminal records may be pruned. An incoming terminal record whose
receipt or result has not entered the local Tox queue remains unfinished. If the store has no
prunable record, new admission fails.

Current lifecycle:

```text
outgoing: reserved -> locally-queued -> succeeded|failed|expired|timed-out-unconfirmed
          reserved -> cancelled
incoming: received -> admitted -> started -> succeeded|failed|expired
```

Request, receipt, and result have independent persisted attempt/error/next-attempt schedules.
Delivery state for receipt and result advances independently:

```text
none -> pending -> send-failed|queued|terminal-failure|observed
```

Exact transition rules are stricter than this shorthand and live in `command_store.cpp` tests.
Terminal lifecycle and frozen bytes cannot be rewritten. Scheduling is priority-first with bounded
exponential backoff, stable jitter, and a steady process clock anchored to signed high-water state
on restart. Expiring work requires explicit non-rollback wall-clock trust; non-expiring work does
not.

### 8.4 Known storage limits

The store is signed, not encrypted. It does not hide peer keys, timing, operations, or payloads
from local readers. A local attacker able to replace files can restore an older valid signed
snapshot because there is no external monotonic anchor.

Every mutation rewrites and fsyncs the complete bounded snapshot. This is a correctness-first
baseline. An append/checkpoint design may later reduce flash wear and write amplification, but it
must preserve the same crash, duplicate, and exact-byte semantics.

### 8.5 Operation executor

After canonical parsing, authority admission, and durable `STARTED` commit, the coordinator calls a
transport- and storage-blind executor:

```text
CommandRequest + immutable CommandExecutionContext
                    -> CommandResultPayload
```

`device.describe` is the first executor. It reads only revision/version, negotiated protocol,
stable device principal, feature mask, and offered-operation mask. It cannot call toxcore or mutate
the command store. The coordinator still owns exact result encoding, terminal commit, delivery,
retry, and projection.

Future mutable operations may need hardware effect adapters, but those adapters remain separate
from transport and journal mechanics and require explicit restart/idempotency policy before
registration.

## 9. Local surface

### Structured authority

Unix `SOCK_SEQPACKET` carries bounded, versioned, correlated request/response records. This is the
authoritative local mutation surface. The administrative server shares the same bidirectional
per-record credential/pidfd parser as `terminal.sock` and rejects ancillary capabilities. It polls a
bounded set of pending clients, each with an independent complete-request lease, and services ready
records before expiring silent peers. Global and per-process pending quotas, a finite accept-refill
budget and interval, and a finite ready-request budget per cycle prevent one silent lease from
serializing unrelated callers. Overload responses are nonblocking best effort. The server preserves a
reachable owned listener and removes only its exact bound socket inode. These bounds do not provide
authorization between same-UID processes, preempt a blocking handler callback, or prove starvation
freedom against an unlimited same-UID process coalition.

It provides:

```text
explicit operation code
request ID
bounded payload
structured error code
one complete response packet
same-user peer credential checks
```

### Ratox pre-network restart fence

An enabled host now reserves one signed device-bound incarnation before toxcore or `terminal.sock`
starts. The default ledger is `<savedata-parent>/ratox/incarnation.state` in a dedicated owner-only
directory. Component-wise no-follow opens, a lifetime `flock`, fixed-record signature verification,
descriptor-relative temporary write/`renameat`, file and directory `fsync`, and strict committed
re-read form one fail-closed startup transaction. Newly created hierarchy components are fsynced after
mode enforcement and their containing directories are fsynced before descendants are trusted. The
enabled service API defaults to the invalid zero sentinel, so a direct caller cannot silently reuse a
fixed incarnation; the Agent injects the reserved lease value into every successful OPEN. Runtime
status exposes only content-free lease facts. Client-only activation creates no lease.

Authenticated route identity is stored separately from exact-head terminal authority. The former may
route one explicit denied ATTACH/RESUME after revocation; it cannot admit a PTY effect. R6 exercises
this boundary through the actual Agent, local stream, mock transport, and real PTY helper. Agent
restart intentionally reaps the process and loses controller state; the next host advances the
incarnation and old-session resume returns `not found`.

## Ratox-style projection

The private runtime tree exposes inspectable files and journals for humans and small programs. It
projects, but does not define, state.

```text
status
Tox address/profile
stable device public key
authority summary and principals
transport peers and incoming requests
session and directional authority state
signed command summary and per-record views
bound peer device descriptions
message/protocol journals
file offers/transfers
Ratox lifecycle counters and content-free events
events
```

rev0015 introduced the complete transport-friend lifecycle through hardened private files; rev0019
added a separate owner-private `terminal.sock`, and rev0020 bounds that socket's first-OPEN and
contention behavior while preserving Ratox status plus a content-free `ratox-events` journal. Terminal bytes are not projected through runtime files
or FIFOs, and finite administrative `control.sock` RPC still has no terminal-stream operation. The
root/public-key-first surface is:

```text
friendship.help                         exact lifecycle contract
request                                 mode-0600 FIFO: complete address + TAB + message
request.help                            exact bytes, bounds, evidence, and authority warning
friend-events                           bounded local lifecycle evidence
requests/<public-key>/accept            mode-0600 FIFO: exact `accept` token
requests/<public-key>/reject            mode-0600 FIFO: exact `reject` token
peers/<public-key>/remove               mode-0600 FIFO: exact `remove` token
```

The root request record carries 76 hexadecimal complete-address characters, one literal TAB, and a
1..921-byte message. The parser preserves every non-LF message byte, requires the 999-byte maximum
including LF to fit the opened FIFO's actual `PIPE_BUF`, and converges on the same typed Agent method
as `transport-peer-request`. Address checksum, own-key, duplicate, and nospam semantics remain with
c-toxcore. Local `tox_friend_add` admission is not remote receipt or acceptance.

Incoming accept requires the same public key to remain in the live callback inbox. Reject withdraws
only that live IoTox record because c-toxcore exposes no pending-request object. Established removal
resolves the public key and deletes the resulting friend number in one serialized toxcore
owner-thread operation. This prevents a delayed mutation from landing on a later peer that inherited
a reused numeric gap. Every friendship operation leaves the independent signed authorization ledger
unchanged.

Established peers project six additional literal write lanes:

```text
peers/<public-key>/command          mode-0600 FIFO: printable durable operation
peers/<public-key>/message          mode-0600 FIFO: normal Tox text ingress
peers/<public-key>/action           mode-0600 FIFO: Tox action-text ingress
peers/<public-key>/file-send        mode-0600 FIFO: absolute finite source path
peers/<public-key>/file-receive     mode-0600 FIFO: file number + TAB + destination
peers/<public-key>/file-control     mode-0600 FIFO: file number + TAB + control
peers/<public-key>/command-events   bounded durable-admission ingress evidence
peers/<public-key>/message-events   bounded live-text ingress evidence
peers/<public-key>/messages         bounded text transport lifecycle journal
peers/<public-key>/file-events      bounded file ingress and callback journal
peers/<public-key>/files/...        atomic disposable live transfer projection
```

The lanes converge only at typed Agent operations and the toxcore owner thread; their meanings
remain separate. `command` enters the signed durable engine. `message` and `action` enter
c-toxcore's live text queue without durable spooling or machine authority. `file-send`,
`file-receive`, and `file-control` name one finite local file operation and enter the existing typed
`FileTransferManager`; FIFO bytes are never the file payload. Friendship FIFOs enter lifecycle
methods, never the command executor or authority ledger.

A complete record plus LF must fit the configured lane bound and the opened FIFO's actual
`_PC_PIPE_BUF`. Destructive lifecycle lanes accept one exact lowercase word only; they do not trim,
case-fold, or infer intent. Human text preserves every non-LF byte locally while valid UTF-8 remains
the Tox interoperability contract. File paths are absolute local operator choices, never
remote-selected or shell-evaluated. The `file-control` grammar admits one literal TAB before
`pause|resume|cancel` and otherwise fails closed.

Evidence is layered. `friend-events` records request arrival, outgoing request disposition, local
accept/reject/remove decisions, and observed add/remove events. `message-events` records local
framing and exact typed send disposition; `messages` records outgoing acceptance, incoming text, and
read receipt. `file-events` records local path/control admission and toxcore file callbacks.
`files/incoming` and `files/outgoing` are current in-memory projections. None of these journals or
projections is durable authority or completion truth. Incoming destination publication is the
finite receive completion boundary.

The ordinary receiver owns a hidden no-clobber temporary and deletes it on failure. ADR 0223 adds a
separate upper-protocol-only entrance for an existing private partial: its opened inode must match
the inspected absolute path, be single-link, owner-owned, mode `0600`, and exactly the requested
nonzero offset. c-toxcore seeks before resume; loss preserves the caller-owned prefix; completion
revalidates path identity and fsyncs in place. This is transport progress only. The caller must hash
the complete immutable object before publication. ADR 0224 uses this only for whole-object sync:
available-policy auxiliary loss fences the old scheduler attempt, a fresh attempt/FileId/carrier
inherits the exact private prefix with no-replace rename, and commit still requires the full digest.
Fail-closed and range attempts discard. Restart recovery cleans inactive burned-ID staging but does
not continue its bytes.

All paths use daemon ownership, private modes, no-follow opens, opened-versus-inspected inode
checks, bounded rescans, distinct structural/lane error keys, and expiration of abandoned partial
records. One generalized monitor supports both canonical public-key directories and required
process-wide root lanes. Startup and live readiness require every promised root lane; removing or
substituting `request` cannot leave status falsely green. FIFO services own no authorization policy
and never call toxcore directly. Additional compatibility must preserve these rules and must not
collapse friendship, human text, machine command, and bulk file semantics.

### Runtime publication semantics

Runtime files are disposable projections. Individual values are published through private
temporary regular files and atomic rename so readers do not observe torn contents. Transactional
records publish their marker last. These writes intentionally do not `fsync`: the entire runtime
tree may disappear on reboot and is reconstructed from signed stores and live transport state.

Append journals such as `events`, `friend-events`, `messages`, `message-events`,
`file-events`, `ratox-events`, protocol records, and `command-events` are bounded and rotating. They are operator evidence, not durable audit authority.

## 10. R7 observability and evidence flow

The transport owner records command admission-to-execution waits in one fixed-allocation histogram per
traffic class. Runtime reads occur under the command mutex, so queue totals and percentile projections
belong to one coherent state. Sensitive custom-lossless outcomes use a separate coherent mutex because
the call boundary begins outside the owner thread and classification ends inside it.

The Agent records controller and host retained-send pressure independently. These gauges describe the
current immutable head and its steady-clock age; lifetime totals and maximum streaks survive a clear.
Ratox lifecycle events use service-relative steady microseconds. The runtime tree is a projection only:
it does not feed authority or scheduling decisions and contains no terminal payload.

The external R7 evidence chain is deliberately outside the live Agent. The constructor rebuilds a
balanced deterministic schedule, joins raw same-clock timestamps to exact content-free Ratox event and
byte-span coordinates, and binds canonical schedule/sample digests plus the exact route and bulk
observation files. Controller and host use distinct ephemeral Ed25519 keys to sign role-separated
payloads containing the same complete unsigned run; signing also checks the role's local Linux boot
ID and secret/public-key consistency.

The analyzer re-verifies both signatures, reconstructs every trial, requires the bound auxiliary files,
derives only same-clock durations, validates global event/timestamp/span invariants, and emits
deterministic reports. The signatures are capture agreement, not stable device authority or hardware
remote attestation. A report cannot grant runtime authority or cause a device effect.

### Authenticated content-free flight recorder

ADR 0291 adds a different evidence path for ordinary support. After stable identity and the Agent
incarnation lock exist, startup opens one bounded canonical recorder and verifies the entire existing
state against that exact device key. Each sparse state transition copies only closed phase/network/
feature fields, one `ErrorCode`, a structural redacted-config commitment, and ten coarse counters.
The resulting 128-byte records form a contiguous tail; the header binds mutation, high sequence,
eviction count, configured 16..256 bound, and retained count. A domain-separated digest and stable-
device signature authenticate the complete store. StateStore replacement supplies crash atomicity.

The runtime writers cover secure initialization, running/stopping/failure, self-transport changes,
authority mutation, Ratox lifecycle, and projection failure. High-rate payload/progress is never an
event source. The Agent incarnation lock is the single-writer boundary. Startup's first write is
fail-closed; later write failures are counted but do not take down the control plane.

Local-control v1.49 operation 108 asks the Agent for a canonical redacted projection. The Agent does
not expose the signed bytes, device key, signature, path, or timestamp. The CLI validates the closed
projection, wraps it with version/revision and a digest, validates it again, and creates one private
no-clobber file. Offline inspection validates shape and integrity only. Because the bundle omits its
device identity, it is not authenticatable by its recipient and cannot be remote attestation. See
`diagnostics.md` for the exact exclusion and correlation contract.

### Explicit peer introduction

ADR 0293 keeps introduction above the existing transport lifecycle. The live Agent is the only
creator: it takes a bounded lifetime, closed requested-capability bitset, and optional canonical
alias, then signs its exact current 38-byte Tox address with the already loaded stable device key.
The fixed body also binds issue/expiry times and a fresh random nonce. The client independently
verifies before one private no-clobber write.

Inspection proves only self-signature. Dry import and acceptance both require the same independently
pinned stable inviter key; import mutates no state. Acceptance first reuses or requests the exact
transport key, then optionally calls the same one-to-one alias mutation. These are retry-idempotent
effects but not one rollback transaction: a failed alias after successful friendship is reported as
partial and exact retry completes it. The artifact's requested capabilities never enter the ledger.
See `peer-invitations.md`.

### Forward-only synchronization time machine

ADR 0294 layers owner-local recovery over tree-v2's existing immutable history. Enumeration reloads
and verifies live record/manifest pairs rather than trusting directory names. Diff retains exact
candidate/provenance changes while reporting the ordinary projected-content distinction. Current and
historical conflict inspection renders byte-safe path identities and no content.

Planning holds the namespace transaction but writes nothing. Its domain-separated digest binds the
canonical namespace policy, signed maintenance record or established absence, exact current frontier
and merged manifest, signed stable workspace record, clean worktree scan, target record/manifest,
and required object identities and sizes. Apply recomputes that commitment and requires equality
before its first effect.

The effect is an ordinary new local branch: target paths and current-only tombstones are re-originated
at the next generation, the current local record remains `previous`, and every other current branch
is observed. Branch truth commits before the existing workspace exchange journal projects it. A
post-commit projection error names the durable forward record for normal reconciliation. The
historical record never becomes a current pointer. `sync-restore` remains the unrelated inverse of
GC quarantine. See `sync-time-machine.md`.

### Sparse tree-v2 custody

ADR 0295 reuses the recipient-local projection prefixes as a content-custody boundary. The graph
receiver authenticates every branch and manifest but schedules only file digests needed by selected
paths. This preserves global causal/conflict knowledge while making local byte custody explicit.
Tree pull snapshots, repair, and GC distinguish complete from partial and account declared,
selected, and skipped objects.

The private worktree marker now commits the merged manifest plus metadata/include/exclude policy.
After a policy mutation, its mismatch instructs the first scan to preserve absent baseline values;
present newly selected files remain local events. The post-transfer reconcile then uses the existing
immutable-first branch commit and signed workspace exchange to install the new projection marker.
There is no pre-inventory reconcile that could author a false tombstone. A sparse publisher may lack
bytes named by its complete metadata, and the ordinary exact object result reports that fact. A
ADR 0296 uses the existing authenticated exact object-result disposition as that layer: one primary
frontier is frozen, then complementary authorized primary-lane sources are tried in bounded order.
They gain neither branch nor destination authority. This is serial correctness and recovery, not
tree-v2 striping or auxiliary-route acceleration.

ADRs 0329--0331 pipeline a bounded window of exact tree-v2 object requests and remove local
whole-store hashing amplification without changing the wire protocol. Completed file lanes share
one CAS commit batch. The first file-bearing batch creates a strict pull-private object inventory;
later batches verify their exact inputs and update that view. Immediately before branch acceptance
and projection, the subscriber rebuilds the complete strict inventory under the same namespace
transaction. It requires every cached member to survive unchanged, admits only verified additive
objects from other serialized jobs, and re-applies the complete store quota. Thus cached accounting
can improve construction cost but can never authorize a visible effect by itself.

ADR 0297 aggregates the local side of that model without changing the peer protocol. A fixed
stable-device-signed record commits only policy/namespace digests, closed flags, and counters for
selected custody, frontier/workspace convergence, conflicts, cutoffs, automation, pressure, and
last source evidence. The health level is derived during canonical encoding. Sparse selected
custody can be green; structural corruption is an error; every rendered record denies both a
rollback witness and backup certification.

ADR 0298 joins that truth to support diagnostics without exporting the records. Under the namespace
mutation lock, the Agent verifies each eligible cached tree-v2 record and reduces the set to anonymous
health, custody, repair, pressure, automation, and source totals. No namespace or policy commitment
survives the reduction. Redacted diagnostics v2 keeps the existing byte ceilings and no-attestation
boundary; legacy v1 payloads remain inspectable.

ADR 0299 extracts the administrator's live host-capability sampler into one reusable local snapshot.
The multithreaded Agent deliberately selects its passive/no-fork mode, then reduces the result to
closed grades, masks, and counts for diagnostics v3. This preserves the explicit command's stronger
live-child evidence without forking the running control daemon or copying cgroup paths and raw kernel
text into a support artifact.

## 11. Concurrency

One thread owns each `Tox*`. Other components submit bounded command objects and consume bounded
events.

Current invariants:

```text
no concurrent toxcore calls
pre-start timeout can cancel only work that has not begun
required semantic events apply backpressure
observational event loss is counted
file callbacks pace at explicit high/low watermarks before consuming semantic reserve
transport and application state persist independently
command-store mutations are serialized
peer FIFO per-lane statistics exist from construction and are zero before start
peer FIFO maps are owned only by their worker after startup
```

A local timeout does not imply cancellation. Future physical operations require explicit durable
cancellation and indeterminate-state semantics.

## 12. Persistence

### Tox savedata

Private atomic file replacement with file and directory synchronization. It remains a Tox route
identity, not the stable IoTox application identity. Default primary savedata is route-scoped:
`device.toxsave` for native, `device.tox-tor.toxsave` for Tor, and a reserved
`device.tox-i2p.toxsave` for I2P. Explicit path overrides are compatibility/linkability choices;
they do not merge those transport identities into the stable device principal.

### Device identity

Exactly 80 bytes, private regular file, seed plus re-derived public key. Missing identity plus an
existing ledger/store fails closed.

### Peer aliases

The alias registry is a separate stable-device-signed local projection from canonical human names to
exact Tox public keys. It is neither friendship nor the authority ledger. Canonical lexical ordering,
unique names, unique keys, a 256-entry bound, and one generation make each changed state exact.
Startup verifies the expected device signature and private stable file before control admission.

Resolution is client-visible syntax but Agent-authoritative mapping. The shared parser distinguishes
explicit friend number, Tox key, and alias forms; alias resolution crosses same-user local control.
Set then rechecks current friend inventory at the Agent mutation boundary. Removing a friend leaves
the durable mapping intact, so only explicit alias removal can release a human name for reuse.

### Authority ledger

Private bounded file, strict format-specific header/record sizes, deterministic signed replay,
explicit non-widening v1-to-v2 migration, and atomic complete-history replacement. A separate private
committed/pending head guard detects unrelated local rollback and reconciles only exact interrupted
replacement states. Logical append-only history; not append-in-place.

### Durable command store

Private bounded signed v3 snapshot with persistent sender epoch, exact canonical artifacts,
independent schedules, priority/quota/clock state, strict monotonic transitions, verified v2
migration, atomic replacement, and runtime projection.

### Synchronization publication state

One fixed 296-byte signed HEAD names the namespace, stable device writer, engine, exact linked
generation, immutable artifact/manifest identities and sizes, and Ed25519 signature. Signature and
complete-record identities use separate IoTox hash domains. The private local publisher store accepts
only canonical mode-0600, owner-owned, single-link, no-follow records, serializes live publication,
and treats an exact retry as a duplicate. It is constructed by the explicit default-off Agent sync
gate; it still has no external rollback witness.

The local revision publication job commits the artifact and manifest as separate digest-named
immutable objects before invoking that HEAD store. Each bounded copy uses private staging and
no-clobber publication, then verifies the final object's exact size and digest. Existing objects must
be private owner-owned single-link regular files. Cancellation or failure can leave reusable
unreferenced objects, but cannot advance the signed HEAD.

Artifact and manifest identities use the preserved toxsync SHA-256 contract. The production IoTox
hasher reads an `O_NOFOLLOW` descriptor in bounded chunks and rejects any inode, size, timestamp,
mode, ownership, link-count, or observed-byte change across the read. Signed HEAD record identities
and other IoTox metadata retain their separate domain-separated BLAKE2b-256 contracts.

The default-off publisher protocol boundary resolves namespace policy locally and requires an exact
current authority-ledger v3 proof, `sync.subscribe`, and subscriber membership before revealing a
HEAD or deriving an object path. ADR 0282 makes request replay a bounded FIFO exact-replay window:
retained duplicates return exactly without another offer, while a retired immutable read is
re-authorized against current session, authority, HEAD, and object truth before it may run again.
The response is retained before an exact-FileId offer and fenced by the authority head and remote
principal used for admission. The matching subscriber requires exact current v3 `sync.publish` authority and writer
membership before evaluating the signed HEAD. Under the explicit `--enable-sync` gate, Agent strictly
loads every namespace and attempt store, constructs both roles, and only then advertises the feature.
Blocking verification and commit run on a bounded worker outside the owner callback; each effect
reconstructs current session and authority context. Both exact immutable objects commit before the
accepted HEAD, and acceptance never activates content.

ADR 0141 extends that boundary to indirect waits. The sole toxcore event pump never waits for a
publisher statistics snapshot, periodic best-effort Ratox service, or a synchronization file hook
that has no effect for the current event. `sync-status` exposes `publisher-busy=1` when its exact
publisher snapshot is unavailable while still reporting independent queue and subscriber state.
Ratox maintenance uses a nonblocking authority-effect attempt, and unrelated events leave the sync
file hook before authority serialization. The worker queue remains hard, bounded, non-evicting, and
observable: overload is refused and an exact retained request may retry only after capacity returns.

### Synchronization automation state

ADR 0270 adds an owner-local scheduler without adding a peer protocol. One fixed-size `IOTXSAU1`
record per namespace is signed by the stable device and binds its local generation, publish/follow/
disabled mode, timing bounds, and either a canonical source path or a proven remote stable principal.
The store is a strict private sibling of `namespaces/`; managed namespace state lives beneath the
separate private `data/` child, and the namespace root grammar admits exactly these known entries.
Automation performs its own fixed-record verification. Disabled records
remain as higher-generation tombstones. Active automation blocks namespace update/removal until the
owner disables it.

The Agent service loop performs only scheduler claims. Every scan, publication, principal/session
resolution, pull request, accepted/active-state read, and activation runs on the existing bounded sync
worker. Runtime state preserves one periodic and one activation in-flight bit per namespace,
saturating counters, bounded exponential retry, and the policy generation used by each claimed
action. Replacement discards old runtime; late completion becomes a no-op. Exact reload preserves
runtime within one process, while daemon restart deliberately schedules a fresh reconciliation.

Automatic effects re-enter the ordinary local controls. Publication therefore retains immutable
objects-before-HEAD ordering and duplicate semantics. Pull again proves current v3 authority,
capability, namespace writer membership, and feature negotiation for a currently ready session that
matches the stored principal. Verified activation reads the device-authenticated accepted HEAD on the
worker and passes its exact record digest through the existing activation transaction. Arrival,
friendship, stored policy, and scheduler timing are never activation authority by themselves.
If a periodic retry finds an active pull whose control replies are complete while its admitted file
receive is still running, the local control reports `sync-request-pending ... frames=0` as healthy
success. Treating that state as failure would exponentially delay the next HEAD behind ordinary bulk
latency; genuine control/authority/session/transport failures still use bounded backoff.

ADR 0271 adds local-control v1.45's ordinary owner entrance without changing peer framing.
`sync-create` descriptor-prepares `<sync-policy-root>/data/<namespace>`, refuses source/state
containment in either direction, infers the existing content-v2 or treepack-v1 publisher from the
source type, installs a sole-local-writer/manual-activation policy, and enables automation. Existing
policy or automation bytes must be exact duplicates; the command is not an implicit edit or
migration surface.

Read-only sharing is a two-step local transaction around RecallRoot signing. Preparation resolves an
application-ready friend through its exact current v3 session to a stable device principal and emits
at most one owner grant body. The CLI validates and signs that body. Commit rechecks the same binding,
appends the grant if needed, and adds only subscriber membership. Authority and namespace membership
remain independent checks: if the grant becomes durable before membership can quiesce, the partial
state grants no namespace entrance and an exact retry completes it. The recipient's local root,
writer grant, follow mode, and activation policy remain recipient-local decisions.

### Tree-v2 multiwriter synchronization

ADR 0272 reserves engine 4. `IOTXTVM1` names directory, file, and tombstone
events by stable writer and branch generation; files name strict SHA-256 CAS objects. `IOTXTVB1`
keeps one exact signed predecessor chain per writer and a sorted vector of exact signed branch-record
observations. Immutable manifests and complete branch records commit before one writer-specific
current pointer. Observation records remain addressable history: a receiver must resolve the exact
signature and manifest before treating a carried foreign-origin value as authentic.

Merge is a causal set operation. A branch may dominate a candidate only after observing its exact
origin and replacing it. Omission by a branch that has not seen the candidate is inert. Equal
payloads coalesce; unequal concurrent candidates survive. The ordinary filesystem projection is
deterministic, while every alternate value or tombstone is retained under `.iotox-conflicts` with
writer/generation/kind provenance.

`IOTXTWS1` separates daemon knowledge from human-visible causality. Its signed active frontier is the
exact set of branch records represented by the current writable projection. A scan publishes against
that frontier even when newer remote records are already stored, so an offline local edit stays
concurrent. A following merge branch may observe the new frontier only while retaining every
candidate. Pending workspace state binds active, scanned, and target manifests plus the target
frontier before a same-parent `RENAME_EXCHANGE`; exact projection markers make restart orientation
recoverable and ambiguity fail closed.

ADR 0273 activates the bounded pairwise path. Negotiated feature bit 30 and lossless frame types
32--35 exchange a bounded writer frontier and exact branch-record, manifest, or file-object requests.
The receiver recursively closes predecessor and observation proofs, commits verified CAS before
branch metadata, advances writer pointers only in dependency order, and reconciles the writable
workspace last. Requests and file offers remain bound to the exact friend, online epoch, primary
route, FileId, authority head, stable principal, and capability set. One malformed edge, changed
authority context, same-writer fork, or over-quota graph fails the job closed and cleans its lane.

`sync-create ... read-write` installs the local writer and a signed `writable` automation record.
The owner on each device then runs `sync-share ... read-write`; its two-phase RecallRoot transaction
adds the exact proven peer to writers/subscribers, grants `sync.publish|sync.subscribe`, and binds
`bidirectional` automation to that stable principal. Both local roots remain recipient-selected.
Each automatic pull reconciles local changes first, preserving visible-frontier causality across
offline reconnect. `sync-repair` revalidates the signed frontier and unique CAS closure.

The retained `sync-bidirectional` Sandwurm cell closes this first pairwise construction gate in two
simultaneous source-linked guests. Both daemons stop before unequal edits to the same path, then
restart and converge on one projection plus the same provenance-bearing conflict. A later ordinary
edit resolves the conflict causally; deletion and a zero-byte file converge before both peers pass
repair. No manual publish or pull occurs after the reciprocal setup ceremony.

ADR 0274 extends signed automation to a sorted set of remote stable principals, with one serialized
namespace lane and independent fair retry clocks. ADR 0275 then bounds history. A format-2 branch is
a negotiated conflict-free checkpoint and authenticated traversal floor. Current writer pointers,
explicit pins, and the signed workspace's active/pending manifests and frontiers are GC roots.
Candidates move only into private recoverable quarantine and are reauthenticated before restore;
there is no purge path. A device-signed terminal cutoff binds one writer to its exact last admitted
record, removes its current pointer and local automation source, and rejects later records while
retaining historical verification policy. Cutoff remains per-survivor owner policy, not distributed
membership or general authority revocation.

Reconciliation no longer signs a branch merely to acknowledge a remote frontier. A derived merged
manifest is retained for the signed workspace journal without claiming an authored event. Only a
visible local filesystem change advances the branch, and that edit uses the journaled frontier as
its causal observations. This makes quiet full-mesh convergence quiescent while preserving offline
edit causality.

ADR 0278 adds a recipient-local projection layer without changing causal graph exchange. Canonical
namespace-policy v2 include/exclude component-prefixes decide which paths a local scan may author and
which manifest paths materialization may replace; exclude wins. Unselected entries already present
in the signed baseline remain in the next manifest, and unselected local filesystem entries are
copied into staging before the atomic exchange. Hiding a path therefore neither authors a tombstone
nor deletes the owner's local-only bytes. Manifest v2 carries exact regular-file owner `r/w/x` bits
for private readable modes; v1 executable-only entries canonically map to `0600`/`0700`. Selection
now also bounds content-object custody under ADR 0295 while retaining complete authenticated branch
and manifest transfer.

The initial transport is one exact object at a time on primary Tox lanes. Tree-v2 complementary
sources use exact authenticated absence probing; range/auxiliary/parallel transfer, metadata beyond private file owner mode,
and permanent purge remain absent rather than implicit properties of the format. ADRs 0280--0283
close the finite founding-machine adversarial/scale and two-hour incumbent-shadow qualifications;
they do not add physical power-cut, dishonest-storage, or independent-machine claims.

ADR 0332 adds one explicitly narrow crash claim. A two-epoch Sandwurm coordinator binds the exact
task-owned writable root disk to one Cloud Hypervisor PID/start-time/argv identity, kills that VMM
after the guest observes raw signed workspace phase byte 2, and preseeds epoch two from the exact
crash disk. The recovery guest mounts three inner ext4 volumes after journal replay and classifies
projections before starting any Agent: the two completed writers remained completed and the
interrupted writer remained exact prior with pending byte 2. A second boot ID, persistent identities,
final three-branch repair, noncooperative first exit, cooperative second exit, and networkless launch
are proof-bound. The phase-reversed v1 predecessor is withdrawn and rejected. This does not
generalize one linearization into every cut or make virtual storage evidence for physical or
dishonest storage.

ADR 0333 makes the two workspace linearizations independently targetable. While the journal remains
raw pending byte 2, the observer compares the visible canonical projection marker against the active
and pending manifest identities embedded in that same workspace record, then rereads the record to
exclude a concurrent stable commit. Active means pre-exchange; pending means post-exchange. Recovery
must keep a post-exchange follower completed. This is a qualification observer only: no crashpoint,
pause, or new product protocol is introduced.

The accepted post-exchange run retained the strongest expected crash tuple: completed visible tree,
pending journal byte 2, marker naming pending, and the old active tree still present at the stage
path. Recovery validates and removes the old side before stabilizing. Combined with ADR 0332's
prior-visible pre-exchange run, both workspace directory-exchange linearizations are now qualified on
the same ext4/KVM construction stack.

ADR 0334 separates the earlier object pipeline from that workspace transaction. Partial authenticated
incoming bytes live under the generic manager's private
`.iotox-.receive-*.part.part-<six-base62>` temporary; only a complete fsynced transfer is
link-published as canonical `.receive-*.part`. Completed file windows then enter
the digest-verifying, quota-fenced importer; each new CAS object is copied and fsynced under the
expected fanout's `.install.tmp`, renamed with `RENAME_NOREPLACE`, and followed by a fanout-directory
fsync before it can support metadata effects. Receive unlink batches now end in one incoming
directory barrier, and startup removal of a recovered CAS temporary ends in its own fanout barrier.
The v4 VMM observer may stop the follower at either temporary before host power-cut simulation. A
temporary may disappear after remount, but a digest-named final object may be only absent or exact.
Source-linked receive and CAS-install cuts now pass this contract: the former recovered a surviving
zero-length generic temporary and the latter a complete canonical incoming file after its partial CAS
copy disappeared; ordinary startup removed all staging and converged the exact object in both cases.
ADR 0335 treats branch publication as a separate three-prefix transaction family. The successor
manifest and signed immutable record each cross an exact `.install.tmp` plus `RENAME_NOREPLACE` and
directory fsync; only then does `.update.tmp` replace the writer's mutable pointer. Proof v5 uses an
external exact-path-filtered syscall-entry delay to stop the real sync worker before each selected
rename without adding a product crash hook or delaying unrelated runtime projection renames. Offline
recovery must see respectively absent/absent/prior, exact/absent/prior, or
exact/exact/prior; any surviving selected temporary must be byte-exact and every unrelated temporary
must be absent. Its scheduler fence stops the multithreaded Agent while ptrace remains live, proves
all Agent tasks stopped, then stops the exact tracer; stopping both simultaneously can strand
sleeping tracee threads. Source-linked qualification and the post-rename/pre-directory-fsync sides
were initially open. All three repaired-source-linked prefixes now pass on the founding Sandwurm
stack.

ADR 0336 targets the other side of each publication rename. Qualification-owned `strace` filters on
the exact metadata parent directory and delays the selected `fsync` at syscall entry. A v6 live arm
therefore proves that the rename is visible while its parent-directory durability barrier has not
entered the kernel. Recovery admits only the old or new state of that one directory entry: manifest
`absent|exact`, immutable record `absent|exact`, or mutable pointer `prior|successor`, while earlier
prefix members remain exact and later members remain uncommitted. Startup must finish at the exact
successor with no publication temporary. This is a crash-consistency contract, not evidence that
storage firmware honored the flush.

All three v6 cells now pass on the founding stack. Each real crash selected the old directory state
and retained the exact temporary; startup safely replayed through exact/exact/successor. The first
record attempt also exposed unconditional preparation barriers: frontier reads had fsynced five
directories even without mutation. Preparation now emits child-to-parent barriers only for directory
creation, while publication barriers remain unchanged.

ADR 0337 closes a different failure class: present but byte-invalid signed
metadata. The authoritative namespace-local set is the current branch
pointer, its exact immutable branch record and manifest, signed workspace
state, and signed maintenance state. Both startup and `sync-repair`
authenticate that closure under the namespace transaction before exposing
work or claiming content verification. A failure is labeled by family and
blocks effects.

Those paths are intentionally validation-only. Startup, repair, and ordinary
publication do not delete, quarantine, replace, or overwrite a corrupt signed
root. The exact bytes remain for forensic/operator recovery, and the
namespace opens only after externally supplied byte-exact restoration passes
the same authentication. Immutable CAS object quarantine, derived projection
markers, and the ADR 0314 external freshness witness remain distinct
boundaries.

An immutable branch record and an incorporated branch are deliberately different subscriber states.
A cut before mutable-pointer replacement can leave a valid successor record and manifest beside the
prior pointer. Local graph discovery reuses those exact bytes but does not mark the successor
incorporated; an authenticated advertised frontier drives it through ordinary dependency validation
and branch acceptance, which idempotently reuses the immutable files and replaces the pointer last.
Current or older exact records settle as history without pointer movement. This distinction prevents
a durable orphan record from turning a recoverable prefix into a permanent convergence stall.

ADR 0136 adds an optional range extension without changing those roots. After verifying and committing
the complete candidate manifest, a subscriber with an exact accepted artifact basis plans missing
target ranges locally. The request carries only 1..64 canonical target-address-space ranges, current
HEAD identity, namespace, and explicit FileId. The publisher exposes their concatenation directly
from one descriptor-pinned, mutation-checked immutable artifact; it creates no range-bundle file.
The subscriber journals the target attempt before receive, unlinks the completed bundle while holding
its descriptor, reconstructs into the attempt-derived staging path, verifies the complete SHA-256,
commits the object, clears attempt truth, and accepts HEAD last. No peer nominates a basis or reuse
plan, and no partial bundle becomes object or activation authority.

ADR 0137 makes the accepted basis explicitly optional for liveness, not for authority. After the
candidate manifest is committed and reverified, an absent or digest/size-invalid basis selects a new
ordinary whole-artifact request with its own FileId and durable attempt. Complete target verification
and accepted-HEAD-last ordering are unchanged. The fallback does not delete, replace, or quarantine
the unusable object; broader scrub/GC semantics remain disabled.

ADR 0138 permits one same-job range retry, but only after the failed attempt's exact staging path,
signed active-attempt record, and scheduler reservation are all cleared. The canonical plan, signed
HEAD, authority context, and authenticated epoch remain fixed; the durable attempt, request message
ID, FileId, and provider file number are fresh. A received prefix is counted as discarded and is not
an input to reconstruction. If cleanup is uncertain or the second attempt fails, the pull is
terminal. Generic local file cancellation reaches this terminal bridge, while explicit job
cancellation and disconnect retire the job before retry admission.

ADR 0230 supersedes the unconditional-discard clause only for one same-carrier retry with an exact
seek-capable private prefix. ADR 0231 applies the same primitive to one native `available` carrier
loss: finish/fence old attempt truth, hide stale correlations, require a distinct authenticated
range-capable replacement, and hand off only a strict prefix under fresh identities. Neither
decision changes complete reconstruction or HEAD ordering; fail-closed I2P still discards and
blocks. ADR 0232 qualifies composition through two sequential carrier deaths: the prefix crosses
three fresh attempts, both old FileId/terminal generations remain fenced, and cumulative retained/
resumed accounting stays exact. A bounded request hold orders recovery-before-refault only when the
explicit two-fault qualification seam is enabled; it is not ordinary scheduler behavior and changes
no wire bytes. ADR 0233 exercises the same unchanged transition after at least 15/16 of a concrete
range. The laboratory slows only that selected range so the final 1/16 window is observable, and
binds threshold plus rate in strict evidence; product pacing and scheduling remain unchanged.

Explicit `sync-repair NAMESPACE` is a namespace-transaction maintenance effect, not an implicit read
or convergence side effect. It enumerates only strict digest-named private final objects, hashes each
against its filename identity, and moves verified mismatches to a unique private quarantine name.
Signed publication, accepted, activation, and retained roots are not rewritten. Genuine direct-UDP
and forced-TCP construction cells fsync one target-artifact corruption, preserve accepted and active
state, explicitly re-pull the same signed revision, retain the corrupt quarantine copy, and finish
with a clean two-object scan. Quarantine has no automatic purge authority.

ADR 0139 adds signed engine 3, `treepack-v1`. A matching namespace may publish an absolute
owner-controlled directory through the preserved deterministic treepack codec; fixed product bounds
and namespace quotas cover complete artifact bytes, entries, individual files, paths, and in-memory
sorting. Links, special entries, foreign ownership, and group/other writable source state fail before
publication. The resulting treepack still has a canonical range index and currently transfers only
as one whole immutable object.

After the ordinary artifact/index checks and signed activation commit, a projection callback unpacks
the tree to one exact private staging directory, deterministically repacks it to the signed digest,
fsyncs it, freezes files to `0400`/`0500` and directories to `0500`, renames the complete revision,
and atomically replaces a relative `materialized-trees/current` symlink. Signed activation state is
truth; the tree is derived. Exact retry therefore re-verifies or reconstructs the projection even
when activation is already current. Under the namespace transaction, recovery accepts only canonical
revision/staging directory names, validates selected subtrees before mutation, removes abandoned
staging, and prunes every noncurrent derived revision after the pointer is durable. ADR 0140 applies
the same complete-classification rule to exact `.current.part.PID.SEQUENCE` symlinks: each must be an
owner symlink to a canonical relative revision path, every neighbor must be understood before the
first unlink, and the activation directory is fsynced after recovery. Eight injected post-effect
checkpoints permit a separate process to terminate at each projection boundary. Revision and pointer
candidate vectors are bounded by the namespace object ceiling (plus one complete predecessor during
revision switching) and refuse excess state before mutation. A fresh exact retry must reduce every
resulting state to one complete current revision.

Each pull also retains one nonzero process-local job ID, initially identical to its HEAD-request
message ID and collision-checked across the bounded job set. Cancellation marks that job terminal
while holding the subscriber lock before invoking transport or storage cleanup. It then closes every
admitted receive at most once, discards attempt-derived staging, finishes signed attempt truth, and
fences unoffered scheduler work. HEAD, object-result, offer, and terminal dispatch all exclude the
cancelled state, so a late callback cannot advance accepted HEAD. A failed remote CANCEL enqueue does
not suppress local cleanup; it remains an operator-visible error until exact retry settles the
already-fenced job. Job IDs and cancelled tombstones do not survive daemon restart because startup
recovery independently fences every signed attempt and never reconstructs a Tox handle.

Signed-HEAD load/derive/replace is serialized across local processes by the namespace transaction
described below. The object directory has a canonical inventory that accepts only private
digest-named artifact/manifest files, uses checked byte accumulation, and applies configured
whole-store object/byte ceilings before sequential local growth.

The genuine whole-store byte-quota gate deliberately leaves less space than either object in a valid
successor. Whichever transfer completes first is refused under the namespace transaction; subscriber
failure cleanup removes staging and active-attempt truth without accepting the HEAD or changing the
old object inventory, activation, or derived tree. No automatic eviction follows quota pressure.
Until conservative pin/GC authority exists, immutable-store sizing must include retention headroom.

Namespace v1 `maximum-objects` is intentionally a shared conservative ceiling: it bounds canonical
immutable-store inventory and treepack entry parsing/sort population. The genuine object-count gate
therefore uses a ceiling of six for the six-entry canonical tree, preloads four valid one-byte
digest-named objects, then admits the generation-1 artifact and manifest to reach six exactly. Its
33,554,432-byte store ceiling can fit the complete successor by bytes. Candidate refusal is thus a
count result, while activation remains a valid treepack operation. ADR 0142 freezes this coupling and
the required sizing rule for namespace v1.

Storage writability is part of synchronization mutation admission. The production pull and activation
paths must first acquire and secure the persistent namespace transaction hierarchy; `EROFS` is a typed
terminal failure for that operation, never permission to continue with process-local truth. The
genuine read-only gate uses a loop-backed ext4 mount rather than discretionary mode bits. Pull refusal
occurs before object requests or staging and preserves predecessor acceptance, activation, inventory,
and projection. After explicit read-write remount, exact pull retry may accept the successor but does
not activate it. A second read-only interval refuses activation while preserving that accepted
successor and the old visible tree; exact activation retry after another read-write remount performs
the switch. ADR 0143 freezes this boundary and keeps automatic retry absent.

Directory memory qualification observes the long-lived IoTox process rather than whole-VM demand.
After generation 1 is active, the genuine gate publishes a 128-entry successor at the configured
entry ceiling, transfers its 7,616,908-byte artifact and manifest, and activates the complete deep
tree. Linux `VmHWM` is sampled after baseline, publisher construction, subscriber pull, serving, and
projection; phase order, exact deltas, pair maximum, signed identities, and a 65,536 KiB construction
ceiling are bound into both receipts. The accepted UDP/TCP peaks are 12,924/13,132 KiB. `VmHWM`
includes resident anonymous, mapped-file, and shared pages attributed to the process, not ordinary
unmapped page cache or whole-guest demand. ADR 0144 explicitly makes the ceiling evidence-only: no
namespace memory quota, cgroup enforcement, allocator proof, or fleet guarantee follows from it.

Publisher object identity is checked at service time, not merely when `sync-publish` first commits the
store. The provider acquires the namespace transaction and verifies the exact requested digest before
creating a file offer; missing or mismatched bytes return unavailable. Before any offer, the
subscriber may retry that typed result with a fresh message ID and FileId up to its bounded limit;
this also absorbs transient skew between signed route capacity and the publisher's physical attempt
ledger. Exhaustion terminally fails the job, clears private staging, and preserves
accepted/activated/visible predecessor truth. Unavailable after an offer is a protocol error.
Repair remains a separate operator action: `sync-repair` quarantines mismatches without rewriting the
signed HEAD, deterministic duplicate publication may reconstruct the same artifact and manifest from
unchanged source, and the subscriber must explicitly retry. The genuine dual-carrier gate corrupts
both generation-2 source objects, observes zero subscriber admission/commit, quarantines exactly both
objects, reconstructs identical revision identities, and then converges. ADR 0145 freezes this
fail-near-source contract; it is not automatic replication or source recovery.

A content replica is deliberately a separate HEAD role, distinct from authored publication, remote
acceptance, and local activation. `sync-replica-import` verifies one foreign-writer content-v2 HEAD
and its complete root/page graph, then wraps the unmodified signed record in a fixed local-device
custody signature. The resulting private `replica-heads/` file means only “this device elects to
cache and serve immutable bytes named by this exact record.” It can drive exact availability/object
responses after restart when no local publication exists, but the subscriber's primary HEAD gate
still binds the writer to the authenticated peer. Thus a replica cannot impersonate that writer or
change effect state. Reachability traverses the replica metadata as a live graph and roots only
present chunks; missing replica-only chunks are normal, while missing root/page metadata prevents GC
classification. Same-writer linked advance is mandatory after first import. ADR 0257 freezes this
availability/authority split and its true cold-start gate.

Content-v2 source authority and content transport are also distinct. Agent retains each source's
exact primary v3 authority session for writer membership and the primary source's signed HEAD. An
owner-local pre-HEAD transition may replace only that source's transfer carrier with one reciprocal
private-v2 bulk-worker incarnation. Types 28--31, FileId, CTA1, offer, and terminal then use the
worker; HEAD, activation, authority records, coordination, and reconstruction stay in the parent.
The binding cannot change after HEAD and exact worker loss fails the job without another route.
`sync-pull-multi-route` performs that transition atomically for every known source in one named
native/Tor/I2P class before releasing the primary HEAD request. The supervisor derives worker
content advertisement only after both parent content services exist and freezes it before worker
startup. The accepted one-source Sandwurm cell retains native authority/HEAD context while an exact
actual-Tor worker carries the complete revision with zero reassignment (ADR 0258). The accepted
multi-source companion retains two independently authorized native publisher sessions and maps each
stable source principal to a distinct exact Tor worker. Bounded owner-private `content-source-job=`
records expose that frozen mapping, and the independent verifier recomputes its sorted carrier-set
commitment before accepting complementary contribution and activation (ADR 0259).

ADR 0269 permits that mapping to contain more than one source path for the same stable principal and
primary authority tuple. A repeated routed source selector must resolve atomically to another exact
ready worker; insufficient distinct carriers refuse the whole admission. The scheduler assigns
complete immutable objects to paths and exposes requested/committed/fetched counters for each. It
does not split an object or move HEAD authority. Since numeric friend/file identifiers belong to one
Tox transport instance, two workers may both report `friend=0`; every cross-worker join therefore
uses the complete route key, worker incarnation, and carrier epochs in addition to FileId/CTA1.
Exact path loss remains whole-job failure with no post-HEAD replacement.

A completed incoming file is likewise only transport truth. The subscriber hashes the complete
attempt-derived staging file under the namespace transaction before its digest-named object can
commit. Size or digest mismatch terminally fails the job, clears that attempt and corrupt staging,
and cannot advance accepted, activated, or visible tree truth. Independently committed candidate
objects remain eligible only after exact size/digest re-verification by a fresh explicit pull. In
whole-object mode those verified objects enter scheduler truth without a transport lane, so only
missing objects are requested; an existing malformed object is refused until explicit repair rather
than overwritten. The dual-carrier destination-corruption gate ends its selective retry with one
requested/admitted artifact and two committed candidate objects. ADR 0146 freezes the distinction
between transport work and verified local progress.

Synchronization request replay is scoped to one authenticated friend/online epoch and canonical
message identifier. The publisher retains the canonical request and response before performing a
file offer. An exact replay returns that response while suppressing another offer; different bytes
under the same identifier are a protocol conflict and do not replace retained truth while that ID
is in the bounded recent window. A retired ID is fresh immutable-read work and must pass current
authorization, namespace, HEAD, and object validation again (ADR 0282). The subscriber
likewise retains canonical HEAD/object responses: exact duplicates are no-ops, conflicts fail the
pull, and a duplicate HEAD result can request only lanes without retained object results. The genuine
dual-carrier gate reorders duplicate object results behind two admitted file lanes, proves a later
HEAD duplicate emits no requests, refuses one altered-payload replay, and still converges through the
original FileIds with HEAD-last acceptance and explicit activation. ADR 0147 freezes this bounded
same-epoch behavior; it does not claim replay durability across process restart.

Explicit retained revisions are stored as one canonical bounded snapshot per namespace. Every entry
copies the exact accepted generation, record, artifact, manifest, and sizes; pin/unpin mutation is
atomically replaced under the namespace transaction. The stable device signs a domain-separated canonical
record whose mutation number commits the preceding signed record digest. This authenticates authorship
and in-order live transitions, but a complete older record can still be replayed after restart; the
state cannot authorize destructive collection by itself.

One private persistent `transactions/<namespace>.transaction.lock` now serializes every implemented
local sync mutation across threads and processes. The move-only proof token is bound to its acquiring
process and thread; top-level install, publication, activation, accepted-HEAD, and retention operations
acquire it once, while nested stores require that exact token instead of reopening the flock. Invalid
inputs that can be decided without state are rejected before creating the lock hierarchy.

The object inventory additionally exposes canonical kind/digest/size records. A pure bounded
reachability planner merges stable-device-signed publication, authenticated accepted HEAD,
activation, and authenticated retained-revision roots; it preserves exact source masks and reports missing,
size-mismatched, and unreferenced objects separately. A stored-state entrypoint loads every root,
checks the rollback guard, and scans inventory under one namespace transaction. Accepted and activation state each use a separate
domain-separated stable-device signature and reject unsigned legacy or foreign state. Complete older
valid coherent snapshots remain replayable without an independent monotonic witness. The planner
therefore emits evidence only and has no removal operation.

ADR 0149 adds a separate explicit local consumer of that evidence. `sync-gc NAMESPACE dry-run` loads
authenticated roots and the rollback guard under one namespace transaction, captures the strict
object directory through Linux descriptors, and reports only bounded counts/bytes. The transaction
token itself retains the namespace-root descriptor and device/inode identity; root, transaction
directory, or lock substitution invalidates it. `quarantine` repeats the plan rather than trusting an
old dry run, requires complete live-root consistency, and compares the entire frozen inventory before
its first effect.

Candidate names are reconstructed only from validated kind/digest records. `openat2` enforces
beneath/no-symlink/no-mount traversal from the pinned root, every private single-link regular file is
reopened and compared with frozen metadata, and `renameat2(RENAME_NOREPLACE)` moves it onto the same
filesystem under `gc-quarantine`. The root is fsynced when that directory is created; source and
quarantine directories are fsynced after each rename. Results separate moved bytes from the durable
prefix, including cancellation or late sync failure. No pathname, remote entrance, unlink, `apply`,
or purge operation exists. Coordinated replay remains sufficient reason to retain quarantine
indefinitely.

A fixed 496-byte rollback guard binds the stable device and namespace to four exact
`(counter, record)` heads for publication, acceptance, activation, and retention. Its signed body
contains a committed set plus at most one pending successor. Under the namespace transaction,
`begin -> state replace -> finish` makes a power cut before or after state replacement distinguishable
and recoverable; every third head is a rollback or fork. The store rejects missing guards beside
nonempty state, foreign signatures, tampering, symlinked/multiply linked files, and weak parent
directories. Every implemented publication, acceptance, activation, pin, and unpin root replacement
is wrapped in this protocol. A failed root commit deliberately leaves pending evidence because a late
filesystem synchronization failure can follow a landed atomic rename. The next signed mutation
reconciles the actual exact side; read-only reachability checks either exact side without repairing
it. Coordinated replay of both state and guard remains possible without hardware or an external
witness.

Current persistence limitations:

```text
default mode keeps local seeds and command metadata behind Unix permissions; optional required
fscrypt-v2 mode now enforces one externally unlocked complete state closure before runtime creation
and requires the deployment's public master-key identifier as an exact configuration pin
no hardware keystore
authority plus optional application/Ratox startup incarnations, signed route generations, and the
complete Ratox terminal-policy tree have exact-CAS rollback-witness coordination and an authenticated
remote-service backend; the exact durable mutable-command `STARTED` frontier is witnessed before
provider/update effects; the exact namespace/automation policy tree is witnessed and startup-frozen;
the update policy/lifecycle is witnessed before pointer effects; each opted-in single-writer
namespace externally anchors its signed published/accepted/activated/retained roots; and each
opted-in tree-v2 namespace anchors its live branch frontier plus signed workspace and maintenance
state. Broader namespace-state freshness remains open; the local two-head
guard, same-disk mock, or same-snapshot
service are not independent witnesses
no command-log compaction/checkpoint format
no external secure-time source; wall-clock trust is explicit, startup-checkpointed against signed
local history, and guarded by monotonic elapsed time only within one process lifetime
no backup/recovery protocol for a lost device filesystem
```

ADRs 0303 and 0305 leave existing store codecs and crash ordering unchanged inside fscrypt. ADR 0303 descriptor-
pins the policy-v2 root, matches its exact public master-key-identifier configuration pin and live
key, binds mount identity, recursively verifies every extant inode,
closes every configured/derived durable path, requires tmpfs or same-policy runtime, and fails before
runtime/network/effects. Its authority pilot writes an exact signed next-record intent before an
external pending CAS, commits the guarded ledger, then commits the witness. Missing intent, stale
whole-root state, fork, or unresolved witness unavailability fail closed. The coordinator alone is
not an independent witness. ADR 0305 supplies a dedicated witness-role Ed25519 service: the device
signs nonce-bound fixed query/CAS requests, the Agent pins signed responses, and a device-signed
no-replace enrollment binds one exact initial authority head. Its owner-private service store signs
and atomically replaces records under an exclusive lock and accepts only exact begin/finish
transitions. Live Agent construction creates this backend after device identity load and reconciles
authority before runtime creation; absence, wrong key, stale state, and fork fail closed. A two-guest
gate proves separate-process/disk protocol logic, but production still requires separately
administered rollback-resistant or independently checkpointed service persistence. ADR 0313 now
provides the latter mechanism: one bounded service-signed complete selector snapshot can be retained
outside the service failure domain and enforced as an exact-or-later restart floor before bind. It
does not decide where the trusted copy lives or turn a same-disk artifact into independence. ADR 0306 adds
separately enrolled application and Ratox lanes. Each startup binds an exact signed next incarnation
through durable intent and pending/committed CAS before runtime; older valid local records refuse.
ADR 0307 separately enrolls the signed route artifact generation/digest. It accepts only the exact
next generation through a durable intent containing the exact signed high-water record; restoring
both local route files or skipping history refuses before route construction. ADR 0308 separately
enrolls the complete canonical Ratox profile/binding tree. Policy mutations remain inert until an
explicit witness commit; startup verifies and caches the exact reviewed tree before any runtime or
terminal activation, so coordinated rollback of an old sudo-capable tree and local checkpoint
refuses.
ADR 0309 separately enrolls a stable digest over all retained incoming non-read-only command
identities that have crossed the signed `STARTED` boundary. The Agent commits that external head
before invoking a mutable provider and retains effect identities against journal rollback. Result
delivery cannot consume positions, and failure to resolve the service prevents the effect. This
does not claim generic exactly-once actuation.
ADR 0310 separately enrolls the exact canonical namespace and stable-device-signed automation
policy tree. Startup verifies, rereads, and freezes that externally committed snapshot before
RuntimeTree. Agent-mediated policy mutations durably install a candidate, externally commit the
complete candidate tree, and only then replace the live namespace/automation view. Quiescent offline
edits require explicit commit plus restart. Per-namespace heads, guards, objects, workspaces,
maintenance, projections, and content remain outside this low-frequency policy lane.
ADR 0311 adds the exact update-policy plus signed lifecycle-state lane. Its signed successor intent
must externally commit before state and the derived selected-slot pointer; policy replacement is
frozen within the enrolled witness epoch.
ADR 0312 adds one domain-separated lane per non-tree-v2 namespace for the exact signed published,
accepted, activated, and retained roots. It requires the externally frozen complete sync-policy
tree, reconciles every namespace before RuntimeTree, and verifies root reads under the namespace
transaction. ADR 0314 adds a distinct lane for tree-v2's live branch frontier plus signed workspace
and maintenance state, with the same pre-runtime reconciliation and transaction-held read fence.
Neither lane covers content availability, quarantine, projection markers/current pointers, health,
worktree bytes, or backup.
The path-free diagnostics configuration commitment v9 includes separate protection-required,
authority-witness-present, application-incarnation-witness, Ratox-incarnation-witness, and
route-generation-witness plus terminal-policy-witness, command-effect-witness, sync-policy-witness,
update-lifecycle-witness, and sync-guarded-state-witness bits, but
never the root, policy ID, backend endpoint, or key material.

## 13. File transfer

Tox file transfer handles bounded finite regular files. The manager separates incoming/outgoing
state, keeps incoming offers paused until explicit private destination acquisition, checks outgoing
source stability, answers exact positional chunk requests, and synchronizes completed files before
no-clobber publication.

ADR 0160 keeps file production below the transport event queue's lossless boundary. A callback that
observes 64 pending events schedules local PAUSE after `tox_iterate()` returns; scheduler-owned
transfers resume only below 16 events after at least 5 ms and after pending interactive/control owner
work. The 1,024-entry queue remains semantic reserve and required-event blocking remains the final
fail-safe. Explicit PAUSE takes scheduler ownership without a duplicate provider control. Runtime
status and new bilateral Ratox proofs expose thresholds, transitions, failures, and hold duration.
The exact direct-UDP `bulk-1` gate passes at render p95 42.727 ms and owner p99 1.499 ms with event
high-water 180/130, zero required-event waits, and zero pacing failures. The protected route remains
available for later load cells but is not required for this one-stream direct-route boundary.

Synchronization may additionally choose one nonzero 32-byte Tox FileId when offering an immutable
object. The manager reads the value back and cancels provider substitution. This joins the prior
authorized object request to a paused offer without trusting its filename; exact object size and
digest still come from the verified signed HEAD, and provider file numbers remain ephemeral.

The ratox-style surface passes path/control records into that manager:

```text
file-send      absolute local source path
file-receive   full provider file number + absolute local destination
file-control   full provider file number + pause|resume|cancel
```

The complete file number is preserved as an opaque friend-specific handle. The pinned implementation
currently encodes incoming direction inside that number, but IoTox does not make the pattern a public
contract.

Pause is two-sided. `local_paused` and `peer_paused` are independent facts; a transfer moves only
when both are false. Generic RESUME cannot accept a pending incoming offer before `file-receive` has
acquired its destination. CANCEL releases local resources even if the provider cannot transmit the
control after disconnect.

A successful local `file-receive` response means destination policy passed, a private staged file
exists, receiver state was installed, and toxcore accepted RESUME. Completion is a later callback
and filesystem-publication boundary. A tiny transfer may already be published and absent from the
live map by the time the admission response reaches its caller; live map residency is never used as
a second success condition. Transfer state is not durable across disconnect or process restart.

The synchronization layer has one narrower exception to that generic file-manager rule. ADR 0234
may retain a strict positive canonical whole-object prefix across daemon restart, but restores none
of the file manager, job, epoch, route, handle, or descriptor state. A fresh authorized signed-HEAD
pull allocates new transport identities and may seek to the retained length; the final immutable
digest remains the only commit authority.

File receipt does not grant execution. IoTox's update layer independently joins an accepted sync
HEAD to a release-signed manifest and an owner-local policy before bytes may enter an inactive slot.

## 14. Signed update boundary

`signed-update-bundle-v1` places a fixed 320-byte manifest before one payload that remains inert
during delivery and staging. Its release key
is independent of Tox friendship, sync membership, sync HEAD signing, and the stable device key. The
manifest binds the exact namespace, target, sequence, version, size, digest, and payload kind;
owner-private policy pins admissible release signers, the kind, and local limits. Policy v1/v2 and
kind 1 mean `opaque-slot-v1`; policy v3 and kind 2 name only `linux-service-v1`.

Staging requires one already accepted immutable sync HEAD, reopens and rehashes its artifact, verifies
the release signature, copies only the payload to a digest-named mode-`0400` inactive slot, and commits
stable-device-signed lifecycle state. Apply commits `pending-restart` before changing one exact
relative `current` symlink. A greater durable Agent incarnation opens the health window, and only its
exact one-use token can advance the confirmed sequence. Expiry, a second unconfirmed restart, or an
incomplete pointer/state transition selects the last confirmed slot again.

Remote `update.stage` enters through the signed durable command journal. Fixed `ICQ2` names only the
exact current accepted HEAD; current `install.firmware` authority and bilateral feature bit 20 are
mandatory. The receiver repeats the same verification and inactive-slot staging path, then returns
fixed `IUS1` evidence binding release sequence, accepted HEAD, and manifest. Exact duplicates,
identity conflicts, quotas, restart recovery, audit, and pre-first-send cancellation retain the
ordinary command-store contract.

The ordinary opaque adapter intentionally stops there. The slot is not executed or booted, the store
never deletes rollback material, and the peer cannot apply, restart, obtain the health token, or
confirm. Historical
slots leave the eight-slot hot set only through explicit local dry-run/recoverable quarantine. The
stable-device-signed confirmed slot and live candidate are protected exactly; moves are no-replace,
bounded to a 256-file recovery directory, and safely resumable after partial completion. Release
signers use a device-incompatible release role, are created no-clobber in owner-private storage,
inspected by public key, and rotated by
emitting a new incremented policy rather than editing the loaded record in place. Feature
bit 20 is absent unless the local update construction opens and its durable/sync dependencies are
offered.

The separately gated `linux-service-v1` adapter consumes only kind-2 state selected by a matching
policy-v3 record. It reopens the exact mode-`0400` slot, rehashes it into a mode-`0700` anonymous
memfd, verifies write/grow/shrink/seal seals, and enters it through an exact IoTox helper using
`fexecve`. The helper is no-new-privileges and parent-death armed, starts a new session/process group,
requires Linux `close_range`, and passes no remote argument, pathname, or ambient environment. The
payload must emit `IOTOXSR1 || release-sequence-u64be` on descriptor 3 while still live. Confirmation
requires that exact readiness and the existing one-use local health token. Exec failure, malformed or
closed readiness, early exit, or deadline expiry invokes signed rollback and relaunches the prior
confirmed service through the same sealed path. Existing opaque policy/state bytes remain exact and
cannot be reinterpreted as executable.

The service manager must still own the whole descendant cgroup because a malicious payload can
re-session beyond process-group teardown. Boot integration, hardware monotonic witnesses, physical
power cuts, flash wear, secure boot, and recovery media remain separate effect-bearing boundaries.

## 15. Network model

Transport and route are distinct:

```text
peer transport: Tox
route:          native | Tor | I2P
```

Current evidence:

```text
Tox/native: adapter-, binary-, source-linked-, and network-verified for the retained founding-host
            normal-native and TCP-relay-only fixtures
Tox/Tor:    strict numeric SOCKS/bootstrap/relay configuration plus source-linked local socket and
            two-guest TAP-contained generic-SOCKS recovery evidence; separately bounded actual-Tor
            public-relay circuit/loss/restart evidence for one host, relay, Tor build, and time sample
Tox/I2P:    VM-qualified strict routed-Tox options plus qualified client and persistent
            service SAM boundaries; pinned provider expands only proxy/relay establishment to 120 s;
            two-guest containment, router/front recovery, and one exact private-member 131,369-byte
            sync payload pass; production spelling passes the same actual-I2P topology under
            ADR 0253; broad availability, diversity, anonymity, and physical-host claims remain open
```

Multi-route sync keeps initial placement and loss behavior orthogonal. `fixed|adaptive` chooses an
eligible carrier only at admission or permitted replacement. `available|fail-closed` separately
decides whether loss may invoke replacement at all; fail-closed retains the fenced awaiting job for
explicit cancellation/new pull and reports the block (ADR 0220). Each pull now freezes its own
choice, conflicting retries fail, and loss handling never rereads the process default (ADR 0221).
This local per-job intent is separate from signed membership policy.
Named per-pull route classes now filter initial placement and replacement against the exact locally
constructed worker network. `any` alone permits primary fallback; native, Tor, and I2P
classes require a matching authenticated auxiliary worker (ADR 0222). Route-set v2 now binds that
coarse class to the exact member key and requires primary, constructed worker, and coordinator proof
agreement. Exact proxies, routers, relays, and endpoints remain private unsigned deployment inputs
(ADR 0225).

The redacted retained reports support only the named c-toxcore version, host, bootstrap/relay
catalog, and normal-native or TCP-only topology. They do not justify an unqualified
network-verified release claim across providers, packet-loss conditions, NATs, or public routes.
Tox/Tor suppresses compiled native catalogs, disables UDP/discovery/announcements/hole punching and
native DNS, and refuses hostname or incomplete topology configuration before state mutation. Its
generic SOCKS boundary does not prove Tor implementation or circuit use. The separate operator gate
authenticates Tor's local control plane, joins each configured-target stream from a new Agent source
to a built three-hop `GENERAL` or `CONFLUX_LINKED` application circuit, joins both exact process
identities to their Linux socket sets, and repeats after
Tor death plus a held no-bypass outage. This verifies one actual-Tor route, not anonymity or the
complete two-IoTox-over-Tor matrix (ADRs 0191/0195). Accepted compact proof `pair.2mycvy9n`
separately verifies two exact Tor auxiliaries on distinct circuits become private-v2 ready in a
converged sync topology (ADR 0203). Accepted compact proof `pair.lzsyitvy` additionally binds the
complete signed-tree job to the exact Tor auxiliary with zero reassignment and independently
verified Tor/control plus TAP evidence (ADR 0204). ADR 0205 constructs the separate two-IoTox
external Tor-process-loss/reassignment/recovery cell. Accepted compact proof `pair.iompvehf`
records external loss after positive object progress, native-member completion, and the real Tor
carrier's return with zero IoTox route-worker restarts and zero unexpected-context TAP packets.
None of these samples proves anonymity, physical path independence, or long-duration/multi-relay
reliability.

ADR 0206 keeps the terminal lifecycle separate from immutable-object reassignment. Its distinct
actual-Tor primary-route cell kills only client Tor after initial PTY progress, observes heartbeat
warning before authoritative offline, retains one detached live device PTY, and permits only
explicit higher-epoch resume of the same session/incarnation after the exact Tor instance returns.
Three Tor phases, raw byte/timing captures, and TCP-only TAP containment enter the strict proof;
accepted compact proof `pair.2waqdpgk` independently binds them to a real client Tor `SIGKILL`,
one detached live PTY, exact-session generation-2 resume, and zero IoTox daemon restarts.

ADR 0207 keeps ordinary circuit churn on the other side of that process-loss boundary. Accepted
compact proof `pair.k8o54n2v` for `ratox-route-actual-tor-soak` preserves one session and contiguous
byte sequences across 120 paced heartbeat/PTTY exchanges while exact client and device application
circuits are closed and replaced under authenticated Tor control. Live attempts observed both an
authoritative-loss branch and a no-error branch despite continuous Tor/IoTox processes. Circuit
observations remain evidence only: a post-replacement PONG proves unchanged epoch/generation, while
c-toxcore's authoritative offline alone drives detach and explicit higher-epoch resume. Neither
branch changes session/incarnation/PTY/byte positions. The accepted run exercises both branches,
with no Tor, IoTox, or guest restart and with strict TCP-only guest containment.

ADR 0208's distinct-record repetition observes both Tor streams reopen while both Ratox checkpoints
remain same-epoch/generation continuous. Together the two proofs show that `stream-reopened` is not
a carrier/session event: it appears beside both continuity and explicit resume. The architecture
therefore keeps Tor control evidence observational and grants transition authority only to the
provider carrier plus authenticated Ratox protocol.

The auxiliary `route-health [FRIEND]` read keeps three truths separate: c-toxcore's exact carrier
label, a TCP connection to only the configured local SOCKS listener, and an optional confirmed-peer
lossless echo. A listening proxy does not establish upstream health, so offline-plus-reachable stays
`unresolved`. The operation neither publishes a replacement connection state nor calls a session
transition; its Agent gate requires the complete session projection to remain unchanged (ADR 0192).

`route-health-watch [FRIEND]` strictly parses that canonical report and maintains independent
process-local local-boundary and application latches. Thresholds are bounded to 1..64 (three failure,
two recovery by default); inconclusive samples clear streaks without inventing state and evidence
counters saturate. This observation-only loop does not install daemon policy or cause carrier,
session, detach, resume, or epoch effects. Ratox terminal PING/PONG is a separate attachment-specific
signal with the same non-mutating policy boundary (ADR 0193).

The separately explicit `route-target-health` crosses one additional boundary without accepting a
destination from the caller. For Tox/Tor the Agent selects index zero of the already validated
numeric TCP-relay configuration, performs one bounded SOCKS5 no-auth CONNECT, consumes the complete
reply, sends no application bytes, and closes. Stage, typed result, RTT, numeric reply, and copied
carrier state are the only output. The 250 ms watch never invokes it. Neither configured-target
success nor failure has carrier, route-worker, transcript, terminal, or epoch authority (ADR 0194).

Future direct Tor/I2P transports are separate from routing Tox through those networks. No selected
privacy route may silently fall back to native networking.

## 16. Dependency boundary

Preferred product:

```text
pinned c-toxcore source
pinned libsodium source
pinned Argon2 source
one linked iotox executable
```

Research/test mode retains runtime loading for exact mocks and diagnostics. Supplying a shared
library path authorizes native code in-process.

c-toxcore is a substantial network-facing dependency. IoTox keeps it behind a narrow seam, fuzzes
owned decoders, separates application authority from Tox identity, pins current security fixes,
and must retain a rapid patch path.

## 17. Mutorr placement

Mutorr small-circle replication remains under `incubator/` and runs in a preservation lane. It is
not part of the default product and not the immediate northstar.

The ratox successor, generic durable commands, writable Unix façade, real Tox, and owner re-entry
come first.
