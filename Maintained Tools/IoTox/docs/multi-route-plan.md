# IoTox multi-route architecture and qualification plan

Status: accepted direction; Gate 3 complete and Gate 4 in progress. Updated 2026-08-31.

## Product meaning

Multi-route IoTox is an authenticated application-layer coordinator over independent Tox instances.
It is not packet bonding and does not pretend that several Tox connections are one reliable stream.

```text
stable IoTox device principal and authority
                    |
          authenticated route set
        /           |             \
protected route   bulk route     bulk route ...
Ratox/control     sync objects   sync objects
        \           |             /
         independent Tox identities
```

The stable principal answers “which device is this?” Each Tox identity answers “which current road
reaches it?” Replacing or reconnecting a road does not replace the device and does not grant the road
application authority. Native, Tor, and future I2P contexts use independently random route
identities by default; the stable principal, never a derived Tox key, is their common product
identity (ADR 0198).

ADR 0211 freezes a lab-only future-I2P construction adapter below this model. An exact numeric Tox
record maps to one canonical b32 Destination through loopback SAM; the transient SAM Destination is
plumbing and never replaces the route-specific Tox identity or stable principal. Product
`tox/i2p`, actual router containment, and private route membership remain unqualified.

## What is measured

On the founding host with pinned c-toxcore `0.2.23+iotox-file-rr1-tcp-connect120` and forced TCP:

- one Tox route serviced 16 concurrent files but advanced only 17 of 32 in the larger cell;
- four independently keyed routes advanced 32 of 32 twice with eight streams per route;
- 40 aggregate streams were not repeatably qualified, and 48/56/64 crossed terminal or lifecycle
  bounds;
- Ratox remained exact at the accepted four-route 32-stream point;
- a deliberately stopped auxiliary route recovered from unchanged savedata before workload release;
- the recovery cell recorded one injected and two automatic restarts, then advanced 32 of 32 files,
  rendered 40 of 40 terminal samples with a 103.412 ms maximum, and canceled cleanly;
- that complete gate took about 361 seconds, making convergence latency a real optimization target.

The compact proofs are `.sandwurm/exports/pairs/pair.hb491hc_` for steady establishment and
`.sandwurm/exports/pairs/pair.fmf8pynz` for establishment recovery. The protected live-loss proof is
`.sandwurm/exports/pairs/pair.0xk33kco`. Detailed measurements and nonclaims are in
`evidence/2026-08-20-sandwurm-ratox-bulk.md`.

## What the evidence suggests

The improvement is consistent with a per-instance, per-connection, or TCP head-of-line service
boundary: independent Tox instances create independent scheduling and congestion domains. This is
an inference, not localization of the exact provider bottleneck.

The evidence supports these construction policies:

- retain eight forced-TCP bulk streams per route as this host's conservative measured point;
- reserve Ratox's protected route from bulk work by default; eight same-route bulk streams passed
  once and then caused an immediate five-second Ratox receive failure in an identically sequenced
  live-loss rerun, so a merely prioritized queue is not route isolation;
- authenticate and confirm every required route before admitting the planned population;
- recover establishment with finite, staggered, savedata-preserving retries;
- expose degraded capacity instead of silently redistributing excess work.

It does not establish:

- proportional aggregate throughput or packet-level striping;
- diversity across physical links, hosts, relays, or administrative domains;
- a benefit for direct UDP equivalent to the observed forced-TCP result;
- preservation of a toxcore file transfer across route-process death;
- safe duplicate-free reassignment of active work;
- a universal eight-stream limit for other machines or provider versions.

## Authority and route-set binding

Product integration requires a route set that is authenticated above Tox friendship. Its frozen
semantic inputs must include at least:

```text
stable device principal
coordinator identity and route-set generation
member Tox public key
member role: protected or bulk
member network class: native, Tor, or laboratory I2P construction
route policy and expiry/revocation state
proof bound to the confirmed IoTox transcript
```

An unlisted Tox identity cannot replace a failed member merely by connecting. Route membership must
be signed or otherwise proved by the stable device principal inside the existing transcript-bound
identity model. Ownership and capabilities continue to come from the authority ledger; membership
only says that a transport route belongs to the device's current route set.

The complete route set is private authorization material. Route-binding v1 currently sends that
roster on the auxiliary friendship and remains valid for the accepted same-context laboratory, but
it is not the M8 cross-context discovery design. Before native/Tor membership is qualified, the
remote roster must arrive through an already authority-authenticated primary association and an
auxiliary route may disclose only a transcript-bound proof for its exact expected member. There is
no public stable-principal-to-route lookup. ADR 0199 implements the canonical feature/type
allocations, authority-bound primary inventory frame, and digest-anchored 256-byte member proof.
ADR 0200 implements bounded Agent replay/high-water, primary delivery, worker handoff, v2-only
auxiliary exchange, and authority-loss readiness withdrawal behind an explicit default-off gate.
ADR 0201 adds exact-key local worker network policy and closes the genuine generic-SOCKS
mixed-context gate: accepted compact proof `pair.z948jeii` joins a native UDP primary, native UDP
bulk member, and strict generic-SOCKS/TCP bulk member in both guests, then converges one signed
4,194,389-byte tree through two ready bulk routes per role. The actual-Tor multi-peer matrix remains
separate. ADR 0202 closes its next construction prerequisite: exact-key worker bootstrap
and TCP-relay lists can replace the primary template without entering the signed route inventory,
so a Tor member may use public numeric infrastructure while native members retain the private lab
fixture. ADR 0203 accepts compact proof `pair.2mycvy9n`: two exact Tor members use separate
three-hop circuits and become private-v2 ready in a converged sync topology with zero unexpected
context packets. ADR 0204 accepts compact proof `pair.lzsyitvy`: the complete signed tree job stays
on the exact Tor member with zero reassignment while Tor/control and TAP evidence independently
reverify. ADR 0205 accepts compact proof `pair.iompvehf` for exact-member external Tor loss,
surviving-member reassignment, and real carrier return without an IoTox worker restart. ADR 0206
accepts compact proof `pair.2waqdpgk` for primary actual-Tor terminal process loss, one detached
device PTY, and explicit exact-session resume without an IoTox daemon restart. Route health remains
evidence rather than session authority. The multi-relay/exit/time/duration and adversarial-proxy
matrix remains open. ADR 0207 accepts compact proof `pair.k8o54n2v` for the first bounded duration
slice: one 120-sample Ratox session across exact client/device Tor circuit replacement, with processes and session/PTY/byte
identity held fixed. Live attempts observed both carrier loss and no error, so each replacement must
prove either same-epoch/generation PONG continuity or exact loss with explicit higher-epoch resume.
The accepted run exercises both outcomes without a Tor, IoTox, or guest restart.
ADR 0208 repeats that frozen terminal cell through a second public record and observes two stream
reopenings with same-epoch/generation continuity. This begins relay-record sampling without
claiming Tor exit/time diversity or changing route/session authority.
ADR 0209 closes the bounded adversarial local-boundary slice without promoting listener or target
admission into carrier/session authority. ADR 0243 later repeats the duration gate against the third
public record and exercises both application outcomes after stream reopenings. ADR 0210's expanded
eight-proof accounting resolves 30 exact-target/churn declarations to 24 normalized paths and 23
last-hop identities with no cross-proof path or last-hop reuse. Independent exit/operator review
and schema-witnessed separated time windows remain open.

