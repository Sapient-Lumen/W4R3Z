# IoTox auxiliary route workers v1

Status: implemented experimental authenticated bulk-worker and object-reassignment slice

Enable the worker boundary explicitly:

```sh
iotox run \
  --route-set /private/state/routes.signed \
  --route-generation-state /private/state/routes.generation \
  --enable-route-workers \
  --route-worker-root /private/state/route-workers
```

That command preserves route-binding v1. For an inventory that spans native and privacy-routed Tox
contexts, opt into the separate v2 disclosure policy:

```sh
iotox run \
  --route-set /private/state/routes.signed \
  --route-generation-state /private/state/routes.generation \
  --enable-route-workers \
  --enable-private-route-bindings \
  --route-worker-root /private/state/route-workers \
  --route-worker-network AUXILIARY_KEY_A=tox/native \
  --route-worker-network AUXILIARY_KEY_B=tox/tor@127.0.0.1:9050 \
  --route-worker-bootstrap AUXILIARY_KEY_B=203.0.113.8:33445:TOX_NODE_KEY \
  --route-worker-tcp-relay AUXILIARY_KEY_B=203.0.113.8:33445:TOX_NODE_KEY
```

V2 sends the complete signed inventory only after the primary session is independently authority
authenticated. An auxiliary may confirm its application transcript before then, but sends no route
proof and cannot become ready. Once the primary inventory is admitted, it exchanges only the fixed
256-byte member proof. Primary authority loss cancels live auxiliary work, purges queued sync frames,
clears reciprocal proof state, and withdraws coordinator readiness. The primary registry is bounded
to 64 active edges and 64 process-lifetime stable-principal/coordinator generation high-water
records; exact duplicate inventory is idempotent, while same-epoch conflict, rollback, and fork fail
closed (ADR 0200).

Each repeatable `--route-worker-network` names one exact signed non-primary member. Omitted members
inherit the primary network configuration. Overrides must be unique, implemented, and complete;
Tor requires one numeric SOCKS endpoint and a signed TCP connection class. The Agent derives and
validates every worker's full toxcore configuration and savedata identity before starting any of
them, so a bad later override cannot leave a partially active topology. Repeatable exact-key
`--route-worker-bootstrap` and `--route-worker-tcp-relay` records optionally replace the primary
template's corresponding catalog for that worker; each nonempty list is bounded to 16 unique
records and requires the same key's network override. This lets a native primary retain private
fixture records while a Tor worker uses public numeric records reachable from an exit. Proxy and
rendezvous endpoints remain local deployment policy rather than shared signed route-set fields
(ADR 0202).

Private context adoption is ordering-safe. A reciprocal member proof that arrives before its primary
inventory remains inert, then is reverified against the exact admitted context instead of being
erased during handoff. A stale prior-context proof is discarded without authority so a fresh frame
can arrive; primary withdrawal still clears everything. ADR 0201 qualifies this behavior in two
Sandwurm guests across native and strict generic-SOCKS workers.

The root must be an owner-owned mode-0700 real directory. Each auxiliary savedata file must be a
nonempty owner-owned mode-0600 single-link regular file named with the uppercase 64-character Tox
public key from its signed member record followed by `.toxsave`. Missing files are not generated:
provisioning a new route identity is a separate deliberate ceremony.

The signed coordinator Tox key remains owned by the parent Agent. If it also appears as a member, the
supervisor skips it rather than constructing the same identity twice. Every other member gets one
independent `ToxTransport` and toxcore owner thread, its exact savedata expectation, signed TCP/UDP
policy, a random nonzero worker incarnation, and a canonical `PeerSessionRegistry`. Initial v1
worker savedata must contain exactly one peer; ambiguity fails startup rather than selecting a friend
number opportunistically.

The supervisor handles Tox connection events, IoTox HELLO/CAPABILITIES, and the bounded route-binding
exchange. Route binding remains construction-gated: only an injected narrow signing callback plus a
sodium verifier enables feature bit 21. The mutually exclusive private callback also enables
dependent bit 28. After transcript confirmation a v1 worker freezes and sends
one locally signed frame. It retains at most one reciprocal frame while primary-route trust is
unavailable, then evaluates it through the bounded coordinator-owned replay registry. Invalid proof
verification is latched until trust changes instead of repeating every service cycle. Disconnect
clears all epoch-bound frames and authentication facts.

