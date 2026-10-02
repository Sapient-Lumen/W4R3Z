# IoTox decision ledger

Accepted decisions are historical records. A changed decision receives a new ADR that
names what it supersedes; the old record is not rewritten into agreement.

| ADR | Decision | Current consequence |
|---|---|---|
| 0001 | C++20 with a narrow runtime c-toxcore adapter | IoTox-owned implementation stays C++; external C is isolated |
| 0002 | Separate transport from route | Tox/native, Tox/Tor, and Tox/I2P are route forms; direct overlays are separate transports |
| 0003 | Structured core, ratox façade | Unix simplicity sits over explicit semantics |
| 0004 | Permanent RecallRoot-v1 | Re-entry is reproducible from a strong generated phrase and permits offline guessing |
| 0005 | No vendor reassignment authority | The project cannot take customer devices |
| 0006 | Keep Tox and contribute infrastructure | Native Tox is first; bootstrap/relay stewardship is encouraged |
| 0007 | Independent authorization ledger | Friendship never grants capabilities |
| 0008 | Mutorr as optional namespace replication | Historical rev0003 integration; narrowed by ADR 0010 |
| 0009 | Lone BOOTSTRAPROSE entrance | All working material lives under `.datacube/` |
| 0010 | Ratox successor is immediate northstar | Mutorr moved to an explicit non-default incubator |
| 0011 | `SOCK_SEQPACKET` local control | Versioned bounded local requests and same-user admission |
| 0012 | Bootstrap/relays are roads | Endpoint operation carries no ownership authority |
| 0013 | One product executable | `iotox run` and local commands share one installed binary |
| 0014 | Dual toxcore provider | Source-linked standalone and dlopen test paths share one API table |
| 0015 | Required-event backpressure | Semantic events do not disappear from bounded queues |
| 0016 | Separate mutation persistence | Friend mutations need not depend on graceful shutdown |
| 0017 | Native finite-file transfer | Bulk path operations use c-toxcore file transfer with safe local policy |
| 0018 | Opaque file handles | Full c-toxcore file numbers are preserved without decoding patterns |
| 0019 | Transactional runtime records | Request and transfer directories appear complete by rename |
| 0020 | Tox presentation and text lane | Human messaging is useful but never device authority |
| 0021 | Private byte-preserving peer journals | Message and protocol bodies stay separate, bounded, and escaped |
| 0022 | Public-key-first peer selection | Friend numbers are local implementation details |
| 0023 | Standard input before FIFO compatibility | Unix pipelines use structured local control today |
| 0024 | Decoded IoTox protocol journal | Valid frames are inspectable without polluting global events |
| 0025 | Canonical HELLO per online epoch | IoTox compatibility is negotiated and frozen per real reconnect |
| 0026 | Linked provider requires official headers | Standalone builds cannot silently use fallback ABI declarations |
| 0027 | Live explicit friend-request inbox | Request accept/reject is public-key-first, transport-only, and currently transient |
| 0028 | Mutual transcript confirmation | Application traffic waits for both exact HELLOs and the selected result to be confirmed |
| 0029 | Custom-packet acceptance and retry | Retry only frozen records that toxcore explicitly did not accept |
| 0030 | Stable Ed25519 device identity above Tox | Device identity survives transport endpoint replacement |
| 0031 | RecallRoot derives one stable owner principal | From memory, the same owner signing authority can return |
| 0032 | Canonical signed authority ledger v1 | Friendship and session state cannot grant application capabilities |
| 0033 | Embedded pinned recall word list | Sovereign re-entry remains inside the one product executable |
| 0034 | Transcript-bound directional stable-principal proof | Tox friendship is transport; each authority direction is independently proved per online epoch |
| 0035 | Capability-gated `device.describe` | The first real operation is bounded, read-only, and principal-bound; ADR 0036 supersedes its transient reservation |
| 0036 | Commit command before transport or effect | Durable identity, exact receipts/results, deduplication, and restart recovery precede any physical effect |
| 0037 | Directional local command lanes | Incoming and outgoing records with equal wire identities coexist without changing the wire protocol |
| 0038 | Command operation registry and restart policy | Names, capability, class, advertisement, and recovery behavior are bound before an operation is admitted |
| 0039 | Generic one-binary command entrance | `iotox command FRIEND OPERATION` enters the same durable engine used by every adapter |
| 0040 | FIFO adapter is not a queue | A private per-peer command FIFO frames ordinary writes into the existing durable engine; FIFO bytes are never durable truth |
| 0041 | Operation executor is transport/storage blind | Validated operations return typed results without calling toxcore or mutating stores |
| 0042 | Runtime projections are atomic, not durable | `/run` files and bounded journals avoid torn reads but never replace signed persistent state |
| 0043 | Ratox message/action FIFOs are live transport lanes | Ordinary byte-preserving writes use native UTF-8 text semantics; ingress, send acceptance, disconnect-scoped receipt, and command authority remain distinct |
| 0044 | Required connection callbacks own online epochs | Friend-list snapshots reconcile inventory; only required ordered connection callbacks open or close protocol epochs |
| 0045 | File receive acknowledges admission, not live residency | Successful RESUME returns a frozen accepted record even when a tiny transfer has already completed asynchronously |
| 0046 | Ratox file FIFOs name finite local files | Ordinary writes name finite local paths; FIFO bytes are never the transfer payload or completion truth |
| 0047 | File control tracks two-sided pause ownership | Local and peer pause facts remain distinct; one side cannot resume the other side's pause |
| 0048 | Friendship mutations are public-key-bound exact-token decisions | Request decisions and established removal use ordinary private FIFOs, but deletion resolves and deletes one public key inside one toxcore owner-thread turn |
| 0049 | Root request FIFO is an exact complete-address adapter | One ordinary atomic write reaches the typed outgoing request operation without becoming a queue or authority grant |
| 0050 | Self-profile projections and mutation FIFOs are distinct | `self/*-set` writes converge on typed control while unsuffixed files remain provider-confirmed reads |
| 0051 | `system.summary` is coarse typed telemetry | Fixed, identifier-free host health crosses the deterministic executor under signed read authority |
| 0052 | Remote controller delegation is a signed ledger append | A recalled owner may delegate only the connected stable controller through an exact owner-signed record |
| 0053 | Remote revocation requires a proven owner | A recalled owner may revoke an active non-owner through an exact signed mutation and correlated result |
| 0054 | Ownership-epoch transition requires successor possession | An adjacent current-owner nomination and successor-signed cut retire every old-epoch principal |
| 0055 | Durable offline outbox lifecycle | Signed v3 schedules freeze offline admission, clock, retry, priority, quota, cancellation, and failure rules |
| 0056 | Genuine tests reuse clean key baselines | Stable test-only Tox/device keys are copied into fresh logical state; explicit fresh generation remains a qualification gate |
| 0057 | Synchronous file chunks and coalesced progress | Chunk data is supplied inside the toxcore callback; required bookkeeping remains lossless while disposable progress projection is sampled |
| 0058 | Cache unchanged live-transfer projections | Atomic runtime truth rewrites only changed records and immediately withdraws terminal entries |
| 0059 | Prioritize interactive work and qualify custom carriers | Weighted owner service and a 20 ms wake cap protect latency; custom lossless is Ratox-first while lossy stays experimental |
| 0060 | Pace interactive traffic and split reliable control from replaceable state | Sparse control/input stays lossless; lossy is eligible only for sequenced replaceable state, and TCP relay is one HOL domain |
| 0061 | Freeze Ratox v1 as a fenced, paced, lossless byte protocol | Canonical 1,200-byte frames carry complete attachment identity and cumulative byte positions; PTY service remains closed |
| 0062 | Complete Ratox R1 with a fail-closed pure session engine | Pre-effect replay reservation, atomic attachment ACKs, lifecycle fencing, bounded events, and session quotas land without PTY or advertisement |
| 0063 | Explicit signed authority-ledger v2 migration | Bit 7 is opt-in after one non-widening signed format transition; v1 meanings and plain `all` remain frozen |
| 0064 | Seal local terminal profiles behind a fork-safe PTY adapter | Strict local policy and a verified Linux process handoff exist before network dispatch |
| 0065 | Gate live Ratox dispatch before network startup | Bit 23 is default-off and selected only after secure construction; exact epoch/authority and retained-send gates own live `0xA2` traffic |
| 0066 | Separate the private terminal controller stream from local control | One owner-private seqpacket stream joins the pure Ratox client to the one-binary terminal without weakening remote authority |
| 0067 | Bound local controller admission and contention | A finite first-OPEN lease and bounded typed-denial path prevent silent or queued same-user clients from monopolizing or confusing the sole terminal stream |
| 0068 | Reserve a signed Ratox host incarnation before network startup | One device-bound durable lease fences concurrent daemons and exact restart succession before Ratox advertisement |
| 0069 | Measure queue tails and typed Ratox send outcomes | Exact-at-the-gate histograms, coherent provider outcomes, retained-head pressure, and steady lifecycle time make R7 stalls observable |
| 0070 | Qualify Ratox R7 with bounded fail-closed evidence | One canonical two-route load matrix and deterministic analyzer gate shape R7 evidence; sanitizer sharding remains opt-in |
| 0071 | Bind Ratox R7 to an attested raw-evidence chain | Balanced schedules, raw same-clock timestamps, exact byte/event joins, auxiliary digests, and two capture signatures bind one canonical run |
| 0072 | Seal terminal capabilities and add tiered kernel confinement | Every target receives capability hygiene; baseline adds seccomp, while strict adds fail-closed MDWE and Landlock ABI 10 |
| 0073 | Fence terminal lifecycle and contain baseline PTY sessions | Baseline inspects dangerous ioctl and clone arguments; modern supervisors observe the exact child through a pidfd |
| 0074 | Pin session identities and seal the terminal process domain | Procfs directory/start-time witnesses, repeated quiescence, payload process-handle denial, and host non-dumpability narrow the PTY process boundary |
| 0075 | Own hardened PTY lifecycles with delegated cgroup v2 | Optional fail-closed session leaves use cgroup.kill and recursive populated quiescence |
| 0076 | Bind local seqpacket records to kernel sender evidence | Bidirectional per-record credentials, optional sender pidfds, ancillary rejection, and exact socket ownership close descriptor-handoff gaps |
| 0077 | Bound and multiplex local seqpacket admission | Readiness-driven pending sets, per-process quotas, and refill budgets remove silent-peer head-of-line waits without widening local authority |
| 0078 | Pin local seqpacket connections to peer process lifetimes | Optional `SO_PEERPIDFD` handles release retained pre-record sockets and dead-server waits without reopening numeric PIDs |
| 0079 | Bind delegated cgroup lifecycles to boot and process incarnations | Versioned boot/PID/start-time ownership plus lease-serialized bounded recovery reclaims only proved-stale leaves |
| 0080 | Enforce global PTY resource budgets in delegated cgroups | Optional pids, memory, swap, and CPU controls are preflighted, applied, and read back before payload attachment |
| 0081 | Compose profile cgroup budgets under host ceilings | Local profile limits may only preserve or tighten host maxima, and every distinct effective policy is proved before exposure |
| 0082 | Admit PTY sessions under exact aggregate cgroup reservations | Effective process, memory, and swap maxima are atomically reserved before mutation; unproved teardown strands rather than releases capacity |
| 0083 | Admit exact rational aggregate CPU bandwidth | Heterogeneous finite `cpu.max` ratios normalize exactly into the same atomic reservation vector |
| 0084 | Add a soft memory throttle and retain exact kernel session outcomes | Canonical profile v4 adds monotone `memory.high`; proved teardown contributes bounded content-free controller counters |
| 0085 | Add exact-device I/O ceilings and retain kernel I/O accounting | Canonical profile v5 applies semantic `io.max` policy and preserves bounded unlabeled `io.stat` outcomes |
| 0086 | Retain exact per-session cgroup pressure-stall outcomes | Optional zero-baseline CPU, memory, and I/O PSI totals survive proved teardown with explicit capability counts |
| 0087 | Retain cgroup lifetime peaks and complete CPU work | Optional zero-baseline resource peaks and quota-independent CPU tuples survive proved teardown with explicit capability counts |
| 0088 | Retain memory work, swap failures, freeze duration, and IRQ pressure | Descriptor-pinned cumulative work and stall evidence survives proved teardown without fabricating unsupported capabilities |
| 0089 | Admit new PTY sessions with cgroup PSI hysteresis | Exact delegated-root PSI samples fail closed before reservation or spawn mutation and reopen only below configured hysteresis boundaries |
| 0090 | Latch admission with continuous cgroup PSI triggers | One descriptor per trigger, bounded monitor shutdown, full-window hold, hysteresis recovery, and fail-closed monitor loss |
| 0091 | Reserve synchronization authority without widening v2 | Four v3-only capabilities require explicit migration and later grant |
| 0092 | Freeze synchronization service admission | Exact-head negotiated authority and namespace policy precede every future service effect |
| 0093 | Use stable device identity for signed synchronization HEADs | Publication has no parallel toxsync trust root |
| 0094 | Commit immutable synchronization objects before HEAD | Artifact and manifest verification precede the only mutable publication pointer |
| 0095 | Serialize sync publishers and account objects | One process lock and prospective whole-store quotas bound publication |
| 0096 | Freeze bounded synchronization retention before GC | Explicit accepted revisions are pinned; deletion remains absent |
| 0097 | Authenticate synchronization retention without claiming anti-rollback | Signed hash-linked snapshots detect alteration, not complete replay |
| 0098 | Plan synchronization reachability before removal | Mark-only evidence distinguishes rooted, missing, mismatched, and unreferenced objects |
| 0099 | Unify local synchronization under one namespace transaction | All implemented mutations and stable reads share one process/thread-bound lock proof |
| 0100 | Authenticate accepted synchronization state | Unsigned, foreign, and altered accepted HEADs fail closed |
| 0101 | Authenticate synchronization activation state | Activation pointers use an independent stable-device signature domain |
| 0102 | Freeze the local synchronization rollback guard | Four committed/pending roots distinguish the two exact power-cut sides |
| 0103 | Wrap synchronization root mutations in the rollback guard | Every live root replacement and stored reachability check uses the signed guard |
| 0104 | Reconcile synchronization duplicates after uncertain commit | Exact retries finalize either valid guarded failure side before returning |
| 0105 | Round-robin pinned toxcore file service | A named source-linked variant removes low-slot starvation without widening queues |
| 0106 | Stripe bulk with per-route headroom | Four independent TCP routes qualify eight bulk streams each; higher admission is not capacity |
| 0107 | Restart routes without silent degradation | Bounded savedata-preserving establishment retries fail closed until every named route confirms |
| 0108 | Coordinate routes above Tox | Stable-principal-bound routes protect Ratox and schedule immutable bulk objects without pretending to be one socket |
| 0109 | Reserve and fence the protected route | Ratox gets a bulk-free resource class; failed bulk cancellation fences and recycles only the affected worker |
| 0110 | Sign route inventory with the stable device | Exact principal, generation, transcript, protocol, role, and budget claims precede route readiness |
| 0111 | Checkpoint route generation before networking | Private signed high-water state rejects ordinary rollback and forks before toxcore starts |
| 0112 | Fence route savedata and bind confirmed transcripts | Exact expected Tox keys fail before networking; signed route evidence derives from the canonical session |
| 0113 | Supervise auxiliary routes in process | Independent exact-key toxcore owners share no authority state and remain unschedulable until binding |
| 0114 | Carry the signed route set with each binding | One bounded frame verifies the complete set against local principal and generation trust before transcript membership |
| 0115 | Anchor auxiliary routes in primary-session authority | Bounded primary trust, generation/fork state, and exact-epoch replay admission precede worker readiness |
| 0116 | Freeze one binding per worker epoch | Construction-gated workers send one frozen proof, retain one reciprocal record, and latch invalid verification |
| 0117 | Drive route readiness from reciprocal proof | Agent primary authority populates worker trust; two-sided bindings alone advance a member to ready |
| 0118 | Fence immutable synchronization object attempts | Stable object and attempt identities make reassignment stale-safe and reserve only ready bulk routes |
| 0119 | Derive private staging from attempt identity | Exact attempt paths are no-clobber received, verified, transactionally object-committed, or shape-safe discarded |
| 0120 | Reserve staging bytes with route work | Every live object attempt consumes its full namespace byte budget until fence or commit |
| 0121 | Own file-transfer state per bulk worker | Exact authenticated worker incarnations contain bounded file numbers and receive destinations |
| 0122 | Bind worker terminals to sync attempts | Reserved lossless outcomes drive verified object commit and exact attempt fencing |
| 0123 | Persist live sync attempts before receive | Signed high-water and active records reconstruct commit or fence without reviving Tox handles |
| 0124 | Bind sync requests to explicit Tox file IDs | Fixed HEAD/object frames join authorized requests to filename-independent bounded worker offers |
| 0125 | Use toxsync SHA-256 object identities | The preserved content identity is reused through a race-detecting production file hasher |
| 0126 | Admit publisher effects behind bounded epoch replay | Exact v3 subscribe authority, HEAD pinning, pre-effect replay retention, and FileId offers form one default-off gate |
| 0127 | Construct the default-off sync vertical slice | Strict Agent wiring, bounded worker dispatch, durable subscriber attempts, exact retry, and accepted-HEAD-last ordering form the first operable path |
| 0128 | Bind range manifests before publication and activation | A canonical toxsync range index must describe the exact immutable artifact before published, accepted, or activated root mutation |
| 0129 | Recover crashed synchronization transport temporaries | Signed attempt identity scopes exact fail-closed pre-rename cleanup before journal clearance |
| 0130 | Install synchronization namespaces without clobber | Canonical same-user creation is unnamed-file durable, atomic, live-reloaded, and never replacement |
| 0131 | Cancel synchronization pulls before cleanup | Process-local job identity becomes terminal before receive, staging, journal, and scheduler fencing |
| 0132 | Fence synchronization pulls across online epochs | Disconnect terminally retires the old job; only explicit retry on a higher authenticated epoch may continue |
| 0133 | Administer synchronization namespaces only while quiescent | Live membership/activation replacement and policy-only removal serialize, preserve data, and fail closed on reload uncertainty |
| 0134 | Pause synchronization receives without retiring the job | One live FileId and attempt retain their identity, reservation, and authority state while local flow control is paused |
| 0135 | Recover synchronization publisher guest restart from persisted state | Reboot preserves durable publication truth but retires transport; a higher stable epoch and explicit whole-object pull recover the subscriber |
| 0136 | Negotiate bounded range reconstruction | Manifest-first local planning fetches one canonical missing-range bundle, verifies the complete artifact, and accepts the HEAD last |
| 0137 | Recover from an unusable synchronization basis | Missing or corrupt accepted basis bytes trigger a fully verified whole-successor request without deleting local objects or weakening HEAD/activation ordering |
| 0138 | Retry one fully cleared range attempt | One same-epoch retry gets fresh durable and transport identities only after exact staging, journal, and scheduler clearance |
| 0139 | Bind deterministic directory revisions as treepack-v1 | Signed engine 3, bounded canonical packing, post-commit atomic projection, exact retry, and derived-tree cleanup define directory sync |
| 0140 | Bound directory-projection crash recovery | Exact pointer-temporary recovery and eight separate-process crash checkpoints preserve one complete old-or-new tree |
| 0141 | Keep synchronization pressure off the transport pump | Nonblocking telemetry and best-effort maintenance preserve bounded queue admission and terminal latency under publisher work |
| 0142 | Share the v1 object and tree-entry ceiling explicitly | Saturate immutable-store count without making the admitted tree itself invalid |
| 0143 | Fail closed before synchronization effects on read-only storage | Transaction setup refuses pull and activation before mutation; exact retry is explicit |
| 0144 | Measure synchronization process high-water without calling it a quota | Maximum-entry dual-carrier `VmHWM` evidence stays distinct from hard runtime enforcement |
| 0145 | Verify synchronization source objects before offering them | Publisher bit rot is refused at request time; explicit quarantine, exact republication, and explicit retry recover the same signed revision |
| 0146 | Verify synchronization destinations and reuse valid progress | Completed transport bytes are hashed before commit; valid sibling objects reduce explicit retry traffic |
| 0147 | Retain exact synchronization controls and refuse conflicts | Same-epoch request replay returns one retained result without repeating file offers; conflicting reuse fails closed |
| 0148 | Reapply only one bounded desired state | Durable `profile.status.set` converges through provider readback and may repeat only its exact value under the same principal, ownership epoch, and fresh authority |
| 0149 | Quarantine unreferenced objects without purge | Descriptor-pinned no-replace moves reclaim active-store quota without granting permanent deletion authority |
| 0150 | Bind release components and compare clean builds | Deterministic SPDX plus distinct empty build roots expose dependency and build-path drift |
| 0151 | Distinguish partial-loss continuity from outage recovery | Seeded bilateral TAP loss must preserve the epoch while exposing carrier-specific delivery behavior |
| 0152 | Qualify provider savedata before rolling network upgrades | Exact previous-provider state must survive current product load before mixed-version route claims |
| 0153 | Qualify live mixed-provider routes in Sandwurm | Exact old/current providers must exchange bilaterally on both native carriers before a rolling claim |
| 0154 | Bound cumulative Ratox output-ack replay in constant space | One attachment retains an exact cumulative ACK high-water fence while side-effect controls keep never-evicted replay |
| 0155 | Separate Ratox render timing from live queue evidence | Render completes before evidence inspection, and authenticated in-memory snapshots expose live transport counters without depending on a coalesced filesystem projection |
| 0156 | Tighten Ratox cadence only for live attachments | Active terminal state uses 5 ms transport/service caps and immediate local wakes; idle cadence is restored |
| 0157 | Separate Ratox service from required-event draining | One independent cadence worker keeps bounded required file backpressure from suppressing interactive progress |
| 0158 | Reduce per-chunk file-event work | Sample redundant inline-send progress and retain one pinned receive descriptor while exposing exact backpressure counters |
| 0159 | Preserve file-callback pacing until explicit scheduling | Failed coalescing exposed reliable carrier HOL; restore required per-chunk bookkeeping while retaining cheaper receive and diagnostics |
| 0160 | Reserve semantic headroom with explicit file pacing | Pause file callbacks at 64 events and resume below 16 after 5 ms without using queue saturation as the normal scheduler |
| 0161 | Count paced transfers as present | Bulk evidence treats active and intentionally paused transfers as live while preserving exact population and progress accounting |
| 0162 | Resume paced files in bounded oldest-first batches | Resume one oldest eligible producer per toxcore iteration instead of releasing every paused file in one burst |
| 0163 | Bound runnable incoming files per peer | The receiver admits one incoming file carrier per peer and rotates accepted waiters without changing framing or transfer identity |
| 0164 | Coordinate file-pacing ownership | Typed already-paused handoff separates proactive and reactive resume ownership; a 50 ms quantum reduces churn and bounded cancellation tombstones absorb queued terminal events |
| 0165 | Freeze the qualified single-Agent transfer ceiling | One Agent qualifies at 32 accepted sends/receives; larger explicit values remain experimental and excess work stays outside the accepted population |
| 0166 | Defer full-ledger synchronization offers | A paused exact FileId offer keeps its immutable attempt while bounded fair service waits below the 32-receive ceiling |
| 0167 | Bound auxiliary synchronization object frames | A default-off authenticated bulk carrier accepts only canonical object request/result records into one incarnation-fenced bounded parent queue |
| 0168 | Bind sync authority to an exact transfer carrier | Primary proof authorizes one exact object-only worker; loss fences before fresh immutable-object reassignment |
| 0169 | Qualify immutable sync reassignment across live routes | Exact mid-object loss fences, reassigns, rejects stale truth, restores the worker, and preserves protected Ratox on UDP and TCP |
| 0170 | Select sync routes by bounded visible load | Adaptive admission minimizes exact signed-capacity utilization without moving healthy work or changing framing |
| 0171 | Qualify load-aware sync admission topology | Counterbalanced genuine UDP/TCP A/B proves fixed reuse and adaptive idle-route placement without making a throughput claim |
| 0172 | Qualify bounded multi-route sync cancellation | Exact auxiliary byte progress, terminal withdrawal, zero residual signed work, and bounded UDP/TCP tails close the first cancellation row |
| 0173 | Qualify bounded multi-route sync population | Eight jobs fill both signed route budgets with exact fixed/adaptive patterns, full activation, resource intervals, and protected Ratox |
| 0174 | Qualify concurrent route cancellation and separate physical QoS | Four balanced simultaneous withdrawals preserve four survivors on UDP/TCP; a larger shared-FIFO failure remains a distinct common-link gate |
| 0175 | Qualify loss before cancellation and terminal recovery | An affected pull reassigns, progresses, cancels without migrating again, and permits bounded qualification-worker recovery on UDP/TCP |
| 0176 | Qualify exact auxiliary readiness order | One exact worker must become reciprocally ready before a post-authentication hold releases its peers; both corresponding orders pass on UDP/TCP without framing changes |
| 0177 | Qualify cancellation before route loss | A settled cancelled pull retains its exact carrier identity; subsequent loss causes zero reassignment and one bounded route recovery on UDP/TCP |
| 0178 | Qualify the cancellation and route-loss race | One shared arm edge drives ordinary cancellation and exact-worker loss; terminal authority linearization, bounded cleanup retry, and route recovery are strictly evidenced on UDP/TCP |
| 0179 | Qualify both shared-arm linearizations | A fault-leading companion requires one real reassignment and replacement cancellation; both authority outcomes now pass genuine UDP/TCP cells |
| 0180 | Qualify population route loss without blocking event delivery | Four same-carrier jobs migrate as complete work sets; bounded transient refusal retry and split auxiliary event/carrier service preserve convergence and protected Ratox on UDP/TCP |
| 0181 | Qualify new admission during active route loss | Two migrated and two genuinely late jobs converge through the sole survivor; carrier-first shutdown quiescence preserves required-event liveness on UDP/TCP |
| 0182 | Qualify degraded-route admission after Agent startup | Two large jobs start through one authenticated ready route and remain on it when the held route joins; UDP/TCP evidence separates controlled readiness from physical absence |
| 0183 | Freeze application restart and qualify multi-route throughput | Durable process incarnation plus process-local connection epoch prevents false HELLO conflict; fixed/adaptive 16 MiB ABBA cells pass on UDP/TCP |
| 0184 | Separate signed update intent from sync delivery | A canonical release-signed bundle stays inert until independent owner-local update policy and lifecycle gates admit it |
| 0185 | Qualify the signed update slot lifecycle | Device-signed state, later-incarnation health, deterministic crash recovery, and fail-closed inactive slots pass UDP/TCP without advertising remote OTA |
| 0186 | Authorize remote update staging through durable commands | Exact accepted-HEAD ICQ2/IUS1 records reuse signed command authority, replay, quotas, restart, cancellation, and audit while keeping apply local |
| 0187 | Freeze release signer revocation policy | Policy v2 adds a signer epoch plus bounded revoked release keys for future-staging denial without changing signed bundle v1 |
| 0188 | Operate release keys and quarantine update slots | No-clobber signer creation, reviewable epoch rotation, and bounded recoverable slot quarantine add no purge or remote authority |
| 0189 | Freeze the Linux service deployment adapter | A distinct signed kind enters one sealed native-image helper and sequence-bound readiness/rollback path without reinterpreting opaque slots or granting remote execution |
| 0190 | Freeze the strict Tox/Tor SOCKS route | Explicit numeric proxy/bootstrap/relay policy disables UDP, native DNS, discovery, compiled catalogs, and fallback; SOCKS plumbing is not itself a Tor claim |
| 0191 | Qualify the operator Tor public route without claiming anonymity | Exact Tor control/process-socket evidence proves one public relay route across restart; multi-peer reliability and anonymity remain unclaimed |
| 0192 | Separate auxiliary route health from carrier truth | On-demand local-boundary and confirmed-peer observations remain content-free and cannot relabel c-toxcore or advance a session epoch |
| 0193 | Bound persistent route and Ratox heartbeats | Independent process-local latches and one exact PING per attachment add warning-only liveness without replay growth or carrier/session mutation |
| 0194 | Probe only the configured SOCKS target | One-shot numeric SOCKS5 CONNECT observes the first frozen relay without accepting arbitrary targets or mutating carrier/session truth |
| 0195 | Bind the configured target to authenticated Tor control | Exact NEW-to-SUCCEEDED source/stream correlation joins relay zero to a three-hop general or linked-Conflux application circuit |
| 0196 | Qualify Ratox under bounded route impairment | Keep carrier, heartbeat, PTY progress, and visible stall distinct; partial impairment warns without mutating the authenticated session |
| 0197 | Freeze Ratox total-loss recovery | Authoritative offline detaches the controller while retaining the remote PTY; explicit higher-epoch resume preserves exact session identity and byte positions |
| 0198 | Separate route identities and keep inventory private | Native and privacy-routed contexts use independent random Tox savedata by default while authority-confirmed primary exchange gates cross-route roster disclosure |
| 0199 | Split private route inventory from member proof | Negotiated v2 sends the full signed roster only on an authority-authenticated primary edge and binds one digest-anchored proof on the auxiliary transcript |
| 0200 | Gate private workers on primary inventory | Explicit v2 construction freezes bounded primary replay/high-water state, hands only admitted inventory to workers, and withdraws auxiliary readiness with the authority edge |
| 0201 | Qualify private routes across network contexts | Exact-key worker network policy and race-safe context adoption converge signed sync through native and strict generic-SOCKS members without disclosing the roster on auxiliaries |
| 0202 | Bind workers to independent rendezvous catalogs | Exact-key bounded bootstrap and relay replacements let privacy workers use independently reachable infrastructure without changing signed route membership |
| 0203 | Qualify two independent Tor route workers | A distinct Sandwurm cell joins each guest's exact Tor auxiliary to its own Tor process/control evidence while native routes retain the private fixture |
| 0204 | Attribute sync payload to an actual-Tor member | A distinct stable-key qualification cell requires the completed zero-reassignment sync job to name the exact Tor member without adding a production force knob |
| 0205 | Count real carrier recovery and fault the Tor process | Production lifecycle telemetry counts the actual member's return; a host-killed Tor process proves exact loss, native reassignment, and recovery without restarting IoTox's route worker |
| 0206 | Qualify Ratox across actual-Tor process loss | Kill only the client Tor process after PTY progress, separate heartbeat from carrier loss, retain the detached host PTY, and explicitly resume the same session after Tor returns |
| 0207 | Qualify Ratox duration across actual-Tor circuit churn | Accepted `pair.k8o54n2v` holds one session/PTY/byte timeline for 120 paced samples while exact client/device circuit replacements exercise same-epoch PONG continuity and authoritative-loss explicit resume |
| 0208 | Repeat Ratox churn across a distinct relay record | Accepted `pair.9cx0jels` repeats the unchanged gate on a second public record and proves that Tor stream reopening does not predict Ratox continuity versus explicit resume |
| 0209 | Construct and qualify an adversarial local Tor boundary | Accepted `pair.vx6z0csh` keeps listener and fresh SOCKS target admission positive while held relay bytes produce Ratox warning, authoritative offline, detached PTY, and exact higher-epoch resume without Tor/interposer/IoTox restart |
| 0210 | Account for actual-Tor target-circuit populations | The expanded eight-proof corpus resolves 30 exact-target/churn declarations to 24 three-hop paths and 23 last hops without promoting population observations into exit/time/anonymity claims |
| 0211 | Construct the strict I2P SAM boundary | A lab-only numeric SOCKS-to-SAM v3.1 adapter freezes exact b32 mapping, transient session identity, bounded concurrency, loss/recovery, and no-fallback behavior while product `tox/i2p` remains unsupported |
| 0212 | Qualify actual I2P SAM streams | Two distinct source-attributed i2pd processes carry one warm-up and four simultaneous exact streams while a strict receipt joins router, source, destination, payload, and adapter-audit commitments |
| 0213 | Freeze the I2P Tox-service construction | A persistent owner-only Destination and exact silent SAM forward expose one loopback TCP service; lab-only `tox/i2p-construction` reuses strict routed-Tox containment while `tox/i2p` stays unsupported |
| 0214 | Budget slow-overlay TCP establishment | The pinned provider gives proxy plus SAM/I2P plus encrypted relay setup 120 seconds while onion and established-carrier lifetimes remain upstream-exact |
| 0215 | Preserve Tox node addresses across I2P service fronts | Fresh TCP-only I2P uses at least three exact address-preserving node fronts; a two-peer application E2E pass falsifies the onion-timeout patch |
| 0216 | Qualify the Sandwurm actual-I2P baseline | Accepted `pair.k_vopzf5` joins two source-linked guests, three persistent fronts, canonical session/text, strict TAP containment, and secret-free verification |
| 0217 | Qualify I2P router loss and recovery | Accepted `pair.v_11i2me` separates a live adapter from lost SAM, replaces the exact router over preserved state, and proves bilateral higher-epoch text without fallback |
| 0218 | Qualify I2P service-front replacement | Accepted `pair.6rrdsdc_` replaces all three persistent fronts over unchanged Destination keys while both routers stay live and both guests recover at higher epochs without fallback |
| 0219 | Qualify a bounded private-member I2P sync payload | Accepted `pair.5xjf2n4d` assigns one exact 131,369-byte signed tree to the authenticated I2P member with zero reassignment; larger-object loss exposes the need for chunk/range and signed privacy-class failover policy |
| 0220 | Add fail-closed synchronization route loss policy | Separate initial placement from replacement; explicit fail-closed mode fences loss, retains the original carrier/job, counts the block, and never selects an available route |
| 0221 | Freeze failover intent per synchronization pull | One explicit per-job choice overrides the process default, survives retry, and controls the same first-byte-loss oracle |
| 0222 | Pin synchronization pulls to a constructed route class | Named classes select only exact authenticated auxiliary worker contexts and never fall back to primary |
| 0223 | Freeze private-prefix file resume | One exact caller-owned private prefix survives carrier loss and resumes through Tox seek without weakening final verification |
| 0224 | Resume whole synchronization objects across route loss | A fresh attempt and carrier inherit an exact same-process prefix while stale terminals remain fenced and full digest gates commit |
| 0225 | Sign exact route network classes | Route-set v2 binds every member key to native, Tor, or construction-I2P and enforces primary, worker, and coordinator agreement |
| 0226 | Qualify fail-closed I2P route loss | Fault the signed I2P member after positive sync bytes, forbid native reassignment, explicitly cancel the blocked job, and complete a fresh pull on the recovered member |
| 0227 | Carry bounded sync ranges over authenticated auxiliary routes | Reuse frozen range-v1 frames only after primary and exact-worker negotiation; accepted I2P proof reconstructs 4 MiB from one 128-byte fetch plus verified basis bytes |
| 0228 | Qualify fail-closed I2P range loss | Fault a concrete range after positive bytes, discard it without downgrade, recover the same member, and permit convergence only through explicit cancellation plus a distinct fresh range pull |
| 0229 | Reuse verified range manifests locally | A fresh range job re-proves an exact durable manifest, emits only the missing-range request, and still accepts the signed HEAD only after both immutable objects commit |
| 0230 | Resume bounded range retries from exact prefixes | One same-job/same-carrier retry hands an exact private prefix to fresh durable and transport identities, seeks to it, and retains complete verification |
| 0231 | Resume bounded ranges across available carrier loss | One available-policy range hands an exact private prefix to a fresh attempt on a distinct authenticated carrier while fail-closed loss still discards and blocks |
| 0232 | Qualify repeated native bounded-range loss | Direct UDP and forced TCP preserve one exact range prefix through two sequential authenticated carrier deaths with fresh attempts, exact cumulative accounting, and no retransmission fallback |
| 0233 | Qualify late native bounded-range loss | Direct UDP and forced TCP preserve at least 15/16 of one exact range across carrier death and receive only the bounded suffix under fresh identities |
| 0234 | Resume exact whole objects after daemon restart | Retain only strict device-signed prefixes; direct UDP and forced TCP prove fresh authorized pulls seek under fresh identities and verify the complete digest |
| 0235 | Qualify three sequential native bounded-range losses | A bounded lab-only third fault proves another exact prefix handoff, two request-hold releases, alternating carrier parity, and healthy exhaustion of one route's restart budget |
| 0236 | Retry exact application-handshake records | Bounded HELLO and CAPABILITIES retransmission closes an asymmetric reconnect race while preserving the frozen online-epoch transcript |
| 0237 | Bind sync attempt tombstones to namespace policy | Per-pull fence history uses the validated host-local request ceiling; the three-loss lab grants the exact fifth record it needs |
| 0238 | Render remaining route restart budget explicitly | Route status keeps the signed restart ceiling and derives its unambiguous remaining capacity beside the consumed restart count |
| 0239 | Bind bounded-range prefixes across daemon restart | ATM1 commits the exact local range plan and bundle length so only a fresh authorized pull deriving the same plan may resume a strict prefix |
| 0240 | Package opt-in bootstrap/relay stewardship | An inert NixOS module, pinned single-port daemon, private identity, resource bounds, and VM gate let owners contribute capacity without creating IoTox authority or mandatory infrastructure |
| 0241 | Qualify shared-edge fair queuing | HTB plus fq_codel restores protected Ratox at the previously failing 1 MiB/job shared-link load on direct UDP and forced TCP, without becoming a striping or universal-QoS claim |
| 0242 | Separate content sources from signed-HEAD authority | Additional content-v2 sources require exact-head v3 proof, sync.publish, writer membership, and the frozen signed-HEAD digest without gaining HEAD-transition or activation authority |
| 0243 | Repeat actual-Tor in a later operator window | A third-relay 120-sample two-IoTox churn proof adds four nonreused paths while preserving explicit resume authority and the unqualified wall-clock/exit-operator boundary |
| 0244 | Freeze the bounded content-v2 object fabric | Dark feature bit 29 and types 28/29 bind exact immutable objects to one frozen HEAD while a bounded authority-gated coordinator and replay-safe publisher await live Agent qualification |
| 0245 | Freeze exact content-v2 availability | Dark types 30/31 bind a bounded exact sparse window to one frozen HEAD so complementary authorized stores can schedule without complete-mirror claims |
| 0246 | Bind the content CAS to namespace quotas | One strict transaction-bound physical inventory counts the canonical SHA-256 CAS and flat objects against the same namespace ceilings without granting publication or deletion authority |
| 0247 | Enforce content CAS commits | Canonical private roots, exact staging identities, verified-copy publication, and prospective combined quotas close the content coordinator's local write bypass while bit 29 stays dark |
| 0248 | Sign content-v2 attempt restart truth | CTA1 binds each frozen HEAD/object/FileId/carrier assignment before effect and recovers only verified complete objects while fencing partial or absent work |
| 0249 | Publish the complete content CAS before signed HEAD | Local flat/paged publication preflights the whole fabric, verifies every CAS commit, and signs HEAD last while exact abandoned workspaces recover safely |
| 0250 | Bootstrap and accept complete content revisions | A root-manifest kind plus CTA1-gated one-source subscriber reconstructs whole CAS and advances accepted HEAD last while early offers remain paused |
| 0251 | Dispatch and maintain content-v2 in the Agent | Dynamic bit-29 advertisement follows complete construction; primary-carrier convergence, explicit activation, signed reachability, repair, and quarantine GC now pass the deterministic Agent gate |
| 0252 | Qualify one-source content-v2 on genuine native carriers | One paged 4 MiB revision converges and explicitly activates through independent c-toxcore microVMs over direct UDP and forced TCP, with exact shape retained in compact evidence |
| 0253 | Promote the qualified Tox/I2P route without changing its wire class | The canonical production spelling reuses signed class 3 and strict savedata/provider policy; two actual-I2P microVM guests pass with zero native fallback |
| 0254 | Consume exact sparse content from explicit primary peers | An owner-local job mutation adds independently authorized writers while the original HEAD stays frozen; complementary stores converge deterministically through exact availability windows |
| 0255 | Qualify genuine multi-source content on native UDP | Two authorized live sources contribute exact objects to one frozen HEAD over direct UDP; thirteen forced-TCP relay/admission/rendezvous cells retain a measured durable-second-session limitation rather than an accepted claim |
| 0256 | Qualify fail-closed selected content-source loss on native UDP | Atomic owner-local source admission removes the initial race; selected-source loss fences the whole job and a distinct explicit pull converges only after higher-epoch recovery |
| 0257 | Persist availability-only replica HEADs | One foreign-writer content-v2 HEAD gains device-authenticated custody, partial-graph GC rooting, and cold-start service without entering publication, acceptance, or activation authority |
| 0258 | Bind content sources to exact auxiliary routes | Primary sessions retain writer/HEAD authority while frozen content lanes may use independently fenced workers; one-source actual-Tor passes and loss remains fail-closed |
| 0259 | Qualify multi-source content over exact actual-Tor workers | Two native-authority publishers contribute complementary objects through distinct Tor worker identities in one atomic pull; per-source carrier evidence and strict effective-topology preflight make the claim independently verifiable |
| 0260 | Qualify selected actual-Tor content-worker loss | Positive-progress loss fails the whole content job without downgrade or reassignment; the exact signed route recovers under a fresh worker and only a distinct explicit pull converges |
| 0261 | Repeat actual-Tor content loss through a second relay | The unchanged destructive content gate passes a second public relay record; common loss-manifest fields now share one frozen scenario set while exit/time/long-running claims stay open |
| 0262 | Enable bounded same-source content lanes | A conservative default-one process ceiling and signed namespace quotas permit exact page/chunk overlap while root, HEAD, attribution, and whole-job failure remain unchanged |
| 0263 | Measure same-source content lane scaling | Stable-session 1/2/4/8 Sandwurm cells find a forced-TCP knee at four lanes, retain default one, and defer any bulk profile to repeated and Ratox-latency evidence |
| 0264 | Qualify persistent Ratox under content lane load | One 720-sample attachment spans caps 1/4/8 on UDP and TCP; cap 4 remains a bulk candidate, cap 8 regresses, and fresh post-bulk admission stays separate |
| 0265 | Qualify fresh Ratox admission after content backlog | A newly opened terminal meets the ordinary five-second OPEN bound after reliable cap-8 completion on UDP and TCP, preserves carrier/epoch truth, and completes 40 exact samples |
| 0266 | Counterbalance content lane scaling | Ascending/descending UDP/TCP cells retain default one, recommend explicit cap 2 for efficient mixed bulk and cap 4 for fixed UDP, keep cap 8 stress-only, and reject automatic tuning |
| 0267 | Qualify multi-lane content restart | Cap-2/cap-4 UDP/TCP cells preserve exact complete CAS truth, remove transport residue, fence old attempts, and converge only through a two-sided-authorized distinct pull |
| 0268 | Freeze the cap-two interactive bulk SLA | A persistent Ratox attachment meets one predeclared cross-carrier construction SLA at explicit cap two; default one remains and caps four/eight miss the p95 ceiling |
| 0269 | Distribute same-source content across exact auxiliary carriers | Repeating one routed source selector binds one authority session to distinct workers; both contribute whole objects over actual Tor while route-local friend collisions remain safe and framing stays frozen |
| 0270 | Build everyday one-writer synchronization automation | Device-signed publish/follow policy drives existing bounded sync and exact activation paths; deterministic local restart establishes the construction boundary |
| 0271 | Add owner sync creation and read-only sharing ceremonies | One command creates managed one-writer automation; RecallRoot-bound sharing adds only exact subscriber authority/membership while read-write remains refused pending a multiwriter protocol |
| 0272 | Freeze the tree-v2 local multiwriter core | Per-file CAS, authenticated writer branches, visible-frontier causality, conflicts, tombstones, atomic projection, and signed recovery state pass locally while peer/Agent read-write remains dark |
| 0273 | Enable pairwise tree-v2 bidirectional synchronization | Bounded authenticated graph exchange, reciprocal owner grants, pair-bound automation, writable reconciliation, repair, and a two-guest offline-conflict gate activate the first read-write surface |
| 0274 | Extend tree-v2 automation to a bounded full mesh | Signed automation-v2 stores canonical remote-principal sets; additive bilateral grants and independent fair retry converge three concurrent writers without changing peer framing |
| 0275 | Bound tree-v2 history and retire writers exactly | Negotiated checkpoint floors, workspace-rooted recoverable quarantine, explicit pins, quiescent merges, and exact local writer cutoffs bound lifecycle without adding purge |
| 0276 | Qualify unattended one-writer synchronization | Two-guest UDP/TCP cells install policy once, restart publisher and replica Agents independently, and materialize three exact generations with no manual transfer or activation command |
| 0277 | Freeze founding-machine completion scope | Hosted, independent-party, physical-target, and witnessed public-history checkboxes are retired rather than mislabeled; Sandwurm and the founding machine own the remaining four gates |
| 0278 | Freeze selective tree-v2 projection and owner mode | Canonical local include/exclude prefixes preserve hidden causal state and local files; manifest v2 carries exact private owner r/w/x bits without remote path selection |
| 0279 | Close the founding route-policy campaign | Sixteen integrity-checked UDP/TCP cells provide stratified timing/object populations; adaptive becomes the bounded ordinary selector while physical/QoS claims remain separate |
| 0280 | Extend tree-v2 manifest identity to its quota | Former small digests stay exact; oversized canonical manifests use bounded indexed leaf commitments so the 4,096-entry advertised ceiling is usable |
| 0281 | Close the bounded tree-v2 adversarial gate | Named durable layouts, full 16-way conflicts, 128 seeded arrivals, candidate-17 refusal, and a 4,096-file end-to-end tree make the scale claim finite and testable |
| 0282 | Roll synchronization reads through a bounded exact-replay window | Recent duplicates replay exactly; retired immutable reads re-authorize as fresh work so long-lived sessions cannot exhaust a finite lifetime budget |
| 0283 | Accept the founding sync shadow and close the roadmap | A two-hour networkless IoTox/Resilio shadow crosses the former replay ceiling, survives alternating Agent restarts, and closes the fourth founding-machine gate |
| 0284 | Separate synchronization confidence from backup trust | Founding completion permits bounded synchronization use, while precious-data promotion requires independent versioned recovery plus explicit operator and engineering graduation gates |
| 0285 | Add owner-local Ratox operations without changing Ratox v1 | Canonical profile administration, live host probes, retained-session list/close, and batch attachment land entirely on owner-local surfaces while peer framing remains frozen |
| 0286 | Make owner shells real login accounts with explicit sudo | Profile v6 freezes account groups, denies elevation by default, and permits a separately reviewed non-root compatibility shell to use host-authorized sudo |
| 0287 | Ship an explicit static rescue toolbox | Optional static oksh plus Toybox supplies a qualified baseline fallback without trusting Toybox's pending shell or changing Ratox framing |
| 0288 | Add read-only synchronization source preflight | `sync-doctor` reuses production source rules and reports bounded first-revision estimates without creating a namespace or claiming managed-store/backup truth |
| 0289 | Add exact-session Ratox reconnect | `terminal --reconnect` retries only the exact retained session above the frozen framing and accepts only a higher authenticated generation |
| 0290 | Add canonical Agent configuration and preflight | One owner-private shell-free argument record feeds the existing parser; `run-check` shares non-mutating static preflight with `run` and names recovery-only deferrals |
| 0291 | Add authenticated content-free diagnostics | A device-signed bounded local tail exports only an identity-free closed-field support bundle with offline inspection and explicit non-attestation limits |
| 0292 | Add durable human peer aliases | One signed one-to-one local registry and explicit selector grammar make peer names usable without implicit retargeting or authority |
| 0293 | Add explicit signed peer invitations | One fixed signed address/expiry/nonce artifact supports pinned dry import and replay-safe friendship acceptance while granting zero authority |
| 0294 | Add a forward-only synchronization time machine | Retained tree-v2 history/diff/conflict inspection and exact restore plans re-author old content only as a higher local generation |
| 0295 | Add tree-v2 sparse content custody | Recipient-local prefixes retain complete signed metadata while selected-only transfer, repair, GC, and policy-safe widening report partial custody exactly |
| 0296 | Add tree-v2 exact-probe multi-source recovery | One primary freezes the frontier while bounded complementary sources satisfy immutable objects through existing authenticated result dispositions |
| 0297 | Add signed tree-v2 namespace health | A closed green/yellow/red observation binds selected custody, convergence, conflicts, automation, pressure, and source evidence without content or backup claims |
| 0298 | Join namespace health to content-free diagnostics | Shareable v2 diagnostics aggregate locally verified health without namespace handles and preserve explicit no-witness/no-backup truth |
| 0299 | Add normalized host capabilities to diagnostics | Redacted v3 reuses the live host probe through a passive Agent sampler and exports only closed grades, masks, and counts |
| 0300 | Qualify production Ratox reconnect across real route loss | One unchanged `terminal --reconnect` process resumes the exact retained PTY after seeded direct-UDP and forced-TCP total loss |
| 0301 | Reproduce AArch64 rescue and pin payloads | Static AArch64 oksh/Toybox gains validated SPDX, qemu execution, and profile-v7 descriptor-rechecked SHA-256 pins while native-kernel PTY qualification remains open |
| 0302 | Freeze protected state and witness boundary | Externally unlocked fscrypt covers the complete state closure before startup; a separately controlled pending/committed witness supplies freshness through explicit ceremonies |
| 0303 | Enforce fscrypt state and pilot the authority witness | Required fscrypt-v2 closure now gates runtime creation; exact signed intent plus independent-CAS coordination detects authority rollback and recovers lost replies; ADR 0305 adds its remote service |
| 0304 | Qualify AArch64 rescue through an ARM kernel | A minimal QEMU-system guest runs the pinned capsule as UID 1000 through the unchanged profile-v7 and production PTY path on AArch64 Linux 6.6.94; one named real target remains |
| 0305 | Deploy an authenticated authority witness service | Device-signed fixed CAS, pinned witness replies, explicit enrollment, durable service state, and a two-guest rollback/outage gate make the authority coordinator remotely deployable without claiming same-host independence |
| 0306 | Witness application and Ratox incarnations | Separately enrolled startup lanes reject old valid process namespaces before runtime |
| 0307 | Witness route-generation policy | Exact signed route artifacts and generation state advance together through external CAS |
| 0308 | Witness the terminal policy tree | Complete reviewed profile and binding state, including sudo policy, must match the external head |
| 0309 | Witness the mutable-command effect frontier | Exact durable STARTED identities commit externally before an idempotent effect provider is called |
| 0310 | Witness the complete sync policy tree | Namespace and automation policy become live only after exact external commitment |
| 0311 | Witness update policy and lifecycle state | Exact signed successor intent makes state authoritative and the selected-slot pointer repairable |
| 0312 | Witness per-namespace synchronization four-root state | Domain-separated records anchor each non-tree-v2 namespace's signed publication, acceptance, activation, and retention roots |
| 0313 | Add complete witness-service checkpoint floors | A bounded service-signed complete selector snapshot can be retained independently and enforced before the listener binds |
| 0314 | Witness tree-v2 semantic state | Per-namespace records anchor the live branch frontier plus signed workspace and maintenance state without claiming content custody |
| 0315 | Join sync doctor to live managed headroom | Exact configured automation, live store/staging occupancy, nondefault quotas, and filesystem availability form one read-only admission report |
| 0316 | Qualify repeated production Ratox reconnect | One production client and retained shell cross two sequential direct-UDP and relay-only-TCP losses with exact generations and byte progress |
| 0317 | Add a typed CLI registry and generated completion | All 199 stable spellings drive parser classes, the help index, aliases, and Bash/Zsh/Fish command-name completion |
| 0318 | Enforce the synchronization-doctor filesystem contract | Both doctor paths refuse unsupported links, metadata, sparse layout, and ASCII collisions while reporting every deliberate transformation |
| 0319 | Verify independent synchronization restore drills | A bounded read-only command compares an operator-selected backup view with a disjoint restored tree without consulting live IoTox state or inferring backup independence |
| 0320 | Measure persistent three-writer synchronization capacity | A bounded full-mesh cell records catch-up, repair, memory, and allocated growth for 512 files on persistent ext4 |
| 0321 | Batch tree-v2 projection durability | Derived projection files are validated then covered by one filesystem barrier before atomic exposure while immutable CAS keeps per-object fsync |
| 0322 | Recover live writes across a tree-v2 exchange | Startup reconciles pending workspaces and preserves path-based edits made after atomic exchange without accepting ambiguous pre-exchange state |
| 0323 | Automate tree-v2 node-loss recovery | Ordered replay retirement, writer cutoff/checkpoint barriers, fresh identity reconstruction, reseeding, and exact restore verification form one bounded ceremony |
| 0324 | Supersede unfinished authority rounds | A strictly newer head from the same verifier/session replaces an unfinished proof round while same-head conflict remains fail-closed |
| 0325 | Exercise bounded synchronization storage faults | Separate ext4 node roots recover from real ENOSPC, read-only startup refusal, and abrupt Agent death during a signed pending exchange |
| 0326 | Qualify Ratox password sudo through the production PTY | One NixOS KVM gate retains noninteractive elevation and crosses a real PAM password prompt without echo or root-shell leakage |
| 0327 | Qualify Ratox cgroups under NixOS systemd | One NixOS KVM gate runs all five Ratox cgroup lifecycle, resource, I/O, and PSI process oracles under systemd delegation |
| 0328 | Fence open-descriptor sync source mutation | A held writer descriptor mutating a scanned file makes CAS installation fail closed without installing the stale object or retaining `.install.tmp` |
| 0329 | Pipeline tree-v2 exact object lanes | Tree-v2 pulls may keep a bounded active exact-object lane window capped by process and namespace policy, with per-lane status evidence |
| 0330 | Batch tree-v2 file-object commits | Completed file lanes share one strict CAS admission pass per bounded lane window and exact late-offer retirement prevents paused-transfer leakage |
| 0331 | Effect-fence cached tree-v2 CAS inventory | One pull reuses a private verified CAS view across batches and strictly revalidates it under the final metadata/projection transaction |
| 0332 | Qualify one whole-VMM tree-v2 workspace cut | Raw pending byte 2 arms an exact-VMM cut; a second kernel admits only old/new projections and converges with identity intact; phase-reversed v1 is withdrawn |
| 0333 | Target both workspace-exchange sides by projection identity | Double-read pending journals and canonical projection markers distinguish pre- from post-exchange VMM cuts without a product crash hook |
| 0334 | Make object-pipeline recovery durable and directly cuttable | Receive-staging batches and recovered CAS temporary removal gain exact directory barriers, with v4 whole-VMM cuts at both semantic temporaries |
| 0335 | Qualify tree-v2 branch-publication prefixes | External syscall-entry fencing makes exact manifest, immutable-record, and mutable-pointer pre-commit prefixes independently cuttable without a product crash hook |
| 0336 | Cut post-rename directory-durability windows | Proof v6 separately fences the manifest, record, and pointer parent-directory fsync entries and accepts only their honest old-or-new crash prefixes |
| 0337 | Refuse corrupt tree-v2 metadata until exact restoration | Startup and repair authenticate all five live signed semantic roots, retain corrupt bytes, and resume only after exact operator restoration |
| 0338 | Preserve bounded exchanged-projection descriptor writes | Immediate old-stage validation and authenticated projection-policy transitions preserve the held-descriptor-before-exchange case while later descriptor writes remain open |
| 0339 | Make metadata freshness and co-resident corruption explicit | Repair exposes external-witness participation, valid-old mutable semantic roots refuse under a current witness, and receipt v2 constructs stopped-task all-five corruption |
| 0340 | Qualify exchanged-projection open-descriptor retention | External ptrace fences selected/unselected descriptor writes around the real exchange; source-linked raw proof qualifies ext4 busy-remount refusal, closed-descriptor remount, cold refusal, and explicit salvage |
| 0341 | Wake sync automation from source changes | A bounded Linux inotify watcher accelerates local publish/reconcile work without changing signed policy, wire frames, authority, or periodic fallback |
| 0342 | Debounce source wakeups and skip no-op refresh work | A 250 ms Agent debounce coalesces source-watch bursts and unchanged stable tree-v2 reconciles no longer repeat implicit CAS refresh or a second marker-only worktree scan |
| 0343 | Qualify Ratox cgroups under delegated user services | A host helper runs Ratox cgroup process oracles in transient `systemd-run --user` delegated services and records 4 pass/1 environment skip locally |
| 0344 | Cache stable tree-v2 source digests in process | Writable tree-v2 scans reuse file digests only from private in-process metadata identities and clear across projection exchange/restart rather than adding durable trust |
| 0345 | Group tree-v2 path work before scan, merge, and projection decisions | Large tree-v2 scan/merge/summary/projection phases reuse per-path groups instead of repeatedly searching canonical manifests, without changing protocol or trust boundaries |
| 0346 | Index tree-v2 directory ancestors during manifest validation | Manifest validation proves nested live ancestry through one directory-path set instead of repeated manifest searches, without changing accepted tree semantics |
| 0347 | Index tree-v2 branch transition validation by path | Branch acceptance authenticates carried history and dropped-value rules through per-path baseline/successor/proof indexes instead of repeated whole-manifest searches |
| 0348 | Group tree-v2 time-machine diff paths | Retained-history diffs compare indexed per-path candidate groups instead of repeatedly searching both manifests, without changing forward-restore semantics |
| 0349 | Harden Ratox sudo-shell qualification sequencing | The isolated password-sudo VM gate waits across sudo/PAM terminal handoff and emits bounded PTY lifecycle diagnostics without changing product privilege defaults |
| 0350 | Target sparse tree-v2 source walks | Positive include rules scan only required ancestors and included roots/subtrees, reducing source-walk cost without changing tree-v2 manifests, projection exchange, or peer path authority |
| 0351 | Skip empty unselected projection work | Complete tree-v2 projection exchange bypasses provably empty unselected-preservation/compare walkers while retaining all baseline, visible, and old-side validation |
| 0352 | Report tree-v2 preservation counts | Reconcile and `sync-publish` expose content-free counters for preserved unselected projection entries, directories, files, and bytes |
| 0353 | Throttle tree-v2 busy republish churn | Tree-v2 source-watch changes observed during an active publish cool down before the next local republish, reducing intermediate head churn while preserving peer pulls |
| 0354 | Report tree-v2 CAS reconciliation counters | Reconcile and `sync-publish` expose content-free CAS inspection, installation, byte, and reuse counters so scale gates can separate object-store work from source/projection costs |
| 0355 | Report tree-v2 projection rebuild counters | Reconcile and `sync-publish` expose content-free selected projection and conflict-material counters so scale gates can separate projection rebuild work from CAS and source walks |
| 0356 | Report tree-v2 pull apply counters | Retained tree-v2 pull snapshots and `sync-status` carry the final content-free reconcile/apply counters beside transfer-side lane and source counters |
| 0357 | Retain tree-v2 apply counters in Sandwurm receipts | Three-writer capacity receipts optionally retain per-node final reconcile/apply counter dictionaries, with verifier support that preserves old proof compatibility |
| 0358 | Cache tree-v2 subscriber apply source digests | Subscriber pull completion reuses volatile source digest caches for repeated no-op applies without changing signed state, wire frames, or durable records |
| 0359 | Retain tree-v2 timeout transfer frontier | Rejected three-writer receipts can retain content-free in-progress tree-v2 job/lane/source counters, preserving old-proof compatibility while making timeout bottlenecks diagnosable |
| 0360 | Record recovery provenance and witness checkpoint custody | Restore verification and signed witness-checkpoint custody reports can retain strict operator labels while continuing to mark backup and operational independence as not assessed |
| 0361 | Duration-bound sync soak and retained recovery drill | Three-writer Sandwurm profiles can run short or 24-hour writable soaks and retain content-free recovery drill receipts without claiming backup independence |
| 0362 | Keep terminal cutoff replays out of live frontiers | Valid retired-writer cutoff history remains retained but cannot re-enter the live writer frontier during replacement recovery |
| 0363 | Freeze public page and script boundary | The public Bash/Nix helper and MonsterNix adapter guide build/test/evidence workflows without becoming authority roots |
| 0364 | Retain interrupted long-soak evidence | Normal `SIGINT`/`SIGTERM` interruption of the three-writer soak writes a rejected content-free partial-soak receipt |
| 0365 | Retain witness checkpoint custody drill receipts | A repository wrapper turns witness checkpoint custody reports into durable content-free JSON evidence while preserving the operational-independence nonclaim |
| 0366 | Enforce retained drill local requirements | Recovery and witness custody wrappers can reject receipts unless operator labels and different-device observations satisfy requested local prerequisites |
| 0367 | Harden long-soak recovery evidence | Late-soak rejects retain content-free projection, store, pull, restart, and wait-channel facts without pretending a failed run accepted |
| 0368 | Separate soak from high-churn stress | The 24-hour graduation profile uses a representative sparse edit cadence while preserving five-second churn as separate stress science |
| 0369 | Derive live soak staleness from cadence | The live Sandwurm soak inspector/watch tools calculate stale progress from the configured cadence and timeout instead of a fixed short threshold |
| 0370 | Make rejected soak receipts signal-robust | Shutdown and interruption paths retain machine-verifiable rejected soak receipts rather than only host/VMM launch evidence |
| 0371 | Keep the 24-hour soak passive on slow cycles | The primary 24-hour profile disables emergency stalled-cycle recovery and relies on a hard per-cycle timeout for representative evidence |
| 0372 | Schedule soak restarts before edits | Scheduled long-soak daemon restarts happen before the synthetic cycle edit and record their phase in receipts |
| 0373 | Defer soak repair across scheduled restarts | Representative soaks defer periodic repair away from scheduled restart cycles and prove deferred repairs drain before acceptance |
| 0374 | Settle soak restarts before edits | Scheduled restart cycles run a bounded sync-settle pass before the next synthetic edit and record that pass separately from periodic repair |
| 0375 | Recover stalled 24-hour soak cycles explicitly | The VM-only 24-hour gate uses a 600-second recorded recovery threshold before the 900-second hard cycle timeout |
| 0376 | Log each representative soak cycle | Long sparse soaks emit content-free per-cycle edit and convergence progress so live watching cannot confuse expected silence with a hidden stall |
| 0377 | Use explicit maintenance control deadlines | Post-soak checkpoint, GC, writer-cutoff, and automation evidence commands use the same explicit long local-control deadline as bounded repair |
| 0378 | Accept first dishonest-storage drill | A same-host dm-snapshot/ext4 drill proves one acknowledged-write valid-old rollback is detected and refused against an external witness floor |
| 0379 | Extend dishonest-storage to btrfs and flakey writes | The matrix harness covers ext4 and btrfs across valid-old, cross-family, torn-record, and dm-flakey dropped-write cells |
| 0380 | Accept dm-log-writes prefix replay | Exact ext4+btrfs synthetic block-log prefixes replay through dm-log-writes as the substrate beneath the later production-prefix gate |
| 0381 | Accept live-Agent production prefix replay | Real Agent sync-create and sync-publish transaction marks replay from ext4+btrfs dm-log-writes prefixes while recovery-custody gates remain blocked |
| 0382 | Select self mode for Ratox-first multidevice | `--mode self` selects Ratox host/controller roles for self-owned machines while keeping profiles, authority, route policy, and sudo explicit |
| 0383 | Implement signed self-swarm roster v1 | Owner-signed self-machine rosters create, join, retire, inspect, verify, plan, grant, and revoke narrow self grants without making Tox friendship authoritative |
| 0384 | Add self-swarm daily-driver and sync-readiness porches | Self-swarm floors, roster fanout, route proof, Ratox continuity, and sync readiness porches make self mode more operable without hiding authority |
| 0385 | Add person delivery cards and signed message fanout | Public person cards and bounded person-message envelopes let one person key fan out across active device route keys |
| 0386 | Add person delegations, card floors, seen stores, and group descriptors | Device sender delegations, contact-side card floors, local duplicate suppression, and signed group messages complete the first multidevice conversation substrate |
| 0387 | Add person messenger stores | Contact books, local transcripts, delegated device receipts, and reviewed outbox route accounting make the first manual messenger substrate durable without claiming background delivery |
| 0388 | Add outbox send storage receipts and Ratox activation check | One-shot outbox sending, backup-custody receipt verification, and a fail-closed terminal activation gate make the next proof boundaries executable |
| 0389 | Add ordinary trust status and receive porches | Native receive, messenger-status, sync trust-plan, and terminal daily-status commands make daily operation boring while preserving explicit nonclaims |
| 0390 | Add normal Tox compatibility bridge | Normal Tox text/action remains the outside carrier while IoTox self devices exchange signed delegated bridge observations without treating Tox keys as person keys |
| 0391 | Add sync and Ratox graduation checks | Native fail-closed graduation porches aggregate sync working-copy and Ratox daily-driver evidence labels while preserving precious-data and fleet-certification nonclaims |
| 0392 | Add ship-check release gate | Native stable/founder-preview release checks fail closed for no-concern sync/Ratox shipping while preserving explicit founder-preview nonclaims |
| 0393 | Add founder-preview release trail | Repository release-plan/release-check commands align clean-tree, script, native ship-check, stable brake, datacube, and source-input steps |
| 0394 | Add datacube snapshot history fallback | Repository datacubes remain below the strict byte ceiling by recording full-history or exact source-snapshot Git bundle mode explicitly |
| 0395 | Add evidence-gated stable release | Native stable ship-check can graduate only through a complete hash-bound sync/Ratox evidence manifest; defaults remain fail-closed |
| 0396 | Make long soaks first-class stable evidence | Stable now requires an explicit sync long-soak receipt and semantically verifies terminal long-soak receipts before accepting terminal.long-soak |
| 0397 | Retain final-restart long-soak rejection | A later 24h candidate is retained as verified rejected evidence after reaching 287/288 cycles and exposing a final scheduled-restart repair timeout |
| 0398 | Harden stable sync evidence semantics | Stable sync manifests now hash-bind and shape-check every sync receipt class instead of accepting placeholder prose for precious-data evidence |
| 0399 | Plan precious-data gates and handle the final soak boundary honestly | A read-only precious-data gate planner writes invalid templates and the 24h soak records any final-boundary restart skip instead of hiding it |
| 0400 | Remove storage-media certification from IoTox scope | IoTox no longer plans or requires destructive media qualification; precious-data gates focus on storage science, recovery custody, restore drills, and runbooks |
| 0401 | Add native precious-data sign-off porches | Native backup receipt, retention policy, evidence collection, manifest, and precious-status commands make the precious working-copy sign-off path ordinary and fail-closed |
| 0402 | Add operator precious-data signoff receipts | Native precious-signoff writes a content-free owner acceptance receipt only after precious-status is operator-signable and responsibility is explicit |
| 0403 | Accept fresh precious-data-era sync long-soak proof | Compact proof run.2nPKtCoX becomes the current accepted sync.long-soak proof; the native verifier receipt is generated from it while recovery custody remains separate |
| 0404 | Require native recovery-runbook receipts for precious-data signoff | Recovery-runbook evidence is now generated by a native hash-bound content-free receipt and old four-line hand-authored records are rejected |
| 0405 | Scope precious-data custody to sync-layer recovery | Current sync signoff uses versioned recovery custody, not disk-loss, host-compromise, or filesystem-wide corruption protection; `sync.independent-backup` remains only a legacy alias |
| 0406 | Accept nested storage-readiness evidence reports | Native stable sync intake accepts official storage-readiness JSON with nested evidence statuses instead of requiring a flattened special receipt |
| 0407 | Add native terminal stable evidence collection | Terminal stable evidence now has native content-free receipts, a 24h long-soak intake check, and auto/sync/terminal/all manifest scopes |
| 0408 | Add native terminal long-soak runner | `iotox terminal soak-run` creates elapsed wall-clock terminal long-soak receipts through the same verifier schema and preserves interrupted runs as rejected evidence |
| 0409 | Add operator watch/freeze, terminal readiness, and background plans | Stable evidence pointer, sync watch/local freeze, Ratox profile readiness, and person retry/card-freshness plans become native operator porches |
| 0410 | Add native messenger runner and sync safety rails | Person receipt rollups, outbox attempt/dead-letter state, bounded background-run, sync folder-status, safe-delete quarantine, and native freeze guards become binary behavior |
| 0411 | Add native terminal service artifacts | `iotox terminal service plan|render|receipt` generates systemd/NixOS service shapes and content-free supervision receipts without collapsing service-manager, cgroup, route, or sudo proof into one claim |
| 0412 | Add native graduation dashboards | Stable dossier plan/status, precious-data signoff command trails, self-swarm daily-status, and person messenger-plan make the five current graduation gates ordinary without weakening their nonclaims |
| 0413 | Add resident services and messenger readiness polish | `iotox service plan|render|receipt` renders Agent/person resident service shapes while person read-state, transcript convergence, and group-status commands make lived multidevice messaging clearer without overclaiming |
| 0414 | Add service reality receipts for stable evidence | `iotox service status-plan|status-receipt` records active/enabled/log-reviewed/health-passed/upgrade-passed resident service observations and `evidence collect terminal --service-reality` accepts them as the preferred `terminal.service-supervision` stable gate |
| 0415 | Add person, bridge, and route graduation checks | `iotox person graduation-check`, `person tox-bridge-graduation-check`, and `route-qualification-check` make multidevice messaging, Toxic compatibility, and Tor/I2P route claims evidence-gated without certifying anonymity or silent fallback |
| 0416 | Add native claim/help front doors | `iotox help routes|evidence|shipping|support` makes product-claim, evidence, shipping, and support surfaces discoverable while preserving explicit nonclaims and keeping exhaustive inventory in `iotox help all` |
| 0417 | Add seed repository datacube profile | `tools/iotox-repo.sh datacube --seed` creates the recommended public/GitHub source seed with one snapshot commit while upload remains the deliberate full-history provenance profile |
| 0418 | Align explain topics with human help porches | `iotox explain` now accepts the same top-level human topics as `iotox help` and keeps next-step guidance table-driven |
| 0419 | Make standalone build generator tolerant | `tools/build-standalone.sh` uses Ninja when present, falls back to Unix Makefiles, and records the generator in standalone build provenance |
| 0420 | Scrub founder host paths from the public seed | Public seed source uses portable paths for avoidable founder-host locations while retaining useful lab topology and evidence scope |