The coordinator owns admission, assignment, fencing, and evidence. Whether route workers are
threads, child processes, or separately supervised invocations remains open. They must not each own
independent authority ledgers, sync heads, or activation decisions.

## Route lifecycle

The planned externally meaningful state machine is:

```text
configured
    -> connecting
    -> authenticated
    -> ready
    -> recovering -> authenticated -> ready
    -> unavailable
```

`authenticated` means the Tox route has a confirmed application session and a valid route-set
binding. `ready` additionally means its configured service class and admission budget are available.
`recovering` retains identity and bounded retry state but contributes no schedulable capacity.
`unavailable` is a stable, operator-visible outcome after retry exhaustion.

Required-capacity policy is fail closed. A workload planned for four routes does not start on three.
Later adaptive scheduling may plan a smaller population against three ready routes, but it must be a
new explicit plan, never silent overflow from a four-route plan.

## Ratox and future resumable terminal work

Ratox v1 framing stays frozen. One attachment uses one protected route, preserving ordered byte
semantics and the existing incarnation, attachment, cumulative-position, and replay fences.

Future Eternal/Mosh-style continuity belongs above Tox:

- the application session has a durable/fenced identity independent of a Tox connection;
- reconnection authenticates a route before attachment resume;
- cumulative positions determine the exact missing byte interval;
- old-route frames cannot commit after a newer attachment incarnation wins;
- terminal input is never sprayed across routes for throughput;
- bulk work cannot consume the protected route's interactive reservation.

This is session resumption over a replacement road, not transparent migration of a socket.

## Sync and OTA scheduling

Synchronization is the first suitable multi-route product workload because its committed objects are
immutable and digest-addressed. The scheduler must operate on stable object or chunk identities, not
toxcore file numbers.

Before reassignment, freeze and prove:

1. one signed immutable object manifest and full-object digest;
2. a disjoint assignment map with stable chunk boundaries;
3. an attempt identity and fence for every route assignment;
4. explicit pause, cancellation, disconnect, and timeout outcomes;
5. duplicate and late completion rejection;
6. digest verification before object commit and HEAD publication;
7. restart reconstruction from durable object/job state;
8. per-route admission that preserves the protected route's headroom;
9. atomic completion and activation independent of transfer arrival order.

OTA inherits this mechanism only after signed manifests, anti-rollback policy, staging, health
confirmation, and rollback are independently complete. Received bytes never gain execution
authority because a route delivered them.

## Ordered implementation and science gates

### Gate 1: live auxiliary loss without reassignment (complete)

- Admit 32 transfers across four forced-TCP routes and prove eight are active on each.
- Keep Ratox sampling on route zero.
- Stop one bulk route after admission, not during establishment.
- Record the exact local/remote transfer outcomes for its eight members.
- Require explicit cancellation or a named paused/unavailable state; forbid reassignment.
- Recover the same route identity and prove a clean new session and empty stale transfer set.
- Require unaffected routes and Ratox to remain within their existing bounds.

This gate discovers current behavior before product semantics are frozen.

The first discovery cell is complete but did not pass the gate. With 32 active transfers distributed
eight per route, stopping route three caused the client to purge exactly that route's eight incoming
transfers, left 24 active on routes zero through two, performed no reassignment, and recovered the
same route identity with an empty transfer set. Ratox on route zero completed 40/40 samples in one
correctly sequenced run, then failed its first five-second receive bound in the next. The successful
run's teardown also exposed serialized file-control pressure: 45 bounded attempts produced 17
successful replies before six local transfers remained at the 60-second cleanup deadline. These are
diagnostic results, not an accepted compact proof; all private roots were deleted after read-only
inspection.

Gate 1 therefore continues with `ratox-stripe-protected-live-loss-24`: route zero carries Ratox and
control only, routes one through three carry eight bulk transfers each, and route three is faulted
after admission. Acceptance requires 8 affected, 16 unaffected, zero reassigned, same-identity
recovery, 40 exact Ratox samples during the positively observed offline interval, progress on all 16
unaffected transfers, and bounded cleanup to empty. Per-sample progress is
published content-free so a failed capture identifies its exact ordinal and maximum completed RTT.
The two-vCPU construction cell pins the primary agent and probe to vCPU 0 and all auxiliary agents to
vCPU 1; route separation without resource separation already produced one 506.113 ms outlier and is
not the acceptance configuration.

Per-file cancel is best-effort at this load, not the final reclamation primitive. Repeated protected
cells left three live transfers after 58 attempts even with one sequential worker per route. The
bounded cleanup policy is therefore: attempt each file once, then restart only a route whose local
transfer set remains non-empty; require unchanged savedata identity, a fresh confirmed session, and
an empty transfer set before that route is ready again. The verifier binds direct cleanup versus this
fallback and the exact number of route restarts. This is route-worker fencing, not transfer
reassignment.