Explicit Agent route-worker construction installs that callback and verifier. The parent populates
trust only from a connected, confirmed, currently authorized primary authority session whose Tox key
and online epoch agree across both registries. A worker reaches `ready` only after local-send evidence
and reciprocal verification; losing that association returns it to `connecting` without spending a
transport restart. Each worker now owns a file-transfer manager whose active count is bounded by its
signed route policy. Parent receive/cancel calls require an exact authenticated bulk incarnation;
protected routes fail closed. Workers still own no authority ledger, namespace state, scheduler, or
signer. Every accepted receive first reserves one slot in a bounded preallocated supervisor terminal
ledger and one provisional file binding. Completion, cancellation, peer loss, file failure, and trust
replacement move that reservation to an exact route/worker/file outcome without eviction. New
receives fail before resume when the ledger is full.

Ordered transport-event application and periodic receiver-carrier pause/resume service use separate
supervisor threads. Every toxcore instance still has exactly one owner thread. Carrier service copies
shared worker incarnations under the supervisor snapshot mutex, releases it, and only then waits on a
synchronous owner command; exact sync-frame sends follow the same rule. A concurrent qualification
replacement therefore stops the retained old transport instead of invalidating memory or retargeting
the operation. This preserves bounded required-event delivery and keeps snapshots/local status
available under multi-transfer pressure (ADR 0180).
Shutdown uses the same dependency deliberately. A distinct carrier-stop request first prevents new
synchronous carrier operations; carrier service joins while the ordered event consumer continues to
drain required toxcore events. Only then does event consumption stop, followed by transfer managers
and transports. This prevents clean Agent restart from recreating the owner/event liveness cycle in
reverse (ADR 0181).

The process-local namespace bridge consumes those outcomes and commits verified immutable bytes.
When synchronization and route workers are both explicitly enabled, Agent adds `state-sync-v1` and
carries only canonical immutable object/range records. If both parent content services are also
constructed, the worker separately advertises `state-sync-content-v2` and may carry only content
object and exact sparse availability types 28--31. Agent finalizes this service-derived gate after
content construction and before supervisor start; the supervisor refuses post-start changes. This
keeps the advertised feature immutable for the worker lifetime without depending on constructor
order. Its bounded pre-reserved parent queue tags each
record with route key, worker incarnation, friend/online epoch, remote route-set generation, and
stable principal; trust loss purges queued records. The parent joins that exact carrier to an
unchanged real primary authority session, charges the signed route work budget, and sends/receives
FileId-bound whole objects, bounded range bundles, or content CAS objects through the worker. HEAD,
activation, authority, planning/reconstruction, and scheduler ownership remain in the parent. Range
or content frames are admitted only when both the primary authority session and exact auxiliary
worker negotiated their respective feature. Content source binding is owner-local, pre-HEAD, and
fail-closed after it freezes (ADRs 0227 and 0258).

The accepted one-source actual-Tor content gate keeps direct-native authority and HEAD context while
the exact reciprocal Tor worker carries the paged 4 MiB revision with zero reassignment (ADR 0258).
The accepted multi-source companion keeps two independent publisher authority sessions native and
binds each source principal to a distinct exact Tor worker before complementary object contribution
and activation. Owner-private per-source status makes those bindings independently verifiable (ADR
0259). These gates prove worker identity and route confinement, not routed authority, anonymity,
per-source circuit diversity, or independent physical paths.

ADR 0219 qualifies one 131,369-byte whole-object job on an actual-I2P auxiliary with zero
reassignment, but larger diagnostic jobs expose this intentional exclusion: loss fences the I2P
attempt and may reissue the complete missing object on a ready native member. That is availability
truth, not privacy preservation. ADR 0227 reuses the already digest-bound range-v1 framing on an
auxiliary rather than inventing another chunk protocol. It remains bounded by signed work and by the
route-set-v2 member class plus per-job class/failover policy; the fixed/adaptive selector alone cannot
authorize a privacy downgrade.

If an auxiliary carrier disappears, Agent first fences its attempts and clears its exact
correlations, then may assign the still-missing immutable objects to another ready worker for the same
proven principal under fresh attempt, message, FileId, and staging identities. Old-carrier events are
stale. Already committed digest-addressed objects are reused. Ordinary single-route operation never
constructs this path. ADR 0167 owns framing and ADR 0168 owns the authority/carrier split and
reassignment contract.