## Product axioms in force

```text
From memory, you can reach your devices.
No IoTox-controlled key can reassign them.
Tox does the connection work.
IoTox decides authority above Tox friendship.
The ratox successor is the immediate product path.
The outside should be ordinary; the inside must tell the truth.
```

## Important choices not frozen

- post-fscrypt data-key custodian integrations, operationally independent witness deployment and
  checkpoint retention, replacement/re-anchor ceremonies, and broader namespace-state freshness
  beyond the implemented single-writer and tree-v2 semantic lanes;
- remembered-phrase remote discovery and re-entry transcript;
- destructive physical reclaim after all owner secrets are lost, and rollback protection;
- command-store rollback protection, compaction, archive/export, effect-specific idempotency, and post-send remote cancellation/compensation;
- argument grammar and effect contracts for additional mutable command operations;
- whether a future offline human-message spool is justified and how its expiry, retry, and privacy contract differs from the live text FIFOs;
- durable friendship/request-history retention, signature, redaction, and sequence policy;
- whether a separately named compound transport-remove plus principal-revoke ceremony is useful;
- public bootstrap-list provenance and update policy;
- real Tox fixture topology;
- independently reviewed exit/time actual-Tor diversity and live I2P router/service policy;
- official source-linked build and GPL distribution evidence;
- first target hardware class.