The protected follow-up passed. Its 180 KiB compact proof records 24 active transfers, 8 purged on
the faulted route, 16 unaffected and progressed, zero reassigned, same-identity recovery, and all
four routes confirmed at evidence release. Ratox completed 40/40 exact samples during the offline
interval at p50 111.045 ms, p95 164.825 ms, and maximum 232.356 ms. Ten of 16 cleanup controls
returned success; six returned errors; one remaining client bulk worker was fenced and recycled.
Together with the deliberately recovered device route, the pair recorded two route restarts. Gate 1
is complete for the construction policy frozen by ADR 0109; the narrow latency headroom does not
replace the 1,000-sample or long-running gates.

### Gate 2: coordinator and authenticated route inventory

- Implement one authority-owning coordinator with multiple route workers.
- Bind every member Tox key to the stable device principal and confirmed transcript.
- Expose coherent content-free route states, generations, budgets, and restart counters.
- Prove unknown, duplicated, stale-generation, foreign-principal, and downgraded routes fail closed.
- Preserve single-route default behavior byte for byte when no route-set policy is configured.

The first implementation slice is complete. `route_inventory` freezes a canonical
stable-device-signed v1 artifact, exact member roles/connection classes/work and restart budgets,
and the full lifecycle coordinator. Its negative matrix rejects unknown inventory keys, duplicate
members and worker claims, unconfirmed transcripts, stale generations, foreign principals,
protocol downgrades, expired membership, connection-class mismatch, budget overflow, and restart
exhaustion. `protocol-route-set-v1.md` and ADR 0110 own the contract.

ADR 0225 preserves those v1 bytes and adds the creation-only v2 artifact. V2 consumes one reserved
member byte for the required native/Tor/I2P-construction class, domain-separates its signature,
requires the coordinator to be the protected member, and enforces the primary/worker construction
before transport admission. `protocol-route-set-v2.md` owns the exact contract.

The second implementation slice is also complete. `--route-set` now activates strict private-file
loading and a stable-device-signed generation/artifact-digest high-water checkpoint before toxcore
starts. Ordinary rollback, same-generation forks, corrupt/foreign state, links, and weak permissions
fail closed. Local control v1.24 operation 66 backs the implemented `routes` and change-only
`routes-watch` commands with one content-free schema; arbitrary failure text was removed in favor of
a closed failure enum. An absent policy enters no store/coordinator code and reports explicit
single-route mode. ADR 0111 owns this boundary.

The third prerequisite slice is complete. A configured route set now binds the primary transport's
savedata to the signed coordinator Tox key before bootstrap, relay registration, or iteration.
Route-binding-v1 has an exact 224-byte stable-device-signed record that derives its session digest
only from the canonical confirmed transcript, verifies the peer Tox key and exact signed member
policy, and rejects stale, foreign, replayed, or modified evidence. Message type 19 and feature bit
21 remain deliberately unadvertised until the live exchange exists. ADR 0112 owns this boundary.

The fourth construction slice is complete. Explicit `--enable-route-workers` activation now loads
key-named savedata from one strict private root, starts an independent toxcore owner for every
non-coordinator member, applies its signed connection class and exact pre-network identity fence,
and progresses the real canonical HELLO/confirmation state machine. Initial savedata is deliberately
limited to one peer. Successfully constructed members become `connecting`, not authenticated or
ready; they admit no work and own no authority or synchronization state. ADR 0113 owns this boundary.

The fifth protocol slice is complete. Message type 19 now carries the complete signed route set and
its 224-byte transcript binding in one canonical payload no larger than 1,150 bytes. Verification is
anchored to an expected remote stable principal and minimum generation supplied by local trusted
state; payload claims cannot nominate their own trust root. Exact envelope semantics are frozen by
ADR 0114. Feature bit 21 remains unadvertised.

The sixth coordinator slice is complete. A bounded registry now derives remote route trust from an
independently authority-authenticated primary session, requires the signed remote set to name that
exact primary Tox key as coordinator, retains generation and same-generation-fork state, admits one
binding per worker and auxiliary online epoch, and makes only exact retries idempotent. Primary
trust removal revokes dependent admissions; worker replacement requires explicit retirement. ADR
0115 owns this boundary.

The seventh worker slice is complete. A worker can advertise bit 21 only when given a narrow parent
signing callback and verifier, creates one frozen binding after transcript confirmation, retains one
reciprocal record while primary trust catches up, and latches invalid verification until trust
changes. Disconnect clears the exact epoch state. The deterministic provider proves one signer call
and one accepted outbound frame. ADR 0116 owns this boundary.

The eighth integration slice completes the Gate 2 implementation. Agent installs the restricted
signer only for explicitly enabled workers, derives trust from an exact connected and authorized
primary session, and advances a member through `authenticated` to `ready` only after local-send and
reciprocal-binding evidence. Authentication loss clears admitted work and returns the same worker to
`connecting` without falsely charging a transport restart. The deterministic provider proves the
complete transition with distinct primary and auxiliary peer keys. ADR 0117 owns this boundary.

Gate 2 implementation is complete. Genuine Sandwurm route-loss/restart qualification remains part of
the later randomized and long-running gates; it does not block Gate 3.

### Gate 3: immutable sync-object reassignment

- Use the existing signed HEAD, object publication, transaction, retention, and rollback machinery.
- Assign disjoint immutable objects or chunks to ready bulk routes.
- Kill a route at deterministic assignment, partial-transfer, and completion boundaries.
- Fence the old attempt before reassignment and reject its late completion.
- Verify complete bytes and commit the object once, then advance accepted HEAD and activation through
  their existing independent signed domains.

The first transport-neutral Gate 3 slice is complete. `SyncObjectScheduler` admits only canonical
kind/digest/size records to exact ready bulk-worker incarnations, reserves coordinator capacity,
retains bounded attempt tombstones, fences before reassignment, rejects late completion, separates
verification from commit, commits exactly once, and releases every live reservation on close.
Authentication-loss cleanup composes with the coordinator's earlier atomic work withdrawal without
masking inconsistent accounting on a still-ready route. The protected route is ineligible. ADR 0118
and `sync-object-scheduler-v1.md` own this boundary.

The second filesystem slice is complete. An attempt ID now derives its sole no-clobber path under the
private namespace staging directory. Preparation, verified commit, and shape-safe discard require the
namespace transaction; commit checks the completed private file's exact size and digest, reuses the
existing exclusive double-verification object publication, removes staging durably, and never advances
accepted HEAD or activation. ADR 0119 owns this boundary.

