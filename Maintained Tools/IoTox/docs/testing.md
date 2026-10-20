# Testing and evidence — rev0051

The facility exists to find construction defects and to state exactly what has been exercised. It is
not a substitute for building the full product, official provider integration, genuine peers, or
target-hardware work.

## 2026-09-17 first dishonest-storage drill

ADR 0378 adds a same-host dm-snapshot/ext4 drill and verifier:

```sh
tools/iotox-repo.sh sync-dishonest-storage-drill
python3 tools/verify-sync-dishonest-storage-drill.py \
  .sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X
```

Source-linked run `run.UbmYPe1X` writes generation 2 through an acknowledged
snapshot COW, discards the COW, cold-reads generation 1 from the origin, and
refuses mutation because the external witness floor remembers generation 2.
The compact receipt is content-free and lives at
`.sandwurm/exports/sync-dishonest-storage/run.UbmYPe1X/receipt.json`.
This is the first accepted dishonest-storage substrate gate, not full
production write-prefix replay or storage-media certification. Details are in
`evidence/2026-09-17-sync-dishonest-storage.md`.

## 2026-09-17 ext4+btrfs dishonest-storage matrix

ADR 0379 adds the matrix runner:

```sh
tools/iotox-repo.sh sync-dishonest-storage-matrix \
  --origin-size-mib 256 \
  --cow-size-mib 128
python3 tools/verify-sync-dishonest-storage-matrix.py \
  .sandwurm/exports/sync-dishonest-storage/run.qGwEvF17
```

Source-linked run `run.qGwEvF17` passes eight cells: ext4 and btrfs each cover
valid-old rollback, cross-family rollback, torn manifest content, and
`dm-flakey drop_writes` masked write loss across six content-free
production-shaped families. The compact receipt is
`.sandwurm/exports/sync-dishonest-storage/run.qGwEvF17/matrix.json`.
This closes the first btrfs dishonest-storage matrix, but by itself not
storage-media certification, exact live Agent production prefix replay,
versioned recovery custody, or precious-data readiness. Details are in
`evidence/2026-09-17-sync-dishonest-storage-matrix.md`.

## 2026-09-17 dm-log-writes prefix replay

ADR 0380 adds exact block-log prefix replay on the same host:

```sh
tools/iotox-repo.sh sync-log-writes-prefix-replay \
  --origin-size-mib 256 \
  --log-size-mib 512
python3 tools/verify-sync-log-writes-prefix-replay.py \
  .sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra
tools/iotox-repo.sh storage-readiness
```

Source-linked run `run.90LCC7ra` passes ext4 and btrfs `dm-log-writes`
replay for three marked prefixes: older valid generation 1, mixed
manifest/branch-record generation 2 before mutable pointer update, and complete
generation 2. The compact receipt is
`.sandwurm/exports/sync-log-writes-prefix/run.90LCC7ra/prefix-replay.json`.
This accepts the exact block-prefix substrate. ADR 0381 separately closes the
first live-Agent production transaction-prefix replay gate; this substrate
receipt alone still does not close independent
backup custody, or precious-data readiness. Details are in
`evidence/2026-09-17-sync-log-writes-prefix-replay.md`.

## 2026-09-17 live-Agent production prefix replay

ADR 0381 adds live Agent transaction-boundary replay on the same host:

```sh
tools/iotox-repo.sh sync-production-prefix-replay \
  --origin-size-mib 512 \
  --log-size-mib 2048
python3 tools/verify-sync-production-prefix-replay.py \
  .sandwurm/exports/sync-production-prefix/run.HYXJnDzI
tools/iotox-repo.sh storage-readiness
```

Committed-source run `run.HYXJnDzI` starts the real Agent with sync enabled,
uses the mock toxcore provider, places durable Agent state plus the source and
sync-policy roots on `dm-log-writes`, runs real `sync-create`, `sync-publish`,
and `sync-repair`, and replays the ext4+btrfs transaction prefixes
`sync-create-generation-1` and `sync-publish-generation-2`. The compact receipt
is `.sandwurm/exports/sync-production-prefix/run.HYXJnDzI/production-prefix-replay.json`.
This accepts local production transaction-prefix science, but not every
internal subtransaction interleaving, independent
backup custody, or precious-data readiness. Details are in
`evidence/2026-09-17-sync-production-prefix-replay.md`.

## 2026-09-10 duration soak and retained recovery slice

ADR 0361 adds a duration-bound three-writer writable soak and a retained recovery drill wrapper.
ADR 0362 fixes the edge exposed by the first soak-smoke recovery run: an exact terminal cutoff record
for a retired writer remains valid history, but it no longer re-enters
`tree-v2/branches/<writer>.branch` as live authority.
ADR 0364 adds normal `SIGINT`/`SIGTERM` retention for long soaks: an interrupted run can now write a
rejected receipt with validated `partial_soak_evidence` instead of losing the useful cycle, restart,
repair, and timing counters accumulated before the stop.

The accepted same-host Sandwurm/KVM/ext4 proof is
`.sandwurm/exports/three-writer/run.UFBCMzt9`. It passes
`verify-sync-three-writer-sandwurm.py` and `verify-sandwurm-vm-smoke.py`, binds IoTox binary SHA-256
`1784a1a9fbca4cb89bf044636cd8659256c093ac4e391eecb4fe826414697c22`, and retains a 96,198-byte
compact export with `contains_secrets=false`.

That proof includes 128 4-KiB files, 4 soak cycles over 34.235 seconds, 2 daemon restarts, 2 repair
passes, retained same-VM recovery provenance across 4 restore verifier reports, and the bounded
storage-fault follow-up. It does not close the 24-hour soak, versioned recovery custody, or
dishonest-storage gates. Details are recorded in
`evidence/2026-09-10-sync-soak-smoke-and-retained-recovery.md`. The ADR 0364/0365 wrapper validation
is recorded in `evidence/2026-09-10-retained-soak-and-witness-custody-wrappers.md`.

## 2026-09-10 retained witness custody drill wrapper

ADR 0365 adds `tools/run-witness-checkpoint-custody-drill.py` and the public helper entry point
`tools/iotox-repo.sh witness-custody ...`. The wrapper runs the production
`witness-service-checkpoint-custody` command, validates that the report remains authentic,
outside-root, public-key-bound, and explicitly non-claiming, then writes a content-free JSON receipt.

The wrapper self-test exercises the receipt path with a fake IoTox-compatible custody report:

```sh
python3 tools/run-witness-checkpoint-custody-drill.py --self-test
```

This is evidence tooling only. It does not prove operational independence; a real deployment still
needs an independently retained, rollback-resistant checkpoint artifact outside the service
root/admin/snapshot domain.

## 2026-09-10 retained drill local requirements

ADR 0366 hardens both retained drill wrappers. `tools/run-sync-retained-recovery-drill.py` now
validates production label hex, writes rejected command receipts without raw stdout/stderr, and can
enforce:

```sh
tools/iotox-repo.sh sync-recovery-drill \
  --require-operator-provenance \
  --require-different-device \
  --evidence recovery-drill.json \
  BACKUP_ROOT RESTORED_ROOT
```

`tools/run-witness-checkpoint-custody-drill.py` can enforce:

```sh
tools/iotox-repo.sh witness-custody \
  --require-custody-labels \
  --require-different-device \
  --evidence witness-custody.json \
  SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX
```

Both wrappers still record `operator-evidence-required` rather than certifying backup or operational
independence. Different filesystem device numbers are useful local metadata, not proof
of disk-loss or host-compromise protection. Validation for this pass is recorded in
`evidence/2026-09-10-retained-drill-requirement-gates.md`.

## Default suite

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --preset gcc-debug --output-on-failure
```

The default suite has sixty-two entries:

```text
iotox.unit-and-integration
iotox.terminal-posix-process
iotox.sync-publication-process
iotox.sync-retention-process
iotox.sync-transaction-process
iotox.sync-rollback-process
iotox.sync-tree-process
iotox.terminal-cgroup-recovery-process
iotox.terminal-cgroup-memory-resource-process
iotox.terminal-cgroup-cpu-resource-process
iotox.terminal-cgroup-io-resource-process
iotox.terminal-cgroup-pressure-admission-process
iotox.terminal-controller-process
iotox.binary-process-lifecycle
iotox.ratox-restart-fence-process
iotox.cli-authority-ceremony
iotox.client-version
iotox.client-help
iotox.bootstrap-seeds
iotox.recall-generate
iotox.client-absent-daemon
iotox.terminal-invalid-key
iotox.terminal-absent-daemon
iotox.socks5-forwarder
iotox.socks5-adversary
iotox.i2p-sam-socks-adapter
iotox.i2p-sam-service-forward
iotox.i2p-sam-two-router-smoke
iotox.i2p-tox-fronts
iotox.i2p-sam-smoke-verifier
iotox.route-target-process
iotox.operator-tor-smoke
iotox.operator-tor-receipt-verifier
iotox.workspace-cleaner
iotox.sandwurm-vm-smoke-verifier
iotox.sync-three-writer-sandwurm-verifier
iotox.sync-three-writer-sandwurm-exporter
iotox.sync-power-cut-rehearsal-runner
iotox.sync-power-cut-sandwurm-runner
iotox.sync-power-cut-sandwurm-verifier
iotox.sync-power-cut-sandwurm-exporter
iotox.sync-metadata-corruption-rehearsal
iotox.sync-metadata-corruption-sandwurm-verifier
iotox.sync-metadata-corruption-sandwurm-exporter
iotox.sync-shadow-runner
iotox.sync-shadow-sandwurm-verifier
iotox.sync-shadow-sandwurm-exporter
iotox.route-policy-campaign
iotox.spdx-sbom
iotox.sandwurm-pair-verifier
iotox.sandwurm-pair-exporter
iotox.actual-tor-path-population-analyzer
iotox.content-lane-counterbalance-analyzer
iotox.sandwurm-pair-runner
iotox.sandwurm-provider-rolling-verifier
iotox.ratox-r7-analyzer
iotox.ratox-terminal-probe
iotox.content-ratox-latency-summarizer
iotox.ratox-route-impairment-analyzer
iotox.ratox-route-loss-analyzer
iotox.process-resource-capture
```

The historical cube-layout validation is opt-in with
`IOTOX_VALIDATE_REVISION_CUBE_LAYOUT=ON` and adds `iotox.lone-entrance-layout`.

The direct owned C++ registry contains 859 checks. The preserved Mutorr incubator adds its own
research registry and two CTest entries; its current combined count is reported by the matrix rather
than inferred here.

The content-v2 construction slice adds canonical/adversarial type-28/29 wire checks, bit-29 feature
dependency, publisher authorization and replay tests, exact local flat/paged CAS resolution, flat and
paged reconstruction, two authorized simultaneous complete sources, in-flight source disappearance,
stale completion fencing, survivor convergence, and bounded coordinator workspace. ADR 0251 adds the
live deterministic Agent boundary: bit 29 is dynamically advertised after content construction and
startup graph validation, and one paged revision crosses real Agent packet/FileId/terminal dispatch,
HEAD-last acceptance, exact-token activation, repair, and dry-run GC through mock toxcore. This is
not by itself genuine-provider evidence; ADR 0252 supplies that separate gate below.

ADR 0245 extends that dark slice with canonical/adversarial type-30/31 checks, exact local
availability derived from size/digest-verified CAS objects, publisher replay without a second scan,
and a multi-window flat-content reconstruction whose two authorized writers advertise disjoint
even/odd chunk sets. Each assignment is checked against its source's exact bitmap and both sources
contribute. This qualifies the deterministic complementary-store scheduler seam, not Agent dispatch
or network behavior.

ADR 0246 adds physical-store adversarial coverage. The tests build the real embedded toxsync
`sha256` fanout under a transaction, verify every digest, reject root permission drift, an unexpected
algorithm entry, a hard-linked object, and corrupt bytes, and prove preparation does not chmod
through a symlink. Separate flat and CAS inventories are then made to fit independently while their
combined object-count and byte totals exceed the one namespace quota; only the combined view fails.
This qualifies the inventory primitive, not a product CAS writer, reachability, repair, or GC.

ADR 0247 adds product-write checks. One root manifest is committed through a verified copy into its
canonical digest path before coordinator construction. Standalone commit tests cover source
consumption, exact reuse, corruption refusal, and retained staging on failure. Coordinator tests now
use only the derived CAS/staging roots, admit every page/chunk against combined quota under the
transaction, retain the exact active staging file when quota is exhausted, and reject completion-path
substitution and hard-linked staging without publishing an object. This still does not qualify live
FileId/event joining.

ADR 0248 adds the content-specific restart boundary. Canonical codec tests bind every HEAD, object,
FileId, source, and carrier field and reject signed-field mutation or nonzero padding. Store tests
burn IDs before insertion, distinguish exact replay from conflicting reuse, refuse active aliases and
bounds overflow, and detect journal tampering. Recovery tests enter one exact complete staging object
through the product CAS commit, fence and remove partial/absent work, replay idempotently from CAS, and
retain both an ambiguous hard-linked file and its signed active record. These tests qualify local
restart classification, not live Agent dispatch or a killed provider process.

ADR 0249 adds the real local publication boundary. Flat and paged product tests build complete CAS
fabrics, resolve signed chunks/pages, advance an exact successor, and reuse an exact duplicate.
Whole-set quota, unauthorized-writer, impossible-workspace, and mid-commit cancellation tests keep
HEAD absent; exact startup cleanup removes only recognized private local workspaces and refuses a
foreign entry. An Agent/control-socket test publishes a real content-v2 revision and reloads its
signed HEAD plus committed chunk after shutdown. These checks qualify local publication and startup
recovery, not remote root bootstrap, content file-event dispatch, activation, or provider behavior.

ADR 0250 adds the transport-neutral receive boundary. One real paged publication traverses the real
publisher service, root-manifest bootstrap, an intentionally early paused offer, CTA1-gated page and
chunk receives, reconstruction, whole-artifact CAS, and accepted-HEAD-last persistence. A cancelled
early offer performs no receive, clears signed attempt truth, and cannot be revived by its delayed
result. Post-artifact/pre-HEAD cancellation reuses exact CAS on retry. These checks qualify the local
subscriber state machine, not Agent dispatch, genuine c-toxcore, activation, or multiple sources.

ADR 0251 adds three checks at the product and maintenance boundaries. The full Agent test publishes
a separate paged 384 KiB-plus provider revision with multiple manifest pages, negotiates bit 29,
pulls every object through mock-toxcore callbacks, reconstructs byte-identical whole CAS, accepts HEAD
last, explicitly activates the exact record, and invokes content repair plus dry-run GC. A paged
reachability test quarantines only an unreferenced object and suppresses all candidate classification
when one required page is missing. A corruption test moves a same-size digest mismatch to private
repair quarantine without moving valid rooted bytes.

ADR 0252 adds the genuine-provider `sync-content` gate. Two independent source-linked Sandwurm
guests publish and pull the same 4 MiB paged revision through c-toxcore over direct UDP and forced
TCP. Both cells require negotiated bit 29, one pull with zero failure, four chunk objects plus one
manifest page, whole-artifact/root CAS verification, signed-HEAD-last acceptance, explicit
activation, and matching terminal truth at the publisher. The compact exporter retains the ordered
content completion record, and strict replay binds its shape and hashes back to the pair manifest.
ADR 0254 adds the deterministic multi-source product gate. Two independently signed publishers hold
an identical frozen revision and complementary even/odd chunk stores while retaining required root
metadata. Exact availability exchanges drive selected-source object requests and FileId joins over
two distinct authenticated contexts; both sources must contribute before byte-identical
reconstruction and HEAD-last acceptance. ADR 0255 narrows the genuine-carrier nonclaim: three live
agents in two source-linked KVM guests pass over direct UDP, with four exact availability requests/
results and positive object traffic from both sources. Forced TCP does not pass. Thirteen bounded
900-second cells separated relay count, request order, ordinary pending acceptance, reusable-key
pre-provision, full-address rendezvous, and A/B route placement. Most leave the secondary Tox-offline
with zero IoTox HELLO attempts. The strongest hybrid briefly passes the exact secondary TCP/confirmed
checkpoint, then remains offline throughout the 300-second v3-authority window, before any content
request. That is a retained topology result, not a universal c-toxcore limit and not a reason to
reinterpret relay connectivity or transient confirmation as a usable source. ADR 0256 adds an atomic multi-source pull
and a destructive native-UDP companion. The selected secondary is stopped only after positive
object work; the first job must fail and clean all transient authority/effect state; the same identity
must return at a higher epoch; and a distinct explicit atomic job must converge. ADR 0257 repeats
that gate after one availability-only import: the foreign publication path stays absent, the partial
replica survives a true Agent cold start, GC sees a complete consistent graph with zero candidates,
and no post-start HEAD injection occurs. At that gate, multiple lanes, transparent same-job
continuation, general content-v2 daemon restart, and forced-TCP multi-source convergence remained
open. ADR 0267 now closes the bounded native-carrier restart question at explicit caps two and four;
transparent same-job continuation and partial-prefix resume remain intentionally unqualified. ADR
0268 separately closes the already-attached cap-two interactive construction-SLA question.

The registry additionally includes a strict file-chunk callback mode: the exact toxcore double
returns `TOX_ERR_FILE_SEND_CHUNK_SENDQ` for any chunk submitted after the request callback returns,
and a multi-chunk manager transfer must still complete byte-identically.

Warnings are errors in all release-evidence lanes.

## Private route binding v2 live gate

Three layers now freeze the default-off privacy path. The pure registry test admits one signed
primary inventory, accepts its exact replay, rejects same-epoch conflict and same-generation fork,
retains generation/digest high-water across authority retirement, and admits a later generation.
The worker/provider test proves an auxiliary can confirm HELLO/CAPABILITIES but neither sends nor
authenticates before primary inventory handoff; afterward it exchanges a fixed 256-byte type-27 proof
and clears both directions when the context is removed. The full Agent/provider test observes type
26 verification before type 27, reaches coordinator `ready`, removes the primary friendship, and
requires readiness withdrawal. Existing v1 worker coverage remains unchanged.

The worker regression also advances a live primary epoch after the reciprocal proof arrives. Context
replacement must retain and reverify that frame, regenerate the local proof, and return to reciprocal
readiness; this freezes the ordering bug found by the first genuine guest attempt.

The genuine `sync-tree-route-private-mixed` cell now passes in two simultaneous Sandwurm guests:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT \
  sync-tree-route-private-mixed
```

Each role constructs a native UDP primary, native UDP bulk member, and strict generic-SOCKS/TCP bulk
member under independent keys. Acceptance requires primary authority on both sides, two ready bulk
members per role, exact signed 4,194,389-byte tree convergence and activation, immutable reusable
identity baselines, and independently verified raw/compact roots. TAP decoding selects outermost IP
fields: native UDP and related ICMP may use public destinations, while every TCP packet must stay on
the configured local SOCKS/relay endpoints. Accepted compact proof `pair.z948jeii` records 4 admitted
SOCKS connections, zero denials, and zero unexpected context packets. The forwarder is not Tor;
the separate actual-Tor result below does not widen this generic-SOCKS claim (ADR 0201).

The same worker regression now makes the inherited primary bootstrap/relay host deliberately
invalid for strict Tor, supplies numeric exact-key replacement lists, and reaches construction only
through those replacements. Removing either replacement restores the fail-closed result; a
17-record list is rejected before any worker starts. CLI adversarial cases separately reject
malformed, unpaired, nonnumeric Tor, and duplicate exact-key endpoint records (ADR 0202). The direct
owned registry remains 598 checks.

The follow-on `sync-tree-route-private-actual-tor` cell is accepted behind an explicit
operator-supplied `IPV4:PORT:KEY` record. It preserves the private native control routes but sends
each role's second worker through a separate real Tor process and source-only SOCKS policy. Its
offline verifier independently reparses authenticated STREAM/CIRC events, Tor process socket
commitments, configuration commitments, and both TAP captures before accepting the same private-v2
readiness and signed 4,194,389-byte tree result. The verifier's negative fixture changes the client
target and must fail. Accepted compact proof `pair.2mycvy9n` records two successful exact-target
streams and a distinct three-hop `CONFLUX_LINKED` circuit per role, 583/531 role-specific Tor proxy
packets, and zero unexpected context packets. It proves actual-Tor member readiness in the
application topology, not scheduler attribution of the tree payload to Tor (ADR 0203).

`sync-tree-route-private-actual-tor-payload` is the qualified attribution cell. It fails unless
the founding reusable client's lane-1 key sorts before lane 2, assigns that exact lane to Tor in
both guests, retains fixed scheduling, and observes the completed sync job on the Tor member with
zero reassignment. The ordinary Tor-control, TAP, route-readiness, convergence, and compact-proof
checks still apply. Initial pull admission has a 120-second idempotent retry window and retains the
attempt/failure counts plus a content-free first-error digest; strict verification binds those
fields to the client receipt. Offline and Nix evaluation pass; the first live qualification is
accepted as compact proof `pair.lzsyitvy`: the exact Tor member carries the complete signed tree
with zero reassignment and first-attempt admission, while both Tor/TAP evidence sets independently
reverify (ADR 0204).

`sync-tree-route-private-actual-tor-loss` is the external-fault follow-on. The 16,777,513-byte
treepack is rate-limited to leave a bounded host observation window. The client
must expose at least 65,536 partial object bytes on the exact Tor member before the host captures its
authenticated control/process evidence and sends `SIGKILL` to that Tor process group. IoTox must
observe one carrier loss, reassign the immutable job to the other auxiliary, converge, and count the
same Tor route as recovered after the host starts the identical binary again. The proof rejects an
internal qualification fault or route-worker restart and binds stopped carrier, position, PIDs,
control sockets, guest receipt, and TAP containment. Construction, direct tests, and strict schema
checks pass. Accepted compact proof `pair.iompvehf` kills Tor after 74,034 exact-carrier bytes and
records one loss, one reassignment, two stale terminals, one real recovery, two ready bulk members,
zero IoTox route-worker restarts, complete signed-tree convergence, three authenticated Tor phases,
and zero unexpected-context packets on both TAPs (ADR 0205).

`ratox-route-actual-tor-loss` is the terminal-specific external-fault gate. Both primary agents use
independent actual Tor clients and only the operator-supplied public Tox record. After the first PTY
heartbeat/byte exchange, the host captures authenticated client Tor evidence and kills only that
process. The ordinary Ratox probe must retain carrier `tcp` at its two-second heartbeat timeout,
later observe authoritative offline and local `unavailable`, while the device retains exactly one
detached live PTY. After the same Tor instance bootstraps, explicit resume must preserve the exact
session/incarnation and advance generation and byte sequences from 1 to 2 under a higher online
epoch. The strict raw/compact verifier joins this lifecycle to distinct pre-loss/recovered client
Tor evidence, continuous device Tor evidence, zero IoTox daemon restarts, and TCP-only TAP
containment. Accepted compact proof `pair.2waqdpgk` records a 2.204-second heartbeat warning,
27.379-second authoritative-offline observation, one detached PTY, exact-session generation-2
resume, and zero UDP/direct guest packets. Its private and compact forms independently pass the
strict verifier (ADR 0206).

`ratox-route-actual-tor-soak` is the continuous-process duration companion. It runs 120 paired
heartbeat/PTTY samples one second apart and pauses at ordinals 20 and 100 so the host can close only
the exact role's active Tor application circuit. The gate rejects a Tor/IoTox restart, a session or
sequence discontinuity, a close without raw `REASON=REQUESTED`, recovery without a distinct
successful three-hop application circuit, a run shorter than the paced sample span, or any TAP
egress outside the exact local Tor listener. Because live attempts observed both carrier loss and no
error, it sends post-replacement PING and accepts only canonical PONG with unchanged epoch/generation
or exact `unavailable` with higher-epoch explicit resume and one generation increment. Neither branch
may change session/incarnation/PTY/byte positions. Accepted compact proof `pair.k8o54n2v` exercises
both branches in one run: client same-stream reattachment preserves epoch/generation, while device
stream reopening leads to authoritative loss and explicit generation-2 resume. All 120 samples,
both requested closes, unchanged processes, and TCP-only TAP containment independently reverify
(ADR 0207).

ADR 0209's separate `run-socks5-adversary.py` process test constructs the fault boundary. It chains
an allowlisted numeric target through an upstream SOCKS server, proves exact bytes, holds an
established stream behind a reachable listener, and releases the bytes exactly while auditing both
sides of the chain. That process test alone remains adapter evidence.

The live companion is repeatable as:

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-adversary \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID ratox-route-actual-tor-adversary
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID ratox-route-actual-tor-adversary
```

The cell places one bridge interposer before each loopback-only Tor instance and binds every exact
interposer upstream source port to authenticated Tor STREAM/CIRC evidence. After initial PTY
progress it holds only the client relay bytes, requires both listener reachability and a fresh
successful exact-target SOCKS CONNECT, then separately requires the two-second Ratox warning,
c-toxcore authoritative offline, typed controller unavailability, and one detached live PTY. Only
removing the hold file may recover the route; explicit resume must preserve the exact
session/incarnation/PTY and advance online epoch, generation, and byte positions exactly once.

Accepted compact proof `pair.vx6z0csh` records warning at 2.578 seconds, offline at 27.241 seconds,
zero Tor/interposer/IoTox restarts, exact generation-2 resume, five exact-target chains with zero
denials, and TCP-only TAP containment. Raw and compact forms independently pass the strict verifier.
See `evidence/2026-08-28-sandwurm-actual-tor-adversarial-boundary.md`.

ADR 0211 adds the separate `iotox.i2p-sam-socks-adapter` construction test. An independent SAM
v3.1 process double checks exact HELLO/SESSION/STREAM bytes while ten byte-identical mapped
streams pass, including eight simultaneous streams under one long-lived transient session.
Unmapped numeric and SOCKS domain targets fail. Forced control loss closes admission; generation
two recovers under the stable process-local session ID; the audit retains only a destination
commitment. This is adapter evidence, not a real I2P router, I2P-hosted Tox relay, packet-containment,
or anonymity claim. The double also sends an otherwise unexpected SAM 3.2 PING to freeze a defensive
PONG response; that exchange is not claimed as part of negotiated SAM 3.1. The separately registered
two-router smoke performs only a construction-runner self-test during ordinary CTest. Its live mode
requires two already-running, distinct, source-attributed router processes and refuses a dirty tree.
ADR 0253 later promotes this exact qualified construction to product `tox/i2p` without changing the
adapter or its protocol.

ADR 0213 adds `iotox.i2p-sam-service-forward`. Its process double freezes exact SAM 3.1
DEST/SESSION/FORWARD bytes, canonical padded I2P Base64, an owner-only persistent Destination,
restart-stable b32 naming, `SILENT=true`, exact raw loopback-service bytes, loss/recovery, no-clobber
audit, and content-free destination commitments. A live two-router check also passed exact bytes
through the paired client adapter and persistent forward. The separately named
`tox/i2p-construction` route has direct option/topology tests. It is now a deprecated alias for
canonical `tox/i2p`; both converge on the same strict topology (ADR 0253).

The first real c-toxcore attempt is a retained design finding, not a passing route claim. Both Agent
sockets were confined to the adapter, both SAM streams were admitted and reached the pinned relay,
and the same relay/key reached `tcp` immediately through a direct strict-SOCKS control. The I2P cell
remained `offline`: its 0.468-second SAM setup was not the bottleneck; the complete relay response
reached the client boundary at roughly 34 seconds, after c-toxcore's ten-second combined proxy/relay
establishment deadline. A TCP-only 120-second retry retained the stream but remained offline because
the cell had only one bootstrap record and replaced its address with an unroutable documentation
address that Tox embedded in its onion path. Three address-preserving I2P service fronts reached
`tcp` in about twenty seconds with `iotox-file-rr1-tcp-connect120`; no onion-lifetime patch is carried.
Two fresh peers then passed the complete genuine-peer lifecycle through those same two live routers
and three fronts: friendship, protocol confirmation, authority, text, durable command, exact file,
two process restarts, ownership epoch transition, and friendship removal/re-add (ADR 0215).

ADR 0216 adds `iotox.i2p-tox-fronts` and the original Sandwurm
`tox-i2p-construction baseline` gate. The
supervisor binds one exact i2pd 2.60.0 executable and 315-file source-tree commitment, two routers,
three persistent service fronts, three exact-target egress shims, and one bridge adapter. Accepted
compact proof `pair.k_vopzf5` records TCP friendship, canonical session confirmation, bidirectional
text, and TCP-only TAP containment for both source-linked guests. It permits only bounded
`denied-stream` tunnel-convergence retries to committed Destinations and requires all three fronts to
admit. Raw and 1.59 MB secret-free compact forms independently pass the strict verifier. That
baseline intentionally left I2P route loss/recovery and a private member-bound Ratox or sync payload
open.

ADR 0217 adds the companion `i2p-router-restart` gate. The supervisor pins the 21 certificate files
from the exact i2pd source, enables signed reseed verification, and records the certificate-tree
commitment. Only the client router is terminated; the bridge listener must stay reachable while SAM
is absent and the adapter records generation-one loss. Both guests must independently observe
c-toxcore offline before a distinct router PID reuses the same datadir. The proof passes only after
generation two is ready, both guests advance authenticated epoch 1-to-2, and both receive fresh text.
Accepted compact proof `pair.v_11i2me` records six admissions over all three fronts in each
generation, eight bounded SAM-unavailable retries, 68.991 seconds of router absence, TCP-only TAP
containment, and zero native fallback. Raw 2.46 GB and 1.76 MB content-free forms independently pass.

ADR 0218 adds `i2p-service-restart`, the complementary server-side fault. The supervisor records
the exact router PIDs/start ticks, proves their ownership of the two SAM listeners and established
public TCP socket sets, then stops all three forward processes without touching either router or the
generation-one adapter session. Both guests must observe c-toxcore offline before three distinct
processes load the same mode-0600 Destination keys. The run passes only after both guest epochs
advance 1-to-2 and fresh text crosses bilaterally. Accepted compact proof `pair.6rrdsdc_` records
three `created -> ready` initial audits, three `loaded -> ready` replacement audits, 19 exact
admissions with all commitments represented before and after recovery, and TCP-only TAP containment.
Raw 2.46 GB and 1.61 MB secret-free forms independently pass.

ADR 0219 closes the first bounded private member-bound sync payload. The
`sync-tree-route-private-actual-i2p-payload` cell waits for both exact auxiliary routes belonging to
the remote stable principal, assigns a 131,369-byte signed tree to the expected actual-I2P member,
and requires zero reassignment before activation. Accepted compact proof `pair.5xjf2n4d` passes.
The exporter regression keeps I2P captures/topology/audits and excludes Tor artifacts. Diagnostic
512 KiB and 4 MiB attempts instead crossed a carrier epoch and reassigned complete work to native.
ADRs 0225–0226 implement/qualify the signed class and fail-closed whole-object loss behavior;
ADR 0227 adds the positive 4 MiB auxiliary range gate, and ADR 0228 qualifies live range loss plus
explicit fresh recovery. Failed-prefix byte resume remains open.

ADR 0220 adds the deterministic no-downgrade prerequisite. The same full-Agent mock fixture runs
both policies across first-byte auxiliary loss. `available` completes through the other authenticated
member. `fail-closed` retains `state=awaiting-objects` on the original carrier with one loss, one
blocked job, one initial selection, and zero reassignment. CLI hostile cases reject unknown policy
and explicit policy without sync plus route workers. The actual-I2P payload guest now selects
fail-closed and requires zero blocked jobs on its successful path.

ADR 0221 makes the same loss oracle a per-job proof. The fixture deliberately configures the
opposite process default, submits local-control v1.38 operation 85, and requires the explicit job
choice to win in both directions: `available` reassigns under a fail-closed daemon, while
`fail-closed` remains fenced under an available daemon. Subscriber tests separately reject a
same-epoch begin/retry with a conflicting value, and local-control tests freeze operation 85 and the
v1.38 ceiling. No peer-wire feature is inferred from this local proof.

ADR 0222 adds one simultaneous native/Tor/I2P-construction selector oracle and moves the full-Agent
loss fixture to local-control v1.39 operation 86 with an exact `tox/native` requirement. The
actual-I2P Sandwurm guest supplies `fail-closed tox/i2p-construction`, eliminating route-key-order
dependence from its next run. A named-class absence leaves the HEAD request live and sends no object
request through primary. This remains local network-context evidence, not a signed route-class
claim.

ADR 0224 moves that same full-Agent loss oracle three bytes into the immutable object. The first
authenticated worker writes exactly `pay` into its canonical private attempt file and then emits an
authoritative offline event. Under `available`, the replacement worker accepts a fresh attempt,
message ID, and FileId, seeks to byte 3, receives only `load`, rejects the old worker's stale
terminal, verifies the full `payload` digest, and commits once. Status must settle at
`retained-partials=0 resumed-attempts=1 resumed-bytes=3`. The fail-closed twin loses the same three
bytes but requires all three counters and reassignment to remain zero. This is a deterministic
same-process construction gate; the native-carrier qualification below is independent evidence.
Lifetime retention telemetry separately requires one positive retained attempt, three retained
bytes, and zero retention fallbacks; empty admitted siblings are fenced rather than mislabeled as
resume state.

ADR 0225 adds the route-set-v2 negative matrix around that scheduler. Canonical tests require exact
`IOTOXRS2` magic/version/signature-domain separation, one nonzero class per member, a protected
coordinator, and v1 refusal of the new field. Agent startup rejects a signed primary/class mismatch
before toxcore creates savedata; worker construction rejects a post-override mismatch before the
worker starts; coordinator admission rejects a proof for the wrong class. The private binding test
changes only the signed class and requires the old complete-artifact digest proof to fail. The CLI
authors and re-verifies one exact v2 artifact. New Sandwurm multi-route guests author v2, compare all
three rendered member classes to their construction inputs, and include the optional
`signed_route_network_classes_observed` truth in each receipt; the pair manifest counts both roles.
Historical compact proofs may omit these new evidence fields and retain their original claim.
The first live attempt positively reached the v2 route projections on both guests, then made 1,054
expected-to-be-retryable pull calls fail because the five-argument CLI encoding omitted the failover
byte. That attempt is not accepted evidence. The regression test now drives both per-job policy
cases through `run_cli` into a live mock Agent, so a hand-built correct packet can no longer hide CLI
serialization drift. Clean compact proof `pair.q2pka1fm` then passes the genuine positive path: both
roles observe all signed classes, the 131,369-byte tree is selected once on the exact actual-I2P
member under fail-closed policy, native stays ready, reassignment remains zero, and exact activation
completes (`evidence/2026-08-28-sandwurm-route-set-v2-actual-i2p.md`).

ADR 0226 constructs the corresponding destructive actual-I2P cell without weakening fail-closed
semantics. The client exports at least 65,536 bytes on the exact signed I2P member before the host
stops only its supervised i2pd process. It must then expose one carrier loss, one blocked
`awaiting-objects` job, and zero reassignment while native remains ready. After the same router
datadir returns under a distinct process and adapter generation, the old job is explicitly
cancelled and a distinct per-job `fail-closed tox/i2p-construction` pull must converge through the
same member with zero worker restart. The strict verifier binds the content-free host record to
both receipts, topology process/socket ownership, TAP containment, and compact inventory; its
negative self-test changes only reassignment to one and requires refusal. Genuine evidence is
accepted as compact proof `pair.jbr89_gc`: the original job reaches 69,921 bytes, records one loss
and one block with native ready and zero reassignment, then remains fenced across a distinct router
PID and adapter generation. The exact member recovers once with zero worker restart; explicit
cancellation plus a distinct fresh job completes the same tree on that member
(`evidence/2026-08-28-sandwurm-fail-closed-i2p-loss.md`).

ADR 0227 permits the already-frozen range-v1 request/result frames on an auxiliary carrier only when
the real primary authority session and exact worker each negotiated `state-sync-ranges-v1`. The
parent retains planning, reconstruction, final digest, accepted-HEAD-last, activation, and authority
ownership. The distinct `sync-file-range-actual-i2p` cell first installs a 4 MiB generation-1 basis
over native, then submits generation 2 under `fail-closed tox/i2p-construction`. Accepted compact
proof `pair.ej_4507n` attributes that successor to the signed I2P member with zero reassignment,
fetches one 128-byte artifact range, reuses 4,194,176 verified basis bytes, and activates the exact
4 MiB result. Both roles report positive range evidence and the exact same binary; all three fronts
and both routers remain stable. The 128-byte count excludes range index/manifest and protocol
overhead. This is positive transport evidence, not live range-loss continuation
(`evidence/2026-08-28-sandwurm-actual-i2p-range.md`).

ADR 0228 adds `sync-file-range-actual-i2p-loss`. The client may arm the host fault only after
`sync-status` names the exact signed I2P worker, a concrete range lane, its 1,048,576-byte bundle,
and a provider position in `[65,536, bundle-bytes)`. Loss must retire the carrier receive before
cleanup, leave no staging entry or open staging descriptor, block the fail-closed job once, and make
zero reassignment. The host preserves the router datadir and adapter listener, replaces only i2pd,
and requires SAM generation two. The same route key must recover once with zero IoTox worker restart;
the old job is then explicitly cancelled and a distinct fresh class-pinned job must complete on that
same carrier. Accepted compact proof `pair.a9zwongf` faults at 86,373 bytes, refetches the complete
1 MiB range after recovery, reuses 3 MiB of verified basis, verifies and accepts the 4 MiB target,
and explicitly activates generation 2. The strict verifier independently passes raw and compact
forms and rejects both a false native reassignment and a pre-fault position at/beyond the bundle
boundary (`evidence/2026-08-29-sandwurm-actual-i2p-range-loss.md`).

ADR 0229 repeats that exact gate as compact proof `pair.ip5q0at9` after enabling verified local
manifest reuse. The live replacement job must report `requested=1` and `committed=2`; the versioned
fault record additionally binds `manifest_reused_locally=true`. It therefore fetches only the
1,048,576-byte range instead of refetching the 786,496-byte manifest first. The verifier rejects a
range-loss proof that claims two replacement requests. Raw and compact forms independently pass.

ADR 0230 upgrades the ordinary `sync-file-range-retry` cell without changing its frozen framing or
one-retry bound. Current proofs must bind a fresh replacement FileId, positive
`range-retained-bytes == range-resumed-bytes`, zero `range-discarded-bytes`, and zero
`range-retention-fallbacks`; complete range/artifact/HEAD/activation checks remain unchanged. The
strict verifier detects historical proofs by the absence of the new keys and applies their original
positive-discard invariant, while current proof records must satisfy exact prefix resume. Accepted
compact roots are `pair.cj5y5vgt` for direct UDP and `pair.qeb99i4o` for forced TCP.

ADR 0253 adds the production-spelling boundary without creating another topology. Owned tests
require `tox/i2p` to reject incomplete strict configuration, then start both canonical and legacy
spellings against mock c-toxcore and require byte-identical TCP-only/numeric-SOCKS options. The
Sandwurm `tox-i2p baseline` cell launches exact source-linked client/device configurations through
the existing actual-I2P two-router/three-front topology. Raw and compact proof `pair.btm5vwr9`
independently report `Tox/I2P`, bilateral application success, and TAP containment with zero native
UDP/direct-bootstrap/direct-peer packets. Historical construction proofs retain their original
route projection and remain replayable.

ADR 0231 adds `sync-file-range-route-loss`. Its exact-size laboratory selector permits the one-shot
256 KiB threshold to arm only on the 1 MiB range bundle, never the 4 MiB basis or 786,496-byte
manifest prerequisite. The client must capture the initial attempt/carrier before fault, observe one
loss and one reassignment, then capture a distinct attempt and carrier. Old offer/result/terminal
truth stays fenced; the stopped identity returns within one restart budget; the job reports two
logical objects requested/committed and zero range retries. Current compact roots are
`pair.urbhf0je` for direct UDP and `pair.n76biwao` for forced TCP. They retain/resume exactly
283,797/293,394 bytes with zero discard/fallback, fetch one 1 MiB range, reuse 3 MiB of verified
basis, and complete the existing artifact/HEAD/activation checks. This is native `available`
evidence; the verifier continues to require ADR 0228's fail-closed I2P discard/block behavior.
The owned subscriber fixture then repeats the loss boundary without weakening it: the inherited 50%
prefix is truncated at a later 75% progress point, the second attempt is finished and fenced, and a
third distinct carrier/attempt/FileId resumes exactly there. Both retired carriers' stale offers and
terminals fail, duplicate loss is idempotent, cumulative retained/resumed bytes equal both handoffs,
the logical request and range-retry counts stay fixed, and the signed attempt journal ends empty.
This deterministic repeatability prerequisite is now paired with the genuine ADR 0232 evidence
below; it remains the faster owned-service regression.

`sync-file-range-repeated-route-loss` is the corresponding genuine gate. It sets the exact-size
selector above plus `--qualify-route-stop-count 2`. The 4 MiB prerequisite crosses a 4 Mbit/s client
path; after generation 2 is published the runner selects 256 kbit/s so the first 256 KiB threshold is
observable. After fault one reassigns the logical pull, the default-off qualification seam holds its
bounded object/range request frames instead of racing successor completion against route recovery.
Only the exact stopped identity returning authenticated and ready releases those frames onto the
replacement carrier. Ordinary one-fault and product paths never populate this queue. `sync-status`,
the guest receipt, and strict manifest evidence require the queue to end empty with exactly one
release. This slow-science cell uses a 1,200-second host range budget, a 1,200-second guest budget,
and a 1,500-second Sandwurm live-chain receipt envelope. Acceptance requires two
qualification faults, carrier losses, reassignments, stale-terminal fences, recoveries, retained
attempts, resumed attempts, and aggregate bulk-worker restarts. The last fault position is strictly
below cumulative retained/resumed bytes, because the latter accounts for both handoffs. Final carrier
equals the initially stopped carrier after the two-route alternation. Both carrier modes are
accepted. Direct UDP compact root `pair.le38qcl5` records 542,916 cumulative retained/resumed bytes
and a 278,313-byte final fault position. Forced TCP compact root `pair.8u14ddcy` records 564,852
cumulative retained/resumed bytes and a 289,281-byte final fault position. Each reports two loss/
reassignment/stale-terminal/recovery/restart events, zero discard/fallback/final partials, zero
queued qualification frames, one release, one 1 MiB range fetched, 3 MiB reused, and the same exact
generation-2 verification and activation (ADR 0232).

`sync-file-range-triple-route-loss` is a separately accepted gate, not a relaxed interpretation of
the two-loss proof. It raises only the default-off qualification count to three. Acceptance
requires three loss/reassignment/stale-terminal/recovery/retained/resumed/restart events, two exact
request-hold releases, cumulative retained/resumed equality, and zero discard/fallback/range retry.
With two auxiliary identities the final carrier must differ from the initially stopped carrier, and
the initially stopped identity must finish ready at `restarts=2`, `restart-budget=2`, and
`restart-budget-remaining=0` after being stopped twice. Only this cell gives each signed bulk member
a two-restart budget and uses a 1,800-second
guest/convergence deadline; existing cells retain a one-restart budget and their shorter bounds. The
first UDP attempt, diagnostic root `pair.7tfxwohw`, reached two losses and two request releases before
the inherited 1,200-second publisher deadline expired. The corrected-budget diagnostic root
`pair.6d2wjm68` then reached 289,281 bytes on attempt six but exposed a missed transient
recovery-edge latch at fault count two. Next-fault arming now shares the exact current-key/new-worker
readiness predicate already required for request release. Neither diagnostic root is acceptance
evidence. Interrupted calibration `pair.4zvkhl5g` then left attempt six at zero after the same second
release. Instrumented diagnostic `pair.ge_y8h28` identified the remaining cause: both publisher
bulk transports had reconnected at online epoch two, but neither application transcript or route
binding had recovered after its peer worker restart. ADR 0236 adds one-second retries of the exact
same HELLO and CAPABILITIES records until confirmation; no message ID, transcript, feature, or wire
format changes. Auxiliary route output now carries sent/received booleans and attempt counters, and
an owned mock-provider regression silently loses the first locally accepted copy of both records.
Post-fix UDP diagnostic `pair.fdskk7te` progressed to the next fail-closed boundary with 542,916
retained/resumed bytes and zero discard/fallback: the four-record scheduler tombstone limit could
not admit the post-third-loss carrier. ADR 0237 binds that limit to the validated host-local
namespace request quota, exports `scheduler-attempts`/`scheduler-attempt-bound`, and gives only this
cell the exact five records required by one manifest plus four range incarnations. It never evicts a
fence, and the diagnostic root is not acceptance evidence.
The triple cell now atomically exports content-free publisher `sync-status` and `routes`
watchdogs while it waits; raw failure text and compact evidence retain them. Baseline convergence
also snapshots client and publisher status/routes on failure and removes the transient records after
success. The ordinary default remains one fault; count four fails before startup. Direct UDP compact
root `pair.3iufekzy` retains/resumes 862,359 bytes at a 301,620-byte final fault; forced TCP compact
root `pair.zleebk2k` retains/resumes 871,956 bytes at a 304,362-byte final fault. Both advance
attempts 4 through 7, report three lifecycle/restart events, two request releases, zero discard/
fallback/final partials, two ready bulk routes, the exhausted `2/2/0` restart tuple, full
reconstruction, HEAD-last acceptance, and explicit activation. Runner, verifier, exporter, shell,
Nix evaluation, build, and unit checks pass (ADR 0235 and
`evidence/2026-08-29-sandwurm-sync-range-triple-route-loss.md`).

Range-bundle daemon restart is a separate accepted gate. ADR 0239 uses one formerly reserved ATM1 record byte
to distinguish old route/worker range records from plan-bound records. New records commit the exact
target/manifest/basis plan and bundle length. Startup retains only a strict positive incomplete
prefix; legacy, zero, complete-bundle, unsafe-shape, and plan-mismatch bytes fence. A fresh authorized
pull must independently reverify the signed HEAD, manifest, and basis, derive the same commitment,
and allocate fresh attempt/message/FileId identities before suffix receive. Deterministic attempt-
store and full-subscriber coverage passes, including exact restart-only counters and final HEAD-last
convergence. The genuine gate adds a two-sided reconnect barrier so the new pull cannot race ahead
of publisher authority recovery. Direct UDP `pair.xg41pthc` retains/resumes 281,055 bytes and fetches
767,521; forced TCP `pair.00992erw` retains/resumes 276,942 bytes and fetches 771,634. Both preserve
the reusable identity baseline, use distinct job/attempt/message/FileId identities, converge the
exact 4 MiB artifact, accept the HEAD last, explicitly activate, and pass raw plus compact strict
verification (`evidence/2026-08-29-sandwurm-sync-range-restart-resume.md`).

`sync-file-range-late-route-loss` isolates the near-complete one-fault row. The manifest must bind a
983,040-byte threshold and 256-kbit/s selected-range rate; the strict verifier requires the observed
fault at or above that threshold and below the 1 MiB terminal. Direct UDP `pair.tev4u3rs` retains/
resumes 984,378 bytes, leaving 64,198; forced TCP `pair.1z7_d0jn` retains/resumes 995,346, leaving
53,230. Both report one loss/reassignment/stale terminal/recovery, zero discard/fallback/final
partials, full reconstruction, HEAD-last acceptance, and explicit activation (ADR 0233). The first
unshaped calibration completed before the late fault was observable and is rejected evidence.
During handoff, the guest atomically refreshes a content-free progress checkpoint with lifecycle,
fault-count, deferred-frame/release counts, attempt/carrier, receive-position, agent-liveness, and
status-digest fields. Before final assertions it exports a second postcondition checkpoint with the
parsed counters, topology, and hashes of the complete status/routes projections. Rejected runs
therefore remain diagnosable without preserving content or treating either checkpoint as acceptance
evidence.
Every long basis, successor-publication, and range-convergence wait is also terminal on either
Sandwurm VM chain exiting. A guest that disappears without writing a failure marker is rejected
promptly with its observed chain exit status; it cannot consume the rest of a slow-science timeout or
be mistaken for transport non-convergence.

The final full-suite pass also stress-tests the adjacent offer/worker-loss interleaving. A queued
auxiliary whole-object offer may observe the exact worker disappear between the parent's live
incarnation check and the supervisor's atomic receive admission. The subscriber must claim that
`unavailable` edge as carrier-loss-in-progress, keep the job nonterminal, prevent duplicate stale
offers from touching the burned attempt, and let the authoritative offline pass apply fail-closed or
available policy. The deterministic subscriber seam and 100 consecutive full-Agent fail-closed
shard repetitions pass.

The enhanced genuine `sync-tree-route-loss` cell now closes those native-carrier rows. After positive
progress, route loss retains every positive whole-object prefix on the failed carrier; the fresh
attempts inherit the prefixes and receive only suffixes. Direct UDP `pair.jlcr7zms` retains/resumes
two attempts and 315,330 bytes; forced TCP `pair.okks1io5` retains/resumes two attempts and 252,264
bytes. Both require exact aggregate equality, zero fallback, zero final retained partials, one
loss/reassignment/recovery, two stale terminals, full activation, and 40 protected Ratox samples.
The strict full and compact verifier owns those invariants. Tor-to-Tor/I2P and whole-object
repeated/late loss remain nonclaims; native range restart is qualified separately above.

ADR 0234 adds deterministic whole-object daemon-restart coverage. Startup retains only an exact
positive canonical prefix classified in stable-device-signed attempt truth; a fresh coordinator for
the identical object burns a new attempt on a different route, seeks from three bytes, receives only
the suffix, hashes/commits the complete object, and clears the journal. Recovery also fences
zero/absent/temporary/full-corrupt/inactive debris and prunes a retained object omitted by the next
verified HEAD. `sync-status` distinguishes the operation with `restart-resumed-attempts` and
`restart-resumed-bytes`. Accepted direct-UDP compact proof `pair.f20ma62y` resumes two prefixes
totaling 115,164 bytes;
forced-TCP `pair.lj0pdz6a` resumes two totaling 159,036 bytes. Both require exact post-kill canonical
bytes = post-startup retained bytes = fresh-attempt resumed bytes, zero transport temporaries at the
crash boundary, identity preservation, full convergence, and activation. Exact bindings and
nonclaims are in `evidence/2026-08-29-sandwurm-sync-restart-resume.md`.

The actual-Tor companion `pair.3u5cjbci` reuses the same invariant under a real process fault. The
host kills only the client Tor process after 75,405 bytes; two positive prefixes totaling 102,825
bytes resume exactly through the native worker, zero fallback and zero IoTox worker restart are
required, and the same Tor member must subsequently recover. Strict verification additionally joins
three authenticated Tor circuit phases and both TAP containment records. This closes one Tor-to-native
construction row, not Tor-to-Tor or I2P continuation and not permission to change privacy class.

ADR 0212 retains the first real-router seam evidence. Two distinct i2pd 2.60.0 processes on the
founding host own separate loopback SAM listeners and nonempty public TCP peer sets. One 4 KiB
warm-up and four barrier-released 64 KiB streams cross actual I2P byte-identically through the strict
adapter. Measured clients start within 0.083 ms; their end-to-end latencies span 23.689–25.390
seconds. The strict verifier reconstructs all deterministic payloads, set commitments, and canonical
audit bytes; joins the adapter's exact b32 commitment to the server commitment; binds the historical
adapter at the receipt's Git commit; and can independently rehash a supplied router binary and
315-entry source tree. The ordinary CTest route verifies the retained content-free receipt without
requiring a live public network. This proves the actual SAM/I2P STREAM seam on one host, not Tox,
guest containment, loss/recovery, anonymity, or production performance.

## Signed update bundle and inactive-slot lifecycle

The owned registry freezes the canonical 320-byte signed manifest, exact policy grammar, signer and
payload binding, owner-private stable-file reads, and no-clobber bundle creation. Hostile or
noncanonical fields, tampered signatures/payloads, unsafe paths, unstable inputs, and policy mismatch
fail before an update effect. Policy v2 additionally freezes a positive signer-policy epoch plus a
bounded revoked-release-signer set; active and revoked keys must be canonical and disjoint, and a
rotated policy rejects future bundles signed by a retired key. The twelfth libFuzzer target drives
both manifest and policy decoders from reviewed valid seeds and requires every accepted input to
re-encode byte-identically.

Policy v3 and manifest kind 2 freeze executable intent as `linux-service-v1` without changing policy
v1/v2 or historical opaque state bytes. Direct tests reopen and rehash the exact mode-`0400` slot,
execute a genuine ELF fixture only from a sealed memfd through the internal helper, accept the exact
sequence-bound readiness record, and stop/reap the process group. Kind confusion, digest drift,
persistent execute permission, exit before readiness, policy/state reinterpretation, and invalid
activation combinations fail closed.

The durable store matrix covers stage/apply/restart/confirm, health expiry, interrupted state-first
apply, pointer-first rollback, abrupt child exit, state or slot tamper, unsafe store shapes, and exact
eight-slot admission exhaustion without deletion, recoverable quarantine, and restart continuation
from a deliberately partial move. The CLI matrix covers no-clobber release signer creation/public
inspection, reviewable overlap/retirement epochs, and last-active-signer refusal. The real-Agent fixture joins sync publication,
accepted HEAD, independent update verification, restart-incarnation health fencing, confirmation,
and a later release that automatically rolls back on its live health deadline and remains rolled back
after another Agent restart. Store-level recovery separately freezes the second-unconfirmed-incarnation
rollback path.

The `signed-update` Sandwurm cell repeats one exact 4 MiB inert bundle between simultaneous
source-linked guests over observed direct UDP and forced TCP. Each subscriber accepts the sync HEAD.
The remote device then issues public `command ... update.stage HEAD high`; the receiver requires
bilateral feature bit 20, exact current `install.firmware` authority, and the same accepted HEAD
before committing the immutable slot and terminal evidence. The receiver then applies locally,
restarts once, opens the health window, confirms the one-use token, and verifies the selected bytes.
Both receipts must agree on remote durable sender epoch/message ID, manifest, payload, and HEAD.
ADR 0186 and `evidence/2026-08-26-sandwurm-remote-update-stage.md` bind exact evidence and nonclaims;
the earlier local-only dark-feature cell remains preserved in
`evidence/2026-08-26-sandwurm-signed-update.md`.

The rev0044 real-Agent fixture goes beyond the isolated adapter. It preloads a signed service
candidate, proves a later Agent incarnation executes it while confirmation remains denied during
delayed readiness, accepts exact readiness, confirms the same live process, then stages a higher
candidate that exits before readiness. The next Agent immediately signs rollback and relaunches the
prior confirmed service through a newly reverified and sealed image.

The `update-service` Sandwurm cell then repeats the authority-gated remote stage and local adapter
lifecycle inside simultaneous source-linked guests. Direct UDP compact proof `pair.pwpgv4si` and
forced TCP compact proof `pair.rntpawny` each require a pre-readiness service kill, an Agent
`SIGKILL` with observed parent-death service exit, a health-expiry rollback, and a final ready
confirmation plus confirmed-service recovery. Every role reports six Agent restarts, three signed
rollbacks, payload kind `linux-service-v1`, and a sealed image. Both compact exports independently
pass the strict verifier; exact hashes and nonclaims are in
`evidence/2026-08-27-sandwurm-linux-service-update.md`.

The 2026-08-26 dual-carrier evidence is authority-gated remote staging and crash recovery for an
opaque inactive file; it does not retroactively prove executable deployment. The 2026-08-27
rev0044 cells qualify one sealed native-service adapter under process interruption inside VMs, but
still do not grant remote apply/restart/confirm or prove an abrupt whole-VMM/physical power cut,
bootloader behavior, hardware anti-rollback, secure boot, destructive retention, fleet rollout, or
production OTA.

## Application restart and larger-object route throughput

`application-epoch-restart-v1` has a direct registry matrix for its ordered nonce generation. The
matrix accepts a greater process-local connection epoch, accepts a greater durable process
incarnation after that counter resets, rejects a stale generation without poisoning current state,
and retains `conflicting_hello` for different nonce bytes at the exact same generation. The ordinary
session test also preserves legacy changed-HELLO conflict behavior when bit 27 is not shared.

`sync-tree-route-throughput` exercises the live Agent/worker boundary inside two simultaneous
Sandwurm guests. It runs `fixed-a,adaptive-a,adaptive-b,fixed-b`; before each phase the subscriber
Agent is stopped for at least 5,000 ms and freshly constructed from the same private identity. A hard
180-second bound requires the primary session, authority proof, and exactly two bulk routes to become
ready. Every phase then pulls two independent 16 MiB trees. Fixed must select `00`, adaptive must
select `01`, all eight revisions must explicitly activate, no reassignment may occur, and signed
work must drain four-to-zero. Four process-resource intervals and 40 post-convergence protected
Ratox samples are retained.

Direct UDP `pair.pw3ogf7q` passes fixed/adaptive totals of 179,940/154,060 ms. Forced TCP
`pair.7zsdwj15` passes 168,410/158,040 ms. Both raw and 270,336-byte compact proofs pass strict
verification against binary
`e23b5ca2fe020e476c4a49f10f188d3d73638b4fb9d2230e267f7c58a4a5ff2d`. ADR 0183 and
`evidence/2026-08-26-sandwurm-sync-route-throughput.md` bind the result, the rejected TCP diagnostic,
and exact nonclaims.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT \
  sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT \
  sync-tree-route-throughput
python3 tools/verify-sandwurm-pair.py --self-test
```

The routes share one shaped host TAP. This gate does not qualify physical bonding, independent relay
capacity, proportional scaling, randomized performance distributions, or protected Ratox latency
during the bulk phases.

## Shared-edge fair-queue qualification

`sync-tree-route-common-link-fairness` retains the known 4 Mbit common client-TAP bottleneck and the
ADR 0174 eight-job/four-withdrawal topology, but restores 1,048,643 bytes per treepack and replaces
the FIFO `netem rate` queue with HTB `1:1` plus an `fq_codel` leaf. The client holds after its 40th
protected Ratox sample until the host captures and validates the live qdisc and class JSON. The
proof manifest records exact handles, parent, 500,000-byte/s rate/ceiling, 1,000-packet limit,
active-flow count, and class/leaf traffic counters.

Direct UDP `pair.am47s4qe` and forced TCP `pair.78uagrhw` pass raw and compact verification. Both
retain `01010101`, four cancellations balanced two per route, four survivor activations, no
reassignment, work 16-to-zero, and 40 protected Ratox samples. Cancellation tails are 80/90 ms and
render maxima are 17.067/112.817 ms. ADR 0241 and
`evidence/2026-08-29-sandwurm-common-link-fairness.md` bind exact counters, hashes, and nonclaims.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-common-link-fairness
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-common-link-fairness
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT \
  sync-tree-route-common-link-fairness
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT \
  sync-tree-route-common-link-fairness
```

This gate proves one flow-aware common-link mechanism. It does not prescribe a universal qdisc,
classify traffic with DSCP or socket priority, reserve bandwidth, or claim byte striping.

## Exact auxiliary readiness-order coverage

The deterministic worker registry accepts one exact selected auxiliary identity, confirms the other
transport is constructed but qualification-held, and requires both application sessions to become
ready only after the selected route triggers the configured release interval. A separate direct-API
case rejects a negative delay. CLI cases reject either detached option, malformed or zero keys,
zero/over-60-second delays, and use without explicit route workers.

The genuine `sync-tree-route-startup-order` cell runs both corresponding two-worker readiness orders
inside two simultaneous Sandwurm guests. Its host-controlled barriers restart the protected primary
Agents one at a time, avoiding simultaneous replacement as an accidental prerequisite failure. Each
guest must observe its exact selected public key as the sole ready bulk route for ten consecutive
samples in each phase; both routes must subsequently become ready before signed tree convergence and
the protected 40-sample Ratox probe. Direct UDP `pair.nyiqwm8t` and forced TCP `pair.mdacri5e` pass
raw and compact replay against one exact binary. ADR 0176 and
`evidence/2026-08-25-sandwurm-sync-route-startup-order.md` bind the result and nonclaims.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-startup-order
python3 tools/verify-sandwurm-pair.py --self-test
```

This qualifies two exact readiness permutations. It does not qualify random timing distributions,
startup during route faults, more-worker partial orders, relay diversity, or physical-path QoS.

## Cancellation-before-route-loss coverage

The default-off `--qualify-route-stop-after-cancel` path is detached from production behavior and
mutually exclusive with the positive-byte loss seam. It waits for a terminal cancelled auxiliary
pull, then addresses only that pull's retained exact route key and worker incarnation. Existing
worker tests prove exact stop/restart identity fencing; CLI coverage rejects use without explicit
sync and signed route workers and rejects conflicting fault orders. The subscriber snapshot exposes
the existing process-private `cancellation_settled` edge: successful cleanup sets it, an injected
transport-cancel failure leaves it false, and exact cleanup retry sets it without repeating the
transport effect. The fault seam therefore cannot arm merely because the public terminal state
already says `cancelled`.

The genuine `sync-tree-route-cancel-loss` cell first requires positive receive progress, one exact
auxiliary carrier, and two units of admitted signed work. Ordinary `sync-cancel` must settle the job,
remove incoming transfers and staging, and drain work to zero before fault injection becomes
eligible. The subsequent exact route loss must cause zero reassignment; one signed-budget restart
must restore both ready bulk routes before protected Ratox. Direct UDP `pair.yv4txv1r` and forced TCP
`pair.m2396itk` pass raw and compact replay against binary
`184cef5e5dcf86f10c9ff1024d118e063ccc40ecebc3d7c59a305ee10f842284`.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-cancel-loss
python3 tools/verify-sandwurm-pair.py --self-test
```

ADR 0177 and `evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md` bind the
result.

## Shared-arm cancellation/route-loss race coverage

The optional `--qualify-route-fault-delay-ms` value is valid only beside the positive-byte seam and
is bounded to 1..60,000 ms. When the receive threshold is crossed, the Agent freezes one exact route
key, worker incarnation, position, and monotonic due time; `qualification-fault-armed=1` makes that
causal edge observable. The zero-delay path retains its immediate same-pass behavior. CLI coverage
rejects zero, detached, and over-limit delay values.

`sync-tree-route-cancel-race` waits for that armed edge with loss/reassignment still zero, then gives
both the Agent stop and an independent ordinary `sync-cancel` client 500 ms. The strict outcome is
derived from authority truth: cancel-first requires zero reassignment and a terminal carrier equal
to the stopped carrier; loss-first requires one reassignment and a distinct terminal carrier. Both
require one loss, one recovery, work two-to-zero, empty transfer/staging state, no HEAD/activation,
and protected Ratox. A first cancellation status 4 is admissible only with typed `unavailable` and
exactly one successful cleanup retry; subscriber regression coverage proves that retry does not
repeat transport cancellation.

Direct UDP `pair.h6kg4fcr` and forced TCP `pair.z9egqd57` both pass raw and compact replay against
binary `881d3abd90374bff8be8ec03191d3d632363a0bfb565677ede9efae807df2615`
as cancel-first with one cleanup retry, zero reassignment, two stale terminals, and one recovery.
ADR 0178 and `evidence/2026-08-26-sandwurm-sync-route-cancel-race.md` bind the result. This is one
shared-arm cell per carrier, not a randomized delay distribution. Startup during faults, multi-job
same-carrier races, larger-object throughput, and physical QoS remain open.

`sync-tree-route-cancel-race-loss-first` exercises the other live branch without waiting for
reassignment in the controller. From the same armed state, exact-worker stop is due at 250 ms and
ordinary cancellation at 1,000 ms. Direct UDP `pair.5gvh__p1` and forced TCP `pair.rxb2dsge` each
require one reassignment, a terminal carrier distinct from the stopped carrier, two adaptive
selections, first-request cleanup, one recovery, and protected Ratox. ADR 0179 and
`evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md` bind the result. The verifier
self-test uses both exact delay/outcome shapes and old compact replay remains valid.

## Eight-job route-population-loss coverage

`sync-tree-route-population-loss` fills two four-job auxiliary routes under fixed selection and
requires the exact initial pattern `00001111`, eight two-object jobs, and 16 signed work units. The
default-off fault seam arms after at least 65,536 aggregate receive bytes, waits 750 ms, stops one
exact worker, and freezes the IDs of every nonterminal job on that incarnation. Recovery is forbidden
until all four remembered jobs are complete or cancelled. Strict evidence requires one loss, four
reassignments, at least four stale terminal fences, 12 fixed selections, eight explicit activations,
one route recovery, work 16-to-zero, a process-resource interval, and 40 protected Ratox renders
below 250 ms.

The selector registry separately proves that a route with one free work unit cannot admit a job that
still needs two. Subscriber coverage injects one pre-offer `unavailable` object result, requires a
fresh message ID and FileId with the same scheduler attempt, rejects a late reply to the old
identity, and converges; the retry bound is finite. The auxiliary supervisor now runs file-carrier
service separately from its ordered event consumer and releases its global snapshot lock before an
exact sync-frame owner wait. The complete owned registry passes after that split.

Direct UDP `pair.j19_uhjj` and forced TCP `pair.rfnsjtqb` pass raw and compact replay against binary
`b401bbbb34259aeeaaa9b0934aadebff22388c6a1e6713957518520330955ed4`. UDP records four stale
terminals and protected Ratox p95/max 19.471/26.792 ms; TCP records eight stale terminals and
143.370/156.251 ms. Both record zero required-event backpressure on the primary transports. ADR 0180
and `evidence/2026-08-26-sandwurm-sync-route-population-loss.md` bind the exact claims and the failed
TCP attempts that selected the repairs.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-population-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-population-loss
python3 tools/verify-sandwurm-pair.py --self-test
```

This closes one deterministic four-affected-job row. Random delay distributions, startup during
fault, larger objects, independent relay paths, common-link priority, and production automatic
recovery remain open.

## New admission during active route loss

`sync-tree-route-loss-admission` distinguishes degraded admission from migration. Two fixed-policy
two-object pulls first consume four work units on one carrier. After at least 65,536 received bytes
plus the minimum valid one-millisecond qualification delay, that worker stops and both jobs must
reassign. The fixture then creates two more pulls and samples the live route/job surface before
recovery: exactly one bulk route must be ready and both new jobs must name it. Acceptance additionally
requires one loss, two reassignments, at least two stale terminal fences, six fixed selections, four
activations, one recovery, work four-to-zero, a process-resource interval, and 40 protected Ratox
renders below 250 ms.

Restart readiness now requires both a live non-zombie daemon PID and a successful local `status`
round trip. The worker supervisor separately requests carrier-service shutdown, joins it while the
event consumer remains live, then stops event draining and transports. This makes the clean restart
part of the liveness proof rather than an unobserved fixture precondition.

Direct UDP `pair.v3qc2kld` and forced TCP `pair.djhqe3we` pass raw and compact replay against binary
`db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`. UDP records a 29,259 ms
fault-to-completion interval and protected Ratox p95/max 19.149/19.980 ms; TCP records 94,046 ms and
95.741/103.416 ms. ADR 0181 and
`evidence/2026-08-26-sandwurm-sync-route-loss-admission.md` bind the exact claim. These single-cell
durations are directional observations, not a transport benchmark distribution.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-loss-admission
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-loss-admission
python3 tools/verify-sandwurm-pair.py --self-test
```

This closes new pull admission after an observed route loss and reassignment. It does not qualify
daemon cold startup with a route absent, random fault distributions, independent relays, or physical
common-link priority.

## Degraded-route admission after Agent startup

`sync-tree-route-startup-admission` begins from ordinary two-route convergence, then cleanly
restarts the same subscriber Agent with adaptive policy and the default-off exact readiness hold.
One named auxiliary route must be the only ready bulk member for ten consecutive samples. During
that interval the fixture creates two independent 16 MiB tree jobs and requires both to select the
sole route, consume four work units, and remain nonterminal. When the held route joins after 20
seconds, both jobs must still be live and retain their original carrier. Both revisions then commit
two objects, explicitly activate, and release all work without reassignment. A client resource
interval and 40 protected Ratox samples are mandatory.

Direct UDP `pair.46f6td4j` and forced TCP `pair.2gvkqs6b` pass strict raw and compact verification
against binary `db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`.
Their sync durations are 103,748/126,919 ms and protected Ratox p95/max are
22.673/23.540 ms and 102.257/129.184 ms. ADR 0182 and
`evidence/2026-08-26-sandwurm-sync-route-startup-admission.md` bind the exact claim.

Focused reproduction:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-startup-admission
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-startup-admission
python3 tools/verify-sandwurm-pair.py --self-test
```

This is a clean Agent restart inside an already-running guest with one application-ready route
deliberately held. Do not cite it as physical route absence, guest/machine cold boot, randomized
startup timing, relay diversity, or a throughput distribution.

CMake configuration also compares the project version, `REVISION`, numeric version/revision fields,
codename, and the constexpr product header. Any release-identity drift is a configuration error before
compilation; the `iotox.client-version` process route independently checks the resulting executable.

## rev0039 continuous PSI-trigger coverage

rev0039 extends the same pressure-admission controller with independently opened per-cgroup PSI trigger
descriptors, a finite poll/eventfd monitor, saturation-safe atomic event transfer, minimum-window holds,
and fail-closed monitor health. Policy tests accept a complete common-window configuration and reject
missing or detached windows, windows outside `2000000..10000000` microseconds, windows that are not
exact 2,000,000-microsecond multiples, zero or over-window stall thresholds, and triggers without their
matching avg10 reopening threshold. A pure encoder test freezes the typed `some`/`full`, decimal
spacing, terminating-NUL, no-newline kernel record and rejects undefined classes or nonportable windows.
A pure poll classifier freezes clean stop and priority-trigger masks, trigger-plus-source-loss ordering,
terminal descriptor failures, unknown-bit refusal, and invalid-role refusal. The pure state-machine test
proves an active trigger hold closes an open gate, does not double-count an already closed gate, blocks
a low sample during the hold, and preserves exact lower-boundary reopening after the hold ends.

CLI tests reject malformed, incomplete, detached, undersized, zero, over-window, and metric-mismatched
trigger options before startup. Agent and runtime-tree tests freeze configuration projection, monitor
health, active/remaining hold, typed monitor error, total/per-resource event counts, monitor failures,
trigger-caused close transitions, and hold-specific rejections. The private-cgroup pressure route
configures a quiet real memory-full trigger with a two-second window accepted for both privileged and
unprivileged monitors; on a capable host controller construction must register it and begin with a
healthy monitor and zero events before the existing disabled-accounting,
reopen, and concurrent-admission proof proceeds. Capability absence remains a named code-77 skip.

The GCC Debug, GCC Release, Clang Debug, Clang ASan+UBSan, and GCC ThreadSanitizer lanes all pass on
the construction host. The linked-Argon2 and Mutorr-preservation routes also pass, all eleven fuzz
targets complete 5,000 runs, and the exact Agent/session shard passes 100/100 repetitions. A required
Clang path-sensitive analyzer lane derives qualified compile commands for the profile resolver,
cgroup pressure controller, Agent, runtime tree, route worker, synchronization service, subscriber,
transfer bridge, and synchronization tree and completes with zero diagnostics. All nine selected
translation units use the explicitly requested deep analyzer mode. The final warm rerun also proved
the Nix-shell `libargon2` discovery path used by the linked-Argon2 lane. Five privileged
private-cgroup routes remain explicit skips because the container does not expose a writable delegated
cgroup-v2/PSI environment. A skipped live trigger event is not represented as positive event-delivery
proof.

Focused reproduction:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 4
ctest --preset gcc-debug --output-on-failure

ctest --test-dir build/gcc-debug \
  -R 'iotox\.(unit-and-integration|terminal-cgroup-pressure-admission-process)$' \
  --output-on-failure
```

These checks establish the implemented policy grammar, deterministic hold/hysteresis composition,
bounded runtime evidence, monitor-registration startup path when supported, and fail-closed construction
semantics. They do not establish real-time notification latency, positive trigger delivery on this host,
safe deployment thresholds, target-fleet compatibility, or production readiness.

## ADR 0327 NixOS systemd cgroup VM coverage

`nix build .#checks.x86_64-linux.ratox-cgroup-vm -L` is now the isolated positive Ratox cgroup/PSI
kernel gate. It boots an x86_64 NixOS KVM guest on Linux 6.6.94 with `psi=1`, verifies cgroup v2 and
the `cpu`, `memory`, and `io` controllers, and runs the cgroup process oracle inside five separate
transient `systemd-run --property=Delegate=yes` services.

The accepted VM output is
`/nix/store/8yssjglgwhs8f943xjk8sjj9qn2x1gka-vm-test-run-iotox-ratox-cgroup`. The source-linked
harness IoTox SHA-256 is
`63fc8acf4c54ad037c2824fbd36d5814ddf13acd709e0310369e45b1b23ff07e`; the cgroup process-oracle
driver SHA-256 is
`5a0f6b20e756465b9f659521cad2ec134ba6bc12eced7e4c38364b1119128648`.

The five positive routes are boot-bound orphan recovery, memory/pids with an observed kernel
pids-controller rejection, CPU throttling with retained work accounting, real block-device I/O
discovery and nonzero write accounting, and PSI admission with quiet trigger registration, disabled
accounting fail-closed behavior, recovery, and concurrent admission accounting. The VM script
completed in 14.73 seconds after boot. This qualifies one Linux/systemd delegation slice; it does not
prove every host cgroup policy, physical device, parent throttling/IO contention, trigger-delivery
latency, Tox traversal, long soak, or production activation. Details live in
`evidence/2026-09-03-ratox-cgroup-kernel-qualification.md`.

## rev0038 PSI-admission hysteresis coverage

The direct owned registry contains 356 checks and the default CTest surface contains 19 entries. New
parser cases retain exact `avg10`, `avg60`, and `avg300` basis points, including `0.00`, ordinary
fractional values, `99.99`, and `100.00`, while preserving cumulative PSI totals. Malformed cases
reject missing or extra fractional digits, signs, leading zeroes, values above `100.00`, duplicate
keys/classes, noncanonical spacing, truncation, overflow, and oversized evidence.

Pure state-machine checks freeze strict close boundaries, exact reopen equality, common hysteresis,
zero thresholds, a full-range `10000/10000` policy, missing configured observations, disabled policy,
and open/closed transition flags. Profile-policy tests reject detached or over-wide hysteresis; CLI
tests reject malformed/out-of-range values, missing thresholds, missing delegated roots, and semantic
threshold/hysteresis conflicts. Agent tests prove policy/controller rejection under the signed host
lease before resource probes, orphan recovery, listener activation, or network exposure. Runtime-tree
checks freeze every configuration, state, counter, last-sample-validity, typed sampling-error,
observation-presence, and last-value field.

Production-factory process tests prove malformed policy is rejected before cgroup filesystem access,
missing roots fail at construction, ordinary filesystems cannot masquerade as cgroup v2, startup
configuration status is immutable, and failed configuration leaves pressure and aggregate accounting
unmodified. The pressure check executes before aggregate reservation, session-cgroup creation, PTY
creation, or helper spawn.

The exclusive Agent/session stress lane retains exact delivery, copy-count, and arrival-rank assertions
for the deterministic mock's successful probe sends. It discovers the linked registry and target shard
from a complete clean run; retained-artifact refresh independently requires that published shard
denominator to equal the current source registry and rejects stale transcripts. Its five-second burst
deadline covers replies crossing the production owner, event, and local-control threads; the request still returns as soon as all
six replies arrive. A one-second prequalification deadline produced one scheduler-induced false loss at
repetition 78 and is not retained as green evidence.

A dedicated nineteenth process route uses a private cgroup-v2 mount when the host exposes per-cgroup
PSI. It creates the real descriptor-pinned controller, admits one valid sample, writes
`cgroup.pressure=0`, requires two fail-closed rejections with one close transition and typed invalid-
sample evidence, restores `1`, requires exactly one reopen, serializes an eight-thread valid-admission
burst with exact counter totals, and independently proves disabled-accounting startup refusal. The
2026-08-19 construction host runs Linux 6.18.35 but exposes no `cgroup.pressure`; the route therefore
returns the named code-77 capability skip and no live positive PSI-admission claim is made.

Focused reproduction:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug --parallel 2
ctest --test-dir build/gcc-debug \
  -R 'iotox\.(unit-and-integration|terminal-posix-process|terminal-cgroup-pressure-admission-process)$' \
  --output-on-failure

cmake --preset clang-debug
cmake --build --preset clang-debug --parallel 2
ctest --test-dir build/clang-debug \
  -R 'iotox\.(unit-and-integration|terminal-posix-process|terminal-cgroup-pressure-admission-process)$' \
  --output-on-failure
```

These checks establish exact grammar, deterministic hysteresis, before/after accounting proof,
fail-closed startup/sampling, pre-recovery and pre-spawn mutation ordering, normalized local failure
classification, bounded private evidence, concurrency-safe state, and capability-aware live-oracle
behavior. They do not
select safe thresholds, make sequential resource reads atomic, forecast demand, guarantee latency or
throughput, qualify kernels without PSI, exclude privileged cgroup writers, or establish production
readiness.

## rev0037 memory-work, swap-failure, freeze, and IRQ-accounting coverage

The direct owned registry contains 351 checks and the default CTest surface remains 18 entries. New
flat-key parser cases freeze reordered complete `memory.stat`, `memory.swap.events`, and
`cgroup.stat.local` records; older optional-tuple absence; future numeric keys; and rejection of
missing mandatory fields, duplicate keys, partial reclaim/swap tuples, signs, leading zeroes,
overflow, malformed spacing, truncation, and oversized evidence. Dedicated IRQ PSI cases require a
complete `full` class, accept a future well-formed class and a future `some` class without assigning
new semantics, and reject missing/partial/duplicate `full` evidence. The cgroup-record fuzzer offers
every input to all four new parsers in addition to the existing controller, peak, I/O, and PSI
grammars.

Factory-state tests retain distinct memory fault/reclaim/swap work, swap high/max/fail events,
freezer duration, and IRQ-full totals; prove whole-interface and nested-tuple capability counts;
suppress duplicate outcome submission; reject every partial incomplete outcome; and exercise
saturation of every counter. Runtime-tree tests freeze all seventeen new owner-private fields and
continue the exclusion oracle for session, profile, payload identity, process, command, path, peer,
device, error string, and terminal content.

The production path pins protected descriptors before payload attachment, verifies zero baselines,
and reads the same descriptors only after recursive `populated=0` and before exact leaf removal. The
lifecycle private-cgroup route induces post-attachment anonymous page faults, freezes and thaws the
attached payload where `cgroup.stat.local` exists, requires positive page-fault and freeze-duration
evidence when supported, and compares every available final memory/swap/local/IRQ record with the
one-shot outcome. On the construction host the lifecycle and complete default GCC Debug suites pass;
the memory/PID, CPU-bandwidth, and I/O policy routes retain explicit code-77 skips where the outer
container does not provide writable preactivated controller delegation. The host does not expose
`irq.pressure`, so no positive live IRQ PSI result is claimed.

These checks establish bounded grammar, zero baselines, exact descriptor-pinned one-shot capture,
capability-aware aggregation, saturation, private projection, and positive live page-fault/freezer
behavior. They do not establish swap-failure generation, positive IRQ pressure, continuous
monitoring, working-set inference, interrupt attribution, adaptive admission, target-fleet support,
or protection from a privileged cgroup co-writer.

## rev0036 peak-resource kernel-accounting coverage

The direct owned registry contains 348 checks and the default CTest surface remains 18 entries. Peak
parser tests freeze canonical single unsigned LF-terminated records and reject empty, multiline,
whitespace-padded, signed, leading-zero, overflowing, truncated, and oversized evidence. CPU parser
tests freeze the mandatory usage/user/system work tuple, controller-disabled records, older bandwidth
records without burst fields, current complete burst records, accepted future counters, and rejection
of every partial or detached bandwidth/burst tuple. The terminal-cgroup fuzzer now offers every input
to the peak parser as well as the existing counter, I/O, and pressure grammars.

Factory-state tests retain independently optional PID, memory, and swap peaks; prove observed-session
counts, sums, maxima, duplicate suppression, and saturation; and freeze nested CPU work, bandwidth, and
burst capability accounting. Runtime-tree tests project every new content-free owner-private value and
continue the exclusion oracle for session, profile, payload identity, process, command, path, peer,
device, error string, and terminal content.

The production path opens available `pids.peak`, `memory.peak`, and `memory.swap.peak` descriptors before
attachment and requires zero fresh-leaf records. It attempts `cpu.stat` even when no CPU quota is
configured. After recursive quiescence and before exact leaf removal, the same pinned descriptors are
read into the one-shot complete outcome. The lifecycle private-cgroup route proves nonzero CPU usage
without quota policy, exact usage/user/system retention, and exact equality for every available peak
read immediately before removal.

On the construction host, the expanded owned registry and lifecycle route pass. Memory/PID, CPU
bandwidth, and I/O policy routes retain named code-77 skips where writable preactivated delegation is
unavailable. These checks establish bounded grammar, zero baselines, quota-independent CPU work,
one-shot capture, explicit capability absence, saturation, and private projection. They do not
establish live peak monitoring, simultaneous demand, working sets, adaptive admission, target-fleet
support, or protection from a privileged co-writer.

The whole-binary lifecycle route keeps byte-identical assertions in every lane. Because sanitizer
instrumentation applies independently to the agent and the many short-lived CLI processes it forks,
ASan and TSan builds compile that harness with a bounded deadline multiplier and a correspondingly
larger outer CTest watchdog. Normal builds retain the original polling budgets. This is scheduler
headroom for asynchronous callback and filesystem projection evidence, not a retry, assertion skip, or
product timeout change.

## rev0035 pressure-stall kernel-accounting coverage

The direct owned registry contains 346 checks and the default CTest surface remains 18 entries. Two
new parser tests freeze valid reordered CPU/memory/I/O PSI grammar, exact absolute totals, optional
`full`, accepted future numeric fields/classes, and strict rejection of missing classes/keys,
duplicates, malformed spacing, truncated records, noncanonical or overflowing integers, malformed
percentages, percentages above `100.00`, and nonnumeric future values. The terminal-cgroup fuzzer now
offers every input to the PSI parser in addition to the PID, memory, CPU, `io.max`, and `io.stat`
grammars.

Factory-state tests attach distinct CPU, memory, and I/O pressure outcomes to a complete session,
prove one-shot duplicate suppression, verify independent observed-interface and observed-`full`
counts, and exercise saturating microsecond accumulation. An incomplete outcome contributes no partial
PSI totals. Runtime-tree tests freeze all twelve new owner-private fields alongside the prior
content-exclusion oracle.

The production path opens protected optional `cgroup.pressure`, `cpu.pressure`, `memory.pressure`, and
`io.pressure` descriptors before attachment. A present control must remain exactly enabled; every
available resource record must begin with zero cumulative totals. After recursive quiescence and
before exact removal, the same bounded parser captures absolute microseconds. Live memory, CPU, and
I/O routes read each available pressure record immediately before removal and require exact equality
with the one-shot outcome returned after removal.

On the construction host, the owned registry and lifecycle cgroup route pass. Memory/PID, CPU, and I/O
resource routes return their named code-77 skips because writable preactivated controller delegation
is unavailable. No positive resource-specific PSI result is fabricated. These checks establish parser,
zero-baseline, one-shot capture, capability-preserving aggregation, saturation, and private projection.
They do not establish live pressure monitoring, threshold triggers, causal diagnosis, adaptive
admission, latency/throughput guarantees, target-fleet support, or protection from a privileged
co-writer.

## rev0034 I/O bandwidth and kernel-accounting coverage

The direct registry contains 344 checks and the default CTest surface contains 18 entries. Canonical
profile tests now freeze `iotox-terminal-profile-v5` with ordered `cgroup-io-device`, `cgroup-io-rbps`,
`cgroup-io-wbps`, `cgroup-io-riops`, and `cgroup-io-wiops` fields. Exact canonical v1 through v4
records are decoded against their own historical encoders and migrate to v5 without invented I/O
policy. The terminal-profile corpus retains every prior seed and adds one current v5 record. A new
terminal-cgroup fuzzer drives the bounded PID, memory, CPU, `io.max`, and `io.stat` parsers from
reviewed valid seeds; together with the previously omitted terminal-protocol target, the retained fuzz
proof now covers all eleven configured fuzzers.

Validation tests reject device-only and ceiling-only envelopes, `0:0`, zero and oversized finite
ceilings, malformed/noncanonical device numbers, and host/profile device mismatches. Composition tests
prove absent-side inheritance and independent per-direction minima for one matching device while
retaining all process, memory, swap, and exact-rational CPU invariants. CLI tests freeze all five host
options and reject incomplete or malformed policy before delegated-tree activation.

Dedicated nested-key tests exercise unordered `io.max` fields, explicit `max`, required standard keys,
unknown future keys, duplicate device lines, duplicate keys, noncanonical spacing and decimals, zero
finite ceilings, truncation, and semantic equality. `io.stat` tests cover an empty zero record,
unordered multi-device records, an optional complete discard pair, unknown future numeric keys, missing
read/write counters, duplicate devices/keys, malformed device identity, truncation, and saturating
cross-device sums.

Factory-state tests retain one-shot complete/incomplete outcomes with the six I/O counters, duplicate
suppression, exact accumulation, and saturation even when aggregate reservation ceilings are disabled.
Runtime-tree tests freeze the six new owner-private fields and retain the content-exclusion oracle.
The production cgroup path compiles with warnings as errors and opens `io.stat`, requires a zero
baseline, captures it after recursive quiescence, and records the outcome before releasing admission.

The construction host exposes `io` in the host controller inventory and a genuine root `io.stat`
record, but its host cgroup-v2 mount is read-only and the isolated namespace root does not have `io`
preactivated for child cgroups. The positive I/O process oracle therefore returns its own named code-77
skip before policy mutation. This is an explicit environmental limitation, not a fabricated pass. The
default 18-entry CTest suite records the memory/PID, CPU, and I/O live resource routes independently;
a target deployment still needs a writable exclusive `io` delegation and a load generator tied to the
reviewed device topology.

These checks establish canonical migration, semantic parsing, monotone composition, production-path
ordering, saturating outcome accounting, and private projection. They do not establish reserved media
bandwidth, deterministic latency, queue-depth policy, filesystem or network I/O control, writeback
causality, correct automatic topology selection, protection from a privileged co-writer, or target-
fleet qualification.

## rev0033 memory-high and kernel outcome telemetry coverage

The direct registry freezes canonical `iotox-terminal-profile-v4` bytes with the sixth ordered
`cgroup-memory-high-bytes` field. Exact canonical v1, v2, and v3 records still decode, each is checked
against its own historical encoder, and public re-encoding migrates to v4 without inventing a high
threshold. The terminal-profile fuzzer retains historical seeds and adds a current v4 seed; its
semantic and second-encode canonicality oracle now targets v4.

Validation checks reject zero and non-page-aligned high thresholds and reject one policy envelope in
which high exceeds hard max. Composition checks prove host/profile minima, absent-side inheritance,
and the cross-layer clamp that prevents effective `memory.high > memory.max`. Existing aggregate
memory charge tests remain tied to hard `memory.max`; no test treats the throttle boundary as reserved
capacity. CLI tests reject malformed high values before startup, and the product help/version routes
freeze the new option and rev0033 identity.

Dedicated keyed-record tests cover canonical and reordered PID, memory, and CPU counters, accepted
unknown future fields, optional older-kernel `oom_group_kill`, missing required keys, duplicate keys,
noncanonical decimals, and truncated records. A factory-state test records complete and incomplete
outcomes with aggregate ceilings disabled, proves one-shot duplicate suppression, verifies exact
counter sums, and exercises the saturating accumulator boundary. Runtime-tree tests freeze all twelve
new owner-private status fields while retaining the content-exclusion oracle.

The production process lifecycle records the session outcome after exact cgroup removal and before
reservation release in normal exit, startup rollback, and destructor cleanup. The real-kernel proof
is split by controller dependency. The memory/PID route requires exact `memory.high` readback, live
pressure that increments the local-or-childless `high` event, and one-shot retention of observed
`pids.max` rejection and memory throttling. The CPU route requires exact `cpu.max` readback and
retention of observed CPU usage, periods, and throttling. Each route reports its own named skip when
that controller delegation is unavailable; a skip is not reported as positive kernel qualification.

These checks establish parser, migration, composition, lifecycle-ordering, aggregation, and private
projection behavior. They do not make `memory.high` a hard ceiling, establish PSI policy, provide
per-session labels or rates, qualify a target fleet, or defend against a privileged competing cgroup
manager.

## rev0032 exact rational aggregate CPU admission coverage

The direct registry retains rev0031's process, memory, and swap policy checks and extends the shared
resolver to CPU quota/period policy. Aggregate period-without-quota, out-of-range quota/period,
missing finite session quota, oversized session ratio, and nonrepresentable normalization all fail as
typed policy errors. Default-period behavior and exact unequal-period normalization are explicit.

A bounded lattice of 1,120 aggregate/session quota-period combinations is checked against an
independent small-integer oracle. The oracle uses safe cross-products and divisibility only within its
bounded domain; the production resolver uses continued-fraction comparison plus GCD reduction. This
separation is intended to catch swapped ratios, accidental raw-quota summation, and quiet floor/ceil
rounding regressions.

The admission-controller checks prove exact atomic process/memory/swap/CPU charging, current and
monotone peak accounting, typed whole-vector capacity rejection, move-only transfer, explicit
idempotent release, automatic scope release, conservative idempotent stranding with the complete
charge retained, no charge on invalid policy, and no active token when aggregate policy is disabled.
A barrier-driven concurrent test saturates both process and normalized CPU dimensions, observes the
exact admitted/rejected split and peak, then requires every releasable charge to drain to zero. The
required GCC ThreadSanitizer lane passes for this path, and the focused Clang analyzer emits no
diagnostic for the exact normalization implementation.

Agent tests reject aggregate policy without a delegated root, reject enabled profiles missing a
configured dimension, reject profiles whose single exact reservation cannot fit, and reject CPU
ratios that cannot be represented at the selected accounting period. These failures occur before
transport state or delegated-tree mutation. The production POSIX process test independently proves
that a normalized CPU charge is claimed before helper-path validation and automatically rolled back
to zero on the forced post-charge failure while peak evidence remains. A separate nonrepresentable
CPU case proves direct-factory rejection before admission state mutates. CLI and runtime-tree checks
freeze both aggregate CPU options and the configured/quota/period/current/peak status fields.

These tests establish deterministic host-local configured-maximum accounting and factory ordering.
They do not reserve physical processor time, synchronize kernel quota periods, enforce a parent
`cpu.max`, model burst concurrency, guarantee latency/throughput, prove PSI policy, qualify a
privileged external cgroup writer, or replace the real-kernel per-session controller oracle.

## rev0030 profile-scoped cgroup budget coverage

The direct registry freezes the canonical `iotox-terminal-profile-v3` record, including all five
ordered `none|u64` budget fields, byte-for-byte round trips, v1/v2 migration to an empty budget, and
refusal of mixed-case absence markers, leading-zero aliases, period-without-quota, and host-page
misalignment. A current v3 corpus seed supplements the retained v1 migration seed for the terminal-
profile fuzzer. Its oracle accepts deliberate canonical v1/v2-to-v3 byte growth and instead requires
semantic equality after canonical v3 encode/decode.

Composition tests prove scalar minima, meaningful zero swap, absent-side inheritance, deterministic
host representation for equal CPU ratios, and exact lower-ratio selection at values whose naive
64-bit cross-products would overflow. The shared validator is exercised through profile validation,
CLI parsing, Agent activation, and the production factory.

Agent coverage proves that an enabled profile budget without a delegated root fails before transport
startup and identifies the local profile in the diagnostic. Production-process coverage independently
proves that direct factory use recomputes and rejects an unrooted effective profile budget before
filesystem or spawn work. Runtime-tree coverage freezes only aggregate host-budget, enabled profile-
budget, and distinct preflight-policy counts.

The real-kernel rev0029 resource process oracle remains the enforcement backend for effective values.
On a qualifying host it writes and reads back the selected policy before helper attachment. On this
cloudtainer it records named skip code 77 because the required `cpu` controller is not preactivated for
child cgroups; no positive resource-controller qualification is fabricated.

## rev0029 controller-enforced cgroup resource-budget coverage

The direct registry rejects zero/out-of-range pids limits, period-without-quota, sub-millisecond CPU
bandwidth, oversized CPU periods, zero/unaligned memory, unaligned swap, policy without a delegated
root, and malformed CLI values before any cgroup filesystem access. Agent tests prove malformed or
unrooted policy fails before transport startup; the production PTY factory repeats the unrooted
policy fence.

`iotox.terminal-cgroup-recovery-process` retains every rev0028 lifecycle and recovery branch.
`iotox.terminal-cgroup-memory-resource-process`, on a suitable non-threaded delegated hierarchy,
proves disposable preflight removal, exact pids/memory-high/memory/swap/OOM read-back, `pids.max`
exhaustion through `EAGAIN`, positive PID-limit and memory-high event counters, recursive kill,
one-shot teardown retention, exact leaf removal, and refusal of an available-but-inactive controller
before a session leaf appears. `iotox.terminal-cgroup-cpu-resource-process` independently proves exact
CPU read-back, positive usage/period/throttling counters, recursive kill, one-shot teardown retention,
and exact removal without making memory/PID qualification depend on CPU delegation.

In the rev0033 qualification run, `iotox.terminal-cgroup-recovery-process` passes its positive
real-kernel lifecycle/recovery branches. The independent memory/PID and CPU routes each return
deterministic skip code 77 because their required controllers are not preactivated for child cgroups
on this host. Those skips are not positive resource-controller qualification; both executable
branches remain active for a suitable delegated host. The retained rev0029 historical report
separately records the topology observed during that earlier qualification and is not rewritten as
current evidence.

## rev0028 boot-bound delegated-cgroup recovery coverage

Seven owned checks freeze the recovery identity and fail-closed parser boundary:

```text
canonical Linux boot UUID parsing and compact-name rendering
exact boot/PID/procfs-start-time/sequence cgroup-name round trips
rejection of aliases, zero fields, uppercase hex, overflow, and trailing fields
live current-incarnation preservation and stale boot/start-time classification
pidfd-backed rejection of a zombie owner as live
bounded candidate-count and recovery-wait policy validation before filesystem access
ordinary-filesystem rejection for both creation and recovery
```

The Agent integration path also proves that the signed Ratox host-incarnation lease is acquired before
delegated-root recovery: a competing legitimate daemon is rejected before it can inspect or mutate the
cgroup namespace. A configured ordinary-directory root fails before toxcore state is created.

`iotox.terminal-cgroup-recovery-process` enters isolated user, mount, and cgroup namespaces, mounts a
fresh cgroup-v2 hierarchy, and exercises the real kernel interfaces. It preserves a leaf owned by an
exact live daemon incarnation; kills the recursive payload of a deliberately crashed creator; waits
for `cgroup.events` to report `populated 0`; removes the pinned leaf; removes an empty legacy leaf;
refuses a populated legacy leaf; refuses a malformed reserved name; and proves candidate-bound
failure occurs before an otherwise stale leaf is mutated. Hosts that deny the required namespace or
cgroup mount return skip code 77 rather than a synthetic pass.

Together these checks establish the local kernel construction for one writable delegated hierarchy.
They do not qualify a deployment fleet, another service manager's delegation policy, hostile
privileged co-writers, target-fleet resource policy, or PTY survival across daemon restart.

## rev0022 R7 attested-evidence-chain coverage

The v2 Python self-test constructs the full 12,000-trial balanced schedule, joins raw controller and
host timestamps to exact session/message/input/output/event coordinates, generates two deterministic
Ed25519 capture keypairs, signs both role-specific payloads, seals the bundle, and verifies identical
qualification reports twice. Negative cases reject canonical-row tampering, signature substitution,
globally reordered host events, altered route evidence, reuse of one file for both auxiliary evidence
roles, and symlink evidence paths. The self-test also verifies that the schedule stream changes when
the run ID changes despite seed reuse, and that host-local durations are never compared arithmetically
with controller-local durations.

The owned C++ registry verifies that one staged INPUT and its whole-frame PTY commit retain the same
message ID, exact sequence range, and byte count. Runtime-tree tests verify projection of those safe
coordinates while continuing to reject terminal content, argv, and environment leakage. Cross-row
v2 validation requires globally monotonic controller/host observations, globally increasing host event
ordinals, unique message IDs, and nonoverlapping per-session input/output spans.
Reports retain independent p50/p95/p99 distributions for every same-clock stage and owner queue wait.

This coverage proves deterministic construction, verification, and content-free local joins. It does
not prove route truth, load-generator truth, clock calibration, uncompromised capture binaries, or a
genuine two-guest Sandwurm R7 latency pass.

## rev0027 bounded and process-pinned local-admission coverage

The direct registry adds nine availability regressions across the two private Linux seqpacket
planes:

```text
silent administrative peers do not serialize a ready request behind their leases
one process cannot occupy the entire administrative pending-client budget
four admitted silent administrative leases expire in one shared poll horizon
the true global administrative pending-client ceiling rejects and recovers
a retained administrative socket is released when its exact connector exits
an administrative client abandons a retained response socket when the exact server exits
silent terminal contenders do not impose their lease latency on an active stream
one process cannot occupy the entire terminal contender budget
a retained silent terminal socket releases the pre-OPEN slot when its exact connector exits
```

The tests use deliberately small global/per-process quotas and admission intervals to exercise the
production scheduler rather than a test-only implementation. On kernels exposing `SO_PEERPIDFD`,
separate-process oracles keep a connected descriptor alive outside the connector/server process and
require exact process exit to release the wait well before its lease. Existing successor-race coverage
still requires an active descriptor terminal event to release the old controller before a same-cycle
contender is denied. Configuration tests reject zero or incoherent pending, per-process, accept,
record-work, and interval bounds. These checks establish finite owned admission behavior under the
tested schedules; they do not establish starvation freedom against unlimited same-UID processes or
preempt a blocking callback. The direct registry is 322/322 at this revision.

## rev0026 message-bound local-IPC coverage

The direct registry adds ten adversarial checks around the two private Linux seqpacket planes:

```text
terminal request from a fork-inherited controller descriptor is rejected
terminal request-side SCM_RIGHTS descriptors are closed and rejected
terminal owner-process exit releases a passed descriptor through pidfd liveness
terminal response-side SCM_RIGHTS descriptors are closed and rejected by the client
control request from a fork-inherited client descriptor is rejected
control request-side SCM_RIGHTS descriptors are closed and rejected
control response from a fork-inherited accepted server descriptor is rejected
control silent request expires and admits a successor
control active listener and shutdown replacement inodes are preserved
unsafe control paths, ownership/modes, and request leases fail before service
```

Every accepted request and response requires exact message credentials in addition to connection-time
peer credentials. Supported kernels also exercise exact `SCM_PIDFD` agreement; the portable Linux
fallback retains mandatory `SCM_CREDENTIALS`, and the terminal server opens an exact owner pidfd when
record delivery is unavailable. Ancillary truncation, duplicate credentials, malformed records, and
unexpected descriptors are fail-closed parser paths. The direct registry is 313/313 at this revision.

## rev0025 delegated-cgroup lifecycle coverage

The owned registry adds seven cgroup-specific checks. They require strict parsing of the recursive
`cgroup.events` record, mandatory and unique boolean `populated`, bounded future numeric fields,
rejection of ambiguous grammar, rejection of inherited/root/daemon-equal payload identities, and
refusal of an ordinary lookalike directory that is not backed by cgroup v2. An Agent-level check
proves that a relative root, an injected process factory, and an inherited profile identity are all
rejected before transport state is created.

The native PTY process oracle crosses the production factory and requires cgroup configuration to
fail closed for an inherited identity, a compatibility profile, and an ordinary non-cgroup directory.
The construction path itself securely walks a normalized absolute delegation, verifies cgroup-v2
filesystem identity and supervisor-only write authority, creates and inode-pins one private leaf,
attaches the blocked helper before releasing its manifest, uses `cgroup.kill` for final teardown, and
waits for recursive `populated=0` before removal and leader reap.

The qualification host exposes a genuine cgroup-v2 mount, but that mount is read-only and provides no
writable delegated subtree. Therefore this revision proves parser, policy, pre-network, ordinary-path,
and named fail-closed behavior here; it does not claim a positive live delegated-cgroup lifecycle on
this host. That success lane remains an explicit supported-host qualification requirement.

## rev0024 procfd, quiescence, process-handle, and host-seal coverage

The owned registry adds a child-local process-hardening oracle. It invokes the enabled-host seal
twice, requires `PR_GET_DUMPABLE == 0`, requires both `RLIMIT_CORE` values to be zero, and confirms the
parent test process retains its original dumpability and limits.

The exec'd baseline payload calls every process-handle interface available in the build headers:
`pidfd_open`, `pidfd_send_signal`, `process_madvise`, and `process_mrelease`. `EPERM` is required before
ordinary PID, descriptor, or argument validation, and the report retains the exact compiled probe
count. The parent-side startup path also requires that the opened `/proc` inventory reports
`PROC_SUPER_MAGIC`.

The native PTY process test adds two lifecycle oracles. The direct quiescence fixture lets the leader
exit and become a zombie; the first and second empty full-session inventories must leave it waitable,
while the third must reap it with unchanged status and idempotent observation. The bounded fork-churn
fixture creates at most 48 descendants, moves them into separate process groups, ignores HUP/TERM,
and starts shutdown while creation is still active. The controller must converge under SIGKILL and
every captured PID/start-time incarnation must be gone. The test is finite and profile-limited; it is
not an unbounded fork workload.

These probes establish the implemented procfs-directory/start-time/pidfd checks and repeated
quiescence rule on the qualification host. They do not establish cgroup-v2 ownership,
`cgroup.kill` fork/migration atomicity, immunity to every theoretical procfs schedule, or target-fleet
qualification.

## rev0023 terminal capability, argument-fence, and supervision coverage

The 294-check owned registry adds canonical profile-v2 round trips, explicit v1-to-compatibility
migration, invalid-tier refusal, and strict-root-cwd refusal. `iotox.terminal-posix-process` crosses the
real hidden-child handoff and requires zero effective/permitted/inheritable capabilities at final exec,
seccomp filter mode plus a denied hazardous syscall in baseline, and—when the launcher has the needed
privilege—locked securebits plus an empty bounding set. The helper also rechecks nondumpability and the
parent-death contract around identity and exec-sensitive transitions.

rev0023 adds paired argument-level probes. Filter generation and the exec'd fixture consume the same
build-header-derived `kDeniedTerminalIoctlRequests` table. The fixture reports the table's exact
compiled size, invokes every entry on descriptor `-1`, and requires `EPERM` before normal descriptor
validation; `TIOCSTI` is also retained as an explicit injection oracle. Ordinary `TIOCGWINSZ`
reaches the kernel and returns `EBADF`. An otherwise-invalid legacy clone carrying a namespace flag must return `EPERM`;
the same invalid shape without a namespace bit must reach the kernel and return `EINVAL`. `clone3`
must return `ENOSYS`, and a real `std::thread` created after final exec must still run through libc's
inspected legacy-clone fallback. A separate registry check parses textual version/revision identities
and requires them to match the numeric fields emitted in the protocol HELLO, preventing release
identity drift.

The parent-side process test requires baseline pidfd/procfs support, proves one additional live
`anon_inode:[pidfd]`, and crosses production `waitid(P_PIDFD, ..., WNOWAIT)` or its narrow direct-child
wait fallback. A descriptor duplicated without CLOEXEC above 255 must be absent after final exec.
Separate-process-group fixtures ignore HUP/TERM and prove repeated session-wide KILL convergence both
for explicit close and after natural leader exit; the latter must preserve leader exit status 0.
Compatibility remains separately documented as the historical process-group path.

ASan and TSan reserve large virtual shadow mappings before the instrumented IoTox setup helper enters
`main()`. Only those sanitizer process-oracle lanes therefore omit the finite `RLIMIT_AS`; ordinary
GCC/Clang debug and release lanes still enforce the 512 MiB profile cap, and the final exec'd payload
fixture remains native. rev0023 extended the existing ASan exception to TSan after the TSan native
oracle exposed a pre-readiness helper exit rather than accepting that closure as a product failure.
rev0024 additionally marks the sanitizer whole-binary lifecycle oracle `RUN_SERIAL`: its queue
coalescing assertions remain deterministic when `ctest -j` is used instead of competing with multiple
shadow-instrumented registries for the same qualification CPU.

Strict process coverage uses an already-open non-root working directory. Its enforcement branch
requires in-tree file creation, cross-directory rename/truncate/unlink, and pathname-UNIX bind to
succeed; requires out-of-tree create/truncate/unlink, TCP connect/bind, UDP send/connect/bind,
pathname-UNIX connect, abstract-UNIX connect, and external signaling to be denied; and checks MDWE
plus the baseline seccomp floor. On a host or outer execution sandbox that cannot provide MDWE,
Landlock ABI 10, or seccomp, the only accepted alternative is a named fail-closed startup stage with
no outside mutation and no target readiness. This establishes the implementation's
success-or-refusal behavior; it does not qualify strict mode as available on every kernel, constrain
filesystem reads/executes, or establish namespaces/cgroups/container isolation.

## rev0021 R7 observability and bounded-evidence coverage

The 292-check owned registry adds exact and conservative histogram percentile tests, the strict
1,999/2,000 us boundary, saturation-safe summaries, typed c-toxcore sensitive-send classification,
concurrent coherent-snapshot invariants, lane-separated retained-head streak/age behavior, monotonic
lifecycle timestamps, and complete runtime-tree projection. The analyzer self-test covers the passing
12,000-sample matrix, deterministic reports, direct-UDP threshold failure, strict owner-boundary
failure, ordinal gaps, impossible stages, missing/oversized cells, zero and noncanonical integers,
metadata/line/input bounds, non-ASCII, symlink refusal, and file encoding failure.

`IOTOX_TEST_SHARD_COUNT=1` preserves the monolithic registry. Four- and sixteen-shard configurations
are release gates for selection completeness and sanitizer wall-time control. Shards are deterministic
and labeled `owned-registry`; they do not create independent product evidence beyond the same checks.

This coverage establishes instrumentation, parser behavior, and deterministic gates. It does not
establish a genuine two-host direct-UDP or forced-TCP run.

## rev0020 controller fault-gate and restart-fence coverage

The owned registry contains 284 fixture-aware unit/integration checks. New incarnation coverage
strictly decodes and signs the 128-byte host record; rejects wrong identity, tamper, zero, complement
failure, wraparound, state/lock/parent symlinks, unsafe parent modes, wrong file shape, hard links, and
same- or cross-process contention; and proves descriptor-relative nested private-lane creation,
post-lock/path revalidation, atomic commit, exact increment, and explicit reservation before any
enabled direct-service construction. The implementation also synchronizes each newly created
directory plus its containing entry before descending. Agent/service tests prove delayed
old-incarnation INPUT cannot reach a replacement PTY, unauthorized RESUME receives one exact
replayable denial without effect authority, and failed-start cleanup preserves `phase=failed` while
releasing the lease.

The local socket and CLI gates cover a configurable 1 ms..60 s first-OPEN lease with a 5 s product
default; silent-client expiry without OPEN dispatch; bounded four-contender denial under one shared
20 ms grace window; exact contender stream IDs; active-controller death before queued-contender
rejection; real CLI winner/loser contention; replacement resume; render-before-ACK; a bounded
1 ms..5 s ACK-only detach drain with one absolute socket-send deadline; rejection of non-ACK effects
before Agent dispatch; exact final ACK commitment; clean detach; and explicit empty-server `not_found`.

`iotox.ratox-restart-fence-process` runs the shipped daemon twice against the exact toxcore double and
proves single-host lease exclusion, a signed 128-byte identity-bound record, failed-start projection,
clean lease release, and exact incarnation `+1`. Retained full-path R6 oracle evidence additionally
crosses the private terminal stream, packet `0xA2`, owner thread, profile resolver, native PTY helper,
SENDQ retention, controller replacement, friend deletion/re-add, reconnect, live signed revocation,
explicit denied resume, daemon replacement, and old-session `not found`. These deterministic gates are
not genuine Tox-network, power-loss, or complete two-guest Sandwurm evidence.

## rev0019 private controller-stream coverage

The current owned suite adds a separately gated, same-user controller plane without weakening the
rev0018 host gate. It covers:

```text
pure controller OPEN/RESUME, input retention, output replay, ACK, resize, detach, close, exit, and reset
exact friend-number, online-epoch, stable-principal, session, nonce, incarnation, and generation fences
byte-identical output overlap validation and destructive duplicate/gap/conflict rejection
independent input, output, outbound-packet, outbound-byte, event, and message-ID exhaustion limits
route loss retaining only resumable state for the same authenticated peer and principal
transactional RESUME_RESULT validation before any retained input or output coordinate is committed
canonical 32-byte ITTS header, two-byte payload length, four zero reserved bytes, and frozen vector
strict local packet direction, stream ID, payload shape, sequence, status, and 16 KiB payload bound
absolute socket paths, embedded-NUL rejection, private real parent, owner/mode/type checks, and SO_PEERCRED
pre/post-connect device-and-inode identity recheck against pathname replacement
one-client admission, first-OPEN enforcement, rejected-OPEN nonpublication, negative-deadline rejection,
active-listener protection, stale owned-inode reclamation, bounded ACK-only detach drain,
post-detach effect rejection, and final-output ACK commitment
and unlink-on-stop only for the exact inode created by the server
Agent controller activation, exact peer resolution, typed unknown-peer denial, route dispatch, and cleanup
one-binary terminal argument checks, absent-daemon behavior, output-before-ACK, resize, restoration, and escapes
```

The local transport is reliable `SOCK_SEQPACKET`, so duplicate OPENED or inconsistent local OUTPUT/GAP
state is rejected rather than being treated as replay from the lossy network boundary. These tests do
not establish daemon-restart persistence, multiple local terminals, or complete two-guest Sandwurm
operation.

## rev0018 default-off live Ratox Agent coverage

The owned suite now crosses the transport boundary without turning Ratox on by default. It covers:

```text
activation rejected before toxcore startup when the profile store or factory contract is incomplete
bit 23 absent from the default HELLO and selected only after explicit secure pre-network activation
separate local-support, local-requirement, peer-support, peer-requirement, and negotiated projections
one-sided advertisement never becoming a negotiated feature
independent mock-peer advertisement and bilateral bit-23 negotiation
live 0xA2 dispatch through the Agent after transcript, feature, epoch, principal, and exact-head checks
v1 owner authority denied at the terminal gate with a canonical response and no PTY factory call
explicit outbound authority fences: unauthorized admission denials remain sendable, while successful
results and session traffic retain their exact-head dependency through duplicate replay
signed authority-head mutation ordered against Ratox receive, bounded PTY progress, and transport send
live OPEN_RESULT retention under repeated toxcore SENDQ followed by signed revocation, exact queue
purge, and no later OPEN_RESULT transport attempt
bounded admission replay, outbound packet/byte, event, live-session, and tombstone accounting
exact duplicate replay and conflicting-message rejection across OPEN, ATTACH, RESUME, and control paths
whole-frame input staging, partial-write completion, one cumulative ACK, and terminal write failure handling
bounded output history, cumulative acknowledgement, replay, and explicit gap generation
attachment replacement, stale token fencing, epoch detach, authority revocation, and terminal closure
SENDQ rejection retaining the exact front packet until accepted or its route becomes stale
bounded shutdown output drain and deterministic HUP -> TERM -> KILL cleanup
round-robin service cursors preventing one busy PTY from starving later live sessions
private, rotating, content-free runtime telemetry with direct negative checks for terminal bytes, argv,
environment, cwd, paths, profile identifiers, and error strings
```

This is construction and regression evidence for an explicitly enabled experimental service. It does
not establish an operator terminal client, restart recovery of live PTYs, namespace/cgroup/LSM
containment, physical-host latency qualification, public bootstrap reliability, or production
support.

## rev0017 sealed terminal profile and PTY coverage

The new local-only prerequisite is split into three independently testable layers. The default
registry and native process executable cover:

```text
strict profile/binding validation and canonical locale-independent byte encodings
malformed, duplicate, hazardous environment, path, identity, dimension, and limit rejection
owner-only no-follow profile-store traversal with hardlink/symlink/extra-entry defenses
atomic registry replacement plus generation-coherent concurrent resolve and snapshot reads
fixed environment resolution, OPEN dimension clamping, and immutable policy-generation capture
bounded nonblocking controller I/O, saturating counters, output drain, and close denial gates
observe-before-signal HUP -> TERM -> KILL escalation with fresh deadlines and explicit reap timeout
real UNIX98 PTY session, controlling terminal, foreground group, cwd, TERM, and window behavior
fixed-descriptor and UNIX peer-credential contract, exact parent PID, frozen parent-death/session contract
core disablement, configured soft limits, no-new-privileges, umask, and high-descriptor closure proof
current identity plus privileged exact UID/GID drop with cleared supplementary groups when available
complete catchable-signal reset despite ignored SIGPIPE/SIGXFSZ in the spawning process
destructor-free supervisor death plus forced/natural-exit cleanup across separate process groups by pidfd/procfs
direct backend read/write/resize bounds, byte-exact binary echo, resize clamps, and setup-stage errors
```

The terminal-profile libFuzzer target mutates profile and binding records up to the 64 KiB policy
limit under ASan/UBSan. The payload fixture is intentionally not sanitizer-instrumented because the
profile deliberately applies a finite `RLIMIT_AS` before its final exec; the parent, hidden helper,
production decoders, controller, and test harness remain instrumented.

At rev0017 these checks did not establish Agent dispatch, negotiated Ratox OPEN, or bit-23
advertisement; rev0018 adds those R4 construction checks separately. They still do not establish PTY
recovery after daemon restart, created namespace/cgroup/LSM isolation, cgroup resource accounting,
proof against unknown future session escapes, a public network path, or a terminal client.

## rev0016 authority-ledger v2 coverage

The owned registry now freezes the one signed format boundary rather than treating bit 7 as an
in-place mask expansion. Coverage includes:

```text
v1/v2 canonical record, header, challenge, and proof round trips
independent v1/v2 signature and digest domains
exact owner-self-signed non-widening migration and one-time replay
mixed v1-prefix plus v2-suffix restart reconstruction
header/history mismatch, post-migration v1, stale-tail, and widened-migration rejection
plain all remains 0x7f while all-v2 is an explicit 0xff opt-in
format-sensitive role ceilings and explicit interactive.terminal grants
exact successor capability preservation across epoch transition
feature-bit-24 challenge/proof and remote-mutation negotiation gates
remote prepare/apply/duplicate behavior bound to format, epoch, sequence, tail, and session
proof invalidation after mutation and fresh-proof requirement
in-flight old-head proof rejection without poisoning the replacement challenge round
private rollback-guard adoption, exact pending recovery, missing-v2-guard, rollback, deletion, and fork rejection
CLI exact prepared-body verification before signing, including substituted-body refusal
CLI local/remote migration plus terminal-capable successor ceremony parsing
```

The authority fuzzer corpus includes reviewed v2 migration, challenge, and proof seeds. The local
guard tests do not claim detection when an attacker restores both ledger and guard as one older
consistent pair. This coverage also does not claim a PTY, process confinement, Agent dispatch, or
Ratox feature-bit-23 advertisement.

## Authority-ledger v3 synchronization-capability coverage

The owned registry extends the same boundary discipline through v3:

```text
v2-to-v3 migration is owner-self-signed, adjacent, exact-mask, and non-widening
v1 direct migration, repeated migration, widened migration, and mixed remove-plus-widen fail
IAL3/IOTOXAL3 records and headers replay only under independent v3 signature/digest domains
all and all-v2 retain exact historical masks; all-v3 is the explicit 0xfff spelling
sync capability parsing/rendering and every v3 role ceiling are direct checks
missing v3 rollback guard, false header, restart, and exact grant recovery fail or pass as specified
challenge/proof format 3 uses an independent proof domain and exact ledger-head binding
feature bit 25 is rejected without the v2 lineage bit in HELLO, registry, and proof paths
remote migration, exact duplicate, owner activation, sync delegation, and restart are covered
RecallRoot CLI local/remote v3 migration verifies exact prepared bytes before signing
```

Eight additional sync-admission checks combine that authority state with canonical namespace policy:

```text
administer, publish, subscribe, and activate map to four independent capability bits
v1, v2, uninitialized authority, missing v3 negotiation, stale head, and denied proof fail
one sync capability never substitutes for another
publish requires the exact proven writer; subscribe and activate require the exact subscriber
disabled host activation policy still refuses an otherwise authorized activation
invalid policy and unknown operation fail deterministically
```

These checks establish a pure admission primitive only. They do not claim a network synchronization
service, wiring at an Agent entrance, content transfer, projection, or activation effect.

## Synchronization namespace administration coverage

The canonical namespace parser/loader checks are joined by creation and quiescent-mutation checks:

```text
strict owner-only no-follow policy root and namespaces directory
cooperative directory-inode serialization before capacity inspection
unnamed mode-0600 record is complete and fsynced before its name exists
atomic no-clobber publication and namespace-directory fsync
strict durable reload with one singly linked canonical record
exact retry is a duplicate with no temporary entry
different policy under the same namespace ID is refused without replacement
update changes only activation and canonical writer/subscriber membership
root, engine, and quota replacement is refused before mutation
update stages one owner-private canonical temporary and atomically renames it over the record
startup/mutation cleanup removes only the exact canonical update temporary and otherwise fails closed
live subscriber work and unresolved cleanup refuse target-namespace mutation
removal deletes only policy; exact absent retry is generation-stable
disk/live reconciliation after every possibly committed result empties the registry on reload failure
```

The CLI template check decodes its own output and proves range-v1/manual defaults plus canonical
principal ordering. The live-Agent synchronization construction check installs the bytes through
local control v1.27, then updates and removes them through v1.29. It observes one registry-generation
advance for each real effect, proves exact retries leave the generation stable, refuses immutable
quota replacement, and reinstalls the same durable policy. The operator sequence is:

```sh
iotox sync-namespace-template NAMESPACE ROOT WRITER_PUBLIC_KEY_HEX \
  [SUBSCRIBER_PUBLIC_KEY_HEX...] > namespace.policy
iotox sync-namespace-lint namespace.policy
iotox --runtime RUNTIME sync-namespace-install namespace.policy
iotox --runtime RUNTIME sync-namespace-update namespace.policy
iotox --runtime RUNTIME sync-namespace-remove NAMESPACE
iotox --runtime RUNTIME sync-namespaces
```

This proves local policy administration and exact retry. Removal is intentionally not state-root
retirement: it preserves content and every signed namespace root. The checks do not prove remote
`sync.admin`, automatic subscription, storage migration, or any data transfer merely because policy
was installed.

## Synchronization pull cancellation coverage

Every pull retains a nonzero job ID equal to its original HEAD request ID and unique across the
bounded live process. Direct checks cancel both a pre-HEAD job and a job with two admitted FileId
receives. They require `cancelled` to become terminal before cleanup, both transport cancellations to
occur at most once, private staging and signed active-attempt truth to disappear, the scheduler to
fence remaining work, a late HEAD to produce no request, a late completion to find no active binding,
and accepted HEAD generation to remain unchanged. An injected transport-cancel enqueue failure is
reported even though local cleanup completes; exact retry settles the same tombstone without another
transport effect. Local protocol v1.28 and the Agent reject malformed, zero, and absent job IDs.

This deterministic implementation evidence is paired with a genuine-provider timing gate. The
rate-shaped Sandwurm cell cancels after positive c-toxcore progress on direct UDP and forced TCP and
proves that no acceptance or activation occurs. It establishes local withdrawal and fencing; it does
not prove that the remote publisher observed a CANCEL packet.

## Signed synchronization publication coverage

Thirteen direct checks freeze the local signed-HEAD and publisher boundary:

```text
one fixed 296-byte canonical binary record and strict decode/re-encode
stable device Ed25519 signature over an independent IoTox domain hash
accepted-candidate record digest computed internally after verification
verified conversion into the existing accepted-candidate evaluator
body, signature, padding, truncation, and oversize tampering refusal
writer, namespace, engine, nonzero identity, and quota binding
generation-one genesis and exact same-writer linked successors
foreign predecessor and mid-chain publisher replacement refusal
bounded owner-only no-follow single-link durable reload
exact publication retry returns a duplicate without generation growth
invalid publication and corrupt prior state preserve/fail before replacement
concurrent calls through one live publisher store serialize one linear chain
weak-permission or multiply linked persistent publisher locks fail closed
```

A separate clean-start process oracle forks eight independent publishers before any threaded test
runtime exists and proves that they commit one exact eight-generation chain. Keeping this out of the
monolithic registry avoids using post-thread `fork()` as evidence.

The signed record alone does not prove object availability. The ordered local publication job below
provides that evidence at commit time. Cross-process publisher locking, rollback detection after
coordinated state restoration, Agent/service wiring, a sync packet family, and remote convergence
remain unclaimed.

## Ordered synchronization object publication coverage

Twelve direct checks exercise the artifact-plus-manifest publication transaction and object inventory:

```text
both immutable objects exist and verify before signed genesis publication
exact retry reuses both objects and consumes no generation
linked successor advances only after both new objects exist
artifact, manifest, combined per-publication store, and zero-size bounds
corrupt existing manifest refusal before HEAD mutation
public or multiply linked existing object refusal
source mutation between initial hash and final commit detection
late cancellation leaves reusable objects but preserves the prior HEAD
symlink source refusal before namespace mutation
stale legacy PID-named staging debris cannot block a fresh random temporary commit
canonical inventory counts exact artifact, manifest, object, and byte totals
unexpected entries, public object directories, and prospective store ceilings fail closed
```

The existing install path also re-hashes each newly copied final object. These twelve checks alone do
not claim reachability, retention, garbage collection, remote availability, service authorization
wiring, or activation; the local retention, reachability, and shared-transaction gates are qualified
separately below.

## Synchronization retention coverage

Eight direct checks freeze the non-destructive retained-revision boundary:

```text
one canonical fixed-layout bounded snapshot with strict decode and re-encode
durable restart and exact duplicate pin idempotency
generation-sorted insertion and record-identity unpin persistence
maximum retained-revision capacity and same-generation fork refusal
accepted-head namespace, writer, engine, identity, size, and quota validation
corrupt, truncated, noncanonical, and over-capacity state refusal
private owner file/directory/lock, hard-link, and symlink enforcement
namespace policy root binding without wrong-root mutation
```

These tests do not authorize deletion. Unified transaction locking, published/accepted/activated/pinned
reachability, interrupted-transfer roots, and quarantine-only GC are qualified separately below;
permanent purge remains absent.

Two additional checks freeze retention authentication: the stable device signs one domain-separated
canonical v2 record, foreign device keys and signature tampering fail closed, unsigned v1 is rejected,
and each real mutation advances its counter while committing the exact preceding signed-record digest.
These checks do not prove restart-safe anti-rollback: an attacker able to replay a complete older valid
record can still erase later pin history from local view.

A dedicated clean-start process executable loads the same stable identity in eight children, pins eight
distinct accepted records concurrently, and requires one authenticated mutation-eight snapshot with
all generations sorted and present after every child exits successfully.

## Synchronization reachability coverage

Five direct checks freeze the non-destructive mark boundary:

```text
published + accepted + activated + retained source-mask merging
distinct old activation and retained-revision preservation
missing live object versus exact-identity size mismatch reporting
foreign device and altered signed-retention refusal
conflicting live-root size and duplicate inventory refusal
```

The underlying filesystem inventory also proves exact kind/digest/size extraction and canonical sort.
The resulting `unreferenced` records are evidence candidates only. A separate accepted-state check
proves the stable-device signature round trip plus foreign-key and body-tamper refusal; unsigned legacy
state is also rejected. Activation authentication is qualified separately below. No test authorizes
unlink because complete older valid state remains replayable after restart.

## Synchronization transaction coverage

Six direct checks cover one shared namespace transaction boundary:

```text
private persistent owner-only lock and exact namespace/root binding
move-only token preservation without stale moved-from authority
cross-thread token reuse refusal
root-descriptor identity pinning and substituted-root refusal
weak, multiply linked, and symlink lock refusal
published/accepted/activated/retained roots plus inventory loaded in one stable transaction
```

A dedicated clean-start process oracle acquires the transaction in the parent, releases a prepared
child into signed publication followed by retention, proves no completion while the lock is held, then
requires both mutations and authenticated restart state after release. The stored reachability path now
does read roots and inventory under this lock; the oracle also rejects a fork-inherited token. The
earlier pure planner remains available for injected tests. The stored plan additionally requires its
four-root rollback guard to match under that same transaction. A separate activation-state check proves
its stable-device signature, foreign-key, body-tamper, and unsigned-legacy refusal. Neither path
authorizes deletion because coordinated replay lacks an independent monotonic witness.

## Synchronization rollback-guard coverage

Six direct checks freeze the local restart witness and its live integration:

```text
published, accepted, activated, and retained root-head derivation
stable-device-signed committed/pending transition and exact finish
power-cut recovery before versus after the state-file commit
missing guard, rolled-back committed head, and third-head fork refusal
foreign key, signature/body tamper, hard-link, and symlinked-directory refusal
guarded publication, acceptance, activation, pin, and unpin under stored reachability
injected failure before replacement and after a landed replacement, followed by exact retry cleanup
```

The 496-byte guard is held beneath the namespace transaction and a nonempty current root set cannot be
silently adopted when its guard is absent. Read-only checks classify either exact pending crash side
without repairing signed state. A dedicated fresh-process route independently restores an older
publication root and an older guard, rejects both incoherent snapshots, restores the current pair, and
then advances normally. Every implemented local root mutation now surrounds state replacement with
guard begin/finish. An attacker able to replay a complete valid guard and all matching roots remains
outside this local claim. No purge API exists.

## Synchronization GC quarantine coverage

Six direct checks freeze the first collector boundary:

```text
dry-run identity freeze, non-mutation, exact quarantine, and empty retry
inconsistent live-root refusal before quarantine-directory creation
hard-link and symlink refusal during descriptor inventory
immediate pre-rename inode-substitution refusal
cancellation after one exact durable prefix
post-rename directory-sync failure with distinct moved and durable counts
```

The public Agent/control check exercises `sync-gc NAMESPACE dry-run|quarantine` against an installed
empty namespace. The ordinary local control has no path field and protocol minor 32 defines only mode
0 dry-run and mode 1 quarantine. Dedicated storage code uses `openat2` beneath/no-symlink/no-mount,
`renameat2(RENAME_NOREPLACE)`, owner/link/mode/inode checks, and no unlink call.

The `sync-file-repair` Sandwurm scenario runs the destructive fixture independently in both source-
linked guests after signed convergence. Each guest requires a real bind mount over `objects` to fail
closed, preserves two outside-root sentinels, observes two rooted objects plus one 32 KiB candidate,
moves the exact inode and fsyncs both directories, and observes zero effects on retry. The accepted
compact proof is `.sandwurm/exports/pairs/pair.ci0p3t6f`; exact bindings and nonclaims are in
`evidence/2026-08-24-sandwurm-sync-gc-quarantine.md`. Permanent purge remains blocked by coordinated
rollback and requires a separate decision and evidence program.

## Exact provider doubles

The shared-library c-toxcore double exports the exact C ABI subset consumed by IoTox. It exercises:

- dynamic symbol resolution and provider version policy;
- options/object lifecycle and one serialized owner thread;
- savedata export/reload and stable address;
- friend request/add/accept/delete/public-key lookup;
- deliberate lowest-gap friend-number reuse;
- connection, friend, text, custom-lossless, custom-lossy, receipt, and file callbacks;
- deterministic send failures and callback ordering used by product tests.

The Argon2 double exports the exact consumed provider boundary for deterministic RecallRoot tests.
Neither double claims upstream cryptography, public networking, address policy completeness, or
performance equivalence.

## One-binary process fixture

`iotox.binary-process-lifecycle` starts the actual `iotox run` executable, then uses the same binary
as a local client. It crosses process, Unix socket/FIFO, filesystem, queue, owner-thread, callback,
store, and restart boundaries.

The fixture covers:

```text
private runtime creation and status
root request FIFO existence/help/status
malformed outgoing request -> explicit keyless rejection evidence
exact complete-address outgoing request -> local requested evidence and peer projection
public-key removal of that temporary peer
live incoming request -> literal reject
session HELLO/capability confirmation
authority challenge/proof and application-ready state
normal/action text, message ids, incoming echo, and read receipt
ratox-style command FIFO -> durable device.describe
authorized profile.status.set -> savedata persistence and exact provider readback
provider stop after effect -> SIGKILL -> STARTED recovery of the same desired value
mutating TTL refusal before durable admission
one-second durable cancellation window and fail-closed untrusted TTL admission
restored offline friendship -> signed admission, zero attempts, safe cancellation
request/result retrieval and restart reconstruction
finite send, incoming offer, receive admission, pause/resume/cancel, completion publication
literal public-key peer removal
orderly shutdown and restart
```

The fixture polls independent asynchronous projections separately. FIFO `write(2)` success is never
treated as semantic completion.

The transport unit gate separately replaces the savedata parent with a regular file after startup
and proves a profile mutation reports the atomic persistence error instead of returning success.
The Agent consequently leaves any remotely admitted uncertain effect at `STARTED` for exact
desired-state recovery rather than committing a false terminal result.

## rev0015 outgoing-request coverage

`tests/test_friend_request_fifo.cpp` freezes the ordinary record:

```text
76 hex address bytes + TAB + 1..921 message bytes, excluding LF
```

Coverage includes:

- minimum and maximum records;
- uppercase and lowercase address hex;
- complete 38-byte decode;
- preservation of TAB, NUL, CR, spaces, and high bytes after the separator;
- short, long, empty, malformed-hex, and wrong-separator rejection;
- direct root-lane monitor use;
- maximum record plus LF against actual `_PC_PIPE_BUF`;
- symlink, regular-file, foreign-mode/owner, and opened-inode substitution rejection where the host
  permits the fixture;
- partial-record expiry and overflow recovery;
- lane replacement/rescan;
- required root-lane startup and monitored-count behavior;
- invalid layout enum rejection.

Agent/runtime tests add:

- ordinary and typed operations converge on one provider method;
- malformed record with no trustworthy prefix journals `public-key=unknown`;
- malformed remainder may retain only a trustworthy public-key hint;
- provider admission creates the canonical public-key peer directory;
- authorization ledger sequence/head remain unchanged;
- status drops if the promised root FIFO is no longer monitored;
- successful local request evidence makes no remote-acceptance claim.

## Other coverage groups

### Transport and friendship

```text
ABI sizes and enum/error mapping
bootstrap/relay configuration
savedata atomic persistence and restart identity
bounded owner command/event queues and timeout-before-start cancellation
connection and friend event normalization
incoming request projection and exact accept/reject
public-key lookup/delete in one owner-thread operation
numeric friend-gap reuse regression
friend-events bounding, escaping, and rotation
```

The separate owner-infrastructure check boots the source-pinned bootstrap/TCP-relay daemon in a
NixOS/KVM guest and validates both fixed-port listeners, exact private state shape, byte-identical
identity across service restart, configured systemd ceilings, `DynamicUser`, and the opt-in TCP/UDP
firewall rules:

```sh
nix build .#checks.x86_64-linux.toxBootstrapServiceTest -L
```

This is local deployment-adapter evidence, not a public reachability, uptime, NAT, bandwidth, or
abuse-resistance claim (ADR 0240).

### Session and authority

```text
frame and payload bounds
canonical HELLO and capability encoding
online epoch and directional transcript order
retry, duplicate, sequence, and incompatibility handling
stable device/owner identity
signed ledger bootstrap/grant/revoke/replay
last-owner and capability-ceiling invariants
authority challenge/proof and principal binding
```

### Durable command truth

```text
request/ACK/result codecs
sender epoch + message id identity
commit-before-observe ordering
signed durable records and restart replay
duplicate request returns prior terminal result
expiry/error handling
read-only device.describe executor
ratox command FIFO converges on the same engine
```

### Human text and finite files

```text
normal/action byte framing and UTF-8 interoperability boundary
send acceptance, incoming text, message id, and read receipt
bounded escaped journals and disconnect cleanup
absolute local send/receive paths
friend-scoped file numbers and exact chunk service
local/peer pause represented independently
safe destination staging, sync, and no-clobber publication
terminal cleanup without invented restart durability
synchronous chunk response inside the exact toxcore callback contract
healthy progress coalescing without coalescing failure or terminal truth
```

## Genuine four-route file laboratory

```sh
./tools/run-four-route-lab.sh --prepare-keys
IOTOX_FOUR_ROUTE_BYTES=8388608 \
IOTOX_FOUR_ROUTE_TRIALS=3 \
  ./tools/run-four-route-lab.sh --reuse-keys

IOTOX_FOUR_ROUTE_BYTES=16777216 \
IOTOX_FOUR_ROUTE_TRIALS=3 \
IOTOX_FOUR_ROUTE_STREAM_TOTALS=8,16,32,64 \
  ./tools/run-four-route-lab.sh --reuse-keys

IOTOX_FOUR_ROUTE_BYTES=16777216 \
IOTOX_FOUR_ROUTE_TRIALS=3 \
IOTOX_FOUR_ROUTE_STREAM_TOTALS=8,16,32,64 \
IOTOX_FOUR_ROUTE_TCP_ONLY=1 \
  ./tools/run-four-route-lab.sh --reuse-keys
```

The default run starts eight source-linked IoTox processes: four independent Tox route pairs bound
to two test-only stable device identities. It compares one route/one stream, one route/four streams,
two routes, and four routes with constant total bytes. Reusable private key material remains under
the ignored `.cache/four-route-lab/` tree; `--fresh-keys` retains the from-scratch gate. Reports are
redacted TSV files under `build/four-route-lab/`. This is a same-client founding-host performance
laboratory, not a product bonding implementation or cross-client test.
Sweep mode raises only the laboratory agents' configurable active-transfer ceiling to the largest
requested stream total, requires the reported peer connection to match UDP or TCP as selected, and
records both end-to-end and post-offer data-window timing.

## Ratox carrier latency laboratory

```sh
IOTOX_BINARY="$PWD/build/standalone/iotox" \
IOTOX_RATOX_LATENCY_SAMPLES=40 \
IOTOX_RATOX_LATENCY_BYTES=67108864 \
IOTOX_FOUR_ROUTE_MAX_ITERATE_MS=20 \
IOTOX_FOUR_ROUTE_PROBE_DEADLINE_MS=250 \
  ./tools/run-ratox-latency-lab.sh --reuse-keys
```

The wrapper runs the genuine four-route fixture once with observed direct UDP and once with UDP,
discovery, DHT announcements, and hole punching disabled so all eight directions report TCP. On
route zero it interleaves three monotonic round-trip probes while idle and beside one finite-file
transfer:

```text
normal Tox text -> c-toxcore read receipt
10-byte custom-lossless request -> confirmed peer echo
10-byte custom-lossy request -> confirmed peer echo
```

The custom echo is unadvertised laboratory traffic outside the IoTox 1.0 frame ID. It carries only
a kind and random nonce, requires a confirmed IoTox session, returns exactly the request size, and
never claims PTY/key-to-render latency. Every custom sample either records RTT or an explicit miss at
the configured deadline. The report also freezes the last-payload transfer timestamp before waiting
for an overlapping latency observer, records CPU ticks/context switches/iteration count for the idle
window, and publishes requested/effective owner intervals plus interactive/bulk queue waits.

`IOTOX_FOUR_ROUTE_MAX_ITERATE_MS=1000` is the no-extra-cap control. It does not force a one-second
sleep; c-toxcore remains free to request a shorter interval. `--fresh-keys` retains the independent
from-scratch identity gate. Reports contain hashed peer identifiers but must still be treated as
research evidence, not cross-client, controlled-impairment, or two-host qualification.

## Controlled Ratox impairment laboratory

```sh
./tools/run-ratox-impairment-lab.sh
```

This bare-metal gate creates two disposable endpoint network namespaces and applies netem only to
their `eth0` egress. It crosses direct UDP and forced TCP relay with baseline, delay/jitter,
loss/duplicate/reorder, and constrained-rate/queue profiles. The default run uses reusable private
test identities, 24 randomized single probes per carrier/state, 64 custom probes at 2 ms spacing,
a 2.5 second deadline, and an overlapping exact file transfer.

Burst output records every ordinal and distinguishes local toxcore send rejection from an admitted
probe that missed its deadline. It also counts reply duplicates and arrival-order inversions. The
atomic matrix manifest records deterministic netem seeds, qdisc counters before/after every run,
the standalone hash, and each report hash. The tool requires noninteractive sudo, `ip`, `tc`,
`iptables`, and `setpriv`; it adds no physical-interface qdisc and removes its exact NAT rule,
namespaces, veths, and bridge on exit.

Use `IOTOX_IMPAIRMENT_PROFILES`, `IOTOX_IMPAIRMENT_MODES`, and the documented sampling, burst,
payload, deadline, timeout, and report-directory variables to narrow a shakedown. This is
same-client controlled-path evidence. TCP still traverses an external public relay, and neither
mode is a complete two-guest Sandwurm or keypress-to-render qualification.

### Seeded Sandwurm partial-loss continuity

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp packet-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp packet-loss
```

Unlike the namespace throughput laboratory, this gate boots both complete source-linked NixOS guests
and exercises the ordinary Agent/control construction. The host applies independently seeded random
5% loss to both private TAP egress paths without lowering carrier or stopping a process. Each role
must complete a 128-sample, 1,200-byte lossy custom-probe burst with no local send errors, deliver
ordinary text while the impairment remains installed, stay confirmed at the original online epoch,
and deliver fresh text after qdisc removal. The strict verifier parses every retained probe row and
binds the kernel packet/drop counters and fixed configuration seeds.

The accepted direct-UDP cell delivered 119/128 and 117/128 probes; the accepted forced-TCP cell
delivered 128/128 in both directions despite positive qdisc drops. That difference is expected:
direct UDP exposes Tox lossy-packet loss, while TCP may repair the dropped IP packets below the Tox
relay stream. The gate therefore requires at least one miss only for direct UDP, never substitutes
application results for kernel drop evidence, and remains distinct from the 100% blackhole/recovery
gate whose online epochs must advance. See ADR 0151 and
`docs/evidence/2026-08-24-sandwurm-packet-loss.md`.

### Sandwurm live mixed-provider rolling boundary

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp provider-rolling
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp provider-rolling
```

This qualification-only scenario does not invent an old IoTox release. Each guest uses the exact
0.2.22 fixture to create a distinct profile and then adds the peer's public key as a friend before
networking. The client performs its live exchange with 0.2.22; the device loads the old-created
savedata and performs its live exchange with 0.2.23. Both roles must observe the requested friend
connection kind, send and receive distinct fixed messages, rewrite savedata through the live
provider, and produce a post-exchange semantic snapshot readable identically by both fixtures.

For direct UDP, only the friend connection must report UDP. The provider's global self connection
may remain TCP because it describes bootstrap/DHT reachability rather than the already-direct friend
path. Forced TCP disables UDP and local discovery and requires both self and friend connections to
report TCP. The strict receipts carry only versions, official source digests, fixture binary digests,
route, booleans, savedata size, KVM truth, and no secrets.

Provider rolling proofs have a separate compact surface:

```sh
./tools/export-sandwurm-provider-rolling.py PROOF_ROOT
./tools/verify-sandwurm-provider-rolling.py \
  .sandwurm/exports/pairs/PAIR_ID --route direct-udp
./tools/verify-sandwurm-provider-rolling.py \
  .sandwurm/exports/pairs/PAIR_ID --route forced-tcp
```

Accepted results and exact nonclaims are recorded in
`docs/evidence/2026-08-24-sandwurm-provider-rolling.md` and ADR 0153.

## Ratox pacing and coalescing laboratory

```sh
./tools/run-ratox-pacing-lab.sh
```

This wrapper sweeps 2, 5, 10, 20, and 40 ms emission intervals with both 64-byte input-like probes
and full 1,200-byte carrier-occupancy probes. Every cell runs the adversity namespace profile over
observed direct UDP or forced TCP beside a finite exact transfer. UDP receives a larger transfer so
the complete probe pair remains inside the bulk interval; TCP is already relay/impairment limited.

The outer atomic manifest hashes every nested impairment manifest and report, then copies each bulk
lossless/lossy summary into one comparison surface. Packet size is part of the report schema. The
sized research echo uses deterministic nonce-bound padding and returns exactly the request size;
malformed padding is ignored. Use `IOTOX_PACING_SPACINGS_MS`, `IOTOX_PACING_PACKET_BYTES`,
`IOTOX_PACING_MODES`, and the documented payload/deadline variables for a smaller shakedown.

The pacing gate qualifies carrier admission, not PTY correctness or human keypress-to-render
latency. The frozen Ratox frame decoder has its own canonical valid fuzz seed and sixth parser fuzz
lane. The seventh stateful fuzzer now drives both standalone input/output primitives and complete
R1 attachment, incarnation, close, quota, event, and replay-reservation sequences under ASan/UBSan;
the service feature bit remains default-off and is selected only by the explicit construction gate.

## Remaining Ratox service qualification

The genuine terminal capture prerequisite is available independently of the synthetic carrier
laboratories:

```sh
python3 tools/ratox-terminal-probe.py \
  --runtime "$RUNTIME" \
  --peer "$DEVICE_TOX_PUBLIC_KEY" \
  --samples 40 \
  --output controller-capture.tsv
```

The controller and remote host must already have negotiated Ratox, the remote principal must be
bound to a fixed byte-echo profile with terminal authority, and that profile must have entered
raw/no-echo mode before capture. Each trial is serialized as INPUT, exact remote PTY output, local
pseudoterminal render observation, then OUTPUT_ACK. The tool rejects startup output, altered or
coalesced bytes, sequence discontinuity, unexpected interactive owner work, and missing status
publication. `controller-capture.tsv` contains no terminal content or raw peer key; it is the
controller-clock half of the frozen R7 join, not qualification evidence on its own.

The explicit `ratox-matrix-idle` and `ratox-matrix-bulk-{1,8,16,32,64}` Sandwurm scenarios raise
that same production path to 1,000 samples without slowing the 40-sample construction cells. A
matrix capture can exceed the runtime tree's 1 MiB Ratox journal boundary, so the device evidence
concatenates the completed previous generation before the current generation. Verification requires
globally consecutive host ordinals and joins every controller byte interval to exactly one
same-session `input-staged`, `input-committed`, and `output-appended` triple with matching input
message ID and increasing host-clock coordinates.

The first two 1,000-sample direct-UDP attempts completed every render but timed out after `CLOSE`.
They exposed that cumulative `OUTPUT_ACK` had consumed all 128 never-evicted exact-control replay
entries. ADR 0154 gives acknowledgements a constant-space attachment-local high-water fence. The
owned regression drives 1,001 increasing ACKs with only one exact-control slot, accepts only an
exact repeat of the latest pair, rejects conflict and backward probes, and then closes the session.
`OPEN`/`ATTACH`/`RESUME`/`RESIZE`/`PING`/`DETACH`/`CLOSE` keep exact pre-effect replay.

The first 1,000-sample loaded attempt reached 457 exact renders and then exposed an evidence-surface
error rather than a terminal stall. Its stopped disk showed 914 executed INPUT/ACK operations,
interactive queue p99 bounded at 1.047 ms, and maximum wait 13.022 ms; the probe had waited on a
coalesced filesystem snapshot that still showed the pre-ACK count. ADR 0155 moves local PTY render
ahead of all evidence collection and obtains exact cumulative deltas through authenticated live
inspection. Filesystem projection freshness is no longer part of latency or gate liveness.

The first clean 1,000-sample direct-UDP idle run after that correction delivered every sample with
render p50/p95/p99/max 62.107/83.115/86.936/91.020 ms and owner queue p99 0.511 ms. A diagnostic
5 ms toxcore cap with the Agent service cadence left at 20 ms improved render p95 to 59.230 ms. A
second diagnostic with both transport iteration and Agent service capped at 5 ms reached render
p50/p95/p99/max 21.241/32.000/47.643/78.324 ms, owner queue p99 0.689 ms, and zero misses. Those
dirty-tree runs localized a product scheduling seam; they are not qualification cells.

ADR 0156 promotes the combined change as a demand-driven product policy. Active host/controller
state uses 5 ms defaults and successful local terminal operations wake the Ratox service worker; idle state
restores the ordinary transport cap and 20 ms Ratox poll. `ratox-latency-mode-active`,
`ratox-active-service-interval-ms`, and `ratox-active-transport-iteration-interval-ms` expose that
state. Every new Ratox Sandwurm proof also carries a process-incarnation-fenced
`ratox-resource-interval.tsv` for both roles with monotonic duration, CPU ticks, page faults, resident
pages/high-water, context switches, bytes read/written, descriptor counts, transport iterations, and
the cadence boundary. The strict verifier accepts either both role records or neither for historical
proof compatibility; newly generated cells always require and export both.

Exact-commit idle reruns then completed 1,000/1,000 samples on each route. Direct UDP rendered at
p50/p95/p99/max 16.345/23.943/31.308/52.402 ms. Forced TCP rendered at
88.810/99.010/128.852/131.091 ms, while remote stage-to-output p95 stayed 11.515 ms versus direct
UDP's 12.764 ms; forced TCP is therefore reported as a distinct route class rather than blamed on
the remote PTY queue.

The first loaded rerun after that policy stopped at sample 599 because periodic Ratox service and
required file-event draining shared the event consumer. ADR 0157 separates the service worker while
leaving one ordered event consumer and one toxcore owner. Its exact clean-commit retry
(`pair.1cfwnkj6`) completed, closed, compacted, and strictly verified all 1,000 samples beside one
simultaneous 1 GiB stream per role. It is reliability evidence but fails R7 latency: render
p50/p95/p99/max 27.617/71.698/96.588/220.327 ms, owner p99 7.114 ms, and zero 250 ms misses. ADR 0158
then tested removing redundant inline-send progress events and receive-descriptor churn before the
dedicated-route branch. The exact coalesced A/B (`pair.bmar1y5q`) completed and strictly verified but
failed badly: render p50/p95/p99 473.704/505.064/508.521 ms and 991 samples at or above 250 ms, while
owner p99 fell to 0.103 ms, remote stage-to-output p95 was 10.759 ms, event high-water was five, and
required-event backpressure was zero. This local/remote split locates the regression in unpaced
c-toxcore reliable-carrier head-of-line blocking, not the Agent event queue or remote PTY service.

ADR 0159 restores required per-chunk outgoing bookkeeping as the known safer pacing behavior until
an explicit bounded bulk scheduler exists. The receive side retains one pinned descriptor and the
runtime retains exact event high-water/backpressure counters. New Ratox proofs additionally bind
`ratox-agent-status.txt` for both roles; the strict verifier permits both-or-neither only so earlier
compact proofs remain verifiable. The next qualification changes only the receive descriptor and
diagnostics relative to ADR 0157.

That descriptor-only clean-commit cell (`pair.y__zgt1p`) completed all 1,000 samples and recovered
render p50/p95/p99/max to 19.918/51.146/73.048/231.738 ms. Owner p99 improved to 3.972 ms; remote
stage-to-output p95 was 12.179 ms; 53 samples reached 50 ms, four reached 100 ms, and none reached
250 ms. It remains a failed latency gate. The new bilateral final status is decisive: the client
event queue reached its exact 1,024 ceiling and incurred 1,227 required waits totaling 248.625 ms
with one 108.002 ms maximum, while the device peaked at 765 and never backpressured. The selected
next experiment is therefore an explicit high/low-water file pacer that pauses before saturation,
reserves semantic headroom, and resumes only after drain plus a minimum hold.

ADR 0160 implements that experiment with defaults of 64 high-water events, 16 low-water events, and
a 5 ms minimum hold while retaining the 1,024-entry semantic queue. Pause controls are scheduled in
the callback but cross the ordinary c-toxcore API only after `tox_iterate()` returns. Interactive and
control commands run before resume. Explicit PAUSE takes ownership without a duplicate provider
control; explicit RESUME/CANCEL and terminal transport states clear scheduler ownership. Focused
mock-provider coverage requires positive pause/resume/hold evidence, no required-event wait, queue
headroom, completion, and manual-pause takeover. Configuration validation covers invalid watermarks
and hold bounds.

The runtime status fields are:

```text
transport-file-pacing-paused-transfers
transport-file-pacing-high-watermark
transport-file-pacing-low-watermark
transport-file-pacing-minimum-hold-us
transport-file-pacing-resume-batch-limit
transport-file-pacing-pause-count
transport-file-pacing-resume-count
transport-file-pacing-resume-batch-count
transport-file-pacing-resume-batch-maximum
transport-file-pacing-external-pause-count
transport-file-pacing-pause-failure-count
transport-file-pacing-resume-failure-count
transport-file-pacing-total-hold-us
transport-file-pacing-maximum-hold-us
```

New Ratox proofs bind the complete current set bilaterally. An exact already-paused provider outcome
means another local scheduler owns the pause; it increments the external-pause counter without
entering the reactive auto-resume set. When that field is present, strict verification requires zero
pause/resume failures. The verifier accepts complete absence of
pacing evidence before ADR 0160 and accepts absence of only the batch trio in ADR 0160/0161 proofs;
historical proofs may also omit the ADR 0164 external-owner field. Partial generations fail. The exact
clean-commit two-guest `ratox-matrix-bulk-1` qualification
passes from commit `5305e7d`: render p50/p95/p99/max is
21.481/42.727/50.730/67.881 ms, exact owner p99 is 1.499 ms, 13 samples reach 50 ms, and none reaches
100 or 250 ms. Client/device event high-water is 180/130 with zero required waits. The pacer records
853/876 matched pause/resume cycles, zero failures, and zero final ownership. The strictly retained
compact proof is `.sandwurm/exports/pairs/pair.a4j1uirz`; higher-load cells remain independent gates.
The matched forced-TCP `bulk-1` cell also passes its route-independent exact owner gate at 1.452 ms
p99. It reports render p50/p95/p99/max 18.838/57.594/70.044/103.892 ms, one 100 ms sample, zero
250 ms misses, event high-water 183/102, zero required waits, and 248/278 matched pacing cycles with
zero failures. Its strict compact proof is `.sandwurm/exports/pairs/pair.0vkhkq96`.

The first paced direct-UDP `ratox-matrix-bulk-8` attempt completed all 1,000 terminal samples but
then failed an active-only workload assertion while one or more transfers were intentionally paused
by that scheduler. ADR 0161 replaces that measurement with exact state accounting: new observation
v6 requires `present = active + paused` before and after the interval, exact expected population,
and positive position for every present transfer. The retained counts expose pause duty rather than
hiding it. v1--v5 observations remain valid under their historical active-only rule. Failure phase
reporting now distinguishes terminal probe, bulk progress, and bulk cancellation.

The incomplete private run is diagnostic only. Its capture measured render p50/p95/p99/max
50.090/194.160/499.049/1,012.296 ms, 37 samples at or above 250 ms, and owner p99 1.023 ms. A
copy-on-write stopped-disk recovery found 2,705 matched pacing cycles, zero pause/resume failures,
event high-water 137, and zero required-event backpressure. Those facts identify the assertion bug
without promoting the cell: it lacks completed receipts, cancellation, and strict proof, and must be
rerun from the committed v6 harness.

That committed rerun is retained as `.sandwurm/exports/pairs/pair.y0d97_ng`. It proves eight present
and progressed transfers, seven active plus one paused at the checkpoint, one-round eight-control
cancel-to-empty, close, bilateral status/resources, and strict raw/compact verification. Render
p50/p95/p99/max is 47.629/144.120/179.491/264.277 ms with one 250 ms miss; owner p99 is 0.420 ms.
Client/device event high-water is only 134/138 with zero required waits, but 2,917/2,996 pacing cycles
accumulate 129.448/129.639 seconds of hold and individual maxima of 187.468/176.869 ms. This is a
valid failed performance cell. The next A/B must address multi-transfer resume fairness or burst
desynchronization without weakening the semantic reserve or lifecycle gates.

ADR 0162 implements that A/B. At low water, the owner selects the oldest eligible pause and resumes
at most `--file-pacing-resume-batch N` files before the next toxcore iteration; the default is one.
A failed resume refreshes that file's pause age rather than monopolizing the oldest slot. The
deterministic provider test drives three simultaneously paused producers to completion and requires
batch count equal to successful resumes, observed batch maximum one, zero control failures, and zero
required-event waits. New bilateral status requires the complete batch limit/count/maximum trio;
ADR 0160/0161 proofs with none remain strictly valid.

The clean two-guest comparison is retained as `pair.xs9phpya`. It completes every semantic and
lifecycle gate, advances all eight transfers by 132,238,434 aggregate bytes, and records
3,167/2,658 singleton batches with zero control failures or required waits. Render
p50/p95/p99/max is 56.349/124.811/161.242/188.401 ms, owner p99 is 0.716 ms, and no sample reaches
250 ms. This is a partial tail improvement over `pair.y0d97_ng`, not a direct-route latency pass.

The same clean commit also retains `pair.dwo77gs0`: all lifecycle checks pass, but neither role
reaches the pacing trigger, aggregate file progress is only 375,654 bytes, CPU is about 5% of one
core, and render p50/p95/p99/max is 468.734/504.428/506.962/510.656 ms. Remote stage-to-output p95
is only 9.999 ms and owner p99 is 0.117 ms. It is a valid carrier-starvation observation but a
zero-activation scheduler observation; both compact proofs remain strict after their 4.8 GiB of raw
VM roots were reclaimed.

ADR 0163 moves the next control point ahead of event pressure. The receiver admits one locally
resumed incoming file per peer and retains the other accepted destinations locally paused. Every
initial 20 ms quantum, the oldest eligible waiter replaces the oldest runnable receive. Explicit
PAUSE takes ownership and explicit RESUME rejoins the fair queue rather than bypassing the window.
The service cadence is present even without Ratox, and the existing signed two-object sync
convergence test must therefore remain complete. ADR 0164 later changes the default quantum to
50 ms without changing these semantics.

New Agent status and strict proofs bind this all-or-none group:

```text
file-carrier-window-per-peer
file-carrier-rotation-quantum-ms
file-carrier-runnable-receives
file-carrier-waiting-receives
file-carrier-admission-count
file-carrier-rotation-count
file-carrier-pause-count
file-carrier-resume-count
file-carrier-control-failure-count
file-carrier-total-wait-us
file-carrier-maximum-wait-us
```

Historical proofs may omit it completely. New proofs require window/quantum bounds, zero final
runnable and waiting receives, zero control failures, admission equal to actual resumes, rotations
bounded by pauses/resumes, and coherent wait totals. The deterministic manager test admits one of
three same-peer receives, rotates through both waiters, proves the counters, and cancels to empty.
The first exact two-guest proof, `.sandwurm/exports/pairs/pair.qrggya8w`, activates 1,454 rotations,
progresses all eight files, and improves render p95 to 56.247 ms with owner p99 1.488 ms. It remains a
rejected near-pass because direct p95 is not below 50 ms, the pre-ADR 0164 reactive counter records
141 undifferentiated pause collisions, and a queued post-cancel chunk becomes the final diagnostic.
ADR 0164 changes the default quantum to 50 ms, classifies already-paused ownership exactly, and keeps
a bounded 1,024-key cancellation history. Deterministic tests prove an external owner alone resumes
its pause, late data/completion after accepted cancellation perform no write or failure, and an
unknown unadmitted key remains a protocol error. The repeat two-guest result follows.

The repeat passes as strict compact proof `.sandwurm/exports/pairs/pair.bo6l0der` from commit
`63e845b`. All eight files progress by 170,498,931 aggregate bytes; the receiver records 512
admissions, 507 rotations, 77 external-pause handoffs, and zero carrier/reactive failures. Both
event queues end empty at high-water 228/168 with zero required waits, and final status has no
file-transfer failure. Render p50/p95/p99/max is 19.934/39.634/55.093/81.084 ms, exact owner p99 is
1.917 ms, 17 samples reach 50 ms, and none reaches 100 or 250 ms. Direct `bulk-8` is accepted.

The matched forced-TCP cell passes as `.sandwurm/exports/pairs/pair.pitcu1pk` with the identical
binary. All eight files progress by 139,548,606 bytes; the receiver records 742 admissions, 739
rotations, 58 typed handoffs, and zero true failures. Event high-water is 141/139 with zero required
waits. Render p50/p95/p99/max is 24.636/76.249/98.314/119.607 ms, owner p99 is 1.525 ms, eight
samples reach 100 ms, and none reaches 250 ms. The forced-TCP route gate and balanced eight-stream
row are accepted; 16/32/64 remain independent cells.

Direct-UDP `bulk-16` passes as `.sandwurm/exports/pairs/pair.xphist_e`. All 16 files progress from a
9,614,823-byte minimum to 169,803,834 aggregate bytes; the receiver records 529 admissions, 524
rotations, 60 typed handoffs, zero true failures, and an 890.887 ms maximum fair wait. Both queues
end empty at high-water 203/183 with zero required waits. Render p50/p95/p99/max is
20.276/40.591/51.960/75.043 ms, owner p99 is 1.894 ms, 14 samples reach 50 ms, and none reaches 100
or 250 ms. The direct 16-stream gate is accepted.

Forced-TCP `bulk-16` passes as `.sandwurm/exports/pairs/pair.qk3d51k6` with the identical binary.
All 16 files progress from a 7,896,960-byte minimum to 140,818,152 aggregate bytes; the receiver
records 786 admissions, 782 rotations, 84 typed handoffs, zero true failures, and an 885.574 ms
maximum fair wait. Both queues end empty at high-water 190/136 with zero required waits. Render
p50/p95/p99/max is 26.565/75.704/87.867/106.025 ms, owner p99 is 1.013 ms, four samples reach
100 ms, and none reaches 250 ms. The balanced 16-stream row is accepted.

Direct-UDP `bulk-32` passes as `.sandwurm/exports/pairs/pair.ktcwivx_`. All 32 files progress from a
4,097,919-byte minimum to 147,315,321 aggregate bytes; the receiver records 605 admissions, 590
rotations, 78 typed handoffs, zero true failures, and a 1.744 second maximum fair wait. Both queues
end empty at high-water 162/152 with zero required waits. Render p50/p95/p99/max is
23.589/47.765/58.319/75.984 ms, owner p99 is 1.811 ms, 37 samples reach 50 ms, and none reaches 100
or 250 ms. The direct 32-stream gate is accepted.

Forced-TCP `bulk-32` passes as `.sandwurm/exports/pairs/pair.lanpv3u7` with the identical binary. All
32 files progress from a 3,175,236-byte minimum to 122,955,393 aggregate bytes; the receiver records
675 admissions, 670 rotations, 56 typed handoffs, zero true failures, and a 1.736 second maximum fair
wait. Both queues end empty at high-water 185/147 with zero required waits. Render p50/p95/p99/max is
21.324/76.331/95.608/163.533 ms, owner p99 is 0.798 ms, nine samples reach 100 ms, and none reaches
250 ms. The balanced 32-stream row is accepted.

Direct-UDP `bulk-64` completes lifecycle and strict raw/compact verification as rejected proof
`.sandwurm/exports/pairs/pair.t736zqqh`. All 64 files progress from a 6,855-byte minimum to 1,549,230
aggregate bytes and cancel cleanly, but only after an 8.036 second progress wait. The receiver records
4,641 admissions, 4,624 rotations, zero typed handoffs or true failures, and a 3.837 second maximum
fair wait. Both queues end empty at high-water 50/50 with zero required waits and reactive pacing
never activates. Owner p99 is 0.118 ms and remote stage-to-output p95 is 10.293 ms, yet render
p50/p95/p99/max is 220.897/331.081/446.692/8053.730 ms; 108 samples reach 250 ms. The lifecycle
verifier's pass is not latency qualification.

Forced-TCP `bulk-64` likewise completes lifecycle and strict raw/compact verification as rejected
proof `.sandwurm/exports/pairs/pair.swij6mj9`. All 64 files progress from a 2,177,148-byte minimum to
168,951,072 aggregate bytes and cancel cleanly. The receiver records 1,212 admissions, 1,183
rotations, 215 typed handoffs, zero true failures, and a 3.486 second maximum fair wait. Queues end
empty at high-water 711/162 with zero required waits. Render p50/p95/p99/max is
49.829/93.790/109.944/560.528 ms; owner p99 is 2.199 ms and one sample reaches 250 ms. This forced
route fails the common owner and miss gates through a high-pressure mode rather than direct UDP's
low-use stall. ADR 0165 therefore freezes 32 as the qualified single-Agent limit; the 64 gate stays
failed and larger configured limits remain experimental.

The first complete two-guest join is retained in
`evidence/2026-08-20-sandwurm-ratox-idle.md`. Its independently verified direct-UDP construction cell
rendered all 40 inputs exactly once: p50 45.442 ms, p95 63.941 ms, p99/max 67.435 ms, zero samples
over 250 ms, and owner interactive queue p99 0.115 ms. The p95 signal is above the provisional 50 ms
direct target, but 40 idle samples do not replace the frozen 1,000-sample route/load qualification.
The matched forced-TCP cell also rendered 40/40 exactly, at p50 65.454 ms, p95 104.139 ms, p99/max
109.183 ms, zero 250 ms misses, and owner queue p99 0.081 ms. Remote stage-to-output p95 remained
about 27.4 ms on both routes, locating the TCP tail outside remote owner queue/PTY execution.

rev0020 completes the default-off R6 construction boundary. The signed pre-network restart lease and
separate-process gate make daemon replacement, controller replacement, reconnect, SENDQ pressure, and
revocation outcomes explicit. R5 still provides the independently gated controller stream: an explicitly configured controller
Agent publishes one private same-user stream, resolves an exact authenticated route, drives bounded
Ratox controller state, and exposes one-binary OPEN/RESUME operation. The rev0018 host gate remains
independently disabled by default and still performs exact authority/profile/PTY enforcement.

The deterministic suite crosses the pure host and controller engines, live Agent route integration,
local canonical protocol, pathname socket security, one-binary CLI failure paths, and retained SENDQ
behavior. It does not prove restart recovery of a live PTY or controller state, multiple local streams,
complete two-guest Sandwurm operation, public enablement, or production support.
`ratox-service-implementation-plan.md` keeps R7 complete-service science and R8 support review as
separate gates.

The historical pinned standalone attempt stopped before compilation: the build tool retried the
immutable libsodium 1.0.22 source URL and curl exited 6 because the container could not resolve the
upstream host. That old bulky log is no longer retained in the tracked source tree. This remains an
evidence boundary, not evidence for the official-source provider, linked binary, or genuine peers.

The final laboratory measures the complete client-to-PTY-to-client path between the two Sandwurm
guests over observed direct UDP and forced TCP, idle and beside 1/8/16/32/64 bulk streams. Diagnostic echo RTT is
not a substitute. Direct-route targets are p95 <= 50 ms, p99 <= 100 ms, zero 250 ms misses, zero
lost/duplicated accepted input, and owner interactive queue p99 < 2 ms. The dedicated-route branch
is entered only when bulk misses those latency targets while the owner queue remains below target.

### Runtime and local IPC

```text
private modes, connection credentials, and bidirectional per-record sender credentials
optional kernel sender pidfds and terminal owner-process lifetime release
ancillary truncation/malformed/duplicate/SCM_RIGHTS rejection and descriptor closure
finite administrative request lease plus exact active/stale/replacement socket inode ownership
bounded SOCK_SEQPACKET request/response correlation
transactional directory publication
atomic regular-file projections
no-follow/type/owner/mode/inode checks
bounded journal rotation
public-key path canonicalization
start/stop/restart and missing-daemon behavior
lone visible BOOTSTRAPROSE entrance
```

## Compiler and dynamic-analysis matrix

```sh
set -o pipefail
IOTOX_MATRIX_JOBS=2 \
IOTOX_FUZZ_LOG=/mnt/data/iotox-rev0043-fuzzer-smoke-final.log \
IOTOX_STATIC_ANALYZER_LOG=/mnt/data/iotox-rev0043-focused-static-analysis-final.log \
  ./tools/build-matrix.sh \
  |& tee /mnt/data/iotox-rev0043-final-matrix.log
printf '%s\n' "${PIPESTATUS[0]}" \
  > /mnt/data/iotox-rev0043-final-matrix.exit
```

Required lanes:

```text
GCC debug                  30 CTest entries
GCC release                30 CTest entries
Clang debug                30 CTest entries
Clang ASan + UBSan         45 CTest entries (16 owned-registry shards)
GCC TSan                   45 CTest entries (16 owned-registry shards)
focused Clang analyzer      11 critical translation units, zero diagnostics
GCC linked system Argon2   30 CTest entries
Mutorr preservation        21 CTest entries
Clang libFuzzer             12 targets x 5000 units
```

The matrix owns `build/.matrix.lock`, cleans its lanes by default, requires exactly one
`focused-static-analysis=pass files=11 diagnostics=0` marker, and ends with exactly one
`final-source-matrix=pass`. A concurrent run fails closed with status 75.

## Repeated Agent/session proof

```sh
IOTOX_AGENT_STRESS_RUNS=100 \
IOTOX_AGENT_STRESS_LOG=/mnt/data/iotox-rev0043-agent-stress-final.log \
IOTOX_AGENT_STRESS_EXIT=/mnt/data/iotox-rev0043-agent-stress-final.exit \
  ./tools/agent-session-stress.sh gcc-debug
```

The harness discovers the current linked test shard instead of freezing an initialization-order
index. It stages the transcript privately, requires run numbers 001–100 exactly once, requires one
terminal summary, and publishes by atomic rename. Another runner cannot share the evidence path.

For repeat-until-failure testing of any CTest selection:

```sh
./tools/repeat-tests.sh gcc-debug 20 '^iotox\.binary-process-lifecycle$'
```

The CI process fixture uses this lane to exercise actual daemon startup, local IPC, shutdown, and
restart twenty times per change.

## Product coverage

```sh
./tools/coverage.sh
```

This instruments the maintained `src/` and `include/` product surface, runs the complete default
suite, writes HTML and Cobertura XML under `build/coverage-report`, and enforces a 70% line baseline.
It also refuses a cache without coverage instrumentation or a PATH without `gcov` matching the
compiler. The reporter treats GCC/gcov negative-hit and suspicious-hit parser overflows as warned
tooling noise rather than product failures while preserving the line-coverage floor.
`IOTOX_GCOV_EXECUTABLE` selects an explicit matching executable when a distribution keeps the
compiler wrapper and coverage tool in separate packages. Set `IOTOX_COVERAGE_MINIMUM` only when
intentionally ratcheting that baseline upward.

The retained rev0043 full source run passes all 30 default targets, with the five delegated-cgroup fixtures
retained as named capability skips, and records 72.5% lines (40,974/56,551), 87.5% functions
(3,071/3,509), and 38.8% branches (37,191/95,861). The line result is the enforced gate; function and
branch values are recorded measurements, not release thresholds.

## Fuzzing

```sh
IOTOX_FUZZ_RUNS=5000 IOTOX_FUZZ_JOBS=2 ./tools/fuzz-smoke.sh
```

Targets:

```text
outer frame decoder
session payload decoder
local control packet decoder
local terminal protocol decoder
durable command codecs
local terminal profile/binding decoder
kernel cgroup record decoder
signed update manifest/policy decoder
authority record/session decoder
Ratox v1 frame decoder
complete interactive session and quota-directory state
complete Ratox service coordinator with fake PTY lifecycle and transport queues
```

The launcher copies reviewed seeds into build-local corpora and validates the Ratox hexadecimal
seed before decoding it. It uses `xxd`, Python 3, or Perl in that order rather than making one
nonessential utility a hidden prerequisite.

The interactive-state target independently mutates the low-level input/output primitives, the
complete session lifecycle, control reservations, attachment fencing, bounded events, incarnation
replacement, and a device directory whose principal/device quota invariants are checked after every
operation.

The interactive-service target drives the production `RatoxService` through valid and malformed
OPEN, ATTACH, RESUME, INPUT, ACK, resize, detach, close, offline, revocation, shutdown, replay, and
transport-pop sequences. A deterministic fake PTY injects partial writes, backpressure, closed
streams, invalid backend reports, read/poll/resize/signal failures, process exit, and output. After
every operation the fuzzer verifies session/tombstone, replay-byte, outbound packet/byte, event,
principal, frame-metadata, and sequence bounds. Its reviewed corpus includes open/service/pop,
partial-write failure, and offline/resume/revocation paths.

The exact root request decoder is covered by exhaustive finite boundary/unit cases and by the Agent
process path. It can gain a dedicated fuzzer if its grammar grows; the current fixed field and bounded
hex decoder do not justify inventing complexity solely for a target count.

## Defects revealed during rev0019 construction

### PTY helper exit could race manifest delivery classification

An executable that closed the configuration socket before implementing the hidden-child protocol
could make the parent observe `EPIPE` or `ECONNRESET` before EOF on the independent startup-status
channel. The parent now closes its configuration endpoint, consumes the bounded status result, and
only then kills and reaps the child. A malformed or prematurely closed helper is therefore classified
at the protocol boundary consistently across schedules; the process regression repeats that case.

### Resume validation must commit replay coordinates atomically

A successful-looking RESUME_RESULT could carry an individually valid input acknowledgement together
with output bounds that contradicted already retained controller output. Input was initially released
before the output contradiction was detected. All peer-controlled coordinates are now validated
first, so a rejected response leaves both replay windows and the input send cursor unchanged.

### A rejected local OPEN is not an attachment lifecycle

The socket worker initially marked the stream open before the Agent packet handler committed it. A
policy-rejected OPEN could therefore call disconnect cleanup for state that had never been published.
Publication now occurs only after handler success. The same boundary rejects negative send deadlines
before attempting `send(2)`, preventing an immediate writable socket from bypassing deadline
validation.

### A pathname socket needed identity checks on both sides of connect

Checking an owner-private pathname before `connect(2)` did not prove that the connected endpoint was
still the same inode. The client now requires an absolute NUL-free path, records the pre-connect
device/inode, authenticates the connected peer with `SO_PEERCRED`, and then rechecks type, owner, mode,
device, and inode. Path replacement fails closed.

### The local protocol document and implementation disagreed on frozen header bytes

The implementation used `ITTS`, a two-byte payload length, and four reserved zero bytes while an early
draft described a different magic/layout. The document now matches the implementation and an exact
32-byte golden vector prevents silent drift.

### Reliable local packets must not inherit network replay tolerance

The first controller draft silently acknowledged some old local OUTPUT and tolerated ambiguous OPENED
or GAP ordering. `SOCK_SEQPACKET` already preserves local message order and boundaries, so such states
indicate a defect or peer violation. Duplicate OPENED, inconsistent pre-open gaps, and any output not
beginning at the exact next byte now fail closed.

### PTY startup had a dual-channel error-classification race

The parent sends the child manifest on one socket and receives readiness or a structured setup error
on another. A wrong helper can close both immediately, so scheduling previously selected either a
manifest `EPIPE`/`ECONNRESET` or status-channel EOF. Both paths rejected the helper, but the typed
result was not deterministic. A manifest-send failure now consults the status channel before
classification, preserving structured child errors and consistently reporting a closed helper at the
readiness protocol boundary. The regression repeats the race eight times per process-suite run.

### Fuzz instrumentation was not a complete link usage requirement

The fuzz tree instrumented the static product archive with fuzzer-no-link, ASan, and UBSan, but only
fuzzer executables linked the sanitizer runtimes. Target-selective smoke builds worked while an
all-target build could leave ordinary product and test executables with unresolved runtime symbols.
The archive now exports the ASan/UBSan link requirement to every consumer; libFuzzer's main remains
private to dedicated targets. The complete fuzz-enabled tree and all twelve fuzzers build together.

### Release provenance lagged behind implementation identity

The source reported rev0019 while the governing entrance, package contract, active build report, and
test topology still described rev0018. Packaging now treats stale identity/count/evidence prose as a
release-blocking defect rather than cosmetic documentation debt.

### Concurrent registry evidence depended on an opportunistic reader schedule

The profile registry already published vectors, bindings, and generation under one shared mutex, but
its optimized stress regression released four readers and immediately performed all replacements.
An optimizer-fast publisher could finish before any reader was scheduled, producing zero observations
without violating the product lock contract. The regression now waits for every reader to reach an
explicit ready point and for the released reader set to complete a minimum observation before
publishing replacement generations. The coherence assertions are unchanged, and the corrected test
passes the repeated GCC Release lane plus the final ThreadSanitizer shards.

## Defects revealed during rev0018 construction

### Local support was initially easy to confuse with bilateral negotiation

Advertising bit 23 locally does not prove that the peer advertised it or that the session negotiated
it. The runtime projection now publishes local support, local requirements, peer support, peer
requirements, and the negotiated intersection separately. The mock peer can advertise Ratox
independently, and tests freeze both one-sided non-negotiation and bilateral negotiation.

### A runtime test waited on a field name that did not exist

An early boundary test waited for `shared-features` while the canonical projection was
`negotiated-features`. The test now consumes the exact public field names and separately asserts all
feature masks, preventing a passing local-advertisement observation from masquerading as a negotiated
session.

### Per-cycle bounds alone did not guarantee fairness

A bounded loop that always began at the first session could repeatedly spend every operation on one
busy PTY and starve later sessions. The service now advances round-robin session and process cursors
across calls. A regression test keeps multiple PTYs busy and proves every live session progresses
under a deliberately tiny global budget.

### SENDQ retry required exact packet ownership

Popping an outbound frame before toxcore accepted it could lose terminal output during queue
pressure; regenerating it could also violate exact replay ordering. The Agent now retains the exact
front packet on `SENDQ`, removes it only after acceptance, and discards it only when the bound route
is demonstrably stale or non-retryable.

### Activation validation had to precede toxcore startup

Discovering an invalid profile store, missing enabled binding, unusable helper, or inconsistent
service bounds after HELLO construction could create a one-sided advertisement window. Ratox
construction now completes or fails before transport startup; the supported-feature mask is then
frozen for the admitted session.

### Replay identity originally omitted the authenticated route

The pure session cache correctly keyed exact packet bytes, but the service initially supplied only
the wire packet. A byte-identical PING or empty control arriving through another authorized
friend/epoch could therefore inherit the owning route's retained outcome before attachment validation.
The service now prefixes a local replay domain, friend number, and online epoch. A regression opens one
session, replays its exact PING through another route, and requires a protocol error with no outbound
packet.

### Rejected routes could poison replay and revocation ownership

Fresh DETACH, OUTPUT_ACK, RESIZE, and CLOSE controls originally completed an empty replay record even
when route validation failed. The duplicate then appeared successful and the invalid route consumed a
bounded message ID. The dispatcher also updated authority-owner fields before validation, allowing a
stale route to become the target of a later revocation call. Rejected controls now cancel their
reservations, and authority ownership changes only after successful OPEN/ATTACH/RESUME. The regression
repeats an invalid resize, proves both attempts fail without a PTY effect, proves revoking the rejected
route is `NOT_FOUND`, and proves the actual owning route still closes the process.

### Route proof loss was too broad for same-principal parallel epochs

One exact route's stale proof originally purged all replay and outbound state for the principal and
could close another still-authorized session on a different epoch. Route revocation now purges and
closes only the matching friend/epoch. Durable ledger revocation remains a separate principal-wide
operation so detached sessions are still fenced. A two-route regression retains the unaffected
route's PONG and admission replay while closing only the stale route. Unauthorized absent
ATTACH/RESUME requests also return retained `DENIED` results so authority-less callers do not learn
session existence.

### Retained packets originally had no explicit authority dependency

The first Agent join knew that an inbound request was authorized when its result was constructed, but
the fixed outbound record did not preserve that fact. A later exact replay or delayed SENDQ retry
therefore had no packet-local way to distinguish an authority-bound success from the intentionally
deliverable denial used to reject an unauthorized admission. Outbound records now retain a boolean
authority fence, admission replay retains the same fence beside the exact bytes, and the Agent
reconstructs the current friend/epoch/principal decision before sending a fenced packet. A regression
proves both the unauthorized denial and its exact replay remain unfenced while a successful OPEN result
is fenced.

### Exact-head checks originally left a check/effect race

The authority ledger and peer-authority registry were individually thread-safe, but a local control
worker could complete a signed append after the Agent's exact-head check and before Ratox spawned,
resized, wrote to, serviced, or sent for a PTY. rev0018 now serializes local and accepted remote
authority mutations with inbound Ratox admission and each bounded service/send cycle. This gives the
Agent one total order without making the ledger own toxcore or PTY state. ThreadSanitizer and the live
authority-denial/revocation fixtures guard the implementation boundary.

### Content-free telemetry needed negative evidence

A counter-only design claim was not enough. Runtime tests now feed distinctive terminal content,
arguments, environment values, cwd/path values, profile identifiers, and error text through the
service, rotate the private journal, and prove those values never appear in retained telemetry.

## Defects revealed during rev0017 construction

### A sanitizer-instrumented payload could not coexist with the profile address-space ceiling

The first ASan/UBSan matrix attempt reached the real PTY path, applied the configured 512 MiB
`RLIMIT_AS`, and then the instrumented fixture failed while reserving ASan's much larger shadow
address range. The product library, hidden IoTox helper, parent controller, decoder, and test harness
remain sanitized; only the tiny post-boundary payload is native. This preserves both sanitizer
coverage of the code under test and an actually enforced finite address-space profile.

### Credential changes can clear the Linux parent-death signal

The exact-identity path initially armed `PR_SET_PDEATHSIG` before dropping UID/GID. Linux may clear
that setting when credentials change. The child now verifies its expected peer PID, arms the signal,
performs and verifies the complete identity transition, then re-arms and verifies the contract before
final exec. A root-only report confirms the exact-identity payload still observes `SIGKILL`; a second
supervisor test kills the controller without destructors and proves the HUP/TERM-ignoring payload
actually exits, using a pidfd when available.

### Ignored daemon signals can survive exec into the target

The initial spawn setup cleared the signal mask but did not reset every ignored disposition. POSIX
exec preserves ignored signals, so a daemon that ignored `SIGPIPE`, `SIGXFSZ`, or another catchable
signal could unintentionally grant that policy to the terminal target. Spawn attributes now restore
the complete catchable set to default while excluding unchangeable `SIGKILL` and `SIGSTOP`. The
native parent deliberately ignores two signals and the final payload reports both as default.

### Ambient daemon capabilities could survive both exec boundaries

`PR_SET_NO_NEW_PRIVS` blocks privilege newly granted by set-ID bits or file capabilities, but it does
not mean an already ambient capability is absent. The hidden child now clears the complete ambient
set and reads back every capability known to the build before identity transition and final exec. A
separate root-only supervisor places `CAP_NET_BIND_SERVICE` into its own inheritable and ambient sets,
launches the ordinary PTY path, and requires the final fixture to report zero ambient capabilities.
Restricted or non-root hosts retain the ordinary zero-count report while skipping only the
privilege-raising precondition.

### Parent identity must come from the handoff, not a timing-only PID sample

The child now requires two distinct UNIX stream sockets, obtains `SO_PEERCRED` from both, rejects any
PID/UID/GID disagreement, and derives the expected parent from that kernel-authenticated pair. It
also proves fd 0/1/2 are the same PTY character device before reading policy. This makes the
parent-death race check and startup status channel part of one descriptor contract rather than
independent assumptions.

### Controller-only byte limits left the backend contract wider than intended

The first controller enforced per-call I/O and dimension bounds, but a future direct backend caller
could bypass those checks. The POSIX backend now independently rejects oversized writes, zero or
oversized reads, and invalid dimensions; the native process suite calls the backend directly to keep
that lower boundary frozen.

### Registry replacement needed explicit reader/writer synchronization

The initial generation swap was failure-atomic for one thread but did not define concurrent reload,
resolve, and snapshot behavior. A shared mutex now publishes profile vectors, bindings, and generation
as one coherent state. A stress check repeatedly alternates distinguishable generations while reader
threads resolve and snapshot, and the TSan lane exercises that contract.

## Defects revealed during rev0016 construction

### A lifecycle fixture retained a stale revision success predicate

The complete process path produced every required authority event, but the final fixture predicate
still encoded the preceding revision's terminal condition. The assertion was updated to the actual
rev0016 state rather than weakening the product path or discarding observed events.

### Authority negotiation needed to be directional

Adding feature bit 24 initially stalled a mixed-version process run because challenge construction
implicitly treated both ledgers as one format. Each verifier now challenges in its own current format,
a capable peer answers the independently negotiated request, and a migrated v2 verifier remains
inactive toward a v1-only peer instead of silently downgrading its local head.

### A pending guard transition must reconcile during a live append

The first guard design recovered exact interrupted states only when reopening the ledger. A long-lived
daemon can instead encounter the next append after the ledger replace landed but final guard
promotion did not, or after the replace failed while pending remained. The live append path now
promotes or discards pending only when the exact current head matches; every third head fails.

### Canonical prepared bytes were not sufficient signing intent

The daemon already prepared canonical authority bytes, but the RecallRoot client initially trusted
those bytes to represent the requested action. A compromised daemon could substitute a different
well-formed grant. The client now decodes and compares every semantic field before deriving or
transmitting a signature, and the process fixture proves the substituted body produces zero signed
append attempts.

### A fixed probe-burst wait exposed a scheduler-dependent rank failure

Repeated Agent lifecycle stress found an impossible arrival rank because the probe helper returned
after a fixed short sleep even when successful sends still had pending replies. The helper now waits
for every successful send to receive its matching reply or for the event loop to stop, with a bounded
test deadline. Evidence is therefore completion-based rather than timing-shaped.

### A fast CLI rejection could terminate its parent fixture with SIGPIPE

The authority process fixture supplies RecallRoot input to the real CLI even when a case is expected
to fail during argument validation. Under one Clang-debug schedule, the child closed stdin before the
parent's post-spawn write and the default `SIGPIPE` action terminated the fixture, hiding the CLI's
intended exit status. Both process harnesses now preload their bounded input while they still own a
read end, reject input larger than the discovered `PIPE_BUF`, and only then spawn or fork. A focused
120-run Clang repetition plus the complete matrix exercises the repaired ordering without changing
the signal disposition inherited by the product process.

## Defects revealed during rev0015 construction

### A process-global one-shot mock fault was consumed by the new peer

The existing fixture armed a “next lossless send fails once” hook and assumed the intended session
would consume it. Adding the root outgoing request created another peer and changed global send
ordering. The fault could be consumed by unrelated work, manufacturing a false retry result.

The immediate fixture correction removes the temporary request peer before deliberate session fault
injection and verifies the lifecycle. The deeper rule is now documented: future deterministic fault
plans should be peer- and operation-bound rather than process-global.

### Malformed request evidence initially lacked an honest identity state

The lifecycle event shape historically expected a public key. A root record can fail before any key
prefix is trustworthy. Filling that field with zero bytes would create a plausible but false peer.
`FriendLifecycleEvent` now supports an explicit keyless state rendered as `public-key=unknown`; exact
validation requires either one canonical key or the keyless marker.

### A projected root FIFO could disappear while service status stayed green

Public-key directory lanes are dynamic by design, but a process-wide promised entrance is required.
Generalizing the monitor without distinguishing those semantics could leave `friendship-fifo-running`
true while `RUNTIME/request` was absent or invalid. Root-lane startup now requires every configured
lane, live readiness includes its monitored count, and replacement remains subject to the same
hardening checks.

### Replaying an unfinished branch required immutable-base recovery

An ephemeral worktree containing valid rev0015 changes was reclaimed after an initial green run. The
released rev0014 cube remained immutable. The changes were replayed from that cube, then rebuilt and
retested. The incident reinforces that an unreleased workspace is not evidence; the datacube and
final retained logs are the handoff unit.

### Clean GCC Release proved a packet precondition was implicit

The first clean full-matrix attempt stopped in the Release lane because GCC's null-dereference analysis
proved that `transport_send_lossless` could reach `packet.front()` without a source-level non-empty
precondition. Existing callers and debug tests supplied non-empty packets, but that was not an adequate
contract. The product path now checks `!packet.empty()` before inspecting the IoTox discriminator. The
failed matrix transcript is not retained as success; all final evidence is regenerated from the corrected
source.

### Foreground stress timeout did not manufacture partial success

The first 100-run invocation exceeded an external foreground wrapper limit before the stress harness
finished. Its private stage was removed and neither a green log nor a zero exit file was published. A
detached rerun acquired the same exclusive lock, completed all 100 fresh processes, self-validated the
ordered run sequence and sole terminal summary, and atomically published the canonical evidence.

### Historical lesson: artifact prose went stale while retained binaries were current

The first refresh correctly replaced rev0015 binaries and reports but preserved an old rev0014
`artifacts/README.md`. That mismatch did not alter executable evidence, but it could mislead an offline
reader. The refresh tool now generates the artifact README from current revision, codename, and check
count before computing `SHA256SUMS`; retained metadata is therefore part of the reproducible evidence
surface rather than hand-maintained residue. The current tracked source avoids this failure mode more
directly: bulky prebuilt artifact sets are not retained under `artifacts/`; only small, referenced
receipts remain there.

### A post-effect replay shortcut weakened the intended API boundary

The first R1 draft exposed a convenience function that could reserve and commit a replay entry in
one call. Product code did not use it, but a future caller could have performed a side effect first
and only then discovered that retention was unavailable. The shortcut is removed. The public path
now requires explicit pre-effect reservation followed by commit or cancellation, and commit releases
unused result capacity while retaining exact request-plus-result byte accounting.

### The fuzz launcher accidentally required one seed-decoding utility

The reviewed Ratox seed is hexadecimal text, but the first seven-target launcher required `xxd`
even when another safe decoder was present. It now validates and decodes with `xxd`, Python 3, or
Perl. The gate remains fail-closed when none is available or when the seed is malformed.

## Earlier defects still guarded

Regression tests retain prior findings:

- stale objects concealing revision mismatch;
- timeout budget reused across unrelated asynchronous waits;
- journal prefix versus whole-file equality under concurrent append;
- FIFO write confused with semantic rejection completion;
- peer projection withdrawal confused with later journal append;
- numeric deletion separated from public-key lookup;
- overlapping stress runners corrupting one transcript;
- accidental sovereign RecallRoot output retention;
- C ABI function-pointer mismatch exposed by UBSan;
- predictable/incomplete state-file replacement.

## Pinned host and Sandwurm VM loop

When the ambient shell does not expose the compiler or runtime crypto libraries, use the locked Nix
development shell rather than borrowing state from a prior build directory:

```sh
nix develop --command bash -c \
  'set -euo pipefail; cmake --fresh --preset gcc-debug; cmake --build --preset gcc-debug; ctest --preset gcc-debug --output-on-failure'
```

The bounded VM bootstrap gates are:

```sh
./tools/iotox-sandwurm-lab.sh preflight
./tools/iotox-sandwurm-lab.sh up device
./tools/iotox-sandwurm-lab.sh up client
./tools/iotox-sandwurm-lab.sh up-pair direct-udp
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp relay-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp daemon-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp link-interruption
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp guest-restart
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-adversity
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-adversity
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-pressure
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-pressure
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-quota
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-quota
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-object-quota
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-object-quota
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-read-only
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-read-only
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-memory
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-memory
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-source-corrupt
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-source-corrupt
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-destination-corrupt
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-destination-corrupt
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh up-pair direct-udp mutable-profile-status
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp mutable-profile-status
./tools/iotox-sandwurm-lab.sh up-pair direct-udp signed-update
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp signed-update
./tools/iotox-sandwurm-lab.sh up-pair direct-udp update-service
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp update-service
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-actual-i2p NODE1 NODE2 NODE3
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-retry
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-retry
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-restart
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-guest-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-guest-restart
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-pause
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-pause
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-cancel
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-cancel
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh status device
./tools/iotox-sandwurm-lab.sh status client
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT relay-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT daemon-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT link-interruption
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT guest-restart
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-adversity
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-adversity
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-pressure
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-pressure
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-quota
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-quota
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-object-quota
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-object-quota
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-read-only
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-read-only
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-memory
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-memory
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-source-corrupt
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-source-corrupt
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-destination-corrupt
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-destination-corrupt
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT mutable-profile-status
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT mutable-profile-status
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT signed-update
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT signed-update
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-actual-i2p
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-retry
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range-retry
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-restart
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-guest-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-guest-restart
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-pause
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-pause
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-cancel
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-cancel
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-repair
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-repair
```

Each individual `up` invocation builds one role-specific NixOS closure, launches it through Sandwurm's reviewed
Cloud Hypervisor chain, waits for complete guest evidence, terminates the VMM, and verifies the
content-free IoTox receipt. It is not yet a persistent or simultaneous two-node command. See
`sandwurm-two-node-lab.md` and the 2026-08-20 bootstrap evidence note.

Each `up-pair` invocation realizes the pinned source-linked package, starts one temporary local
c-toxcore bootstrap/TCP-relay fixture, launches both role closures concurrently with distinct TAPs,
copies the immutable reusable identities into fresh private disks, exchanges public addresses, and
requires exact UDP or TCP connection truth plus confirmed IoTox sessions and bidirectional text.
The manifest binds both IoTox receipt and Sandwurm chain digests. The standalone pair verifier
re-checks those bindings, the planned bridge/TAP topology, provider versions, KVM/cgroup v2, shared
binary digest, unchanged-baseline assertion, and content-free flags. Pair proof roots are ignored and
private because they retain writable guest disks and the bootstrap fixture key; only the exact
declared compact evidence subset is shareable. See the 2026-08-20 two-node transport evidence note.

Accepted pair evidence can be compacted without weakening verification:

```sh
./tools/export-sandwurm-pair.py PROOF_ROOT
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/PAIR_ID --route ROUTE --scenario SCENARIO
```

The exporter admits an immediate `pair.*` child only, verifies it first, and copies the exact manifest,
two guest receipts, two Sandwurm chains, and two planned-launch records into an atomic owner-private
directory. The compact manifest binds the source manifest digest and preserves the fact that private
disks existed at the source; `compact-export.json` hashes the complete allowlist and declares the
omitted private artifact classes. The ordinary verifier checks both layers. No guest disk, injected
identity, bootstrap key, runtime journal, or undeclared proof-root file enters the export.

Completion receipts are scenario data, not an invitation to reinterpret old evidence using the
newest shape. The original `sync-content-multi-source` proof predates atomic initial admission and
therefore omits both `content-atomic-pull` and `multi_source_atomic_pull_role_count`; current proofs
carry and require both. The verifier selects these two exact generations by presence of the manifest
field, requires selected-source-loss proofs to use the atomic generation, and self-tests the ordered
field shapes. This preserves strict replay of ADR 0255 without weakening ADR 0256.

`sync-tree` publishes a deterministic owner-controlled directory under signed HEAD engine 3. Owned
tests prove byte-identical packing independent of creation order, complete-artifact/entry/path/source
policy bounds, private extraction modes, signed-activation-before-projection ordering, deterministic
repack verification, atomic `current`, exact retry, abandoned-staging recovery, ambiguous-entry
refusal before cleanup, exact pointer-temporary recovery, and current-only derived projection. The
candidate populations share the namespace object bound; an excess-pointer test requires
`resource_exhausted` with every candidate untouched. The
`iotox.sync-tree-process` route installs generation 1, terminates a generation-2 child with `_exit`
after each of eight post-effect boundaries, requires a complete old-or-new view, and then requires a
fresh child to converge to one revision with no derived temporary. This is a real process/filesystem
crash boundary, not a power-cut or ENOSPC simulation. The genuine two-guest cell transfers and
activates a three-directory/three-file 4 MiB fixture over both carriers. Accepted compact
observations are `.sandwurm/exports/pairs/pair.qf7x57c7` and
`.sandwurm/exports/pairs/pair.kjr7ksxw`; exact bindings and the disclosed pre-product TCP startup flake are in
`evidence/2026-08-24-sandwurm-sync-tree.md`.

`sync-tree-adversity` begins from that same activated generation 1 in a dedicated loop-mounted 64 MiB
ext4 namespace. The publisher snapshots only a stopped, coherent synchronization root, then performs
four savedata-preserving daemon restarts while presenting generation 2A, restored generation 1, a
distinct valid generation-2 fork, and a generation-3 successor of 2A. Explicit host relays cross the
two separate Sandwurm guest exports; no shared rendezvous directory is assumed. The subscriber must
activate 2A, refuse stale and fork candidates with the exact typed details, and prove by hashes that
accepted state, activation state, and `current` bytes remain 2A. Before generation-3 projection it
uses `fallocate` and `df` to leave approximately 2 MiB free. The first activation must fail after the
signed activation pointer changes while the old visible tree remains byte-identical. Removing only
the filler and retrying the exact token must return `decision=duplicate materialized=1`, expose the
generation-3 payload, retain exactly one revision, and leave no derived temporary. Both compact proofs
bind four restarts, 34,733,056 reserved bytes, 2,096,128 failure free bytes, and the same generation-3
identities: `.sandwurm/exports/pairs/pair.bv44g4mm` for direct UDP and
`.sandwurm/exports/pairs/pair.iuevljep` for forced TCP. Exact identities and nonclaims are in
`evidence/2026-08-24-sandwurm-sync-tree-adversity.md`.

`sync-tree-pressure` keeps the same baseline fixture, adds two signed directory namespaces, and
configures the publisher worker queue to one. A real cross-process transaction lock holds namespace
A while its artifact request is active and its manifest request occupies the queue. Namespace B's
HEAD request must then increase the rejection counter by exactly one without changing that hard bound
or stalling the toxcore event pump. Releasing only the lock must let A converge; exact retry of the
retained B request must then converge B. Both roles require explicit saturation and recovery markers.
The direct-UDP and forced-TCP compact proofs are `.sandwurm/exports/pairs/pair.c3qc5k28` and
`.sandwurm/exports/pairs/pair.5nh407kh`; exact bindings and nonclaims are in
`evidence/2026-08-24-sandwurm-sync-tree-pressure.md`.

`sync-tree-quota` first converges and activates that same generation-1 tree under a subscriber-local
5,242,880-byte whole-store ceiling. The retained artifact and manifest consume 4,981,169 bytes. The
publisher then signs a one-byte-changed generation 2 under its independent larger local ceiling.
Both new objects must individually exceed the subscriber's exact 261,711-byte remainder, making the
failure independent of file completion order. The subscriber must report
`sync staged commit would exceed whole-store quotas`, clean its attempt staging, retain exactly the
two generation-1 objects, and preserve byte-identical accepted, activation, `current`, and payload
truth. The direct-UDP and forced-TCP compact proofs are
`.sandwurm/exports/pairs/pair.0codwav1` and `.sandwurm/exports/pairs/pair.b6pev5yy`; exact bindings
and nonclaims are in `evidence/2026-08-24-sandwurm-sync-tree-quota.md`.

`sync-tree-object-quota` keeps the 33,554,432-byte store ceiling and preloads four private,
correctly digest-named one-byte objects. Generation 1 then contributes its artifact and manifest,
reaches `maximum-objects=6` exactly, and still activates the six-entry tree. The complete successor
would fit under the byte ceiling. Whichever new candidate object completes first must therefore fail
by object count with `requested=2`, `committed=0`, no candidate object or staging residue, and exact
preservation of the six-object inventory, accepted HEAD, activation, `current`, and visible payload.
The direct-UDP and forced-TCP compact proofs are `.sandwurm/exports/pairs/pair.1oaa9bzi` and
`.sandwurm/exports/pairs/pair.x7dul21w`; exact bindings, the shared v1 tree-entry consequence, and
nonclaims are in `evidence/2026-08-24-sandwurm-sync-tree-object-quota.md` and ADR 0142.

`sync-tree-read-only` converges and activates generation 1 in a dedicated loop-backed 64 MiB ext4
subscriber namespace, then signs a one-byte-changed generation 2. After an actual read-only remount,
the first pull must fail at persistent transaction setup with `requested=0`, `admitted=0`, and
`committed=0`, while retaining the exact object inventory, signed roots, `current`, visible payload,
and empty staging. Read-write remount plus exact pull retry must request and commit both candidate
objects and accept generation 2 without activating it. A second read-only remount must make exact
activation return typed `io-error`/`Read-only file system` without changing accepted generation 2 or
activated/visible generation 1. Read-write remount plus exact activation retry must expose the
candidate payload with no staging. The direct-UDP and forced-TCP compact proofs are
`.sandwurm/exports/pairs/pair.pded9tmd` and `.sandwurm/exports/pairs/pair.ddcbkpei`; exact bindings and
nonclaims are in `evidence/2026-08-24-sandwurm-sync-tree-read-only.md` and ADR 0143.

`sync-tree-memory` starts only after the ordinary six-entry generation 1 is accepted and activated,
then records each long-lived IoTox PID's Linux `VmHWM`. The publisher adds twelve deep directories,
one 3 MiB file, and 109 one-byte files; generation 2 therefore reaches exactly 128 entries (15
directories and 113 files), 7,340,226 content bytes, and a 7,616,908-byte artifact. Both carriers must
publish, request/admit/commit two objects, accept HEAD last, explicitly activate the complete tree,
and leave staging empty. Both receipts agree on publisher baseline/post-publication/final high-water,
subscriber baseline/post-pull/final high-water, exact deltas, pair maximum, the 65,536 KiB construction
ceiling, and successor identities. Accepted UDP/TCP pair peaks are 12,924/13,132 KiB; compact proofs
are `.sandwurm/exports/pairs/pair.4ndi9yq_` and `.sandwurm/exports/pairs/pair.vbb7zli3`. Exact
interpretation and nonclaims are in `evidence/2026-08-24-sandwurm-sync-tree-memory.md` and ADR 0144.

`sync-tree-source-corrupt` begins after ordinary generation 1 is accepted and activated. The
publisher signs generation 2, corrupts and fsyncs both of its new digest-named objects, and leaves the
signed HEAD intact. The subscriber must report the first job failed with `requested=2`, `admitted=0`,
and `committed=0`; its accepted HEAD, activation, immutable inventory, visible payload, and empty
staging must remain generation 1. Publisher `sync-repair` must inspect four objects, verify two, and
quarantine exactly two objects/4,981,169 bytes. Publishing the unchanged source again must return the
same generation, HEAD, artifact, and manifest with `duplicate=1` and recreate exact valid objects.
Only a fresh pull may then admit/commit both objects, accept generation 2 last, and explicitly
activate its token. The accepted compact proofs are `.sandwurm/exports/pairs/pair.0yqn_jyc` and
`.sandwurm/exports/pairs/pair.t3celhhl`; exact bindings and nonclaims are in
`evidence/2026-08-24-sandwurm-sync-tree-source-corrupt.md` and ADR 0145.

`sync-tree-destination-corrupt` also begins from accepted and activated generation 1, then publishes
the same deterministic generation-2 successor on each carrier. The subscriber starts both complete
object receives on a rate-shaped link, pauses the artifact only after positive progress, observes ten
stable positions, fsync-corrupts byte zero of the exact private transport temporary, and resumes that
same FileId. The job must fail specifically at complete staged SHA-256 verification; corrupt staging,
signed attempt truth, and the candidate artifact must be absent, while generation-1 accepted,
activated, inventory, and visible truth remain unchanged. The independently completed candidate
manifest may remain only if its exact digest verifies. A fresh explicit pull re-verifies it, requests
only the missing artifact, finishes with `requested=1`, `admitted=1`, and `committed=2`, accepts the
HEAD last, and activates only through the exact token. Accepted compact proofs are
`.sandwurm/exports/pairs/pair.53ouy15u` and `.sandwurm/exports/pairs/pair.nvvzvr4w`; exact bindings
and nonclaims are in `evidence/2026-08-24-sandwurm-sync-tree-destination-corrupt.md` and ADR 0146.

`sync-tree-control-replay` captures the exact generation-2 HEAD request and both object requests from
the subscriber protocol journal. Only after the original object results have admitted both FileId
offers does it inject both object requests again. The publisher must report three exact replay hits
across the two object requests and a later HEAD request, while `file-offers` increases by only two.
The subscriber must observe four object results reordered across the already-admitted file lanes, then
two HEAD results total with no new object requests after the HEAD duplicate. A same-message-ID HEAD
whose canonical namespace byte differs must increment one publisher replay conflict and produce no
replacement result. Both carriers still finish `requested=2`, `admitted=2`, `committed=2`, accept the
candidate HEAD last, and activate only by the exact token. Accepted compact proofs are
`.sandwurm/exports/pairs/pair.control_replay_udp` and
`.sandwurm/exports/pairs/pair.control_replay_tcp`; exact hashes and nonclaims are in
`evidence/2026-08-24-sandwurm-sync-tree-control-replay.md` and ADR 0147.

`mutable-profile-status` bootstraps independent authority on both roles, grants the remote stable
principal exactly `write.settings`, waits for the current transcript-bound proof, and admits one
non-expiring `profile.status.set busy` per role. Each role must retain terminal success for its exact
outgoing durable key and the peer's incoming key, decode `IPS1` as desired busy/observed busy with
convergence true, read `self/status=busy` from the real provider projection, and bind ownership epoch
1. Transient pre-admission unavailability may be retried only until one command is admitted; the
accepted sender epoch/message ID is then immutable. Exact hashes and nonclaims are in
`evidence/2026-08-24-sandwurm-mutable-profile-status.md` and ADR 0148.

Guest agent liveness checks inspect `/proc/PID/stat` as well as `kill -0`, so a rejected namespace
policy cannot remain misclassified as a live zombie until a host-side rendezvous timeout.

The synchronization subscriber's excess-admission regression injects `resource_exhausted` at the
final receive entrance before provider acceptance. It requires the bridge to remove provisional
staging and active-journal truth while the scheduler keeps the exact attempt ID and full byte
reservation. Retrying the same FileId and file number then completes ordinary two-object convergence;
`sync-status` reports `pending-offers` and saturating `admission-retries`. A separate cancellation
branch holds one offer pending and one admitted, injects one cancellation-send failure, and proves
both are locally fenced without repeating either effect. Agent service examines at most the shared
qualified ceiling of 32 transfer records per pass and advances a cyclic cursor. This is ADR 0166
construction evidence, not the still-required direct-UDP/forced-TCP pressure and latency gate.
The owned range-v1 regression applies the same deferral to a missing-range bundle and asserts that a
later terminal retry does not send a redundant cancellation. GCC Debug, Clang ASan/UBSan, GCC TSan,
and focused path-sensitive analysis all pass this construction boundary.

`sync-tree-admission` exercises that boundary through two genuine source-linked guests. The client
sets `--max-active-receives 1`; while the artifact owns that slot, the manifest's exact FileId offer
must remain pending and be retried by normal Agent service. Both accepted carriers reported ten
retries, exactly two eventual admissions, zero pending at completion, generation-1 convergence, HEAD-
last acceptance, and separate exact-token activation. Strict compact proofs are
`.sandwurm/exports/pairs/pair.xrl6_7gv` for direct UDP and
`.sandwurm/exports/pairs/pair.dqbsp21_` for forced TCP. The route-latency half of the roadmap gate is
the separately accepted 1,000-sample `bulk-1` matrix; this scenario measures admission pressure, not
simultaneous terminal interference. Exact hashes and nonclaims are in
`evidence/2026-08-25-sandwurm-sync-admission.md` and ADR 0166.

`sync-file-range` first pulls and explicitly activates a deterministic 4 MiB generation 1. The
publisher then changes one bounded region and signs an exact-parent generation 2. The subscriber
must negotiate `state-sync-ranges-v1`, commit and verify the complete new manifest before planning,
request one bounded FileId-bound range bundle, reconstruct the exact artifact from its accepted
basis, accept the linked HEAD last, and explicitly activate that token. Both guest receipts and the
pair manifest must agree that positive reused bytes plus smaller positive fetched bytes equal the
artifact size. The accepted direct-UDP and forced-TCP cells each fetched 128 bytes and reused
4,194,176 bytes.

`sync-file-range-actual-i2p` preserves the same range-v1 artifact/basis relationship but constructs
the signed private-v2 native/native/I2P route set. Generation 1 deliberately completes over native;
the terminally settled job is retired, and generation 2 may freeze a new per-job
`fail-closed tox/i2p-construction` policy without weakening the unchanged authority fence. The
successor passes only when both primary and selected auxiliary negotiated ranges, the completed job
names the exact I2P carrier commitment, one 128-byte artifact range plus 4,194,176 reused bytes equals
4 MiB, reassignment is zero, and explicit activation matches the reconstructed digest. Accepted
compact proof is `.sandwurm/exports/pairs/pair.ej_4507n`; exact hashes and nonclaims are in
`evidence/2026-08-28-sandwurm-actual-i2p-range.md`.

`sync-file-range-actual-i2p-loss` changes the successor mutation to one observable 1 MiB range and
rate-shapes the client TAP. The fault predicate uses the local-only concrete-lane fields rather than
aggregate transfer progress, so the 786,496-byte prerequisite manifest cannot be mistaken for range
payload. The host stops only the client router after positive partial range bytes. The client must
report one fail-closed block, zero reassignment, empty staging, and no active receive. After the same
datadir returns under a new router PID, the exact auxiliary must recover without worker restart; the
old job is explicitly cancelled and a distinct job fetches a full fresh range. Accepted compact
proof `.sandwurm/exports/pairs/pair.a9zwongf` discards 86,373 failed bytes, fetches 1,048,576 new
bytes, reuses 3,145,728, and activates the exact 4,194,304-byte artifact. This is safe fresh recovery,
not same-job continuation or failed-prefix reuse.

The subscriber regression now continues through a separate fresh job after the failed range. It
first replaces the already committed manifest with same-size corrupt bytes and requires local
`protocol_error`, terminal failure, and `requested=0`; repair remains explicit. Restoring the exact
manifest must make HEAD-result handling return one fresh range request directly, with one committed
manifest, a distinct FileId, and the identical bounded range plan. Accepted actual-I2P compact proof
`.sandwurm/exports/pairs/pair.ip5q0at9` lifts that invariant into two genuine guests: after a 71,292
byte failed prefix is discarded, the replacement requests one range, commits both objects, reuses
the manifest locally, reconstructs, accepts, and activates. It does not reuse any failed range byte.

The ordinary same-carrier retry then exercises a distinct ADR 0230 path. The first range is admitted
into the exact canonical private attempt inode from offset zero. Local file-control cancellation
must produce a positive strict prefix; the old attempt finishes/fences; a fresh attempt and FileId
inherit the inode; and the replacement starts at the same byte count. Deterministic coverage also
defers one initial empty-prefix admission and one retained-prefix admission without losing either
signed attempt. Current direct-UDP/TCP compact proofs retain/resume 15,081/24,678 bytes with zero
discard/fallback and complete the unchanged generation-2 verification and explicit activation.

The owned subscriber test then corrupts that exact accepted basis while preserving a strict private
regular-file shape and presents a valid parent-linked successor. The client must commit and reverify
the successor manifest, emit an ordinary artifact request instead of a range request, fully verify
and commit that artifact, clear durable attempt state, and accept generation 3 last. Its retained
status must report `range-fallback=1` and `range-transfer=0`. The corrupt prior digest path must remain
present and invalid, demonstrating recovery without implicit scrub, quarantine, replacement, or GC.
The `sync-file-corrupt-basis` Sandwurm cell performs the same sequence in both live guests. Accepted
direct-UDP and forced-TCP compact proofs are `.sandwurm/exports/pairs/pair.1fyi5byu` and
`.sandwurm/exports/pairs/pair.9tkvsybe`; exact bindings and nonclaims are in
`evidence/2026-08-22-sandwurm-sync-corrupt-basis.md`.

`sync-file-range-retry` keeps the same valid 4 MiB basis/successor relationship but changes one
1 MiB source region so the missing bundle remains observable under a 4 Mbit/s client-TAP limit. The
client waits for a positive provider position, records the first FileId, and invokes the public
generic file-control cancellation. Every schema requires one retry of the identical range vector and
HEAD under a different FileId, 3 MiB basis reuse, exact full-artifact verification,
accepted-HEAD-last ordering, and explicit activation. Historical compact observations
`pair.phkpgx90`/`pair.4r5xzja_` establish the safe full-discard baseline. Current observations
`pair.cj5y5vgt`/`pair.qeb99i4o` additionally require positive exact retained/resumed equality, zero
discard/fallback, and suffix-only replacement receive under fresh attempt and transport identities.
Exact bindings, failed scientific fixtures, and nonclaims are in
`evidence/2026-08-22-sandwurm-sync-range-retry.md`.

`sync-file-restart` is the unclean synchronization process-restart cell. It rate-shapes the
subscriber path, requires positive c-toxcore receive position, and kills the subscriber daemon with
`SIGKILL`. The pre-restart checkpoint must show status 137, two private transport temporaries, a
signed active-attempt journal, and no accepted or activated HEAD. Startup must preserve identity,
recover only exact attempt-scoped staging residue, and leave staging empty before a fresh pull of the
same signed revision. The gate then requires accepted-HEAD-last convergence and explicit exact-token
activation. This is whole-object retry, not byte-range resume or guest-restart evidence. Accepted
direct-UDP and forced-TCP observations and exact digests are in
`evidence/2026-08-21-sandwurm-sync-restart.md`.

`sync-file-guest-restart` faults the publisher at the guest boundary instead. After positive
rate-shaped progress, the publisher checkpoints its publication evidence and requests an
operating-system reboot without creating another revision. The subscriber must observe offline,
terminally fail the old job, and clear live receives, staging, and signed attempt truth before a
successor can recover. The initial device VMM must exit through the exact bounded Cloud Hypervisor
reboot failure; the successor consumes its prelaunch receipt and persisted writable disk. Verification
joins both VMM epochs, changed publisher and unchanged subscriber boot-ID digests, preserved
Tox/stable identity, authority, namespace, source/object/HEAD identities, 50 stable samples at a
higher subscriber epoch, explicit fresh pull, accepted-HEAD-last convergence, and exact-token
activation. This is controlled guest reboot and whole-object retry, not abrupt power loss or
partial-byte reuse. Accepted compact observations are `.sandwurm/exports/pairs/pair.x3h41g9b` and
`.sandwurm/exports/pairs/pair.9wfzoss6`; exact bindings are in
`evidence/2026-08-22-sandwurm-sync-guest-restart.md`.

`sync-file-pause` keeps the rate-shaped 8 MiB job live. After positive provider progress, the client
selects one active incoming transfer, records its exact file number and request-selected FileId, and
uses the public `file-control` command to pause it. The same transfer must report local pause and one
unchanged positive partial position for 20 consecutive 100 ms samples while accepted-HEAD and
activation files remain absent. Resume must return the same FileId with local pause cleared; the job
then converges through ordinary complete-object verification, accepted-HEAD-last ordering, and
exact-token activation. Pause retains staging and scheduler reservations and does not prove durable
pause intent, peer-pause override, disconnect recovery, or restart recovery. Accepted compact
observations are `.sandwurm/exports/pairs/pair.5qa1ubwd` and
`.sandwurm/exports/pairs/pair.hd71hqag`; exact bindings are in
`evidence/2026-08-21-sandwurm-sync-pause.md`.

`sync-file-cancel` uses the same rate-shaped 8 MiB transfer but stops before convergence. The client
retains the job ID returned by `sync-pull`, waits for positive provider position and admitted receive
truth, invokes `sync-cancel`, and requires terminal cancelled status, no remaining incoming transfer,
empty staging, and absent accepted/activated state after a settling interval. Receipts bind the
observed pre-cancel bytes and admitted receive count to the shared revision identity. This is local
cancellation/fencing evidence, not proof that the remote publisher observed the control packet.
The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.kfpfl6pz` and `.sandwurm/exports/pairs/pair.6x5cujaj`; exact clean-source
bindings and nonclaims are in `evidence/2026-08-21-sandwurm-sync-cancel.md`.

`sync-repair NAMESPACE` has deterministic source coverage and genuine-provider repair evidence. The
storage test publishes an artifact/manifest pair, corrupts one digest-named final object without
changing its private regular-file shape, and requires repair to quarantine only that digest mismatch
while leaving the valid object verifiable. A second test adds an unexpected object-store entry and
requires repair to fail closed without creating quarantine state. The Agent socket test exercises the
local-control v1.30 command on an installed empty namespace and checks the bounded aggregate output.

The `sync-file-repair` Sandwurm scenario advances that primitive across the complete subscriber and
provider path. After ordinary convergence and explicit activation, the client corrupts and fsyncs the
first 4 KiB of the exact 4 MiB artifact object. The first repair must inspect two objects, quarantine
only that mismatch, and preserve the signed accepted-HEAD and activation records. An explicit pull of
the same signed revision must restore the absent digest path. The quarantine file must remain private,
byte-identical to the deliberate corruption, and present while a second repair scan verifies both
final objects and creates no new quarantine state. Both guest receipts bind the exact counts and
preservation booleans. Independently reverified direct-UDP and forced-TCP compact proofs are
`.sandwurm/exports/pairs/pair.gzgjsiqq` and `.sandwurm/exports/pairs/pair.hkwzsf05`; exact bindings and
nonclaims are in `evidence/2026-08-23-sandwurm-sync-repair.md`.

`sync-file-disconnect` exercises a different terminal boundary. After positive rate-shaped progress,
the host blackholes both TAPs until both guests observe transport and application-session offline.
The subscriber must fail the old epoch's job, remove its live receives, staging, and signed attempt
truth, and retain no accepted or activated HEAD. A fresh `sync-pull` is permitted only after a
strictly higher confirmed and authorized epoch; that new job must then converge and activate through
the ordinary complete-object path. Both peers must retain that same recovered epoch for 50
consecutive 100 ms samples before retry; a first scientific attempt exposed a second post-restoration
flap when retry began at the first confirmed callback. The verifier rejects missing cleanup, retry,
stability, epoch advance, or route-bound link-loss evidence. The owned check injects one
transport-cancel failure and requires the
failed tombstone to settle local cleanup without repeating that effect before higher-epoch admission.
After convergence the client remains live behind an explicit evidence-release barrier until the
publisher has finished its own stability observation and received the bound completion record.
The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.ip8h7ud4` and `.sandwurm/exports/pairs/pair.xi96v2re`. Both roles
advance from epoch 1 to epoch 2 in both cells; the subscriber records 37,017 and 56,211 interrupted
bytes respectively, terminal cleanup, explicit retry, convergence, and activation. Exact clean-source
bindings and nonclaims are in `evidence/2026-08-21-sandwurm-sync-disconnect.md`. ADR 0132 freezes
whole-object retry rather than partial-byte resume.

The direct-UDP `ratox-bulk-{1,8,16,32,64}` construction ladder is retained in
`evidence/2026-08-20-sandwurm-ratox-bulk.md`. Every cell requires the complete named transfer
population before probing, exact render and owner-queue joins, progress on every lane, and bounded
retry-to-empty cancellation. The 64 cell opts into 64 active sends/receives explicitly; it does not
change the ordinary limit of 32. Forced-TCP and 1,000-sample cells remain separate qualification
work.

The pinned source-linked package carries one explicit c-toxcore variant,
`nix/patches/c-toxcore-0.2.23-file-transfer-round-robin.patch`. New pair receipts name
`iotox-file-rr1-tcp-connect120`, and Ratox verification requires the retained host status to name the same linked
runtime origin. Historical receipts without a variant remain verifiable as upstream observations.
The patch repairs sender starvation through 16 forced-TCP lanes. Four independent forced-TCP routes
then pass 32 aggregate lanes twice, defeating the one-route 17/32 delivery boundary without changing
the product's ordinary active-transfer limits. The construction ceiling remains eight bulk streams
per route: 40 is not repeatable and 48/56/64 violate terminal or lifecycle bounds. On direct UDP the
named provider passes 1/8/16/32;
the 64-transfer opt-in completes terminal capture but not all-lane progress inside the construction
bound. Ratox VM rendezvous now separates terminal capture from bulk completion and publishes a
content-free changing progress checkpoint for failed-run diagnosis.
Striped runs also retain per-guest confirmed-route counts and aggregate route-process restart counts,
then use a two-party evidence barrier before teardown. Each auxiliary agent may be restarted from
its unchanged savedata at most twice on staggered finite intervals. Work remains withheld unless all
four expected TCP routes confirm; there is no three-route capacity fallback.

The `ratox-stripe-recovery-32` cell injects a one-sided stop/restart of the device's fourth route
after its friend request is applied but before route convergence. Its accepted compact proof,
`.sandwurm/exports/pairs/pair.fmf8pynz`, records one injected and two additional automatic restarts,
four distinct confirmed routes, 32/32 active and progressed transfers, 40/40 exact terminal samples,
and cancel-to-empty. This is establishment recovery. It does not claim that active c-toxcore file
transfers survive an agent process or that work can yet be reassigned safely after live lane loss.

`ratox-stripe-live-loss-32` is the discovery cell for a fault after all 32 transfers are active. It
waits for route three to be offline and its eight incoming transfers to disappear before starting
Ratox, forbids reassignment, recovers the unchanged route identity only after terminal capture, and
then checks the recovered route is empty. The transfer semantics were stable, but Ratox with eight
bulk transfers on its own route was not repeatable: one corrected run captured 40/40 while degraded;
the next exceeded the first five-second receive deadline. Failed roots are diagnostic and are not
exported.

`ratox-stripe-protected-live-loss-24` is the follow-up acceptance cell. Route zero is exclusively
Ratox/control; routes one, two, and three each carry eight bulk transfers. It requires exactly eight
transfers purged on the faulted route, 16 unaffected and progressing, zero reassigned, 40/40 Ratox
samples wholly inside the offline interval, same-identity empty-state recovery, and bounded cleanup
to empty. `client.ratox-terminal-progress` retains only the completed ordinal
and maximum completed round-trip time for diagnosing a failed capture.

The two-vCPU cell additionally pins the primary agent and probe to vCPU 0 and all auxiliary route
agents to vCPU 1. Its v5 observation binds that mapping, and every protected-route render must remain
below 250 ms. Cancellation uses one sequential control worker per route, with route workers in
parallel, so the test does not flood a single agent's local control socket. Each transfer receives
one bounded cancel attempt. A route that still reports live state is restarted from unchanged
savedata, must reconfirm over TCP, and must report an empty transfer set before readiness; schema v5
records the cleanup mode and restart count.

The accepted compact proof is `.sandwurm/exports/pairs/pair.0xk33kco`: 24/24 admitted, 8 purged on
route three, 16/16 unaffected and progressed, zero reassigned, 40/40 exact Ratox samples with p50
111.045 ms / p95 164.825 ms / max 232.356 ms, same-identity recovery, and one client bulk-worker
cleanup restart after 10 of 16 cancel controls succeeded. The total pair route-restart count is two
including recovery of the deliberately faulted device route.

Gate 2 now has an owned non-VM persistence and process boundary. Unit tests create real signed route
artifacts, checkpoint advances under the private advisory lock, and reject rollback,
same-generation forks, checkpoint tampering, weak permissions, hard links, symlinks, and a
replaceable non-private policy directory. Agent tests prove invalid configured policy fails before
toxcore creates savedata, valid policy reaches the
content-free local-control projection, and unconfigured startup returns exact single-route mode.
The binary process test exercises `iotox routes` and an initial `routes-watch` snapshot through the
real same-user control socket. These tests do not claim route workers exist or transcripts are bound.

The ADR 0167 auxiliary sync-frame construction test does use a real mock-backed route worker. It
progresses HELLO/CAPABILITIES, reciprocal stable-principal route binding, and state-sync negotiation,
then sends a canonical object result through the transport and receives the mock peer's reciprocal
packet. The one-record parent queue retains the first record with exact route key, worker ID,
friend/online epoch, remote generation, and principal, rejects the second without eviction, drains
once, and purges a later record on primary-trust withdrawal. A stale worker ID and every non-object
application type fail before send.

ADR 0168 adds the complete deterministic parent-dispatch gate. The Agent starts one protected primary
and two reciprocally authenticated bulk workers. It authorizes and requests HEAD only on the primary,
assigns two whole-object attempts to the first auxiliary incarnation, forces that worker offline, and
requires the final job to name the second exact carrier. The old route is fenced before fresh
attempt/message/FileId/staging identities are sent; both replacement objects verify, accepted HEAD
commits last, and local exact-token activation succeeds. Service-level cases additionally reject stale
old-route results and freeze carrier-scoped replay. This is process-local mock-provider evidence, not
the genuine Sandwurm Gate 3 qualification or a striping claim.

ADR 0169 adds that genuine Gate 3 cell as `sync-tree-route-loss`. Each role authors and loads a
stable-device-signed three-member inventory with one protected primary and two independently keyed,
one-friend bulk workers. The harness exchanges corresponding savedata identities before Agent
startup and requires both workers to reach reciprocal `ready`. On the subscriber only, the
default-off qualification seam stops the exact bulk route after at least 65,536 received bytes. The
proof requires one carrier loss, one fresh-carrier reassignment, at least one rejected stale terminal,
exact object/HEAD/activation convergence, one restart charged to the stopped member, a fresh worker
incarnation for the same savedata identity, and both bulk routes returned to `ready`. The publisher
must retain zero local loss counters.

After convergence the same guests activate the existing protected Ratox profile, emit 40 ordered
keypress-to-render samples, capture both process-resource intervals, and require every render below
250 ms. Direct UDP `pair.gqw1gzkd` and forced TCP `pair.9i62wfpa` pass raw and secret-free compact
verification. The verifier binds the distinct stopped/final carrier hashes and rejects altered
loss, reassignment, stale, recovery, Ratox, resource, route-class, or content truth. This qualifies
whole immutable-object reassignment and subsequent protected-route latency, not byte-prefix reuse,
simultaneous terminal sampling at the exact loss instant, or adaptive scheduling.

ADR 0170's Gate 4 prerequisite has a separate deterministic selector matrix. It compares utilization
as exact integer ratios across unequal signed budgets, refuses full and malformed candidates, isolates
remote principals and the excluded old incarnation, and freezes restart/key tie order. The mock-backed
two-worker Agent gate now selects in adaptive mode and requires live status to report exactly two
adaptive decisions—initial admission and post-fence replacement—with zero fixed decisions. This
proves wiring and conservative policy semantics only.

ADR 0171 adds the first genuine two-guest A/B as `sync-tree-route-balance`. The publisher signs four
namespaces over one deterministic 8,192-byte tree. In each policy phase, the subscriber starts job B
only after job A is post-HEAD, auxiliary, and holding positive work on an eight-slot route. Fixed must
name the same carrier; a clean same-state adaptive restart must name distinct carriers. The gate
requires two decisions per phase, exact two-object requested/admitted/committed truth for every job,
four exact activations, empty staging and route work, bounded recorded HEAD retries, two ready bulk
routes on both roles, and 40 subsequent protected Ratox samples. Fixed-first direct UDP
`pair.ul1pdq7m` and forced TCP `pair.pz9aapaj` pass raw and compact verification with zero retries.
Adaptive-first direct UDP `pair.hhmma27l` and forced TCP `pair.jn5aqbr6` pass the same exact gate and
binary. The verifier explicitly rejects an `awaiting-head` primary route key as an auxiliary
selection or an unknown phase-order marker. The small counterbalanced fixture qualifies load-aware
topology only; ADR 0176 separately qualifies both exact corresponding auxiliary readiness orders.
Performance, random startup/fault delays, startup under fault, fairness/resource attribution,
cancellation fairness under population, and relay diversity remain open.

ADR 0172 adds `sync-tree-route-cancel`. Because auxiliary workers own separate file-manager domains,
the pull snapshot retains its request-selected FileIds only inside the process and joins them to the
exact worker's active transfer truth. Local `sync-status` renders only aggregate receive count,
position, and total bytes. The gate waits for positive position on the selected auxiliary
route/worker, proves positive signed work, invokes ordinary `sync-cancel`, and polls without a fixed
settling sleep until the same job is cancelled, incoming/staging state is empty, signed work is zero,
no reassignment occurred, and both bulk routes remain ready. Neither accepted HEAD nor activation may
exist. Direct UDP `pair.fpkne1pg` observes 70 ms; forced TCP `pair.r_4luysy` observes 80 ms. Both then
pass 40 protected Ratox samples and replay from compact proof. This closes one bounded single-pull
cancellation-tail row, not concurrent-job fairness, cancellation during route loss, or a fleet SLA.

The forced-TCP `relay-restart` scenario adds a synchronized fault gate. It waits for both confirmed
sessions, terminates the fixture process group, requires both guests to observe session and peer
offline, and only then restarts the fixture from the same state. The evidence must record a preserved
relay key, and both receipts must record a strictly greater recovered online epoch, confirmed TCP,
and bidirectional post-recovery text. The verifier rejects route/scenario disagreement, a missing or
extra fixture restart, key replacement, one-sided fault observations, and stale or malformed epochs.
Earlier baseline manifests
remain verifiable by treating absent additive scenario fields as `baseline`.

The `daemon-restart` scenario leaves both guests and the relay running, stops the device IoTox daemon
through its local control surface, and waits for the stable client to observe both peer and
application-session offline before permitting restart. The new process must load the identical Tox
address from savedata and establish a fresh confirmed session; the stable client's online epoch must
strictly advance and new text must cross in both directions. The verifier also requires exactly one
device-daemon restart and zero relay restarts. A restarted process has a new process-local epoch
domain, so its recovered epoch must be positive but is not incorrectly compared with its predecessor.
This is not a Ratox PTY/controller replay-survival claim.

The `link-interruption` scenario applies `netem loss 100%` to both live task-owned TAP root qdiscs,
waits for bilateral peer and application-session offline observations, and then deletes both netem
qdiscs. The kernel restores the host default qdisc without changing TAP carrier state. Both guests
must recover the requested route at strictly higher epochs and exchange new text; the verifier
requires one link interruption and zero relay or daemon restarts. Direct TAP down/up was tested and
rejected because Cloud Hypervisor did not restore guest reachability after the host carrier returned.

The `guest-restart` scenario cleanly stops the device daemon, checkpoints restart metadata on the
writable guest disk, and requests a guest reboot. Cloud Hypervisor's failed virtiofs reconnect and
status-1 exit are retained as the bounded initial chain. A second Sandwurm chain consumes the exact
initial prelaunch receipt and therefore the same runtime-root disk, with a new VMM and virtiofs
backend. Verification requires both chains, distinct device boot-ID hashes, equal client boot-ID
hashes, unchanged device identity, client offline observation and epoch advancement, and fresh text.
The compact form has nine evidence files rather than the baseline seven.

## Retained evidence

After final source verification:

The old rev0043 retained-artifact refresh path has been retired from tracked source. It remains
documented here as historical context for the evidence chain, not as the current public packaging
surface. Current bulky build logs, prebuilt binaries, fuzz executables, and standalone attempts should
stay in ignored build/export locations or in a verified datacube. The tracked `artifacts/` directory is
now limited to small, source-referenced receipts such as the rev0045 route/privacy JSON files.

Current release-facing checks are:

```sh
tools/iotox-repo.sh release-check founder-preview --iotox /path/to/iotox
tools/iotox-repo.sh datacube --seed
tools/make-repository-datacube.sh --verify /path/to/IoTox-seed-repository-datacube.zip
```

Partial evidence must still be explicitly requested and labeled; absent lanes are never described as
green. Stable/no-concern release remains gated by `iotox ship-check all stable` and the stable
evidence manifest.

## Genuine upstream boundary

On a networked CLI:

```sh
./tools/build-standalone.sh
./tools/verify-standalone.sh
./tools/compare-standalone-builds.sh
./tools/run-real-peer-smoke.sh --prepare-keys
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh
IOTOX_REAL_PEER_TIMEOUT_SECONDS=240 ./tools/run-real-peer-smoke.sh --fresh-keys
```

Strict routed modes accept either the singular bootstrap/relay environment variables or
comma-separated plural `IOTOX_REAL_PEER_BOOTSTRAPS` and `IOTOX_REAL_PEER_TCP_RELAYS`; plural values
override singular ones. Fresh I2P requires at least three of each. Every map key must
preserve the exact real numeric Tox endpoint:

```sh
IOTOX_BINARY=/nix/store/.../bin/iotox \
IOTOX_REAL_PEER_TIMEOUT_SECONDS=1200 \
IOTOX_REAL_PEER_NETWORK=tox/i2p \
IOTOX_REAL_PEER_SOCKS5_PROXY=127.0.0.1:39056 \
IOTOX_REAL_PEER_BOOTSTRAPS=IP1:PORT1:KEY1,IP2:PORT2:KEY2,IP3:PORT3:KEY3 \
IOTOX_REAL_PEER_TCP_RELAYS=IP1:PORT1:KEY1,IP2:PORT2:KEY2,IP3:PORT3:KEY3 \
./tools/run-real-peer-smoke.sh --fresh-keys
```

This command assumes the separately managed three-map client adapter and three persistent service
fronts already exist. It neither creates routers nor treats public node records as defaults.

The build emits `dist/standalone/iotox.spdx.json`. Its deterministic SPDX 2.3 document binds the
exact executable plus every locked source/data component; the verifier rejects executable, lock,
package-set, or relationship drift. The comparator uses two empty temporary CMake roots, verifies
both distributions, compares their release surfaces byte for byte, and deletes both roots. Set
`IOTOX_REPRO_BASELINE_DIR` to reuse an already verified distribution for the first side, as CI does.
The standalone builder chooses Ninja when present and falls back to Unix
Makefiles on smaller hosts. Release operators may set `IOTOX_CMAKE_GENERATOR`
to pin the generator explicitly; if a stale default CMake cache was created
with another generator, the script moves to a generator-specific build root
instead of asking the operator to clean manually. It still requires a C and C++
compiler in `PATH`, or explicit `CC` and `CXX`; on Nix hosts the project dev
shell provides those compilers. `IOTOX_STATIC_CXX_RUNTIME=1` asks the host
toolchain to link libstdc++/libgcc statically; `build-info.txt` records the
static-runtime choice and effective extra link flags.
The reported scope is intentionally same-host/same-toolchain; image runtime closure and independent
builders remain distinct evidence. The founding-host two-empty-root pass is retained in
`evidence/2026-08-24-reproducible-standalone.md`.

The full Nix flake additionally builds `toxcore-provider-upgrade`. This qualification-only check
constructs warnings-as-errors fixtures from exact c-toxcore 0.2.22 and current 0.2.23 sources. Two
disposable old-provider profiles carry distinct identities, profile bytes, and mutual friendship;
the current fixture and the real source-linked IoTox product must load and rewrite both without
semantic drift, the old fixture must read the rewritten state, and both fixtures must reject
malformed savedata. The derivation output excludes random keys/state and is byte-reproducible:

```sh
nix build .#toxcoreProviderUpgrade
cat result/provider-upgrade.json
nix build --rebuild --no-link .#toxcoreProviderUpgrade
```

The product remains statically pinned to 0.2.23. Backward-readable savedata does not permit an
automatic downgrade. The separately retained two-guest live route matrix closes the current local
rolling boundary without changing that rule (ADRs 0152 and 0153).

The first lifecycle command defaults to an immutable, private, test-only Tox/device key baseline.
It copies those keys into a new work directory and starts with fresh ledgers, command stores,
runtimes, friendship, and application history. This makes stable-peer testing the ordinary loop
without allowing one run's revocations or epoch changes to contaminate the next. The cache is
provider-version-namespaced, owner-only, serialized across the full run, ignored by Git, and never
packaged. `IOTOX_REAL_PEER_KEY_CACHE` selects a different dedicated test cache; it must never name a
live or customer profile.

The second lifecycle command is the required from-scratch complement. `--fresh-keys` (equivalent to
`IOTOX_REAL_PEER_KEYS=fresh`) generates both Tox and stable device identities in the disposable run
directory. Focused identity creation, persistence, mismatch, and tamper tests also remain isolated
and fresh. Mock-provider transport keys and cryptographic vectors remain deterministic fixtures;
they do not consume the genuine-peer cache. See ADR 0056 and the redacted founding-host evidence in
`docs/evidence/2026-08-15-reusable-and-fresh-test-identities.md`.

Only official pinned source and two genuine peers can establish provider compatibility, real address
validation, bootstrap, request delivery, remote acceptance, NAT/relay/reconnect behavior, and real
text/file/custom-packet callbacks.

### Strict Tox/Tor construction, two-guest SOCKS, and operator-Tor gates

Rev0045 adds two distinct layers. The owned registry verifies strict numeric proxy syntax, complete
route validation, exact mock c-toxcore options, default-catalog suppression, and incomplete-I2P
failure. `iotox.socks5-forwarder` separately proves that the bounded lab boundary forwards only one
allowlisted numeric target and rejects both another numeric target and SOCKS domain-address form.

The genuine-provider layer is repeatable:

```sh
python3 tools/run-tox-tor-smoke.py
```

It realizes the source-linked IoTox and pinned c-toxcore bootstrap fixture, configures one explicit
numeric SOCKS endpoint plus numeric bootstrap/relay record, waits for `Tox/Tor` and TCP, and joins
Linux `/proc` socket ownership to the exact IoTox PID. The accepted state has a TCP stream only to
SOCKS, no IoTox UDP socket, and no IoTox direct relay socket. The gate kills SOCKS, observes
`offline`, rechecks no bypass, restarts the same endpoint, and requires TCP recovery plus a second
allowlisted forward. The gate refuses a dirty source tree. Its JSON receipt binds the exact source
commit, both binaries, and both route tools and labels its scope
`source-linked-local-construction-not-actual-tor`.

The accepted rev0045 receipt is `artifacts/rev0045/tox-tor-smoke.json`, documented in
`docs/evidence/2026-08-27-source-linked-tox-tor-route.md`. It measured 8,038 ms to initial TCP,
77,993 ms from proxy loss to c-toxcore `offline`, and 4,921 ms from exact-endpoint restart to TCP.
The slow loss callback is a finding, not a hidden timeout adjustment: future route health and
application liveness must be separate from the provider's authoritative connection state.

ADR 0192 supplies that first observational seam. The owned network test connects to a real loopback
listener and then observes refusal after its closure. The Agent gate samples native carrier state,
performs a confirmed lossless peer echo, and requires the complete session record before and after
to remain byte-identical. `iotox.binary-process-lifecycle` invokes both on-demand forms and a finite
100 ms watch. Strict parser tests reject field-order, numeric-canonicality, RTT, boundary, upstream,
and application/error incoherence. ADR 0193's independent latches cross two-success healthy,
first-failure suspect, three-failure unavailable, and two-success recovery boundaries without a
session effect. These tests do not promote a listener result to SOCKS target, circuit, or upstream
success.

Ratox client coverage completes 2,048 exact heartbeat cycles with one stable PING message ID and no
replay/message-ID growth. A real Agent/controller test crosses the local terminal protocol, signed
authority, transcript-confirmed remote Ratox OPEN, PING/PONG, authoritative route loss, exact
generation-two RESUME, another PING/PONG, and explicit DETACH. The terminal-controller process gate
requires a live client PING and separately withholds PONG across the three-miss warning, proving that
the CLI retains the session until the fixture sends an authoritative result. This remains one-host
deterministic construction evidence, not impaired-route, PTY-progress, or automatic-recovery proof.

ADR 0194 adds `iotox.route-target-process`. A real installed CLI calls a mock-backed Tox/Tor Agent
through the local control socket while the strict numeric-only SOCKS fixture fronts one allowlisted
TCP listener. Ordered samples prove complete reply-0 target reachability, reply-5 refusal after that
target stops, and local proxy refusal after SOCKS stops; the mock carrier remains TCP throughout.
The proxy audit contains exactly one admitted and one failed-connect record for the sole configured
target. The direct parser rejects endpoint-bearing or stage/result-incoherent reports, and the native
whole-binary lifecycle rejects target probing as unsupported. This is local configured-target
evidence, not an authenticated Tor-circuit or public-relay sample.

The opt-in operator-Tor runner closes that separate public sample. Around each initial and
recovered one-shot target command it authenticates the Tor control cookie, enables extended STREAM
events, snapshots preexisting Agent-to-SOCKS source ports, and requires exactly one NEW source whose
same stream ID later succeeds to configured relay zero. The resulting stream must name a built
three-hop `GENERAL` or `CONFLUX_LINKED` application circuit. The independent verifier freezes both
successful observations/circuits plus the intervening proxy-refusal state. The accepted clean-source
gate binds four real-route states: initial `tcp/reachable`, post-exit `tcp/refused` after 35 ms,
authoritative `offline/refused/blocked-by-local-boundary` after 74.602 seconds, and recovered
`tcp/reachable` after restart. It also binds initial/recovered target CONNECTs to distinct three-hop
linked-Conflux circuits. The verifier requires the fast local observation to precede provider
offline while preserving both labels (ADR 0195).

The separate two-guest gate is:

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor proxy-restart
```

Accepted compact proof `pair.zyy913jf` binds two source-linked guests, a confirmed session, proxy
loss, online-epoch advancement, exact-endpoint recovery, and fresh post-recovery text. Independent
TAP captures contain 474 client and 439 device IPv4 egress packets; every packet is TCP to the
proxy, with zero UDP, direct-bootstrap, or direct-peer packets. Both proxy incarnations admit one
route per guest to the sole target and deny zero. See
`docs/evidence/2026-08-27-sandwurm-tox-tor-route.md`.

This is `network-verified` generic-SOCKS route-policy evidence, not actual-Tor evidence. The
forwarder is not Tor; neither generic gate proves circuits, anonymity, or public relay reachability.

The terminal-specific bounded-impairment matrix is separately repeatable:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-impairment
```

Every cell opens one real authority-bound Ratox PTY and records 20 baseline, 80 impaired, and 20
recovered observations. Each observation performs one frozen PING/PONG before one input-byte/output-
byte cycle, retaining independent captures so heartbeat and terminal progress cannot be conflated.
The middle phase applies independent seeded `75ms 15ms loss 2%` qdiscs to both guest TAP egress
paths; exact qdisc activity and positive drops are acceptance requirements. The terminal session ID,
input/output sequences, authenticated route, source revision, and binary must remain exact.

After the ordinary pair verifier accepts and `export-sandwurm-pair.py` produces independently
reverified compact roots, the measurement analyzer checks all three cells together:

```sh
python3 tools/analyze-ratox-route-impairment.py \
  .sandwurm/exports/pairs/pair.tscy1yrt \
  .sandwurm/exports/pairs/pair.gf5mxexc \
  .sandwurm/exports/pairs/pair.p3dt6g9c
```

The accepted cells complete all 360 heartbeat and 360 PTY observations without detach, resume,
migration, or session-identity change. Direct UDP records a 176.650 ms impaired terminal median and
one 2.158-second maximum; forced TCP records 289.133/666.877 ms; strict SOCKS records
277.522/619.354 ms. Internal impaired local-render and interactive-queue maxima are respectively
6.199/0.150 ms, 0.629/0.255 ms, and 0.771/0.200 ms. ADR 0196 therefore keeps partial impairment
warning-only; ADR 0197's separately named gate below owns total-loss mutation policy. The strict
SOCKS cell retains zero-bypass packet evidence but is not actual Tor. See
`docs/evidence/2026-08-27-sandwurm-ratox-route-impairment.md`.

The corresponding total-loss matrix is separately repeatable:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-loss
```

Each cell opens one exact PTY and completes heartbeat plus byte `A`, installs seeded 100% loss on
both TAP egress paths, and releases a two-second heartbeat probe. Acceptance requires the heartbeat
to miss while route/session truth remains confirmed at the same epoch, followed by authoritative
offline and a typed local `unavailable` outcome. While loss is still active, the device must expose
one live/running, zero-attached PTY and a `peer-detached` journal event naming the captured session.
After qdisc removal, only a higher authenticated epoch permits `resume_only`; session ID,
incarnation, and byte positions remain exact, generation advances one-to-two, and a new heartbeat
plus byte `B` must complete.

Verify each raw and compact root with the ordinary pair verifier, then join the three cells:

```sh
python3 tools/analyze-ratox-route-loss.py \
  .sandwurm/exports/pairs/pair.0cnril1l \
  .sandwurm/exports/pairs/pair.qoty7j1x \
  .sandwurm/exports/pairs/pair.8jjawnwp
```

The accepted direct-UDP, forced-TCP, and strict-SOCKS cells warn at 2.187/2.248/2.139 seconds and
reach authoritative offline at 30.683/30.322/31.145 seconds. Route restoration reaches a fresh
authenticated epoch in 0.769/2.155/4.996 seconds; resumed OPENED follows in
21.123/48.940/28.034 milliseconds. The strict-SOCKS proof retains 1,649 TCP-only proxy-destination
egress packets with zero UDP/direct traffic. ADR 0197 closes the native/strict-SOCKS policy gate:
heartbeat loss warns, authoritative offline detaches while preserving the host PTY, and explicit
higher-epoch exact-session resume is the only qualified mutation. Automatic migration and actual
Tor remain unqualified. See `docs/evidence/2026-08-27-sandwurm-ratox-route-loss.md`.

Actual Tor is a separate opt-in public-network gate:

```sh
python3 tools/run-tox-operator-tor-smoke.py \
  --node IP:TCP_PORT:64_HEX_PUBLIC_KEY \
  --output operator-tor-receipt.json
python3 tools/verify-tox-operator-tor-smoke.py \
  operator-tor-receipt.json \
  --runner tools/run-tox-operator-tor-smoke.py
```

It refuses dirty source, realizes source-linked IoTox, binds the exact Tor binary/version/digest and
normalized loopback configuration, and requires the explicit public relay stream to be `SUCCEEDED`
on a built three-hop `GENERAL` or `CONFLUX_LINKED` application circuit. `/proc` ownership
independently requires IoTox TCP remotes
to be only loopback Tor SOCKS and no IoTox UDP socket, while the Tor PID must own public TCP. The
gate kills Tor, waits for authoritative offline, samples the held outage for bypass, restarts the
same endpoint, and requires a distinct qualifying circuit.

The accepted receipt is `artifacts/rev0045/tox-operator-tor-smoke.json`, documented in
`docs/evidence/2026-08-27-operator-tor-public-route.md`. Tor 0.4.8.11 reached initial Tox TCP in
9,120 ms. Auxiliary local refusal appeared in 35 ms while the carrier still reported TCP; loss
became authoritative offline in 74,602 ms; 30 no-bypass samples covered a 30,290 ms hold; recovery
took 3,913 ms. Initial and recovered configured-target streams each used a distinct three-hop
`CONFLUX_LINKED` circuit. This is a
bounded `operator-route-verified` qualifier, not a new evidence-vocabulary maturity tier: it does
not replace the two-peer requirement of `network-verified`, and it proves no anonymity or SLA.

## Content-v2 auxiliary-carrier construction gate

ADR 0258 moves only content negotiation and bytes onto route workers. The owned registry must prove
all of the following before a Sandwurm claim is attempted:

- the primary HEAD request still names the primary authority carrier;
- two complementary, independently authorized sources bind to two distinct auxiliary incarnations
  before HEAD and both answer exact sparse availability plus contribute verified objects;
- wrong-principal binding and every post-HEAD carrier change are refused;
- FileId offers and terminals use the selected carrier friend/epoch rather than the authority friend;
- exact auxiliary loss fails the job while an unrelated incarnation has no effect; and
- a route worker accepts a canonical content availability result only after bit 29 is separately
  constructed and negotiated, while HEAD remains forbidden.

Run the pinned gate with:

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug -j2
nix develop --no-write-lock-file --command \
  ctest --test-dir build/gcc-debug \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

The 670-check owned registry passes this construction. The first genuine mixed-route gate is:

```sh
python3 tools/run-sandwurm-pair.py direct-udp \
  sync-content-route-private-actual-tor \
  --tor-node IP:TCP_PORT:64_HEX_PUBLIC_KEY
```

Accepted compact proof `.sandwurm/exports/pairs/pair.fahovlrg` keeps direct-native authority/HEAD
truth separate from the exact `tox/tor` byte carrier. Two actual Tor 0.4.8.11 processes and two
source-linked guests move and activate the paged 4 MiB revision in one pull with zero failure or
reassignment. Strict replay retains both TAP captures, Tor control/circuit observations, the exact
content completion record, and the two role receipts. The raw root allocated 2.4 GiB; the
secret-free compact root allocates 14,671,872 bytes. See
`evidence/2026-08-30-sandwurm-sync-content-actual-tor.md`.

The gate first found a construction-order error: workers froze bit 29 false before the parent
content services existed. Agent now finalizes that gate after service construction and before worker
start; the supervisor rejects post-start mutation. Multi-source routed convergence and selected-
worker loss now have separate accepted gates. I2P content-v2 remains open. A TCP worker still does
not make the HEAD session TCP.

## Same-source content-lane gate

ADR 0262 adds one deterministic scheduler test and one dedicated source-linked VM scenario. The
owned test publishes a real paged fabric under a two-lane process and namespace cap. It requires the
first post-discovery wave to contain two requests to one source with distinct request IDs and
FileIds, completes lane 1 before lane 0, observes one-slot refill while two lanes remain live, and
converges with HEAD accepted last. A second job fails one live lane and requires sibling transfer
cancellation, whole-job failure, zero active lanes, and no durable active attempt.

Run the genuine pair cells with:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-same-source-lanes

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.895m5lwy \
  sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.bcecui0l \
  sync-content-same-source-lanes
```

The VM runner shapes the 4 MiB transfer, then accepts only a live client snapshot containing
`content-lane-cap=2`, `active-lanes=2`, two admitted `content-lane-job=` rows, one source, distinct
requests and FileIds, and no root lane. Both independently reverified compact proofs contain nine
files and allocate 163,840 bytes. This qualifies two-object overlap and exact attribution on one
Tox session in each carrier mode. It does not qualify byte striping, physical-path diversity, a
performance improvement, or multi-lane daemon-restart recovery. Exact receipts and hashes are in
`evidence/2026-08-30-sandwurm-sync-content-same-source-lanes.md`.

## Same-source exact-carrier content gate

ADR 0269 adds the complementary multi-route test without raising the lane cap. The deterministic
subscriber fixture publishes one paged revision, splits chunk availability across two auxiliary
contexts that share one principal and primary authority tuple, and requires both availability and
object contribution before accepting the original HEAD. Both transfer contexts deliberately reuse
the same route-local friend number; route key and worker incarnation keep them distinct. An exact
selected-carrier loss fails the job, while a lookalike worker loss is ignored.

The genuine actual-Tor cell and independent replay are:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-same-source-multi-route-actual-tor \
  205.185.115.131:33445:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.iiuhmhy0 \
  sync-content-same-source-multi-route-actual-tor
```

The strict verifier accepts the 21-file, 14,811,136-byte compact proof. It requires one principal
and primary authority session; distinct source IDs, route keys, and worker IDs; equal-or-different
route-local friend numbers; positive per-path commits/bytes; all availability results; exact Tor
payload attribution; and zero unexpected-context TAP packets. Observed path contributions are one
272-byte object and five objects totaling 4,194,560 bytes. The test proves whole-object logical
distribution, not byte striping, balancing, speedup, independent circuits/links, or automatic
policy. Exact bindings and development loss observations are in
`evidence/2026-08-31-sandwurm-sync-content-same-source-multi-route.md`.

## Content lane-count science gate

ADR 0263 turns the scheduler qualification into a neutral measurement without process or session
churn. One stable subscriber runs with process ceiling 8. Four isolated content-v2 namespaces sign
effective lane/outstanding-request ceilings `1`, `2`, `4`, and `8`; each publishes the same
deterministic high-entropy 8 MiB, 24-chunk, 26-object graph. Subscriber ingress remains shaped to
4 Mbit/s. Every cell must expose a coherent nonzero live-lane set no larger than its signed cap,
converge, explicitly activate, and seal a fresh process-resource interval.

Run and independently replay both carrier cells:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.amcrp0_3 \
  sync-content-lane-science
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.805kzu4a \
  sync-content-lane-science
```

The standalone verifier recomputes per-cell bytes/second from artifact bytes and duration, checks
the observed maximum against each cap, joins all four resource digests to the client receipt, and
requires zero phase restarts plus four exact activations. The accepted forced-TCP rates are
301,423/375,833/420,481/415,072 B/s, identifying cap 4 as an observed knee. Direct UDP is
non-monotonic at 378,035/325,771/399,838/443,138 B/s. Default one remains frozen; one ordered sample
does not qualify automatic tuning, variance, or interactive latency. Exact receipts and nonclaims
are in `evidence/2026-08-30-sandwurm-sync-content-lane-science.md`.

## Counterbalanced content lane-count gate

ADR 0266 adds the true reverse order. The ascending base namespace is signed at cap 1; the reverse
base namespace is signed at cap 8. Both keep one cap-8 process/session and publish exactly three
isolated counterphase roots:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-lane-science-reverse
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-lane-science-reverse

python3 tools/analyze-content-lane-counterbalance.py \
  .sandwurm/exports/pairs/pair.t6b6exf1 \
  .sandwurm/exports/pairs/pair.ku2fxml0 \
  .sandwurm/exports/pairs/pair.70p2plez \
  .sandwurm/exports/pairs/pair.o_6q_m1n \
  --verify-report artifacts/rev0045/content-lane-counterbalance.json
```

The analyzer invokes strict pair verification first, requires equal ascending/descending counts per
carrier, one binary/artifact identity, reused-key continuity, no restarts, and content-free compact
exports. It retains each observation plus exact sum/denominator distributions. The current paired
means identify cap 8 as UDP's raw winner by only 0.81% over cap 4, and cap 2 as TCP's winner by 4.56%
over cap 4. Across routes cap 4 and cap 2 differ by 0.013%; cap 2 uses 14.8% fewer CPU ticks. Default
one remains. Exact receipts, rejected setup-only failure, report hash, recommendations, and nonclaims
are in `evidence/2026-08-31-sandwurm-sync-content-lane-counterbalance.md`.

## Multi-lane content client-restart gate

ADR 0267 qualifies unclean subscriber-Agent restart while two or four immutable-object lanes are
live. Every cell publishes the same deterministic high-entropy 8 MiB/24-chunk graph, reaches the
exact signed/process cap with distinct request IDs and FileIds, observes positive bytes in each live
c-toxcore transport temporary, and sends `SIGKILL` only to the client Agent. The publisher, both
microVMs, and the reusable identities remain live.

Run and independently replay all four native-carrier cells:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-restart-cap-4

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.8j7v2irm \
  sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.9q9hsx40 \
  sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.8ulddb9t \
  sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.ol5goyug \
  sync-content-restart-cap-4
```

Startup must preserve the exact complete CAS inventory and remove every exact private toxcore
pre-rename temporary while leaving zero canonical CTA1 partials, zero accepted HEAD, and zero
activation. The old signed attempt set remains fenced. The harness then waits for independently
observed application recovery on both roles before releasing a two-sided authority barrier; only a
fresh, distinct pull may converge and activate. That barrier is security-relevant: Tox friendship
and a client-side verified publisher do not prove that the publisher has consumed the client's
reciprocal authority proof.

The product cleanup accepts only
`objects/HH/.iotox-REST.REQUEST_ID.part.part-XXXXXX` with canonical lowercase digest/shard,
canonical nonzero decimal request ID, six base62 suffix bytes, private ownership/mode, one link,
same filesystem, and bounded inventory. Anything malformed or unsafe fails startup closed. These
transport files are neither canonical CTA1 staging nor resumable truth. Complete-object reuse is
qualified; partial-prefix resume, transparent same-job continuation, power-cut behavior, I2P, byte
striping, and an interactive Ratox SLA are not qualified *by the restart gate*. Exact restart
receipts and hashes are in `evidence/2026-08-31-sandwurm-sync-content-restart.md`; ADR 0268 closes
the separate persistent cap-two SLA below.

## Persistent Ratox under content-lane load

ADR 0264 adds the competing interactive measurement without making fresh session admission part of
every cell. One 720-sample Ratox attachment stays live across content caps 1, 4, and 8, pauses after
samples 240 and 480, and retains one exact terminal identity and Tox online epoch. Cap 2 runs as a
transfer-only control during the first pause. Each measured phase begins after its first terminal
echo and must contain at least 20 samples whose input timestamps lie inside the exact content
interval.

Run and independently replay both carrier cells:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-latency-science
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-latency-science

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.af873531 \
  sync-content-ratox-latency-science
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.a3nglkh3 \
  sync-content-ratox-latency-science
```

The verifier recomputes all latency percentiles from the retained 720-row timeline, checks one
session commitment and capture digest across all phases, joins exact content interval/rate/lane
truth, requires the stable carrier and epoch, and enforces Ratox-active resource transitions
`0->1`, `1->1`, `1->1`, `1->0` over caps 1/2/4/8. Default one remains frozen. Exact results,
bindings, rejected harness attempts, and nonclaims are in
`evidence/2026-08-30-sandwurm-sync-content-ratox-latency.md`.

## Cap-two interactive-bulk construction SLA

ADR 0268 adds the missing cap-two measurement without changing Ratox, content-v2, CTA1, FileId, or
local-control framing. The pass/fail rule was frozen before either VM ran: at least 40 terminal
samples whose input timestamps lie inside the exact content interval; p50/p95/p99/max no greater
than 250/500/1,000/1,500 ms; and owner-queue p95 no greater than 10 ms. No carrier-specific
relaxation is allowed.

`sync-content-ratox-cap-2-sla` holds one 960-sample raw-echo attachment and one authenticated Tox
epoch across ordered caps `1/2/4/8`, with 240 rows per phase and the same 4 Mbit/s subscriber
shaping. Every content phase must start after a completed terminal sample, genuinely overlap the
timeline, converge, explicitly activate, and preserve resource transitions `0->1`, `1->1`, `1->1`,
`1->0`.

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-cap-2-sla

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.rpblreul \
  sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rwiyixfh \
  sync-content-ratox-cap-2-sla
```

Cap two passes every frozen bound: direct UDP has 83 overlap rows, p50/p95/p99/max
83.680/479.100/876.158/876.158 ms, and queue p95 0.298 ms; forced TCP has 68 rows,
199.264/401.813/531.662/531.662 ms, and queue p95 0.083 ms. It improves content rate over cap one
by 2.75% and 9.92%. Cap four adds only 1.11%/2.86% over cap two while missing the p95 ceiling on
both carriers; cap eight misses too.

Keep default one. Explicit cap two is the bounded native interactive-bulk construction profile only
under the tested conditions; selection is manual. This does not promise an Internet, physical-host,
unshaped/faster-link, routed-privacy, multiple-terminal, fresh-admission, or long-duration SLA. The
guest and standalone verifier enforce the same constants independently. Exact bindings and
nonclaims are in `evidence/2026-08-31-sandwurm-sync-content-ratox-cap-2-sla.md`.

## Fresh Ratox admission after content backlog

ADR 0265 keeps fresh OPEN separate from persistent attachment survival. The
`sync-content-ratox-post-bulk-admission` scenario proves authenticated readiness before cap 8, then
performs no more session polling between reliable content completion and a new controller OPEN. The
probe must send OPEN within one second, receive OPENED within the ordinary five-second deadline on
the unchanged carrier/epoch, start fresh generation/input/output positions at one, and complete 40
exact samples.

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-ratox-post-bulk-admission
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-ratox-post-bulk-admission

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.614f4nje \
  sync-content-ratox-post-bulk-admission
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.oengulmm \
  sync-content-ratox-post-bulk-admission
```

The standalone verifier reconstructs all monotonic intervals, carrier/epoch joins, terminal identity
and byte positions, 40-row sequencing, session commitment, capture digest, and receipt digests. Exact
results and nonclaims are in
`evidence/2026-08-30-sandwurm-sync-content-ratox-post-bulk-admission.md`.

## Evidence vocabulary

```text
specified              prose or frozen bytes define intended behavior
compiled               one toolchain built the owned path
unit-verified          in-process deterministic checks passed
process-verified       separate iotox process and local OS boundary passed
adapter-verified       exact consumed provider ABI double passed
source-linked          official pinned provider headers/sources compiled and linked
network-verified       two genuine peers crossed the stated route and lifecycle
target-verified        representative hardware/network/power behavior measured
production             security, operations, update, and support obligations satisfied
```

The current repository is unit-, process-, adapter-, and source-linked-verified on the founding
bare-metal host. Retained redacted reports also make Tox/native network-verified for the named
c-toxcore version and founding-host normal-native and TCP-only fixtures. This remains a qualified
claim, not evidence for every provider, route, NAT, or packet-loss condition. Tox/Tor now has strict
source-linked local construction, two-guest generic-SOCKS network evidence, and one separately
bounded actual-Tor public-relay route sample plus eight qualified two-IoTox actual-Tor samples. The
second binds the complete signed-tree job to the exact Tor auxiliary with zero reassignment; the
third binds external Tor-process loss to one native reassignment and actual carrier return without
an IoTox route-worker restart; the fourth binds primary Tor-process loss to detached-PTY retention
and explicit exact-session resume without an IoTox daemon restart; the fifth binds one continuous
120-sample terminal to exact client/device circuit churn and both lawful continuity/resume outcomes.
The sixth repeats that unchanged gate through a distinct public Tox record and observes two Tor
stream reopenings with application continuity. The seventh holds established client bytes behind a
reachable listener and successful target CONNECT, then proves warning-before-offline, detached PTY,
and exact resume without process restart. ADRs 0207/0208/0209 accept raw- and compact-verified
proofs. ADR 0243 adds the eighth proof in a later operator window against the third public record;
its two stream reopenings again exercise both lawful application outcomes. Independently witnessed
time and reviewed exit-operator populations remain open.
The content-v2 corpus now adds three bounded actual-Tor carrier results. `pair.fahovlrg` binds one
native-authority source to one exact Tor worker. `pair.j0z04_2i` binds two independently authorized
native publishers to two distinct Tor worker identities, requires complementary five-plus-one object
contribution in one atomic pull, accepts HEAD last, activates explicitly, and reports zero unexpected
context packets in both TAP captures. The strict compact export is 14,680,064 allocated bytes and
passes the independent verifier. The two device-side workers share one Tor process and one public
Tox target, so this is not per-source circuit diversity, physical-path diversity, anonymity, or a
performance result. Reproduce it with the command in
`evidence/2026-08-30-sandwurm-sync-content-multi-route-actual-tor.md`.
`pair.w31xqgd_` then stops the selected second worker at 72,663 bytes after two committed objects,
requires whole-job failure with empty staging/no HEAD/no activation, records one loss and zero
reassignment, recovers the same signed route under a different incarnation with both native epochs
unchanged, and converges only through a distinct explicit pull. Its 15,958,016-byte compact export
passes the independent verifier; reproduce it from
`evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss.md`.
`pair.i8ar90tx` repeats that same destructive contract through the distinct compiled public relay
record `205.185.115.131:443`. It stops the selected worker at 76,776 bytes, records the same two
committed objects/528 fetched bytes, preserves zero reassignment and native epochs `1/1`, recovers a
fresh exact worker, and converges only through a new job. Both raw and 15,286,272-byte compact roots
pass the strict verifier after its first rejection exposed and corrected one host-derived
head-fenced count; both guest receipts and the product binary remained unchanged. This is relay-
record repetition, not exit/time/physical-path or long-running qualification; reproduce it from
`evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss-second-relay.md`.
Tox/I2P is VM-qualified only for the pinned two-router/front construction retained under ADR 0253;
it is neither a default route nor anonymity, Internet-population, or fleet evidence.

ADR 0210 makes the retained actual-Tor path population reproducible instead of anecdotal. The
analyzer first re-runs the strict compact verifier over all eight proofs, resolves only exact-target
role/phase or before/after churn path declarations, and matches each raw path digest and purpose.
It reports 30 declarations, 24 distinct normalized three-hop paths, 20 first hops, 23 last hops,
and no complete-path or last-hop reuse across proofs. Relay fingerprints do not enter the report.
The 23 last-hop identities are observed population diversity, not reviewed independent exits;
separated time windows and anonymity remain explicitly false/unclaimed. Reproduce the accepted
18,761-byte report with the command in
`evidence/2026-08-28-actual-tor-path-population.md`.

## M5C everyday-sync and tree-v2 construction gate

ADRs 0270--0283 add everyday automation, owner create/share, the bounded tree-v2 path, recoverable
history maintenance, selective projection, finite adversarial/scale qualification, and the accepted
two-hour shadow. The default CTest surface has 54 targets, including synthetic negative/positive
tests of the dedicated three-writer and sync-shadow Sandwurm verifiers and bounded compact exporters.
Run the complete direct gate with:

```bash
nix develop -c cmake --build --preset gcc-debug --target iotox_tests iotox --parallel 8
nix develop -c ctest --preset gcc-debug \
  -R '^iotox\.unit-and-integration$' --output-on-failure
```

That M5C registry slice proves signed automation codec/store behavior, tamper and unsafe-input
refusal, deterministic scheduler/backoff/stale-generation behavior, local-control v1.48 stability,
malformed command refusal, private deterministic managed roots, and a live `sync-create` publisher
advancing before and after Agent restart. It also proves an empty owner-private synchronization root
is securely prepared on first startup while an unsafe pre-existing store is refused.
A second live path captures an exact-v3-proven publisher as a stable principal, automatically pulls
and accepts one paged CAS revision, and exact-token activates it under `verified`. The complete
follow path also prepares, RecallRoot-signs, commits, and reload-verifies one exact-principal
read-only share.

Run the unattended one-writer two-guest gate on both native carrier classes with:

```bash
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-automation
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-automation
./tools/iotox-sandwurm-lab.sh verify-pair ROUTE PROOF_ROOT sync-automation
./tools/iotox-sandwurm-lab.sh export-pair PROOF_ROOT
```

The publisher uses `sync-create` plus RecallRoot-bound read-only sharing; the replica installs its
own tree policy and exact-principal `sync-follow ... verified` record. After that setup, the harness
restarts the publisher and replica Agents independently and permits only source mutations. Three
exact generations must materialize on both routes with signed automation reload and zero manual
publish, pull, or activate command. Accepted compact proofs are `pair.7vk1u4wn` (direct UDP) and
`pair.s67dd_2e` (forced TCP); see
`evidence/2026-09-01-sandwurm-sync-automation.md`.

Tree-v2 tests freeze manifest/branch/workspace/wire bytes, causal dominance, fork and invented-proof
refusal, tombstones, deterministic conflict projection, atomic exchange recovery, authenticated
publisher replay, recursive object closure, repeated job pruning, failed-lane cleanup, and canonical
crash-part cleanup. A live mock Agent creates a writable namespace, commits the reciprocal
read-write share transaction, and reloads pair-bound automation. The service bridge exchanges more
than the receiver job bound, performs sequential writes both directions, constructs unequal offline
edits, preserves the losing value by origin, resolves with a later edit, and propagates deletion plus
a zero-byte file.

Run the dedicated two-guest gate with:

```bash
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-bidirectional
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT \
  sync-bidirectional
```

Both guests independently create and share the namespace, establish two signed branches, stop their
daemons after a Tox barrier, make concurrent unequal edits, restart, require identical canonical
projection and retained conflict content, resolve causally, propagate a deletion and empty object,
and finish with `sync-repair`. No manual publish or pull is permitted after setup. The accepted
direct-UDP result is retained as compact proof `pair.ms5zsk9l`; reproduce and inspect its exact
bindings through `evidence/2026-08-31-sandwurm-sync-bidirectional.md`.

The three-writer gate uses one networkless Sandwurm guest as a deterministic test cell containing a
private loopback c-toxcore bootstrap plus three source-linked IoTox daemons. Run it with:

```bash
./tools/iotox-sandwurm-lab.sh up-three-writer
./tools/iotox-sandwurm-lab.sh export-three-writer PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-three-writer PROOF_ROOT
```

The near-ceiling scale comparison uses the same wrapper with explicit profiles:

```bash
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-1
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-4
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-8
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-16
```

The harness defaults to `.cache/sync-three-writer/state` and reuses its device/Tox/authority keys on
ordinary developer runs. `--fresh-state` is the explicit from-scratch mode used inside the ephemeral
VM. Acceptance requires three distinct committed Tox identities and stable principals, all three
friendship edges, six directional read-write shares, three branches at every node, exactly two
conflict alternatives at every node after concurrent offline edits, a common explicit resolution,
automation-v2 records, and at least two scheduler attempts per node. The receipt contains only
hashes and counts. See `evidence/2026-08-31-sandwurm-sync-three-writer.md`.
`tools/run-sync-three-writer.py --max-sync-tree-lanes N` selects the Agent process cap for tree-v2
exact-object lanes. `--namespace-maximum-lanes N` changes the generated namespace quota for fresh or
empty science roots only; the effective lane cap is the lower of the two and is recorded as
`tree_lane_cap`, with `tree_lane_process_cap` and `tree_lane_namespace_cap` retained separately.
The default Sandwurm guest asserts `4`. The near-ceiling comparison retains the rejected cap-1
timeout boundary, the accepted cap-4/cap-8/cap-16 compact proofs, and compact cap-32/cap-64
rejections side by side. Cap 1 has no accepted receipt because it timed out before guest evidence;
cap 4 passed as `.sandwurm/exports/three-writer/run.f3q2rjxM`; cap 8 passed as
`.sandwurm/exports/three-writer/run.fEPzg6G1`; cap 16 passed as
`.sandwurm/exports/three-writer/run.LFDsNpxz`; cap 32 timed out after emitting a content-free
`status=rejected` receipt and is retained as `.sandwurm/exports/three-writer/run.RTfmt0r2`; cap 64
timed out the same way and is retained as `.sandwurm/exports/three-writer/run.kM0Wu7VQ`.

ADR 0330 keeps completed file-object lanes private until their bounded window enters the existing
strict CAS importer once. Accepted capacity receipts from the batching implementation additionally
bind `capacity_staged_file_objects_per_node`, `capacity_file_commit_batches_per_node`,
`capacity_largest_file_commit_batch_per_node`, `capacity_late_offers_cancelled_per_node`,
`capacity_retired_offer_ids_per_node`, and `capacity_retired_offer_evictions_per_node`. The verifier
requires zero staged objects, retained IDs, and retirement evictions at convergence; largest batch
must not exceed the effective tree lane cap. Older retained proofs remain valid because the entire
new evidence group is optional, but a new receipt may not provide only part of the group.
The first accepted batching receipt is compact proof
`.sandwurm/exports/three-writer/run.WoveT4SE`: cap 16 committed 3,500 file objects in 219 batches on
each follower, caught 7/8 late offers, drained all retired IDs without eviction, and reduced capacity
catch-up from 1,059.715 to 654.214 seconds on the same 2-vCPU/2-GiB profile.

ADR 0331 adds `capacity_cas_full_inventory_scans_per_node` and
`capacity_cas_inventory_objects_inspected_per_node`. A file-bearing pull now strictly inventories
once before cached batch admission and once under the final branch/projection transaction. Because
periodic publication can create multiple intermediate pull jobs while a large source is being
populated, the receipt binds aggregate scans rather than assuming two scans for the whole campaign.
For a multi-batch capacity run the verifier requires follower scan counts to remain strictly below
their batch counts, while the final inspected population must cover at least the requested files.
The owned registry proves two cached imports, final exact revalidation, safe verified additive
concurrency, and fail-closed cached-object corruption; the four-lane service gate proves two scans
per capacity pull. ADR 0357 then adds optional `capacity_reconcile_apply_per_node` dictionaries for
the final retained `tree-job=` apply counters. Old compact proofs remain valid without that field;
new proofs that include it must provide three complete content-free dictionaries. ADR 0358 adds a
volatile subscriber-side source digest cache for the final reconcile/apply phase, so repeated no-op
pull/apply cycles can reuse unchanged selected file digests after the first stable post-projection
scan. The clean source-linked direct cap-16 run reported 7 and 5
scans versus 219 batches on each follower and completed the full 3,500-file conflict/resolution gate
in 478.979 seconds, including 379.948 seconds of capacity catch-up. The exact 2-vCPU/2-GiB Sandwurm
repeat passed with 21 and 15 scans versus the same 219 batches, completing capacity catch-up in
554.077 seconds and the full gate in 634.194 seconds. That is 15.3% and 19.5% below ADR 0330's exact
VM baseline. It left no staged objects, late cancellations, retained IDs, evictions, or watchdog
restarts. Compact proof `.sandwurm/exports/three-writer/run.yDPmVYg6` independently verifies; its
manifest SHA-256 is `1c758ea9188f4e786d53a9f0743912c52d5e01fc5b6cfff85c43268aa5052b06`.
See `evidence/2026-09-04-sync-cas-inventory.md`.

ADR 0353 remeasured the current rev0051 tree and added a tree-v2 busy-republish cooldown. The
pre-throttle current cap-8 run regressed to 1,084.185 seconds of capacity catch-up with 74/81
follower full scans, even though cap 4 completed in 386.718 seconds with 7/11 scans. After commit
`5203d7bd43a404682c6770fed282f29640fb0342`, the same 2-vCPU/2-GiB Sandwurm profile passed cap 4,
cap 8, and cap 16 again. Cap 8 is the current sweet spot for this exact guest shape:
`.sandwurm/exports/three-writer/run.BKxk74nS` completed capacity catch-up in 480.819 seconds with
23/25 follower scans. Current cap 4 completed in 512.569 seconds with 3/9 scans, while cap 16
completed but regressed to 1,271.565 seconds with 90/111 scans and 20/39 late-offer cancellations.
The verified compact proofs are `.sandwurm/exports/three-writer/run.Ed6ZvJvG`,
`.sandwurm/exports/three-writer/run.BKxk74nS`, and
`.sandwurm/exports/three-writer/run.EFQ2DS2A`. See
`evidence/2026-09-09-sync-tree-v2-busy-republish.md`. A later counter-retaining cap-8 proof,
`.sandwurm/exports/three-writer/run.cbiP45oS`, passed with 538.809 seconds of capacity catch-up and
recorded per-node final apply dictionaries. It confirmed zero final CAS work on all nodes, follower
projection of 3,501 files / 57,344,016 bytes each, and no subscriber-side source digest reuse before
ADR 0358. The first cap-8 VM repeat after ADR 0358 is retained as compact rejected proof
`.sandwurm/exports/three-writer/run.NhlrhpHW`: it timed out at 1,825.073 seconds before capacity
catch-up completed, with the origin at 3,500 files and both followers at 194 files / 195 tree-v2
objects. This does not evaluate final-apply digest reuse; it points the next near-ceiling work back
to in-progress object-transfer/catch-up instrumentation and scheduling. ADR 0359 adds
`partial_tree_v2_pull_summary_per_node` to future rejected receipts when `sync-status` is reachable,
retaining content-free job/lane/source counters for the exact timeout frontier while preserving old
rejected-proof compatibility.
The next source-linked cap-8 repeat, `.sandwurm/exports/three-writer/run.T6m7lxAN`, passed with
940.891 seconds of capacity catch-up. It proves ADR 0358's subscriber apply cache is active under VM
conditions: two nodes reported `source_hashed=0` and `source_reused=28008` in retained final apply
counters. It also shows the cache is not the throughput fix, because follower full-inventory scans
returned to 92/94 and late-offer cancellations to 14/11.

The retained compact proof `.sandwurm/exports/three-writer/run.5OJVbUl2` is the accepted 512-file
networkless Sandwurm rerun under cap 4; it does not replace the larger near-ceiling comparison.
The retained `reuse-first.json` / `reuse-second.json` host pair proves that the default loads the
same three Tox identities, stable principals, and authority-v3 ledgers while repeating the complete
conflict/resolution gate; only the first run performs from-empty initialization.
Direct harness failures write a `status=rejected` receipt to the requested evidence path after the
runtime exists. The rejected receipt is content-free and includes stage history, lane cap, requested
capacity, partial projected capacity shape, partial tree-v2 store shape, branch/conflict counts, and
Agent high-water RSS. It deliberately omits actual paths, keys, savedata, authority ledgers, file
contents, and CAS objects.

ADR 0275 extends that harness with `--shadow-cycles N --maintenance-lifecycle`. After the ordinary
three-writer conflict and resolution it performs sequential real edits around all three writers,
requires quiet cycles not to create acknowledgement-only branches, propagates one negotiated
checkpoint, pins and unpins its exact record, quarantines and restores checkpointed ancestors, then
stops one writer and applies the same exact terminal cutoff on both survivors. Restarting the retired
writer and changing its worktree must neither restore its branch nor project its new path on a
survivor. The receipt binds checkpoint copies, candidate/move/restore counts, two post-cutoff
branches, one remote automation source per survivor, and retired-writer re-entry refusal without
retaining content or keys.

Owned tests additionally freeze format-1 byte compatibility, format-2 domain separation and
conflict refusal, feature-bit dependency and old-peer refusal, checkpoint graph-fetch termination,
signed maintenance codec/tamper bounds, exact pins, workspace-manifest GC rooting, symlink refusal,
quarantine restore authentication, cutoff admission, and public Agent/CLI/local-control behavior.
The 24-cycle Sandwurm cell is an accelerated maintenance gate distinct from the later two-hour
incumbent shadow. Compact proof `.sandwurm/exports/three-writer/run.XXiFEDeB` passes
both verifiers and is interpreted in
`evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md`. The harness emits bounded progress;
after 30 seconds of a stalled shadow cycle it records the writer's kernel wait-channel names,
restarts only that daemon, reconfirms both sessions, and requires the same cycle to converge. The
accepted retry records zero such restarts; the evidence note preserves the preceding intermittent
pending-exchange observation rather than claiming it was reproduced and recovered.

ADR 0278's deterministic selective-sync matrix freezes namespace-policy v1/v2 canonical round trips,
selection precedence and malformed-path refusal, manifest-v2 owner-mode validation, excluded
authorship suppression, hidden baseline retention, and preservation of excluded local files through
atomic workspace exchange. The live Agent test creates a mode-3 read-write namespace, persists the
exact canonical rules, initializes it, and renders only metadata mode plus rule counts. CLI tests
bound malformed/duplicate rules before transport.

ADR 0295 extends that matrix into content custody. The service bridge publishes selected and omitted
files, pulls only the selected object while retaining both signed declarations, proves the omitted
digest is absent from the receiver CAS, then widens to complete interest. The next pull fetches the
deferred object, preserves an unrelated file below the formerly excluded prefix, atomically projects
both, and reports complete custody. A maintenance row proves sparse GC roots complete signed metadata
plus only the selected object, quarantines the omitted object recoverably, makes complete repair fail
closed while it is absent, and succeeds after exact restore. The live Agent test inspects, clears,
and restores canonical interest while writable automation remains configured; CLI and local-control
tests freeze malformed input and v1.53 operations 120--121. These are deterministic same-host
construction proofs, not source-availability, multi-source, long-soak, or backup evidence.

ADR 0296 adds one deterministic complementary-source proof. A primary retains a valid two-file signed
frontier but has one referenced file object removed; a second independently authorized source stores
only that exact digest. The subscriber freezes the primary inventory, observes exactly one
authenticated `absent`, retries the same digest against the second source, verifies and commits it,
and projects the complete receiver tree. Per-source counters prove which peer refused and which peer
committed. Exact duplicate source registration is idempotent, same-epoch authority drift is refused,
and a second job fails closed after both sources lose the object. GCC, Clang, and all 16 ASan/UBSan
registry shards pass. This is exact-probe correctness,
not parallel/routed performance, soak, independent-machine, or backup evidence. The owned registry
contains 743 checks; the default CTest surface remains 54 targets.

ADR 0297 adds two namespace-health checks and brings the owned registry to 745. The pure gate proves
that complete selected sparse custody can be green while conflict/stall states become yellow and
missing selected content becomes red. The durable gate commits and reloads the fixed signed record,
advances its sequence across policy change, exposes stale-policy truth, and refuses byte tampering.
The live Agent writable-tree test refreshes a green partial-custody record after forward restore,
then verifies the cached sequence and permanent `backup-certified=0` qualifier. CLI malformed input
and local-control v1.54 operation 122 are frozen. The complete post-change matrix passes: all 54 GCC
and Clang CTest targets pass apart from the five expected host-cgroup skips, and all 16
Clang ASan/UBSan owned-registry shards pass.

ADR 0298 adds one diagnostics-v2 gate and brings the owned registry to 746. It proves aggregate
namespace-health invariants, v2 encode/inspect/bundle round-trip, legacy-v1 inspection, fixed
no-witness/no-backup qualifiers, and refusal to export inconsistent totals. The live Agent gate
locally verifies the signed tree-v2 health record and exports one green partial-custody aggregate
without its namespace name or commitment. The 48 KiB redacted and 64 KiB bundle ceilings remain;
all 54 GCC and Clang CTest targets pass apart from the five expected host-cgroup skips, and all 16
Clang ASan/UBSan owned-registry shards pass.

ADR 0299 keeps the owned registry at 746 while widening existing host-capability, diagnostics, and
live-Agent gates. The explicit administrative CLI now crosses the shared sampler with live child
probes; Agent diagnostics cross its passive/no-fork mode. Diagnostics v3 round-trips closed grades,
Landlock ABI, cgroup controller/interface masks, health aggregates, and v1/v2 compatibility, and
refuses inconsistent masks. No test treats passive `available` as live confinement or sudo discovery
as authorization. All 54 GCC and Clang CTest targets pass apart from the five expected host-cgroup
skips, and all 16 Clang ASan/UBSan owned-registry shards pass.

## Founding route-policy population

Replay the compact population without private disks or identities:

```bash
python3 tools/qualify-route-policy-campaign.py \
  --proof-root .sandwurm/exports/pairs \
  --evidence .sandwurm/route-policy-campaign-20260901.json \
  --seed 20260901
```

ADR 0279's accepted receipt verifies every file commitment and both role receipts in 16 direct-UDP/
forced-TCP cells. It binds 9,814,432 cumulative observation milliseconds, six exact timing strata,
five artifact-size strata through 16,777,283 bytes, and 16 counterbalanced throughput samples.
Adaptive initial placement improved every accepted aggregate observation by 5.55%--16.80%; this
makes it the bounded ordinary selector, not a performance SLA or physical-bonding claim.

## Tree-v2 adversarial and maximum-tree matrix

The owned registry gives 16 independently signed concurrent candidates one path and checks 128
seeded arrival orders for byte-identical merge output. Candidate 17 must fail at the explicit
resource bound. A separate row drives 4,096 unique regular files through scan, CAS install, signed
branch creation, merge, and projection. That row exposed the former 64 KiB digest mismatch; ADR 0280
keeps every formerly valid manifest identity byte-for-byte and uses indexed 60 KiB leaf commitments
only for larger canonical manifests.

ADR 0281 accounts the named durable crash layouts, same-writer forks, tampered records/quarantine,
invented provenance, all six three-writer orders, the 24-cycle Sandwurm maintenance lifecycle, and
the eight-point treepack process-crash matrix as one finite gate. It does not claim arbitrary crash
points, dishonest storage, more than 4,096 entries, or more than 16 competing values at one path.

## IoTox versus Resilio two-hour shadow

Run the dedicated networkless KVM cell, then reduce it to its content-free proof surface:

```bash
./tools/iotox-sandwurm-lab.sh up-sync-shadow
./tools/iotox-sandwurm-lab.sh verify-sync-shadow PROOF_ROOT
./tools/iotox-sandwurm-lab.sh export-sync-shadow PROOF_ROOT
```

The guest starts a private loopback c-toxcore bootstrap, two source-linked IoTox agents, and a real
Resilio read-write/read-only pair. One deterministic mutation stream is applied independently to
both sources. Every cycle requires the IoTox activation, Resilio source, and Resilio replica to equal
the same canonical regular-file manifest; IoTox agents alternate restarts every 20 cycles. The
receipt requires at least 7,200,000 elapsed milliseconds, no post-setup manual publish/pull/activate
command, exact binary commitments, and no content, keys, or Resilio secret. Timeout diagnostics emit
only manifest commitments/counts and content-free automation status.

ADR 0283 accepts compact proof `.sandwurm/exports/sync-shadow/run.XXdpLNPh`: 240 exact cycles over
7,200,096 ms, six publisher and six replica restarts, zero post-setup manual transfer commands, and
356 publisher replay-window evictions. The positive eviction count proves the run crossed the
former 256-result long-session failure repaired by ADR 0282. The final manifest contains 26 files
and 105,037 bytes; only its commitment and counts survive in the proof. See
`evidence/2026-09-01-sandwurm-iotox-resilio-shadow.md`.

## Ratox owner-local operator surface

ADRs 0285--0287 raised the owned registry to 723 checks. ADR 0288 adds four synchronization-doctor
checks, bringing it to 727. The doctor gates one-writer treepack, one-file content-v2, read-write
tree-v2 selection/metadata, empty/symlink refusal, exact inventory, stable rendering, CLI parsing,
and no source population mutation. CLI tests also generate a valid disabled
canonical v7 profile, lint it, install it into an owner-only exact store, list it, bind one principal, prove
referenced removal fails, unbind it, remove it, and strictly reread after every mutation. A separate
host-capability check requires stable pidfd/seccomp/MDWE/Landlock/cgroup, privilege-prerequisite, and
sudo-mechanism fields without assuming this host delegates controllers or authorizes sudo.

The shell-admin test rejects an invalid exact `--shell` override, canonicalizes a known ELF, resolves
the current non-root account, freezes its exact sorted NSS group vector, constructs a bounded PATH
without inheriting the development sandbox, and emits disabled ordinary and explicit-sudo variants.
The rescue slice also rejects a mutable final toolbox and a non-sticky writable parent component.
Profile tests preserve exact v1-v6 decoding while proving v7 account/group/privilege/pin round trips and
rejecting root, baseline, duplicate-group, or mutable-group escalation records. Native process tests
prove the ordinary branch reaches final exec with no-new-privileges set and the compatibility admin
branch reaches it unset but with zero active and ambient capabilities and a retained privilege
bounding set.

`nix build .#checks.x86_64-linux.ratox-sudo-vm -L` is the isolated positive privilege gate. Its NixOS
guest creates an exact non-root operator, confirms shell and sudo discovery, generates the admin
profile, and launches two real set-ID-root sudo children through the production PTY boundary. A
separate UID-1001 fixture retains one deterministic test-only NOPASSWD rule and the noninteractive
branch. UID-1000 `operator` starts canonical Nix-store Bash, receives a unique prompt, sends the
synthetic password with terminal echo disabled, crosses PAM, observes UID 0 only in the sudo child,
returns to UID 1000, and exits cleanly. The captured terminal output must not contain the password.
ADR 0349 makes the password branch wait across the sudo/PAM terminal handoff before submitting the
post-sudo status/exit command and adds bounded PTY lifecycle diagnostics for future timeouts. The
latest accepted Linux 6.6.94 KVM script completed in 15.82 seconds. This is not an IoTox
installation default or evidence that every user's sudoers/PAM, hardware-token, retry, timeout, or
lockout policy will work. See ADR 0326, ADR 0349, and
`evidence/2026-09-03-ratox-password-sudo.md`.

`nix build .#checks.x86_64-linux.ratox-rescue-toolbox-vm -L` is the isolated fallback-userland gate.
The package build independently pins static oksh 7.9 and Toybox 0.8.14, rejects Toybox `sh`/`toysh`,
installs applet aliases plus provenance/notices, and leaves the IoTox executable unchanged. The guest
qualifies the exact shell/directory, generates a disabled baseline account profile, then crosses the
production PTY as UID 1000 with PATH containing only that toolbox. It requires interactive-shell and
Toybox resolution, non-root `id`, exact file contents/SHA-256, listing, and clean exit. This proves a
bounded x86_64-linux fallback, not boot, kernel, filesystem, network, profile-retention, or automatic-
failover recovery.

ADR 0289 extends the separate terminal-controller process target. One real `iotox --reconnect`
process opens once, receives authoritative `unavailable`, has two exact `resume_only` attempts
refused, accepts generation 2 only, renders retained output, and detaches on stdin close. The fixture
requires one new-session OPEN and one successful resume; it never permits a replacement shell.
ADR 0300 closes the missing genuine-route half. `ratox-cli-reconnect` forks a pseudo-terminal and
executes the actual CLI, then the Sandwurm runner applies independent seeded 100% loss to both guest
TAPs. The verifier requires one PID/start time, zero restarts, exact retained session/incarnation,
warning while the original route is still confirmed, authoritative offline and zero-attached remote
PTY, a higher authenticated epoch, generation and byte sequences 1-to-2, healthy heartbeats, local
detach, and exit zero. Direct-UDP `pair.h3wylill` and forced-TCP `pair.6bf75b_4` pass raw export and
content-free compact re-verification. This remains one-loss construction evidence, not daemon-restart
survival, repeated-loss soak, or deployment qualification.

ADR 0316 adds a separate `ratox-cli-reconnect-repeated` receipt instead of changing ADR 0300's
historical v1 proof. The controller-process fixture now forces two unavailable/resume cycles through
one real CLI process and proves one OPEN, two exact RESUMES, generations 1-to-2-to-3, and no
replacement session. The Sandwurm cell then injects two ordered, independently seeded 100% netem
faults on both guest TAPs. Its verifier requires the same PID/start ticks, zero restarts, one remote
session/incarnation, exact input/output positions 1-to-2-to-3, a higher authenticated epoch after
each loss, post-resume progress and healthy heartbeat, positive drops on both TAPs, exact forced-TCP
carrier truth, and clean detach. Direct-UDP `pair.66mhbsl5` and forced-TCP `pair.pvryy_am` pass raw
and 252 KiB compact verification with identical binary SHA-256
`ada08f7991a86a03a0341db857541f8870571816f1a00a59444e1f903646e033`. The direct registry remains
821 because this extends a separate process oracle. This is bounded repeated-loss construction
evidence, not a long soak, overlay-route cell, or production activation. Final validation passed
821/821 direct checks in 34.76 seconds, all 55 GCC CTest entries in 72.04 seconds with the five
host-undelegated cgroup/PSI positives reported as skips, and all 70 Clang ASan/UBSan entries in
83.31 seconds with the same five explicit skips. The complete run also corrected two reversed
sync-doctor v1/v2 test expectations left by ADR 0315; production output already matched the frozen
v1 pre-creation and v2 configured contracts.

ADR 0301 adds one owned profile-format check and brings the registry to 747. Canonical profile v7
round-trips optional SHA-256 pins, keeps exact v1--v6 compatibility, and refuses malformed or
incomplete shell/toolbox pin combinations. Native process tests prove the already-open shell
descriptor is rehashed immediately before spawn, accept the correct digest, and refuse a mismatch
without running the target. The x86 rescue VM also requires both generated pins. Separate flake
checks build static AArch64 oksh/Toybox from the same sources, validate their SPDX 2.3 record, and
execute both with qemu-user. The binfmt VM requires direct non-root execution and IoTox discovery,
then retains the expected final `fexecve` `ENOENT` at the sealed production PTY boundary. This is
emulated execution and negative kernel-boundary evidence, not native-AArch64-kernel qualification.

ADR 0304 adds the positive `ratox-rescue-toolbox-aarch64-system-vm` layer. It boots the locked
AArch64 Linux 6.6.94 kernel under QEMU `virt`/TCG with a minimal initramfs, runs the cross-built
current rescue qualifier as UID/GID 1000, and requires exact kernel, qualifier, and completion
markers. The unchanged production PTY path validates profile-v7 hashes, sealed oksh execution,
capsule-only applet resolution, identity, file/hash/list work, and clean exit. This is target-kernel
semantic evidence under system emulation; one named physical target ABI/kernel gate remains.

ADR 0303 adds twelve owned checks and brings the direct registry to 759. Two freeze inseparable
protected-state mode/root/policy-pin selection and prove a required plaintext root fails before
runtime mutation. Ten freeze the
authority witness record/CAS protocol, run an actual two-thread clone race with one winner, advance
one owner-signed bootstrap, reject complete local rollback while the witness stays advanced, recover
both sides of pending state and both lost-reply CAS boundaries, discard an intent when the initial
CAS never applied, reject pending state without exact intent, reject same-domain production use, and
reject restoration of a matching ledger/guard snapshot taken before principal revocation. The
`protected-state-fscrypt-vm` check then provisions ext4
fscrypt v2 externally, crosses source-linked `run-check` and real Agent savedata creation, attacks
policy-pin/prefix/symlink/hardlink/FIFO/bind-mount closure, removes the right key, installs a wrong key, requires
pre-runtime refusal, re-adds the right key, and scans the raw unmounted image for a plaintext canary.
This proves the construction-kernel encryption boundary and authority coordinator logic, not key
custody, production witness independence, complete-snapshot freshness for other lanes, or backup.

ADR 0305 adds eight owned checks and brings the direct registry to 767. Fixed authenticated service
records persist query/begin/commit, exact-CAS elects one of two clients, a wrong pinned signer and a
tampered durable record refuse, enrollment binds the exact device/domain/epoch/head, one store admits
one service process, a real authority ledger commits and restarts through TCP, and a truncated
accepted connection cannot terminate the service. The retained
`rollback-witness-service-vm` runs the source-linked release binary in separate Agent and witness
NixOS guests. It advances RecallRoot bootstrap from position zero to one, reconstructs the complete
valid position-zero local ledger/guard while the service remains advanced, and requires refusal before
runtime creation. Exact-current recovery, service outage, service relaunch, wrong-key refusal, and
final recovery pass. Same-host guests prove protocol/state separation only, not physical,
administrative, snapshot, or service-storage independence.

ADR 0306 adds five owned checks and brings the direct registry to 772. Application and Ratox
incarnation lanes enroll independently, advance through exact positions one and two, reject a
complete older device-signed record while the witness stays advanced, refuse a same-domain backend
outside tests, and recover a pending transition left after exact local installation and an injected
final-CAS/query failure. One check crosses the actual authenticated TCP service rather than the
in-memory backend. The widened `rollback-witness-service-vm` enrolls authority, application, and
Ratox separately; starts Ratox against a real UID-1000 login profile; and restores older exact
application and Ratox records one at a time. Both refuse before the requested runtime appears while
the witness guest stays current. These same-host guests establish protocol/state separation, not
physical or administrative witness independence.

ADR 0307 adds four owned checks and brings the direct registry to 776. The route lane enrolls the
newest reviewed signed artifact, materializes or verifies its local high-water checkpoint, admits
only the exact next generation, rejects a complete valid artifact/checkpoint rollback, refuses a
generation skip and same-domain production backend, and recovers an interrupted final CAS with the
exact intent. One check advances a route through the authenticated TCP service. The retained
`rollback-witness-service-vm` also enrolls route generation one, adopts generation two through the
source-linked Agent, restores both generation-one local files, and requires refusal before the
runtime path appears. This does not turn the same-host witness guest into an independently
administered or rollback-resistant service.

ADR 0308 adds five owned checks and brings the direct registry to 781. The complete terminal
profile/binding tree has one canonical semantic digest; the generic policy transaction refuses an
unreviewed digest, advances only through explicit commit, rejects full old-policy plus old-checkpoint
restoration, recovers both prepared-before-CAS and externally pending transitions, and rejects a
same-domain production backend. One check crosses the actual authenticated TCP service. The retained
two-guest gate enrolls a sudo-capable UID-1000 profile, refuses its no-escalation replacement before
explicit commit, accepts the committed replacement, then restores the old sudo profile and matching
signed checkpoint and refuses before RuntimeTree. This does not prove sudoers/PAM correctness or an
independently administered witness.

ADR 0309 adds one owned check and brings the direct registry to 782. It proves that merely received
and read-only commands do not move the mutable-effect frontier, an exact principal/authority-bound
`STARTED` command does, result/delivery churn preserves its digest, and bounded pruning retains the
effect identity while evicting eligible read-only history. The retained generic policy-witness
checks cover interrupted CAS joins and complete old digest/checkpoint rollback. The two-guest gate
enrolls the empty command-effect frontier and starts the source-linked Agent with all six lanes over
the authenticated TCP service. That VM establishes enrollment, wire authentication, startup
reconciliation, and coexistence; it does not yet inject a live remote mutable command or prove
exactly-once physical effects.

ADR 0310 adds one owned check and brings the direct registry to 783. It proves distinct stable
commitments for an empty sync-policy tree, one canonical namespace, and that namespace plus its
stable-device-signed automation; duplicate namespace material refuses. The retained generic
policy-witness checks cover exact advancement, interrupted CAS joins, and complete old
digest/checkpoint rollback. The two-guest gate enrolls the empty policy as the seventh lane, starts
the source-linked Agent, performs a live `sync-create` whose namespace and automation each commit
before activation, then restores the complete enrolled-empty namespace/automation tree and matching
checkpoint while the service remains advanced. Startup refuses before RuntimeTree. This does not
witness per-namespace heads, guards, content, workspaces, maintenance, projections, or current
pointers, and same-host guests do not establish operational independence.

ADR 0311 adds four owned checks and brings the direct registry to 787. The exact update-policy plus
absent-or-signed-state digest is enrolled at position one; every later lifecycle generation advances
the same authenticated lane exactly once. Injected loss after pending CAS recovers by installing the
exact signed successor from durable intent, injected loss after final CAS cleans up without repeating
state, a complete local state rollback refuses, and an interrupted apply pointer repairs forward
before the next incarnation opens its witnessed health window. The eight-lane two-guest gate adds
real authenticated service enrollment/query and rejects a canonical update-policy substitution
before RuntimeTree. It does not inject remote-service loss during a live delivered update, prove
witness independence, or make quarantine purge safe.

ADR 0312 adds 13 owned checks and brings the direct registry to 800. They bind immutable namespace
storage identity and every published/accepted/activated/retained root, keep 64 derived namespace
domains distinct, refuse tree-v2, and advance the external head through publish, accept, activate,
pin, and unpin. The crash matrix distinguishes root replacement that did not land from a late error
after rename, crosses lost replies at both remote CAS boundaries, completes every valid
guard/root/external join, and refuses impossible predecessor/pending states, third heads,
same-position forks, pending-target forks, wrong selectors, and rollback before an otherwise early
mutation result. A concurrent reader remains blocked by the namespace transaction until the
external commit finishes. All 16 Clang ASan/UBSan owned-registry shards pass.

The retained two-guest gate adds the ninth lane type and enrolls two range-v1 namespaces under
distinct derived domains through the actual authenticated service. It publishes `notes`, restores
that namespace's complete enrolled-empty four-root/guard snapshot while the service remains
advanced, and requires refusal before RuntimeTree. Exact-current restoration recovers. The same
guests retain all earlier lane, outage, restart, and wrong-key cells. This proves protocol/state
separation on one founding host and hypervisor, not physical or administrative independence,
content/backup freshness, full namespace-state coverage, or deletion safety.

ADR 0313 adds four owned checks and brings the direct registry to 804. A deterministic
`IOTXWCP1` artifact binds the pinned witness key and the complete sorted selector population,
including exact pending transitions. The checks reject a wrong pinned key and modified bytes,
accept an exact store and legitimate forward progress, reject selective restoration of one older
signed record, require every formerly enrolled selector, accept an exact pending floor and its
committed successor, and reject the predecessor after that pending checkpoint exists. Ordinary
service startup now scans every current record even when no floor is selected.

The retained two-guest witness-service gate uses the source-linked CLI to export and offline-verify
ten service records after enrollment, then starts the listener with that floor. After Agent lane
advancement it exports a new checkpoint, selectively restores the authentic old authority-service
record, and requires refusal before bind. Restoring the exact current record permits restart against
the advanced floor. Both guests and both checkpoint directories remain on one founding host and
hypervisor; this is protocol/ceremony evidence, not independent administration or rollback-resistant
media. The gate does not exercise a continuous clone-fencing lease, hardware counter, service-key
replacement, witness-epoch handoff, or emergency re-anchor.

ADR 0314 adds 13 owned checks and brings the direct registry to 817. They bind immutable tree-v2
storage identity, the writer-sorted live branch frontier, exact signed workspace, and exact signed
maintenance state under 64-way namespace-separated service domains. Publication, workspace
initialize/begin/finish, pin, and unpin each advance the lane. The crash matrix covers root-not-
landed cleanup, landed-before-remote recovery, every valid local-guard/external pending join, and
lost replies at both CAS boundaries. Complete old-state replay, wrong selectors, same-position and
pending-target forks, third local heads, malformed or multiply linked guards, and rollback before an
otherwise early mutator result refuse. A transaction-held reader cannot observe a landed successor
until the external commit finishes. The final direct run passed 817/817 in 39.00 seconds; the
complete 55-entry CTest surface passed in 39.54 seconds with the five unavailable delegated-cgroup
host-capability cases reported as skips. All 16 Clang ASan/UBSan owned-registry shards passed in
26.20 seconds.

The retained two-guest gate now enrolls and checkpoints 11 service records, including a lane-10
tree-v2 namespace beside two lane-9 single-writer namespaces. It advances tree-v2, replaces the
complete local namespace root with its authentic older snapshot while the service remains current,
and requires refusal before RuntimeTree. Exact-current restoration recovers. The guests prove
authenticated protocol and disk/process separation on one founding host and hypervisor, not
physical or administrative independence, content custody, backup, safe deletion, or a continuous
live-clone lease.

ADR 0315 adds four owned checks and brings the direct registry to 821. The configured CLI path loads
one canonical Agent record, stable identity, nondefault namespace policy, and signed source
automation before emitting the strict v2 report with live headroom while pre-creation v1 remains
unchanged. Direct helpers inventory a
content-v2 store and seven-byte incoming partial, refuse over-quota and nonprivate staging state,
refuse a missing transaction boundary without creating it, and join a real reconciled writable
tree-v2 worktree to its immutable object graph, eight-byte incoming partial, and shared-filesystem
projection reserve. The final GCC run passed 821/821 in 34.54 seconds; the complete 55-entry CTest
surface passed in 57.43 seconds with five unavailable delegated-cgroup host-capability cases reported
as skips. All 16 Clang ASan/UBSan registry shards passed in 26.69 seconds. This proves bounded
point-in-time inventory and admission arithmetic on the founding host; it does not reserve space,
simulate ENOSPC/read-only storage, prove `fsync`, measure representative capacity, or certify a
backup.

ADR 0317 adds four owned checks and brings the direct registry to 825. One freezes all 199 sorted,
unique command spellings, their closed execution classes, and the eleven compatibility-to-canonical
edges. One requires `--help` to expose every descriptor through its generated index, including the
previously hidden `transport-peer-add` and `transport-peer-reject` compatibility forms. One requires
all Bash/Zsh/Fish generators to contain the complete registry, and one crosses the public
`completion` dispatch and invalid-shell refusal. Emitted source also passes `bash -n`, Zsh 5.9.2
`zsh -n`, and Fish 4.8.1 `fish -n`. This is deterministic command-name completion, not dynamic
peer/path discovery, positional-argument validation, or shell-configuration mutation. Final
qualification passes 825/825 direct checks in 38.92 seconds, all 55 GCC CTest entries in 82.43
seconds, and all 70 Clang ASan/UBSan CTest entries in 90.57 seconds. Both CTest presets retain only
the five explicit host-cgroup/PSI skips.

ADR 0318 adds two owned checks and brings the direct registry to 827. One creates a real user xattr,
a 1 MiB hole-only sparse file, a hard-link pair, and a FIFO beneath an otherwise valid writable
source and requires every shape to fail the read-only doctor contract. One creates two legal Linux
names differing only by ASCII case and requires collision refusal. Existing successful source
coverage now freezes the strict v3/v4 headers and ten contract fields, including byte-exact case requirements,
refused ACL/xattr and sparse state, local ownership, and non-preserved timestamps. The GCC owned
registry passes 827/827 in 35.28 seconds; the complete GCC matrix passes 55/55 in 73.39 seconds and
the Clang ASan/UBSan matrix passes 70/70 in 85.20 seconds. Both retain only the five explicit
host-cgroup/PSI skips. This proves a point-in-time Linux source inspection, not continuous
enforcement, Unicode/case-insensitive portability, metadata support, `fsync`, storage hardware, or
backup recovery.

ADR 0319 adds four owned checks and brings the direct registry to 831 and the typed command
population to 200. The library cases require exact nested bytes and private owner modes, distinguish
a valid content/mode mismatch from inspection failure, reject canonical alias/containment, and
refuse an unresolved `.iotox-conflicts` projection. The CLI case freezes the strict v1 match record,
bounded byte counts, `iotox-live-state-read=0`, and `backup-independence=not-assessed`. The verifier
also alternates two scans of each tree and repeats ADR 0318's filesystem-contract walk so an observed
change refuses rather than producing a plausible comparison. The final GCC owned registry passes
831/831 in 37.27 seconds; the complete GCC matrix passes 55/55 in 54.82 seconds and the complete
Clang ASan/UBSan matrix passes 70/70 in 64.01 seconds. Both retain only the five explicit
host-cgroup/PSI skips. This proves bounded same-host comparison of operator-supplied disjoint trees,
not recovery custody/provenance, atomic cross-filesystem snapshotting, node-loss recovery,
storage durability, or precious-data readiness. See
`evidence/2026-09-03-sync-recovery-verify.md`.

ADR 0360 extends the same verifier and the witness checkpoint CLI without changing the wire formats.
The sync recovery tests now require optional all-or-none provenance labels, canonical hex rendering,
same/different root device observation, and partial-label refusal while preserving
`backup-independence=not-assessed` and `restore-provenance=not-assessed`. The CLI tests add a real
witness-service identity, one enrolled record, a signed checkpoint retained outside the service root,
`witness-service-checkpoint-custody` success with custody labels, and refusal of a checkpoint copied
under the service root. The typed command population is now 201. Accepted checks:
`nix develop -c bash -lc 'cmake --build build -j2 --target iotox iotox_tests && ctest --test-dir build -R "^(iotox\.unit-and-integration|iotox\.client-help)$" --output-on-failure'`
and `nix flake check -L`.
This proves report plumbing, strict parsing, signature verification, and outside-root enforcement,
not recovery custody, operationally independent witness deployment, rollback-resistant custody,
or precious-data suitability.

The first representative-capacity controls are retained separately from correctness counts. At
commit `c079584`, the isolated 4,096-file scan/CAS/branch/merge/projection test passed in 0.37 seconds
with 23,592 KiB process peak RSS. A distinct 3,621-entry, 53,477,376-byte mixed-size source passed
strict doctor in 0.26 seconds at 9,312 KiB peak RSS and exact double-scan restore comparison in 1.25
seconds at 18,708 KiB peak RSS. Both ran hot on the founding host's tmpfs and reported zero block
I/O. They are useful CPU/process-memory controls, not persistent-storage, cold-cache, page-cache,
disk-amplification, conflict, repair, or multi-node catch-up evidence. The exact commands and
population are in `evidence/2026-09-03-sync-capacity-controls.md`.

ADRs 0320--0322 add the first persistent full-mesh capacity cell and strengthen the existing owned
tree-v2 exchange-recovery check without inflating the registry count. The direct registry remains
831/831 and passes in 38.70 seconds; the complete GCC matrix passes 55/55 in 77.73 seconds and the
complete Clang ASan/UBSan matrix passes 70/70 in 94.57 seconds. Both retain only the five explicit
host-cgroup/PSI capability skips. The fresh 2-vCPU/2-GiB Sandwurm cell converges 512 16-KiB files
across three real daemons on persistent ext4, records a 70.997-second catch-up, 163/318/75-ms repair,
16--18-MiB Agent high-water RSS, and about 20--21-MiB allocated growth per node, then crosses the
existing conflict, 24-cycle, checkpoint, quarantine/restore, and writer-cutoff lifecycle. A second
byte-identical-binary pressure cell crosses the strict watchdog at cycle 24 under ext4 journal
pressure; restarting that writer reconciles the signed pending workspace and preserves its
path-based edit before exact convergence. The retained
compact proof and the rejected diagnostic cells are recorded in
`evidence/2026-09-03-sandwurm-sync-persistent-capacity.md`. This does not prove cold or near-ceiling
behavior, physical power loss, ENOSPC/read-only recovery, open-descriptor safety, dishonest storage,
recovery custody, or precious-data readiness.

ADR 0323 keeps the owned registry at 831 while strengthening classic and tree publisher checks with
namespace-selective additive-share replay retirement and fresh re-admission after retirement. The
final direct source-linked recovery harness passes in 81.771 seconds: 33 files in one directory (131,099
bytes), one erased-and-empty replacement, two capability revocations, two terminal writer cutoffs,
two friendship removals, two survivor restarts, and two ordered post-cutoff graph floors. Each node
again has three current branches. The harness then erases all live roots and creates three further
fresh identities. Six node instances pass `sync-repair`; the selected restore and all three final
views produce four exact `sync-recovery-verify` matches; hashes of all four obsolete principals are
disjoint from the three final principals. The content-free receipt is recorded in
`evidence/2026-09-03-sync-node-loss-recovery.md`. This does not establish recovery custody,
restore provenance, correct generation selection, power-loss durability, or precious-data trust.

The clean retained 2-vCPU/2-GiB Sandwurm replacement runs source revision `2d5e869` and binary
SHA-256 `705d65f96e64c13d4d6079a787e28d12bb02a62467697e18bbe9ada84110d010`. Its 512 16-KiB files
catch up in 46.326 seconds and repair in 46/43/44 ms; Agent high-water RSS is
17,096/16,896/16,256 KiB. All 24 persistent cycles complete in 129.671 seconds with zero watchdog
restarts. The additive recovery phase then completes in 97.238 seconds with `[3,3,3]` branches after
both one-node and all-node replacement, six repaired views, and four exact external-tree matches.
Both verifiers accept compact proof `run.XXJGHoNd`; manifest SHA-256 is
`81213534d4754ad8cd8bebe04838b39d88205e87e092271d6c3b9d8191b72439`.

ADR 0324 strengthens one existing authority-session check without changing the 831-entry registry.
It receives one challenge, advances the exact local ledger again before proof preparation, accepts
the strictly newer challenge from the same verifier/session, proves the latest head, and still
rejects a different nonce at the same head. The direct GCC registry passes 831/831 in 33.70 seconds.
The motivating two-vCPU Sandwurm cell completed the persistent capacity phase but was rejected after
the old state machine left two peers awaiting node 1's proof for 180 seconds; read-only disk
inspection and the exact evidence boundary are recorded in
`evidence/2026-09-03-authority-round-supersession.md`. The clean replacement gate crosses the same
rapid-grant point and all later restart/re-proof and fresh-mesh boundaries without an awaiting-proof
stall; the deterministic check remains the state-machine proof.

ADR 0325 adds a retained storage-fault phase without changing the 831-entry C++ registry. The same
source-linked 2-vCPU/2-GiB Sandwurm cell first passed 512-file capacity, 24 persistent lifecycle
cycles, and one-node/all-node reconstruction. It then mounted three separate 192-MiB loop-backed
ext4 filesystems for three fresh Agents. A live writer observed real `ENOSPC` after 178,147,328
filler bytes and refused an explicit checkpoint mutation; `SIGKILL`, exact filler removal, restart,
convergence, and repair passed. A second node refused startup on an exact read-only remount with
exit 3 while its durable-state digest stayed unchanged, then recovered after read-write remount. A
third node was killed with exit `-9` at signed `pending-workspace` during a 33,554,432-byte
successor exchange; startup reconciliation joined it. Three final repairs matched 19 files, one
directory, 33,620,017 bytes, and canonical SHA-256
`444795f5a52d94a9301bececa30987cc907b650551f11b562f76ac6b4f360b93`.
The storage phase took 144.433 seconds. Both verifiers accept compact proof
`.sandwurm/exports/three-writer/run.XXJNFmNN`; manifest SHA-256 is
`d47fc6347114b63edf9e563b8bc0ec772ca16de35955e9ecab7b848d1e9a8a6e`. This did not cut whole-VM
or host power, inject every durable-record corruption, keep descriptors open across remount, or
assess lying storage.

ADR 0332 adds four Python self-test entries without changing the 834-entry C++ registry. The guest
classifier accepts only `[completed, completed, prior]` or all-completed offline views and rejects a
hybrid. Host runner, strict proof verifier, and compact exporter each have deterministic tests; the
verifier's adversarial fixture updates the campaign digest after tampering so rejection occurs at
the old-or-new semantic gate rather than only at the outer hash boundary.

The exact source-linked Sandwurm campaign at commit `2cd84a2` did run two networkless
2-vCPU/2-GiB Cloud Hypervisor epochs over one crash lineage, kill the first VMM noncooperatively,
boot the exact crash lineage under a distinct kernel, accept only exact prior/completed projections,
preserve identities, and converge and repair. It does **not** close the workspace boundary: later
source audit found that the Python observer decoded byte 1 as pending and byte 2 as stable, opposite
the C++ enum. The reported pending header was therefore stable and the v1 compact proof is withdrawn.

The v2 guest self-test checks the exact ten-byte signed-record prefix and requires
`stable=1,pending-exchange=2`; the arm validator independently rejects raw byte 1. Arm and campaign
receipts carry raw phase byte 2 plus the explicit encoding, recovery labels are checked against raw
bytes, and current verifier/exporter schemas reject all v1 proof.

Corrected source-linked run `4hto8rll` at commit `3dcc675` observed raw phase byte 2 before arming,
cut the exact VMM with exit 137 and no cooperative control, and booted the exact crash lineage under
a distinct second kernel. Before Agent start it found `[completed, completed, prior]`; C retained
pending byte 2 and no stage path. Identities survived, three branches per node converged and repaired
to 18 files, one directory, 33,619,995 bytes, and digest
`e1c1515d0faf3e669849a3913cd0fcb3faddb689ae911eedf2d9cee9e6e9bd2d` in 1.973 seconds. The
complete campaign took 435.628 seconds. Compact proof
`.sandwurm/exports/sync-power-cut/run.4hto8rll` has manifest SHA-256
`33b5ae2a0c1bec039059292db0519550f36fcccf49d275caf052dc1cc5520128` and verifies independently.
This closes one corrected VMM-cut workspace linearization, not the remaining transition matrix,
host/physical power removal, dishonest storage, recovery custody, or precious-data trust.

ADR 0333 adds a v3 selector for the other linearization. The observer reads the active and pending
manifest identities from the durable workspace record, classifies the visible canonical projection
marker between two equal raw-byte-2 snapshots, and exposes distinct pre/post Sandwurm profiles. The
post cell cannot accept a prior follower after reboot. Verifier fixtures cover v2 compatibility and
both v3 orientations; runner fixtures reject an active marker as a post-exchange arm.

Source-linked run `nhjaizl2` at commit `bb0dc88` captured pending orientation and a present stage,
cut the exact VMM with exit 137, and booted the crash lineage under a distinct kernel. All offline
views were completed; C retained pending byte 2, pending marker orientation, and the old stage.
Recovery converged and repaired three branches per node in 1.631 seconds; the full campaign took
477.636 seconds. Compact proof `.sandwurm/exports/sync-power-cut/run.nhjaizl2` has manifest SHA-256
`f163743ff7c4a8e82232e78b9ba6efaa29dcd0b0bffa483115331d2a5d8e3ea4` and verifies independently.
Both workspace sides are qualified; other durable transaction families remain open.

ADR 0334 reserves proof v4 for two earlier object-pipeline boundaries. The
`receive-staging-partial` observer requires one private generic-transfer
`.iotox-.receive-*.part.part-<six-base62>` temporary between 8 MiB and the 32 MiB expected object
size. The `cas-install-temporary` observer requires `.install.tmp`
inside the expected digest fanout. Both require stable raw workspace phase byte 1, active projection
orientation, no final object, mode 0600, one link, and matching ownership. The rehearsal then
immediately stops the follower process group and verifies its kernel stopped state before emitting
the arm receipt; the host still independently finds and kills the exact task-owned VMM. On reboot,
offline inspection permits only absent or exact digest-named state and bounds every surviving
canonical temporary. Startup must durably remove all staging, install the exact object, converge,
restore all three branches, and repair. Runner, verifier, and compact exporter fixtures cover both
v4 boundaries while preserving v2/v3 read compatibility.

Corrected source-linked v4 runs `1e05ayp9` and `jtiyspp_` at commit `885f104` now pass. The receive
cell stopped the follower at 8,393,262 bytes in the real generic transport temporary; reboot retained
one zero-length incoming inode and no final object. The CAS cell stopped at 61,440 copied bytes;
reboot retained no CAS temporary or final object but did retain the complete 33,554,432-byte
canonical incoming file. Both offline trees were `[completed, completed, prior]`; startup left no
temporary, installed the exact object, preserved identity, converged the
18-file/33,619,995-byte tree, restored branches `[3,3,3]`, and repaired all nodes. Strict compact
proofs live at `.sandwurm/exports/sync-power-cut/run.1e05ayp9` and
`.sandwurm/exports/sync-power-cut/run.jtiyspp_`. Details and nonclaims are frozen in
`evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md`.

Rejected source-linked attempt `run.s_2l5lii` at commit `898c04b` looked for a partial canonical
`.receive-*` path and timed out closed. The generic file-transfer manager writes under a second
hidden temporary and only link-publishes `.receive-*` after complete length and file fsync, so the
requested state was impossible. Read-only, no-journal-replay inspection of the retained outer and
three inner ext4 images confirmed A/B held the exact successor CAS object while C remained at the
prior store and projection. This attempt found and motivated cleanup of the real transport
temporary; it is not power-cut qualification evidence.

ADR 0335 reserves proof v5 for the three pre-rename metadata-publication prefixes. The live writers
must agree on one exact successor while the follower retains the same writer set with exactly one
prior pointer. The private marker binds the successor manifest, immutable record, successor pointer,
and prior pointer by canonical name, size, and SHA-256. A redacted object with hashed names and exact
size/hash commitments is carried identically by arm, campaign, and recovery receipts. Only the
follower runs under external
qualification-owned `strace -f`; `-P` restricts tracing and injection to the exact selected temporary
pathname, and a two-second `rename`/`renameat2` syscall-entry delay leaves that fully written and
file-fsynced temporary before its commit enters the kernel. Unrelated Agent/runtime projection
renames are not delayed. The arm requires the exact temporary, stable prior worktree, no projection
stage, correct metadata prefix, and one exact ptrace-stopped sync worker. The fence stops the Agent
thread group while strace is still live, proves every Agent task stopped, then stops the tracer and
requires the process group to contain exactly that tracer and Agent before arming. A simultaneous
process-group stop is deliberately rejected because it can freeze the tracer before sleeping Agent
threads receive group-stop.

On the second boot, offline inspection requires absent/absent/prior at manifest install,
exact/absent/prior at immutable-record install, and exact/exact/prior at pointer update. The selected
temporary may be absent because its directory entry was not fsynced; if present it must equal the
target, while every non-selected temporary must be absent. Startup must leave exact/exact/successor,
zero temporaries, the completed projection, branches `[3,3,3]`, and three repaired nodes. Synthetic
runner/verifier/exporter fixtures cover all three boundaries, the legal absent-temporary branch, v2--
v4 compatibility, and marker-hash cross-binding. Repaired-source-linked Sandwurm runs `l2gckna4`,
`c9xhj26a`, and `_cphu30p` pass all three boundaries with one binary. These cells do not cut after
rename and before parent-directory fsync.

The first source-linked mutable-pointer attempt reached the intended cut and passed its offline
prefix check, but recovery timed out: the successor manifest and immutable branch record were exact
while the mutable pointer remained prior. This rejected run found that the subscriber conflated
local record presence with live-pointer incorporation. The owned regression
`tree-v2 subscriber replays an immutable successor left before pointer commit` now reproduces that
prefix without a VM, requires zero object requests, advances the exact signed successor through the
normal acceptance path, and verifies the successor worktree and generation. With the repair, the
direct development-environment registry passes `tests=835 selected=835 failures=0`. All three real
v5 cells were then rerun from the same clean repaired commit and passed. See
`evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md`.

ADR 0336 reserves proof v6 for the three adjacent post-rename/pre-parent-directory-fsync windows.
The follower runs beneath `strace -f -P` restricted to the exact `manifests`, `records`, or
`branches` parent, with entry delay injected only into `fsync`. The arm is valid only while the
selected final metadata is exact, its temporary is absent, the stable prior worktree remains active,
and the exact traced Agent worker and all Agent tasks are stopped before the tracer. Manifest and
record destinations are `exact`; the pointer destination is the exact `successor`.

After host `SIGKILL` of the independently bound Cloud Hypervisor process and a second-kernel boot of
the crash image, offline inspection permits only the selected directory transaction's old or new
state: manifest `absent|exact`, record `absent`, pointer `prior`; then manifest `exact`, record
`absent|exact`, pointer `prior`; then manifest `exact`, record `exact`, pointer
`prior|successor`. Only the selected exact temporary may survive. Strict synthetic fixtures exercise
both old and new states for all three cells, reject corrupt prefixes, preserve v2--v5 compatibility,
and round-trip v6 through the compact exporter.

Rejected record-directory run `pjo_92d4` never armed. Its raw exact-directory trace recorded 134
delayed `fsync` calls from unconditional tree-v2 frontier preparation before the selected
successor record could arrive. The store now persists directory structure only when preparation
creates it, in child-to-parent order; the manifest/record/pointer publication barriers are unchanged.
Runs `dbgtc3ip`, `jznfzx52`, and `ia70ljmf` then passed from optimized commit `0686cba` and one
byte-identical binary without shortening the two-second fence. Every crash recovered the old selected
directory state with one exact temporary; startup removed it, reached exact/exact/successor, restored
branches `[3,3,3]`, and repaired every node. All three compact proofs pass strict replay. See
`evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md`.

ADR 0328 adds one owned tree-v2 source-race check and brings the direct C++ registry to 832 entries.
The gate scans a source file, rewrites it through an already-open writer descriptor before object
installation, and requires fail-closed CAS behavior: `protocol_error`, no digest-named object, no
retained `.install.tmp`, and successful installation only after a fresh rescan. Focused GCC and
Clang unit/integration CTest runs passed; the direct GCC registry count under the Nix development
environment reported `tests=832 selected=832 shard=0/1 failures=0`. This is scan/store descriptor
coverage, not projection-exchange, remount, power-cut, corrupt-record, or backup evidence. Details
live in `evidence/2026-09-03-sync-open-descriptor-source-mutation.md`.

A same-host near-ceiling diagnostic with 3,500 16-KiB files is retained as a rejected scale sample.
The first run reached three branches on all nodes but timed out after the 1,800-second capacity wait
while followers had only 2,124/2,139 object files and zero capacity projection files. A corrected
observer retry reduced Python sampling load but still timed out with followers at 2,559/2,569
objects and no accepted receipt. This points the next scale work at object transfer/projection
catch-up and does not qualify the near-ceiling Sandwurm gate. Details live in
`evidence/2026-09-03-sync-near-ceiling-timeout.md`.

That diagnostic also exposed harness observer pressure: the capacity predicate rehashed the complete
source tree before checking whether followers had even received the expected shape. The harness now
checks per-node file count and total bytes first, then hashes only after all nodes have the expected
shape. A fresh 16-file smoke passed after the change. The 3,500-file population has since passed
with the tree-v2 lane window; Sandwurm repetition is still required before it becomes qualification
evidence.

ADR 0329 adds bounded tree-v2 exact-object lanes without changing the frozen peer frames. The direct
service test now proves a four-file manifest expansion can leave four exact object requests active
together, with `active-lanes=4`, four `tree-lane-job=` bindings, and empty compatibility
`active-file` fields. Focused GCC and Clang unit/integration CTest runs passed. The first
source-linked 3,500-file same-host retry using the new default four-lane cap passed: full capacity
catch-up completed in 960.696 seconds, full run elapsed time was 1,050.374 seconds, repair took
552/1,822/686 ms, and no stalled-cycle restart fired. It is retained as a direct diagnostic, not
Sandwurm qualification. The direct GCC registry summary with the proper CTest mock arguments is now
`tests=833 selected=833 shard=0/1 failures=0`.

ADR 0290 adds three canonical Agent-config codec/ownership/merge checks, one CLI lint/non-mutation
check, and one read-only route-inspection check, bringing the direct registry to 732. The ordinary
binary lifecycle's persisted-state restart now uses `run --config` and keeps `--run-ms` on the
command line, proving exact-option override before the same real Agent startup. `run-check` loads
providers, verifies managed-path readiness, identity, route policy, sync/update policy, terminal
profiles, and cgroup interfaces without creating the named runtime/state paths. Authority, command,
and incarnation recovery remains intentionally uninvoked and visible in the report; this gate does
not claim a startup, recovery completion, or final PTY-child kernel enforcement.

ADR 0291 adds two owned checks. One commits twenty observations through a sixteen-record signed
tail, verifies exact eviction/reopen, and rejects tampering. The other proves the redacted grammar
does not copy sentinel command/path/device-key material, round-trips the bounded bundle, and rejects
payload mutation. This brings the direct registry to 734. The ordinary one-binary lifecycle also
exports through live local-control v1.49, inspects the result in a fresh CLI process, requires one
mode-0600 single-link regular file no larger than 64 KiB, checks private runtime/state/address strings
are absent, and proves a second export cannot replace the artifact. These gates establish the closed
schema and local redaction path, not recipient-verifiable authorship, rollback resistance, or absence
of activity correlation.

ADR 0292 adds two owned checks for the shared explicit/bare selector grammar, bounded request codecs,
signed canonical one-to-one store, collision refusal, idempotent exact set/remove, atomic rename,
restart, private mode, and tamper refusal. The registry is now 736. The one-binary lifecycle binds
`workstation` to a live peer, proves exact-set retry does not advance generation, uses bare and
explicit alias forms for real action/typing operations, reloads the signed mapping after Agent
restart, removes the transport peer while retaining the name, and releases it only through explicit
retry-idempotent alias removal. This does not prove stable-device discovery, transport-key migration,
invitation acceptance, or any authority grant.

ADR 0293 adds two owned checks for invitation-create request bounds, the fixed 320-byte artifact,
canonical padding, independent signature/artifact hash domains, nonce, stable inviter, full Tox
address, closed capability vocabulary, alias grammar, expiry/skew, pinned identity, and tamper
refusal. The registry is now 738. The one-binary lifecycle creates a private no-clobber artifact,
inspects it without implied trust, dry-imports it with the exact pin, rejects a wrong pin, and starts
a distinct mock Agent identity to accept it. The first acceptance creates one friend and suggested
alias; the exact retry changes neither, while the authority ledger remains empty. This proves the
local ceremony and composition, not out-of-band human identity verification, public-network
delivery, clock integrity, or an authority grant.

ADR 0294 adds two owned tree-v2 time-machine checks, bringing the registry to 740. They create two
successive file revisions, pin and inventory the older record, prove exact candidate and projected-
content diff facts, inspect conflicts, bind a restore plan, reject a dirty worktree and stale token,
then restore old bytes only by creating generation 3 with generation 2 as its predecessor. Exact plan
replay does not create generation 4. A separate missing-object case reports object/byte requirements
and refuses readiness. The live mock-backed Agent test repeats checkpoint, pin, history, diff,
conflict, plan, and apply through local-control v1.52 and the writable automation worktree. These
checks prove forward linkage and optimistic concurrency on one host; they do not prove backup
independence, hardware rollback resistance, hostile-filesystem portability, or remote fleet scale.

The live mock-backed Agent test now inspects a detached retained controller session through local
control v1.48, binds its content-free session/peer/principal/lifecycle coordinates, requests exact
session-and-peer close, and proves the daemon sends RESUME before authenticated CLOSE. The terminal
controller process test closes stdin under `--batch`, requires exactly one PTY EOT input, receives
unmodified output, rejects any operator banner pollution, and returns the remote exit status. These
tests do not claim host-wide inbound-session inventory, arbitrary command execution, or that every
fixed PTY program terminates on EOT.

## ADRs 0337--0339 tree-v2 metadata and projection-recovery gates

The owned registry now covers exact nonmutation and restoration for the
manifest, immutable branch record, mutable branch pointer, workspace state,
and maintenance state. The Agent integration test also proves that
`sync-repair` reports `metadata=verified` only after workspace and
maintenance authentication and refuses a corrupt maintenance record without
rewriting it. The full pinned Nix run reports
`tests=844 selected=844 shard=0/1 failures=0`; all 62 CTest targets pass, with
the five cgroup process gates remaining expected host skips.

The source-linked Sandwurm gate creates a three-node six-edge read/write mesh
inside one networkless KVM guest on ext4, seeds 5 files / 1 directory / 16,411
bytes, and makes workspace plus maintenance records present. With both peers
stopped, it durably flips the final bit in one same-size live record from each
family in this exact order: branch pointer, manifest, immutable branch record,
workspace, maintenance. Each cell requires live `sync-repair` protocol-error
exit 4, exact corrupt-byte retention, clean shutdown, cold Agent startup exit
3 with the family label, a second exact byte-retention check, in-place
operator restoration with file and parent-directory `fsync`, unchanged
identity/worktree, and successful metadata/content verification. The peers
then return and must converge to `[3,3,3]`.

The strict verifier rejects unsafe or oversized JSON, duplicate keys,
unexpected receipt/family fields, an identity incompatible with its receipt schema, incomplete or
reordered families, noncanonical exits, automatic-quarantine claims,
non-networkless launch, non-KVM/non-ext4 substrate, bad completion shape, and
compact-manifest/file-set or digest drift. Compact export projects the
potentially extensible Sandwurm launch records into closed content-free
summaries, is capped at 2 MiB, and retains only five proof records plus its
authenticated manifest.

Source-linked run `mixJ9VUp` passes from commit
`08e4179f7cfeb6448afa2cf5e7b908deb7d3db80` and binary SHA-256
`449107ef7152547ededabd378c6298cda2963169527e2912f79676209fcef5bf`.
The 26,429-ms campaign retains the exact five-file/one-directory/16,411-byte
tree at SHA-256
`1d1c86ea77eadc494258669412902108a02e1e1846ebf7b939bbc6967a12016d`,
converges to `[3,3,3]`, and repairs all three nodes. Both raw and compact roots
pass the strict verifier. The retained content-free proof is
`.sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp`; its five manifested
records total 6,123 bytes and `compact-export.json` has SHA-256
`b0ac88a09ea54f860d575125a8fb79c27f483d9f7f4ba1f7e5a661b4eaf8ffa2`.
See `evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`.

ADR 0338 adds four direct owned checks to the projection exchange boundary.
Test-only seams immediately before real `RENAME_EXCHANGE` and immediately
after it but before projection validation write through a descriptor held from
before the last scan. Selected, excluded, and post-exchange selected writes
cause `protocol_error`, retain the old staged tree and signed pending
workspace, and survive recovery until an explicit forward merge. The same
checks require a canonical current or authenticated-prior projection marker:
marker mismatch cannot hide a selected deletion, and an established tree with
no marker refuses before staging. These are deterministic construction checks,
not a real descriptor/remount qualification. A write after obsolete-tree
validation begins can still race stage removal.

ADR 0340 adds the real descriptor/remount qualification. The
`up-sync-projection-descriptor` Sandwurm gate runs two independent three-node,
six-directed-read/write-share cells in one networkless KVM/ext4 guest. The
first stops the production sync worker at `renameat2` entry for a selected
held descriptor; the second stops at successful `renameat2` exit for an
unselected held descriptor. Both cells require exactly one successful exchange
bound to the exact visible/stage paths, external helper PID/FD/inode
continuity, `sync-repair` protocol-error refusal, retained pending workspace,
explicit salvage, convergence, and repair. The unselected cell additionally
proves ext4 refuses read-only remount while the writable descriptor is open,
then preserves the retained stage across closed-descriptor RO/RW remount and
cold-start refusal. Source-linked run `1fq3WhIY` at commit `e034311` passes the
raw proof, strict descriptor verifier, and VM smoke verifier. Compact proof
`.sandwurm/exports/sync-projection-descriptor/run.1fq3WhIY` independently
replays through the same strict verifier.

ADR 0339 adds three valid-old witness checks and the metadata-corruption v2
construction. Exact older branch, workspace, and maintenance records plus
their matching old local guards are replayed while the external witness keeps
the current semantic root; both live read and cold reconciliation return
`protocol_error` without changing local bytes or witness state. Successful
`sync-repair` renders `rollback-witness=0|1`, distinguishing integrity from
external freshness. Receipt v2 stops every Agent task, writes all five
same-size corrupt roots sequentially while they are co-resident, resumes once,
and requires first-error live refusal, controlled stop, ordered cold-start
peeling, exact restoration, and reconvergence. The harness and strict verifier
are covered by self-tests; source-linked KVM/ext4 run `MG27auOK` at commit
`2be7a2a` now qualifies v2 and its compact proof passes the same verifier.
The accepted rev0050/v1 proof above remains separate one-family-at-a-time
historical evidence. See
`evidence/2026-09-08-sync-tree-v2-co-resident-metadata-corruption.md`.

These gates do not prove automatic repair, independent restore provenance,
complete-frontier freshness without a configured witness, every historical or
non-tree-v2 record family, atomic multi-file storage mutation, a cut during
restoration, remount/open-descriptor behavior, physical power removal,
dishonest storage, backup status, or precious-data suitability.

ADR 0387 adds the person messenger-store slice. Three new direct checks bring
the owned registry to 875. They cover contact-book card floors and
same-generation fork refusal, transcript commit/deduplication for signed
person/group payloads, delegated device receipts, and outbox pending/sent route
accounting. Final qualification from `build/iotox-nix-debug` passes the
875-check direct registry and all 75 CTest entries; the same five delegated
cgroup process tests skip on this host because the required cgroup delegation
is unavailable.

ADR 0390 adds the normal Tox compatibility bridge and a live Toxic gate. The
new `tools/run-toxic-compat-bridge-lab.py` harness starts a fresh source-linked
IoTox daemon and stock Toxic, drives Toxic through first-run and `/myid`,
establishes real friendship over the public Tox network, proves ordinary
normal-Tox text in both directions, and then wraps the observed Toxic inbound
text as a signed delegated bridge observation. The default-route pass sends a
real Toxic `/add` request to IoTox and accepts it from IoTox. The forced-TCP
pass launches Toxic with `-t`, IoTox with `--native-tcp-only`, gives Toxic a
compact lab-local nodes file matching its exact parser, sends IoTox's friend
request to Toxic, and accepts it with stock `/accept`. The passed
founding-machine runs used source-linked IoTox 0.51.0 rev0051 with pinned Toxic
0.15.1, produced `iotox-toxic-compat-live-proof-v1`, committed one inbound
bridge entry, proved duplicate receive idempotence, and generated an outbound
normal-Tox `message-hex` command targeting the actual Toxic public key. The raw
labs contain fresh private savedata and are not committed; see
`evidence/2026-09-19-toxic-compat-bridge.md`.

The stronger ADR 0390 multidevice Toxic gate is
`tools/run-toxic-multidevice-bridge-lab.py`. It starts three independent
source-linked IoTox devices plus one stock Toxic client, friends Toxic to all
three IoTox routes, proves Toxic read receipt plus Toxic-side log/display
evidence for every IoTox route, builds a full A↔B↔C self-route mesh and a
three-route person card, then proves one Toxic inbound normal text observed by
A is live-fanned as a signed bridge observation to B and C. A, B, and C each
then send a delegated normal Toxic bridge message back; each send requires
Toxic read receipt, Toxic-side evidence, sender-side `--bridge-store` commit,
and self-fanout to the other two devices before the payload is committed into
every bridge store. The accepted default-route committed-state
founding-machine replay produced
`iotox-toxic-multidevice-compat-live-proof-v1` at
`/tmp/iotox-toxic-multidev-lab-3camoswk/proof-summary.json`; the accepted
forced-TCP replay produced the same schema at
`/tmp/iotox-toxic-multidev-lab-v1s6aeyu/proof-summary.json`. Both finished with
final per-device status `entries=4`, `inbound=1`, `outbound=3`,
`content-free=1`. The raw labs contain four fresh private Tox savedata profiles
and are not committed.

These Toxic bridge gates prove stock Toxic compatibility for default native
Tox and forced-TCP/native-relay operation only. They do not yet prove the
bridge over `tox/tor` or `tox/i2p`; those remain separate route gates and are
surfaced by `iotox readiness privacy`.

ADR 0413 adds resident-service and messenger-readiness CLI coverage. The human
CLI suite exercises `iotox service plan|render|receipt|status-plan|status-receipt`
for combined Agent/person resident shapes, raw systemd output, MonsterNix
adapter output, explicit receipt acceptance, and service reality receipts that
can satisfy `terminal.service-supervision` in a stable dossier. The same suite
now covers local human-read
state with idempotent `person read-mark`, expected-reader `person read-status`,
matching-store `person transcript-convergence`, and `person group-status`
against a signed group, group transcript, receipt store, and read-state file.
These are UX/readiness gates. The service status receipt covers only the
operator-observed active/enabled/log-reviewed/health-passed/upgrade-passed
service state; it is not proof that a route is healthy, a sync folder is safe,
cgroups/sudo are graduated, or a remote human read a message.

## Current limitations

Passing owned evidence does not establish:

```text
production readiness or independent security audit
formal cryptographic verification
reproducible release artifacts across independent builders
repeatable public bootstrap, DHT, NAT, relay, or packet-loss behavior beyond the retained seeded
Sandwurm construction profile
public-network, reverse-direction, production-fleet, or future-pin rolling upgrades beyond the
retained 0.2.22-to-0.2.23 savedata/product-load and two-Sandwurm-guest live route gates
remote request observation or acceptance outside the named retained genuine-peer fixtures
durable friendship outbox or signed friendship audit
hardware-anchored rollback resistance for all stores or encrypted local metadata
safe expiry or cancellation for physical effects
restart-resumable file objects
Tor/I2P anonymity, actual I2P containment, or long-running/diverse actual-Tor behavior beyond the retained bounded samples
mobile background or constrained-device suitability
daemon-restart survival for PTYs or controller replay state
multiple simultaneous local terminal controller streams
complete two-guest Ratox terminal qualification beyond the founding-machine Sandwurm topology
```