`--qualify-route-stop-after-bytes N` is a default-off laboratory seam accepted only with both sync
and route workers enabled. It stops the exact bulk carrier after a real incoming object crosses `N`
bytes, never selects the protected member, and records content-free loss/reassignment/stale/recovery
counters. After missing objects converge, Agent retires the old incarnation, spends one signed
restart-budget unit, reconstructs the same savedata identity with a fresh random worker ID, and
requires reciprocal authentication before returning it to `ready`. ADR 0169 records the live
dual-carrier qualification; the option is not an operator route-control API.

The `routes` status surface keeps `restart-budget` as that immutable signed ceiling and `restarts`
as consumed capacity. It also derives `restart-budget-remaining` after validating that consumption
does not exceed policy. This makes an exhausted-but-healthy route explicit without changing signed
route state or asking operators to infer whether “budget” means total or remaining (ADR 0238).

`--qualify-route-stop-count N` optionally bounds that seam to one or two sequential receive
incarnations; one preserves the historical behavior. Count two is accepted only with the byte
threshold. After the first affected jobs have migrated, Agent spends one recovery unit and waits for
the exact stopped identity to return to `ready` before the replacement becomes eligible for the
second stop. That leaves one authenticated carrier available for each reassignment. The final loss
waits for ordinary terminal convergence before its own recovery. Status reports the committed count
as `qualification-fault-count`; this is a deterministic science control, not automatic production
fault injection or an operator route-control API.

`--qualify-route-first-worker KEY --qualify-route-other-delay-ms N` is a separate default-off
startup-order seam. Both options are mandatory together; `KEY` must name one exact non-primary signed
member and `N` is 1 through 60,000 milliseconds. The supervisor constructs and identity-checks every
worker, but services only the selected worker until it has a confirmed application session and, when
binding is enabled, both local-send and reciprocal-authentication evidence. The delay starts at that
causal readiness point; a selected worker that never authenticates keeps all other workers held.
Normal startup is unchanged. This is deliberately not an operator route-control API, route-set
reordering, or a wire feature. ADR 0176 qualifies both corresponding two-worker orders over direct
UDP and forced TCP.

`--qualify-route-stop-after-cancel` is the opposite-order fault seam. It requires sync and route
workers, conflicts with the byte-threshold seam, and waits for a settled cancelled auxiliary pull.
Only that tombstone's retained exact route key and worker incarnation are stopped. The coordinator
must observe the loss with zero reassignment before one signed restart-budget unit may reconstruct
the route identity. The pull stays cancelled throughout. ADR 0177 qualifies this order over direct
UDP and forced TCP; the option is not an operator route-control API.

`--qualify-route-fault-delay-ms N` optionally gives the exact-byte seam a bounded 1 through 60,000
millisecond arm-to-stop interval. The Agent freezes the selected route key, worker incarnation,
position, and monotonic deadline as soon as the threshold is crossed and reports
`qualification-fault-armed=1`; it never retargets a later transfer. A zero configured delay keeps the
existing immediate same-pass stop. ADR 0178 uses a 500 ms delay and an independently scheduled
ordinary cancellation from the same observable arm edge. Both carrier classes linearize as
cancel-first with zero reassignment, one typed cleanup retry, and one capacity recovery. This is a
qualification seam, not production fault timing or route policy.

`sync-tree-route-cancel-race-loss-first` reuses that seam with a 250 ms worker-stop deadline and an
independent 1,000 ms cancellation deadline. It does not wait for route-loss status before invoking
the ordinary control. Both carriers require one reassignment to a distinct retained terminal carrier,
zero cleanup retries, and one recovery (ADR 0179). Together with ADR 0178 this live-qualifies both
authority outcomes, not their probability or every scheduling interleaving.

`--sync-route-policy fixed|adaptive` selects among the already authenticated states above. Fixed is
the default stable-key order. Adaptive considers exact admitted work divided by the signed member
budget, then restart count and route key, only for new admission or after fencing. Dynamic score
changes do not alter incarnation equality and cannot manufacture carrier loss. ADR 0170 owns this
Gate 4 prerequisite. ADR 0171 qualifies the first live placement comparison: fixed reuses the busy
eligible route while adaptive admits the later overlapping job to the idle eligible route. It does
not claim a throughput benefit. Eligibility now requires the complete remaining work of the job;
one free slot cannot partially admit a two-object retry. ADR 0180 qualifies four affected jobs moving
from one stopped fixed-policy carrier and delays route restart until every exact remembered job is
terminal.