The third admission slice is complete. Each namespace-scoped scheduler now reserves the immutable
object's full byte count together with one route work unit. Concurrent routes share one configured
staging ceiling; verification retains the reservation, while fence, mismatch, commit, and close
release it exactly once. Refused byte admission does not consume an attempt ID or route capacity.
ADR 0120 owns this boundary.

The fourth worker slice is complete. Every auxiliary worker now owns a file-transfer manager bounded
by its signed work count and configured file-size ceiling. Its service loop applies file events, while
route-scoped receive/cancel operations require the exact current reciprocally authenticated bulk
incarnation; protected, stale, and merely connected routes cancel offers and fail before effect.
Primary-trust replacement cancels retained transfers before revoking worker authentication. ADR 0121
owns this boundary.

The fifth process-local integration slice is complete. Every admitted worker receive reserves actual
bounded terminal-event storage before resume and yields exactly one completion, cancellation, or
failure record for its route incarnation and file number. The namespace bridge binds that live handle
to one already-reserved immutable attempt and derived staging path. Completion reuses strict
size/digest object commit before scheduler verification and commit; every other outcome discards and
fences only that attempt, while replay is stale. ADR 0122 owns this boundary.

The sixth restart slice is complete. Attempt IDs are signed and durably burned before assignment;
the exact immutable object and route incarnation become active journal state before receive resume.
Startup recovery never revives a Tox handle: it verifies an existing object or commits complete
staging, otherwise safely discards and fences. Terminal processing retains its event across retryable
storage failure. ADR 0123 and `sync-attempt-journal-v1.md` own this boundary.

The seventh protocol slice is complete. Fixed HEAD discovery and immutable-object request/result
records bind a namespace and exact signed-HEAD digest to a nonzero request-selected Tox FileId.
Sender readback refuses provider substitution; exact authenticated bulk workers preallocate outgoing
terminal bookkeeping and report both transfer directions through the same lossless bound. Remote
filenames remain presentation only. ADR 0124 and `protocol-sync-wire-v1.md` own this boundary.

The eighth vertical slice is complete. One default-off Agent namespace now performs strict
authorization, HEAD discovery, exact replay, FileId-bound object admission, durable attempt recovery,
verified object commit, and accepted-HEAD-last ordering through the genuine single-route provider.
Activation remains a separate explicit local effect. ADR 0127 and the M5B evidence series own that
boundary.

The ninth admission prerequisite is complete. If the single-Agent receive ledger is already at its
qualified 32-transfer ceiling, an exact sync offer remains paused and keeps the same attempt, FileId,
file number, route, authority context, and staging-byte reservation. Provisional staging/journal state
is removed between bounded fair service passes, and cancellation includes pending offers without
repeating effects. ADR 0166 owns this boundary.

The prerequisite is now live-qualified by `sync-tree-admission`: direct UDP `pair.xrl6_7gv` and
forced TCP `pair.dqbsp21_` each use one receive slot, defer the second immutable object for ten
service attempts, admit exactly two offers sequentially, and finish with no pending work. Existing
accepted 1,000-sample `bulk-1` cells supply the route-latency half of that qualification. This proves
bounded local excess-work admission only; it does not move an offer between route workers.

The tenth auxiliary protocol slice is complete. A default-off worker gate advertises state sync only
when explicitly constructed, accepts and sends only canonical object request/result records through
an exact authenticated bulk incarnation, and retains inbound records in a pre-reserved bounded parent
queue. Every event carries the local route/worker fence, auxiliary friend/epoch, remote route-set
generation, and stable principal; trust or connection loss purges queued records. HEAD, range,
activation, authority, and scheduler effects remain excluded. ADR 0167 owns this boundary.

The eleventh parent-dispatch slice is complete at the deterministic Agent boundary. Primary authority
and HEAD exchange remain on the proven primary session while a separately frozen exact auxiliary
carrier owns only object frames, FileId offers, and terminal outcomes. Publisher replay identity is
carrier-scoped; subscriber receive/cancel and signed coordinator capacity use the exact worker
incarnation. Loss fences and cleans old attempts before another ready worker for the same principal
receives fresh attempt, message, FileId, and staging identities. Late old-carrier truth is rejected,
committed objects remain reusable, accepted HEAD advances only after both objects verify, and
activation remains explicit. The two-worker mock Agent gate forces the first carrier offline and
converges through the second. ADR 0168 owns this boundary.

Gate 3 is complete. The `sync-tree-route-loss` cell constructs one protected primary and two
reciprocally authenticated bulk routes in each of two simultaneous Sandwurm guests. After at least
65,536 incoming bytes it stops only the exact active bulk carrier, observes one loss and one
reassignment, rejects two old-incarnation terminal outcomes, converges and activates through the
other ready carrier, spends one restart-budget unit, and returns the stopped savedata identity under
a fresh worker incarnation to `ready`. The same cell then completes 40 protected-route Ratox samples
with zero 250 ms misses and resource evidence on both roles. Direct UDP (`pair.gqw1gzkd`) and forced
TCP (`pair.9i62wfpa`) independently pass raw and compact verification. ADR 0169 and
`evidence/2026-08-25-sandwurm-sync-route-loss.md` own the claim.

Gate 3 deliberately proves whole-object reassignment, not byte striping. The signed route-set,
route-binding, sync-object, and Ratox framing remain unchanged.

ADR 0219 now demonstrates why that distinction is also a privacy boundary. In a mixed native plus
actual-I2P topology, a 131,369-byte signed tree completes on the exact I2P member with zero
reassignment, but diagnostic 512 KiB and 4 MiB objects select I2P and then move as complete remaining
work to native after authoritative carrier loss. Router and service-front health do not prevent that
Tox carrier epoch change. Fixed/adaptive placement expresses local load policy, not signed permission
to cross privacy classes. ADRs 0225–0228 now bind the exact class into signed authority, carry the
already-frozen digest-bound range frames over an authenticated auxiliary, and qualify live range
loss plus explicit fresh same-carrier recovery; no new framing extension was necessary. Privacy-
required loss must still fail closed or remain within an equivalently authorized class;
availability-selected jobs may retain the existing whole-object reassignment rule.

### Gate 4: scheduler qualification

Status: in progress. Gate 3's deterministic loss seam and exact counters are the fault baseline; the
first genuine fixed/adaptive topology A/B and larger-object ABBA observation are accepted on direct
UDP and forced TCP.

- Compare fixed eight-per-route scheduling with a conservative adaptive policy.
- Measure convergence time, throughput, progress fairness, CPU, memory, descriptors, wakeups, and
  cancellation tails. The first bounded single-pull cancellation and eight-job population/resource
  rows are accepted. Eight-job/four-affected route loss and two-before/two-after degraded admission
  are also accepted. One counterbalanced two-job 16 MiB throughput/resource row is accepted on both
  carriers; exact first-byte timing, repeated distributions, randomized fault timing, and daemon cold
  startup with a route absent remain open.
- Randomize remaining startup delays and fault phase order in two Sandwurm guests; ADR 0176 closes
  both exact corresponding two-worker readiness orders, not stochastic timing or startup under fault.
- Repeat forced TCP with one relay and with independently controlled relays if that distinction can
  be constructed locally.
- Rerun direct UDP to determine whether multiple instances buy capacity there.
- Keep the 1,000-sample Ratox matrix separate and require its latency thresholds throughout.

The first implementation prerequisite is complete. `--sync-route-policy fixed|adaptive` now keeps
adaptive selection as the default after the Gate 5 population audit in ADR 0279. Fixed stable-key
selection remains an explicit diagnostic mode. Conservative adaptive selection occurs only at initial admission
or after a carrier has already been fenced; it minimizes exact admitted-work/signed-work-budget
utilization, then restart count, then route key. It never migrates a healthy pull and publishes
content-free per-policy selection counts. Owned selector and two-worker Agent loss tests pass. ADR
0170 owns this boundary.

ADR 0220 adds the enforcement prerequisite discovered by the I2P size gate. Replacement policy is
now explicit and orthogonal: `available` preserves qualified whole-object recovery, while
`fail-closed` fences a lost carrier and retains the exact awaiting job with a counted block and zero
replacement selection. The actual-I2P payload scenario selects fail-closed. This is local policy;
ADR 0221 freezes that choice per job. ADR 0222 additionally freezes and enforces an owner-local
constructed network class for admission and replacement. The original actual-I2P guest requested
`tox/i2p-construction`; ADR 0253 makes `tox/i2p` canonical for the same numeric class. ADR 0225 adds
route-set v2, signs that exact coarse class per member, and
requires the configured primary, constructed worker, and coordinator proof to agree. ADR 0226 and
compact proof `pair.jbr89_gc` now accept the exact destructive Sandwurm gate: fault after 69,921
positive bytes, fail-closed blocking with native ready and zero reassignment, same-member recovery
under a distinct router process with zero worker restart, explicit old-job cancellation, and
completion only through a fresh per-job class-pinned pull.

ADR 0223 establishes the transport-side byte-resume prerequisite without weakening attempt fences.
ADR 0224 consumes it for same-process whole-object reassignment. Sync owns a canonical private partial
from byte zero; available-policy loss fences the old attempt but retains its exact inode; a fresh
attempt/FileId/authenticated carrier inherits it through no-replace rename and seeks to the retained
size. The complete immutable digest still gates commit, and fail-closed pulls retain nothing. A full
Agent gate proves a three-byte positive-prefix handoff and suffix-only completion across two workers.
Signed-high-water startup cleanup removes only inactive burned-ID canonical paths if the process dies
inside handoff. ADR 0234 separately retains strict positive whole-object prefixes across daemon
restart and allows only a fresh authorized signed-HEAD pull for the identical object to claim them;
range plans remain non-durable. Genuine restart-resume compact proofs `pair.f20ma62y` and
`pair.lj0pdz6a` continue two exact prefixes totaling 115,164 direct-UDP or 159,036 forced-TCP bytes
under fresh identities. The genuine live-loss
two-guest gate now passes direct UDP and forced TCP: each carrier loses once after positive progress,
retains and resumes two concurrent object attempts with exact aggregate byte equality and zero
fallback, rejects two stale terminals, converges/activates, recovers the savedata identity, and then
passes 40 protected Ratox samples. Compact proofs `pair.jlcr7zms` and `pair.okks1io5`, ADR 0224, and
`evidence/2026-08-28-sandwurm-sync-byte-resume.md` own the claim. Positive I2P range transport now
passes under ADR 0227, while ADR 0228 proves that a positive partial I2P range is discarded on loss
and a distinct explicit job can recover on the same member. Tor-to-Tor, I2P failed-prefix byte
resume, whole-object repeated/very-late loss, attributable resource measurement, and restart
continuation remain open.
ADR 0229 optimizes that explicit recovery without weakening it: the fresh job locally re-proves its
durable manifest and requests only the full new range. The failed range prefix remains discarded.
ADR 0230 separately permits one exact prefix handoff inside an ordinary bounded same-carrier range
retry. It uses fresh durable/message/FileId identities and suffix-only receive, but it neither moves
the prefix between routes nor changes fail-closed carrier-loss cleanup.
ADR 0231 closes the corresponding native `available` row. A carrier-lost concrete range becomes
inert only after its receive is retired, old signed attempt is finished, scheduler attempt is
fenced, and old FileId correlation is hidden. The other authenticated range-capable worker receives
the unchanged plan under a fresh attempt/FileId and inherits only an exact strict positive prefix.
Direct UDP `pair.urbhf0je` retains/resumes 283,797 bytes; forced TCP `pair.n76biwao` retains/resumes
293,394 bytes. Both record zero discard/fallback and one loss/reassignment/stale-terminal/recovery.
This closes native cross-carrier range continuation, not fail-closed I2P, Tor-to-Tor, process
restart, or concurrent multi-source striping. The subscriber's owned deterministic boundary now
repeats the operation through four carriers with a 50%-then-75%-then-87.5% prefix and cumulative
exact accounting. Its explicit five-record namespace ceiling retains one manifest fence plus all
four range-attempt fences.
ADR 0232 closes the corresponding genuine two-loss native row: direct UDP `pair.le38qcl5` and forced
TCP `pair.8u14ddcy` preserve/resume 542,916 or 564,852 cumulative bytes through two sequential
losses, reassignments, stale terminals, recoveries, and restarts, with zero discard/fallback. The
recovery-before-refault request hold is an explicit qualification barrier, not product scheduling.
ADR 0233 separately closes one 15/16 late-loss row: direct UDP `pair.tev4u3rs` retains 984,378 bytes
and forced TCP `pair.1z7_d0jn` retains 995,346, then each fresh carrier receives only the remaining
suffix with zero discard/fallback. Repeated-late/final-chunk races and four-plus loss remain open.
ADR 0235 closes a distinct three-loss native cell with two bounded request-hold releases and exact
two-route alternation. Compact direct-UDP proof `pair.3iufekzy` retains/resumes 862,359 bytes and
forced-TCP proof `pair.zleebk2k` retains/resumes 871,956 bytes through three lifecycle events with
zero discard/fallback; four-plus loss stays outside the qualified boundary. Its fourth diagnostic
(`pair.ge_y8h28`) found both
publisher transports online but their application transcripts unconfirmed after reciprocal worker
restart. ADR 0236 closes that underlying route prerequisite with bounded retries of the same frozen
HELLO/CAPABILITIES records and exports content-free attempt counters; it does not relax route
binding and did not by itself make the three-loss claim. The next UDP diagnostic (`pair.fdskk7te`)
retained and
resumed 542,916 bytes before the scheduler correctly refused a fifth tombstone under its hidden
four-record limit. ADR 0237 replaces that constant with the validated host-local namespace request
ceiling; only the triple fixture raises four to the exact five records it requires. ADR 0238 then
separates the immutable restart ceiling from derived remaining capacity; the accepted cells prove
the exhausted route healthy at `restarts=2 restart-budget=2 restart-budget-remaining=0`.