ADR 0220 separates replacement permission from placement. `--sync-route-failover available` keeps
those qualified reassignment paths. `fail-closed` fences the exact lost incarnation, increments the
blocked-job truth, leaves the pull awaiting explicit cancellation/new pull, and never invokes the
selector. ADR 0221 freezes the choice per job. ADR 0222 filters both admission and replacement by an
optional exact constructed worker network class and forbids primary fallback for named classes.
That class remains owner-local; authenticating it is the next signed authority layer.

ADR 0224 preserves an incomplete whole immutable object only when that frozen policy permits
replacement. The new carrier still owns a fresh worker incarnation, scheduler attempt, message ID,
and FileId; the strict private partial moves no-clobber to the new attempt path and c-toxcore seeks
to its exact length. Fail-closed jobs, range bundles, cancellation, and terminal failure discard the
partial. Full-object hashing remains the commit boundary, so retained prefix bytes never become a
route credential or execution authority.

Direct-UDP and forced-TCP Sandwurm cells now qualify this exact same-process handoff with two
simultaneously positive object prefixes, exact retained/resumed byte equality, zero fallback, stale
terminal fencing, full activation, route recovery, and subsequent protected Ratox. ADR 0224 and
`evidence/2026-08-28-sandwurm-sync-byte-resume.md` bind the result. This does not qualify restart
continuation, Tor-to-Tor/I2P, repeated loss, or byte striping.

Actual-Tor compact proof `pair.3u5cjbci` separately kills the independently supervised Tor process,
resumes 102,825 aggregate prefix bytes through the native survivor with zero worker restart, and
recovers the same Tor member. That is mixed-class construction evidence, not a signed authorization
to cross classes; `evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md` owns its nonclaims.

File offers received without that exact bulk authentication are cancelled rather than retained.
Primary-trust replacement cancels existing worker transfer state before clearing reciprocal proof.

Shutdown quiesces carrier service, then event consumption, then worker file-transfer managers and
auxiliary transports before the primary transport is released. A savedata/key crosswire fails inside `ToxTransport` before that
worker bootstraps, registers a relay, or iterates. This is a per-worker identity guarantee;
all-worker atomic network activation is not claimed by this slice. Whole-object two-guest
loss/recovery and the first fixed/adaptive admission-topology comparison are qualified. ADR 0172
also qualifies terminal single-pull cancellation after positive exact-worker progress, zero residual
signed work, and bounded tails on UDP and TCP. ADR 0173 qualifies the complete eight-job signed
population, and ADR 0174 qualifies four balanced simultaneous cancellations with four survivor
activations. ADR 0175 qualifies one loss→reassignment→replacement-progress→cancel order and lets
the explicit qualification restart proceed after a complete or cancelled affected pull; it does not
add automatic production recovery. Policy phase order itself is counterbalanced by ADR 0171. ADR
0176 closes both exact corresponding auxiliary readiness orders without changing route framing or
signed inventory. ADR 0177 closes the opposite deterministic cancellation→loss order. ADRs 0178 and
0179 close both shared-arm authority outcomes per carrier, not a randomized timing distribution.
ADR 0180 closes one eight-job/four-affected population loss and the steady-state auxiliary
event/carrier liveness cycle. ADR 0181 closes new admission through the sole survivor after active
loss and the corresponding clean-shutdown ordering. ADR 0182 closes new admission through one
authenticated ready route after a clean same-state Agent restart and proves a delayed healthy route
does not migrate either live 16 MiB job. ADR 0183 adds an ABBA two-job 16 MiB comparison on both
carriers and freezes the application-generation handshake needed when Tox stays online across Agent
replacement. Fixed selects one route twice; adaptive selects both. The observed aggregate gain is a
logical-path result on one shaped TAP, not byte striping or physical bonding. Multi-worker byte
striping, randomized larger-load performance/fairness/resource behavior, physical route absence,
random startup/fault timing, affected populations larger than four jobs, common-link physical QoS,
independent bottlenecks/relays, and long-running production policy remain open.

ADR 0269 separately allows one content-v2 source/authority session to select two exact auxiliary
workers before HEAD dispatch. It assigns whole immutable objects, records positive contribution per
path, and fails the whole job on exact selected-worker loss. Route-local friend/file numbers are not
worker-global identities: both accepted Tor workers use `friend=0`, so FileId/CTA1 terminals join
only under the full route key, worker incarnation, and carrier epochs. This qualifies logical
same-source carrier distribution, not byte striping, transparent bonding, balanced placement,
independent circuits/links, or throughput gain.