The existing actual-Tor process-loss gate now closes one additional mixed-class row. Host `SIGKILL`
of the independently supervised client Tor process at positive progress retains/resumes two prefixes
and 102,825 aggregate bytes exactly through the native survivor, with zero fallback or IoTox worker
restart; the identical Tor member then recovers. Compact proof `pair.3u5cjbci` and
`evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md` own that claim. It does not authorize
the privacy-class transition. ADR 0227 separately accepts one positive I2P range transfer; I2P range
loss plus explicit fresh recovery is accepted under ADR 0228. I2P failed-prefix byte resume and
Tor-to-Tor continuation remain open.
ADR 0229 removes the redundant manifest transfer from that accepted I2P recovery cell; it does not
change these remaining continuation gates.
ADR 0230's direct-UDP/forced-TCP same-carrier retry evidence does not close carrier loss by itself.
ADR 0231 closes one native available-policy cross-carrier range row, ADR 0232 closes its genuine
two-loss repetition, ADR 0233 closes a separate 15/16 late-loss row, and ADR 0235 closes the
separate bounded three-loss row. None closes I2P/Tor, fail-closed, repeated-late/final-chunk races,
or four-plus loss.
ADR 0234 separately implements whole-object explicit-fresh-job continuation after daemon restart;
direct UDP and forced TCP are qualified by `pair.f20ma62y` and `pair.lj0pdz6a`.
ADR 0236 additionally repairs application-session liveness after asymmetric auxiliary reconnect;
its deterministic dropped-record regression and ADR 0235's genuine cells pass.
ADR 0237 separately keeps scheduler fence history bounded by namespace policy; it never evicts stale
event protection to make another reassignment fit.
ADR 0239 closes range restart without reviving carrier truth. ATM1 binds a retained bundle prefix to
the exact local manifest/basis plan and length; a fresh authorized pull must derive that same
commitment under fresh transport identities. Direct-UDP `pair.xg41pthc` and forced-TCP
`pair.00992erw` pass exact prefix/suffix accounting after a bilateral authority barrier. This remains
separate from multi-source scheduling and does not qualify I2P/Tor continuation.

The first two-guest A/B now passes as `sync-tree-route-balance`. Each bulk route exposes eight signed
work slots. The second two-object job starts only after the first holds positive admitted work while
the route remains eligible. Fixed names the same auxiliary carrier twice; after a clean same-state
Agent restart, adaptive names distinct carriers. Both phases make exactly two decisions, converge and
activate both trees, return staging/work to zero, and use zero HEAD retries. The same guests then pass
40 protected Ratox samples. Fixed-first direct UDP `pair.ul1pdq7m` and forced TCP `pair.pz9aapaj`,
plus adaptive-first direct UDP `pair.hhmma27l` and forced TCP `pair.jn5aqbr6`, pass strict raw and
compact verification against one exact binary (ADR 0171 and
`evidence/2026-08-25-sandwurm-sync-route-balance.md`). The tiny counterbalanced fixture proves
topology, not throughput. ADR 0176 closes both exact corresponding readiness orders below. Random
startup/fault delays, startup during faults, repeated larger-object throughput/resource attribution,
and single-versus-independent-relay TCP rows remain open, so Gate 4 is not fully qualified. ADR 0183
adds the first larger-object ABBA observation below.

The first cancellation-tail row now passes as `sync-tree-route-cancel`. One adaptive pull binds its
random transfer identities internally to the exact auxiliary route/worker and exports only aggregate
active-count/position/size. After positive progress, ordinary `sync-cancel` reaches terminal
quiescence with empty incoming/staging state, signed work two-to-zero, no accepted HEAD or activation,
no reassignment, and both bulk routes still ready. Direct UDP `pair.fpkne1pg` observes 70 ms and forced
TCP `pair.r_4luysy` observes 80 ms, both beneath the 5,000 ms construction ceiling and followed by 40
protected Ratox samples. ADR 0172 and
`evidence/2026-08-25-sandwurm-sync-route-cancel.md` own this bounded claim. Concurrent-job
cancellation fairness is closed below; the loss-before-cancel permutation is also closed below while
opposite/simultaneous ordering remains unqualified at that point.

The bounded population row now passes as `sync-tree-route-population`. Each policy starts eight
independent two-object, 131,139-byte-artifact tree pulls against two ready eight-work-unit bulk
routes. Fixed fills one route before spillover (`00001111`, maximum prefix imbalance 4); adaptive
alternates equally sized jobs (`01010101`, maximum prefix imbalance 1). Every job has a live positive
position or committed-object progress observation, commits both objects, explicitly activates, and
returns staging and signed route work to zero. Each phase retains a process-incarnation-fenced
resource interval, and the guests complete protected Ratox afterward. Direct UDP
`pair.slx3x0kb` and forced TCP `pair.rrizbuky` pass raw and compact verification (ADR 0173 and
`evidence/2026-08-25-sandwurm-sync-route-population.md`). This closes small-object population and
resource observation, not exact first-byte latency or larger-object throughput. Randomized route
startup/fault delays, startup during faults, larger-object sharing, and relay diversity remain.

The population-loss row now passes as `sync-tree-route-population-loss`. Fixed selection first fills
two four-job routes as `00001111` and consumes all 16 signed work units. After at least 65,536 bytes
of aggregate progress plus a 750 ms hold, the Agent stops one exact carrier and remembers its four
nonterminal job IDs. Every affected job is reassigned as its complete remaining two-object work set;
the old incarnation contributes only fenced stale terminals; recovery waits until all four remembered
jobs are terminal. Direct UDP `pair.j19_uhjj` and forced TCP `pair.rfnsjtqb` each record four affected
jobs, one loss, four reassignments, at least four stale terminals, one recovery, 12 fixed selections,
eight activations, work 16-to-zero, and 40 protected Ratox samples below 250 ms (ADR 0180 and
`evidence/2026-08-26-sandwurm-sync-route-population-loss.md`). The TCP campaign also forced repair of
complete-work route eligibility, bounded fresh-identity retry for transient pre-offer publisher
unavailability, and auxiliary event/carrier service separation. This closes deterministic
multi-job same-carrier loss, not random timing, startup during loss, or larger common-link QoS.

The degraded-admission companion now passes as `sync-tree-route-loss-admission`. Two fixed-policy
jobs first bind to one carrier and consume four signed work units. A one-millisecond post-progress
fault stops that exact worker; both jobs reassign to the sole survivor. Only then are two additional
jobs created. Evidence samples exactly one ready bulk route and requires both new jobs to select it
before recovery. All four revisions activate, stale old-worker terminals remain fenced, one
restart-budget unit restores the stopped identity, and work drains four-to-zero. Direct UDP
`pair.v3qc2kld` and forced TCP `pair.djhqe3we` pass raw and compact verification with protected Ratox
(ADR 0181 and `evidence/2026-08-26-sandwurm-sync-route-loss-admission.md`). The run also forced
carrier-first clean-shutdown quiescence while ordered event draining stays live. This closes new
work admission after observed loss/reassignment, not daemon cold startup with an absent route,
random fault timing, or production automatic recovery.

The controlled startup-admission companion now passes as
`sync-tree-route-startup-admission`. After ordinary base convergence and two-route readiness, the
same subscriber Agent cleanly restarts under adaptive selection while one exact authenticated bulk
route is held for 20,000 ms. The first route must be solely ready for ten samples before two
independent 16,777,283-byte-artifact jobs are created. Both consume four signed work units, remain
live on that route when the delayed peer joins, and never reassign. Both exact HEADs activate and
work returns to zero. Direct UDP `pair.46f6td4j` and forced TCP `pair.2gvkqs6b` pass raw and compact
verification with protected Ratox (ADR 0182 and
`evidence/2026-08-26-sandwurm-sync-route-startup-admission.md`). This closes admission through a
controlled degraded route set after same-state Agent startup. It does not emulate a physically
absent path, full guest boot, independent relay loss, or randomized startup/fault timing.

The larger-object comparison now passes as `sync-tree-route-throughput`. It runs four fresh-Agent
phases in `fixed-a,adaptive-a,adaptive-b,fixed-b` order with a 5,000 ms stopped interval before each
start. Every phase pulls two independent 16,777,283-byte artifacts. Fixed patterns are `00,00`;
adaptive patterns are `01,01`; all eight revisions activate, work drains four-to-zero, no
reassignment occurs, and protected Ratox passes afterward. Direct UDP observes 372,952 fixed versus
435,603 adaptive artifact B/s; forced TCP observes 398,486 versus 424,633. The forced-TCP prerequisite
also exposed continuous Tox transport state across Agent replacement, so bit 27 now orders a durable
process/connection generation and forces complete application reauthentication (ADR 0183 and
`evidence/2026-08-26-sandwurm-sync-route-throughput.md`). Both logical routes share one shaped 4
Mbit/s TAP. This is not physical multipath, byte striping, proportional scaling, relay diversity, or
a throughput distribution.

The bounded concurrent-cancellation row now passes as `sync-tree-route-concurrent-cancel`. Eight
independent 262,211-byte artifacts first bind to the two bulk incarnations as `01010101`. Four
ordinary `sync-cancel` clients then run simultaneously against indices 0, 1, 4, and 5: exactly two
withdrawals per route. All four preserve their carrier/worker identity through terminal
`cancelled`; the other four jobs commit and explicitly activate; cancelled namespaces have no
accepted HEAD, activation, or staging; work drains 16-to-zero; both routes remain ready; and no
reassignment occurs. Direct UDP `pair.2laq038h` and forced TCP `pair.rlpuyjth` pass raw and compact
verification with 150 ms and 100 ms cancellation tails, process-resource intervals, and subsequent
protected Ratox (ADR 0174 and
`evidence/2026-08-25-sandwurm-sync-route-concurrent-cancel.md`). This closes bounded concurrent-job
cancellation fairness on healthy routes, not fault ordering or randomized cancellation timing.

The first ordered fault/cancellation combination now passes as `sync-tree-route-loss-cancel`. One
adaptive 4,194,601-byte tree pull loses its active auxiliary incarnation after at least 65,536
artifact bytes, records exactly one reassignment, and must make positive progress on the replacement
before ordinary cancellation. The replacement carrier/worker stays fixed through terminal
`cancelled`; no second reassignment occurs; work drains two-to-zero; no HEAD, activation, incoming
transfer, or staging remains; and the stopped savedata identity consumes one restart-budget unit and
returns under a fresh ready incarnation. Direct UDP `pair._0jwjfe6` and forced TCP `pair.o0ozmdw1`
pass raw and compact verification with 80 ms cancellation tails and subsequent protected Ratox (ADR
0175 and `evidence/2026-08-25-sandwurm-sync-route-loss-cancel.md`). This closes one deterministic
loss→reassignment→progress→cancel order, not the opposite/simultaneous race or randomized timing.

The opposite deterministic order now passes as `sync-tree-route-cancel-loss`. The ordinary local
withdrawal first reaches a terminal cancelled tombstone, removes incoming/staging state, and drains
signed route work two-to-zero. Only then does a default-off seam stop that tombstone's exact retained
carrier. Both direct UDP `pair.yv4txv1r` and forced TCP `pair.m2396itk` record one loss, zero
reassignment, two fenced terminals, one signed-budget recovery, final two-route readiness, and
protected Ratox (ADR 0177 and
`evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md`).

The shared-arm race now passes as `sync-tree-route-cancel-race`. After positive progress, one exact
worker stop and ordinary cancellation each receive 500 ms from the same observed armed edge. Direct
UDP `pair.h6kg4fcr` and forced TCP `pair.z9egqd57` both linearize as cancel-first: one carrier loss,
zero reassignment, one typed nonrepeating cleanup retry, two stale terminals, one signed-budget route
recovery, final two-route readiness, and protected Ratox (ADR 0178 and
`evidence/2026-08-26-sandwurm-sync-route-cancel-race.md`). The verifier also accepts a consistent
single-reassignment loss-first record. This closes one deliberate collision per carrier, not random
inter-event distributions or multiple affected pulls sharing the failed carrier.

The loss-first branch now also passes genuine cells as `sync-tree-route-cancel-race-loss-first`.
The exact worker deadline is 250 ms and ordinary cancellation is independently issued at 1,000 ms,
without polling for loss or reassignment. Direct UDP `pair.5gvh__p1` and forced TCP
`pair.rxb2dsge` each bind one loss, one reassignment to a distinct terminal carrier, zero cleanup
retries, two stale terminals, one recovery, work two-to-zero, and protected Ratox (ADR 0179 and
`evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md`). Together the four shared-arm cells
qualify both authority outcomes, not a random timing distribution.

Exact corresponding readiness order now passes as `sync-tree-route-startup-order`. A default-off
qualification seam selects one exact auxiliary public key and holds every other worker until that
selected worker is application-ready and reciprocally bound; only then does a 20-second hold begin.
Both guests prove lane 1 and, after a savedata-preserving rolling Agent restart, lane 2 as the sole
ready bulk route for ten consecutive samples. Both routes must then return ready before the ordinary
signed 4 MiB tree and 40-sample protected Ratox probe. Direct UDP `pair.nyiqwm8t` and forced TCP
`pair.mdacri5e` pass raw and compact verification against one binary (ADR 0176 and
`evidence/2026-08-25-sandwurm-sync-route-startup-order.md`). This closes two exact readiness
permutations, not random delay distributions, more-worker partial orders, or startup during faults.

The first larger common-link interference signal is now explicit. Two 1 MiB/job direct-UDP cells
completed the same cancellation/survivor/work invariants but missed the five-second Ratox `OPENED`
receive deadline. The remote session and helper existed, the sensitive sends were accepted, and the
IoTox scheduler recorded only microsecond waits; every logical route nevertheless shared the same
4 Mbit FIFO-shaped TAP. A protected route is therefore an application scheduler invariant, not a
physical queue guarantee.

The controlled positive companion now passes as `sync-tree-route-common-link-fairness`. It restores
the exact 1 MiB/job population while changing only that client-TAP bottleneck to one 4 Mbit HTB
class with a 1,000-packet `fq_codel` leaf. A capture/release barrier binds the live hierarchy, rate,
active-flow count, and counters after Ratox completes but before TAP teardown. Direct UDP
`pair.am47s4qe` and forced TCP `pair.78uagrhw` pass raw and compact verification: pattern
`01010101`, four balanced cancellations, four survivor activations, work 16-to-zero, no
reassignment, 80/90 ms cancellation tails, and protected Ratox render maxima of 17.067/112.817 ms.
The fair queues carry 5,795,303/5,782,816 bytes and report 522/150 drops (ADR 0241 and
`evidence/2026-08-29-sandwurm-common-link-fairness.md`). This qualifies one shared-edge mechanism,
not strict class priority, reserved bandwidth, arbitrary offered load, independent capacity, byte
striping, or a universal deployment default.

ADR 0262 independently enables two same-source content object lanes on one authenticated Tox
session. Direct-UDP and forced-TCP Sandwurm cells prove distinct request/FileId/CTA1 attribution and
exact convergence, but both lanes still share one carrier and common bottleneck. This is a scheduler
prerequisite for later lane-count science; it neither closes a multi-route gate nor justifies the
terms bonded transport or striping. ADR 0269 now closes the separate construction step: one stable
source/authority session atomically binds to two independently authenticated exact Tor workers and
both contribute whole objects before HEAD-last acceptance and activation. Both workers use
route-local `friend=0` safely because correlation includes route key and worker incarnation. The
accepted cell does not measure a speedup, prove balanced placement, or separate circuits, links, or
bottlenecks; those common-link comparisons remain open.
ADR 0263 closes that single-session lane-count precursor: forced TCP improves through cap 4 under
the shaped fixture, while direct UDP is non-monotonic and default one remains. All cells still share
one carrier and common bottleneck, so no multi-route claim changes.

### Gate 5: operator policy and long-running behavior

- Default to one route when no explicit policy exists.
- Support a protected route plus a bounded number of warm auxiliary routes.
- Define idle timeout, restart budget, backoff, resource ceiling, and evidence retention.
- Prove hours-long churn, process restart, disk-pressure refusal, configuration replacement, and
  clean shutdown without route-key or state leakage.

## Operator truth

The planned read surface is `iotox routes` with a streaming twin `iotox routes-watch`. It reports
stable-principal digest, route-set generation, member role, connection class, lifecycle state,
admitted/active work, restart count, and last typed failure without revealing private keys or peer
content. Configuration, not an opportunistic command, selects member identities and budgets.

The coordinator and fixed whole-object reassignment path now exist behind explicit construction.
No documentation or CLI should call this bonded transport, byte striping, adaptive failover, or
production multi-route service before Gate 4 and Gate 5 qualify those distinct claims.

## Completion boundary

Multi-route product behavior is ready only when an authorized two-guest sync job survives live route
loss and restart, fences and reassigns immutable work without duplicate commit, preserves Ratox
latency on its protected route, reports exact degraded/recovery state, and retains single-route
compatibility. Physical-host diversity is not part of this repository's local gate.
