# Sandwurm two-node IoTox laboratory

Status: independent no-network boots, simultaneous direct-UDP and forced-TCP pair gates, forced-TCP
relay and link interruption/recovery, device-daemon replacement, persisted-disk guest restart,
live 0.2.22-client/0.2.23-device rolling-provider exchange on both native carriers,
genuine single-file synchronization, unclean sync receiver restart, explicit pull cancellation, and
authenticated-epoch disconnect recovery, live receive pause/resume, and persisted sync-publisher
guest restart over both native carriers accepted. Authenticated multi-route sync loss/reassignment,
fixed/adaptive placement, bounded cancellation, and eight-job population/resource cells also pass on
both carriers while Ratox remains on a protected primary. Both exact corresponding auxiliary
readiness orders and both deterministic loss/cancellation orders now pass on both carriers as well.
One-session Ratox heartbeat/PTY observations now also pass the bounded delay/loss/recovery matrix
over direct UDP, forced TCP, and strict generic SOCKS. Authority-private mixed-context operation now
also passes with native primary/native bulk/strict generic-SOCKS bulk routes and signed tree
convergence in both guests.

## Boundary

IoTox network, synchronization, Ratox latency, route-fault, and positive cgroup qualification use
Sandwurm's stock Cloud Hypervisor `vm-strong` lane. The topology is two sibling IoTox NixOS guests
plus one controlled network/relay role when a separate impairment point is needed. The founding
machine is the complete available substrate and the reports name that topology once without carrying
an unavailable-hardware gate.

Sandwurm, rather than ad hoc QEMU/libvirt scripts, owns guest closures, Cloud Hypervisor launch,
prepared-host TAP/NAT, workspace projection, lifecycle control, and receipts. IoTox owns its binaries,
test identities, bootstrap/relay processes, experiment schedule, protocol evidence, and result
analysis.

## Existing Sandwurm front door

These current commands are read-only and safe to use before building the IoTox guest profile.
Set `SANDWURM_ROOT` to the local Sandwurm checkout that owns the host
substrate, for example `../sandwurm` in the public sibling-checkout layout:

```sh
SANDWURM_ROOT=${SANDWURM_ROOT:-../sandwurm}
$SANDWURM_ROOT/sandwurm status --brief
$SANDWURM_ROOT/sandwurm status --why --json
$SANDWURM_ROOT/sandwurm probe --json
$SANDWURM_ROOT/sandwurm doctor substrate --json
$SANDWURM_ROOT/sandwurm next --json
```

The active Sandwurm contract uses a prepared-host internal bridge plus NAT and task-owned TAP devices.
Guest launch must consume its prepared-host declaration and retain Cloud Hypervisor launch/live-chain
receipts. We do not bypass a blocked IoTox-profile readiness result with ambient host commands.
Before starting the pinned Tox bootstrap/relay fixture, the pair runner restores and exactly verifies
the prepared bridge's `10.0.0.1/24` address, then requires the fixture's TCP listener to become
reachable. This makes a carrier-induced address loss an immediate lab preflight failure instead of a
guest connection timeout.

The 2026-08-20 read-only probe found writable KVM, the prepared-host and runner-authority
declarations, Cloud Hypervisor/ch-remote/virtiofsd, and a substrate classification of
`ready-for-live-plan-review`; it launched no VM. The ambient binaries identify as Cloud Hypervisor
v52, while Sandwurm's current reviewed direct-runner policy may select a different pinned toolchain.
The IoTox lab therefore consumes the exact Sandwurm-built toolchain rather than assuming host `PATH`
is the selected VMM. Sandwurm's global `status --brief` can remain blocked by unrelated provider or
nesting campaigns; only an IoTox-profile plan/readiness receipt decides this lab's launch gate.

## Implemented IoTox-owned VM front door

The thin repository tool composes Sandwurm and never becomes another VM implementation:

```sh
./tools/iotox-sandwurm-lab.sh preflight
./tools/iotox-sandwurm-lab.sh build client
./tools/iotox-sandwurm-lab.sh build device
./tools/iotox-sandwurm-lab.sh up client
./tools/iotox-sandwurm-lab.sh up device
./tools/iotox-sandwurm-lab.sh up-pair direct-udp
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp relay-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp daemon-restart
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp link-interruption
./tools/iotox-sandwurm-lab.sh up-pair direct-udp packet-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp packet-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp provider-rolling
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp provider-rolling
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp guest-restart
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p baseline \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p i2p-router-restart \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-i2p i2p-service-restart \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-i2p-payload \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content-same-source-lanes
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-content-same-source-multi-route-actual-tor IP:PORT:64_HEX_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content-ratox-cap-2-sla
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-multi-source
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content-multi-source-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-content-multi-route-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
# Research/falsification gate; forced-TCP multi-source is not yet qualified.
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content-multi-source
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-retry
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-retry
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
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-disconnect
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-disconnect
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh up-pair direct-udp mutable-profile-status
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp mutable-profile-status
./tools/iotox-sandwurm-lab.sh up-pair direct-udp signed-update
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp signed-update
./tools/iotox-sandwurm-lab.sh up-pair direct-udp update-service
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp update-service
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-idle
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-impairment
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair tox-tor ratox-route-loss
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-cli-reconnect
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-cli-reconnect
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-payload \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-private-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-loss \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-soak \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-adversary \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-stripe-recovery-32
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-stripe-live-loss-32
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-stripe-protected-live-loss-24
./tools/iotox-sandwurm-lab.sh status client
./tools/iotox-sandwurm-lab.sh status device
./tools/iotox-sandwurm-lab.sh verify device PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT relay-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT daemon-restart
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT link-interruption
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT guest-restart
./tools/iotox-sandwurm-lab.sh verify-pair tox-i2p PROOF_ROOT baseline
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-corrupt-basis
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-range-retry
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-range-retry
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
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-file-disconnect
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-file-disconnect
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT sync-tree-control-replay
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT mutable-profile-status
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT mutable-profile-status
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT signed-update
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT signed-update
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT update-service
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT update-service
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT ratox-idle
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT ratox-route-impairment
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-route-impairment
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor PROOF_ROOT ratox-route-impairment
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT ratox-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor PROOF_ROOT ratox-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT ratox-cli-reconnect
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-cli-reconnect
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT sync-tree-route-private-mixed
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-stripe-recovery-32
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT ratox-stripe-protected-live-loss-24
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp PROOF_ROOT provider-rolling
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp PROOF_ROOT provider-rolling
./tools/iotox-sandwurm-lab.sh export-provider-rolling PROOF_ROOT
./tools/iotox-sandwurm-lab.sh up-sync-projection-descriptor
./tools/iotox-sandwurm-lab.sh verify-sync-projection-descriptor PROOF_ROOT
```

`up` is currently a bounded boot/receipt/exit gate, not a persistent background machine. It fails
unless the Sandwurm live chain reaches `guest-evidence-observed` and the IoTox verifier confirms the
role, product identity, binary digest shape, KVM, cgroup v2, complete generic receipts, observed VMM
exit, `network_class=none`, and absence of a Cloud Hypervisor `--net` argument. Git-backed flake
projection excludes ignored runtime FIFOs and other ambient Sandworm state. `.sandwurm/lab/` is the
ignored local proof root.

Superseded proof roots are audited and pruned through `tools/clean-workspace.py`; tracked evidence
references are protected automatically and the newest undocumented root per role/class is retained.
See `workspace-retention.md` for the dry-run and explicit-apply contract.

`up-pair` runs two Sandwurm live chains concurrently, with distinct `vm-iotoxc` and `vm-iotoxd`
TAPs on the prepared `sandwurm-vm` bridge. It copies the private reusable identity baseline into
fresh guest disks, removes the workspace copies after guest intake, exchanges only public Tox
addresses through owner-only rendezvous files, proves both TAPs exist simultaneously, waits for a
confirmed IoTox session and bidirectional text, and emits one content-free manifest. The ignored
proof root still contains private writable guest disks and a temporary bootstrap key and must not be
shared as though it were the receipt.

After acceptance, `tools/export-sandwurm-pair.py PROOF_ROOT` creates an atomic compact export beneath
`.sandwurm/exports/pairs/`. It first verifies the private source, copies only the scenario-specific
allowlist consumed by the pair verifier, records every retained digest plus the original manifest
digest and omitted-private classes, then reverifies the export. Only then may the original private
proof become a cleanup candidate. Baseline compact exports are approximately 96 KiB rather than
2.3 GiB per pair cell; custom partial-loss exports allocate about 152 KiB. Ratox route-impairment
exports retain separate 120-row heartbeat and terminal captures and allocate about 372 KiB on native
routes or 1.7 MiB when strict SOCKS packet/audit evidence is included. Ratox route-loss exports add
the joined lifecycle plus detached-host evidence and allocate about 228 KiB on native routes or
1.3 MiB with strict SOCKS packet/audit evidence.
The mixed private-route export retains both packet captures, proxy audit, exact route/authority guest
receipts, and source-linked VMM chains while omitting all disks, identities, bootstrap secret, and
runtime state; accepted `pair.z948jeii` allocates 3,727,360 bytes and independently reverifies.

The distinct `sync-tree-route-private-actual-tor` scenario keeps the native primary and first bulk
worker on the private fixture, then carries each role's second exact-key bulk worker through its own
host Tor client. The operator must provide one reviewed public IPv4 Tox bootstrap/TCP-relay record;
the runner does not fetch or silently replace it. Client and device use separate Tor data
directories, processes, control sockets, source-only SOCKS policies, and circuit populations.
Acceptance joins authenticated Tor STREAM and CIRC events from each exact guest source to the
operator-supplied target and a built three-or-more-hop circuit, proves distinct Tor-owned public
sockets, independently decodes both TAP captures, and still requires the normal private-v2 route
readiness plus signed 4,194,389-byte tree convergence. Compact export retains the packet captures,
Tor event/config/status projections, and normal pair receipts while omitting both Tor data
directories and all private IoTox state. Accepted compact proof `pair.2mycvy9n` allocates 3,764,224
bytes, records two successful target streams and a distinct three-hop `CONFLUX_LINKED` circuit per
role, confines 583/531 Tor proxy packets with zero unexpected context packets, and independently
reverifies. It proves actual-Tor member readiness in the converged application topology, not that
the tree object payload was scheduled over Tor (ADR 0203).

The separate `sync-tree-route-private-actual-tor-payload` cell uses the founding reusable route-key
ordering to make the Tor member the fixed scheduler's first eligible carrier. It fails if that key
ordering changes and accepts only when the completed client job names the exact Tor member with
zero reassignment. Its bounded initial-pull admission retry records attempts, failures, and a
content-free first-error digest instead of hiding WAN/control transients. This qualification seam
adds no production route-forcing control. Accepted compact proof `pair.lzsyitvy` completes the
signed 4,194,389-byte tree on that exact Tor member with zero reassignment, first-attempt admission,
distinct three-hop circuits, and zero unexpected TAP context packets (ADR 0204).

The external-loss cell starts from the same exact Tor carrier but stops only its host Tor process
after at least 65,536 live object bytes. It holds Tor down until the client proves one carrier loss
and reassignment, then restarts the same binary/configuration and requires the carrier to return
without restarting its IoTox route worker. Pre-loss/recovered PIDs, authenticated Tor control and
circuit records, the host loss interval, guest route counters, completed signed tree, and both TAP
captures enter the strict compact proof. Accepted `pair.iompvehf` faults at 74,034 bytes, records
one loss, one native reassignment, two stale terminals, one real carrier recovery, two ready bulk
members, and zero route-worker restarts, then independently reverifies three Tor phases and zero
unexpected-context packets on both TAPs (ADR 0205).

The terminal-specific `ratox-route-actual-tor-loss` cell instead places each primary IoTox agent
behind its own actual Tor client. After initial terminal progress it kills only client Tor, observes
heartbeat warning before authoritative offline, snapshots one detached live device PTY, restarts
the identical Tor instance, and requires explicit generation-2 resume of the same session and host
incarnation. Its compact allowlist retains raw terminal/heartbeat/loss records, device host-loss
state, three authenticated Tor phases, process-loss identity, both TAP captures, guest receipts, and
source-linked VMM chains. Accepted compact proof `pair.2waqdpgk` binds a real client Tor `SIGKILL`,
one detached live PTY, exact-session generation-2 resume, zero IoTox daemon restarts, and TCP-only
TAP containment (ADR 0206).

The companion `ratox-route-actual-tor-soak` scenario keeps both Tor and IoTox processes alive. One
terminal performs 120 heartbeat/PTTY samples at one-second intervals; after samples 20 and 100 the
host closes the exact client then device application circuit through authenticated Tor control. Its
raw/compact verifier requires requested-close ordering, same-ID stream reattachment or new-ID stream
reopening on a distinct qualifying circuit, unchanged process/control/session identities, contiguous byte sequences, and TCP-only TAP
containment. Live science observed both carrier-loss and no-error attempts; the revised cell sends
post-replacement PING and accepts only unchanged-epoch/generation PONG or exact `unavailable` plus
higher-epoch explicit resume of the same session/incarnation/PTY. Accepted compact proof
`pair.k8o54n2v` exercises both branches across all 120 samples with zero Tor/IoTox/guest restarts
(ADR 0207).

Accepted repetition `pair.9cx0jels` runs the same command and contract through a distinct public Tox
record. Both exact Tor streams reopen, both Ratox checkpoints remain same-epoch/generation
continuous, and all 120 samples plus TCP-only containment reverify (ADR 0208). The two sequential
runs do not constitute exit/time diversity or an availability claim.

`ratox-route-actual-tor-adversary` inserts one bounded numeric interposer between each guest and a
loopback-only Tor SOCKS endpoint. After exact initial PTY progress, the host holds only the client
interposer's established relay bytes. The gate requires that listener reachability and a fresh
exact-target SOCKS CONNECT remain positive, then independently requires Ratox heartbeat warning,
c-toxcore authoritative offline, typed local unavailability, and one detached live PTY. Removal of
only the hold file must recover a higher epoch and explicit exact-session resume; Tor, interposer,
IoTox, guest, session, incarnation, PTY, and retained byte identities may not be replaced. Every
interposer upstream source port is joined to authenticated Tor STREAM/CIRC evidence, and both TAPs
must remain TCP-only to the role's bridge interposer. Accepted compact proof `pair.vx6z0csh`
records warning at 2.578 seconds, offline at 27.241 seconds, exact generation-2 resume, and zero
process restarts or route escape (ADR 0209).

The `update-service` scenario extends the signed-update cell with policy-v3 kind binding and the real
sealed Linux service adapter. The device uses a distinct release-role identity, publishes a padded
native service image, and remotely stages it through the ordinary authority-gated command. The
client then exercises pre-readiness service death, Agent `SIGKILL` plus helper parent-death,
health-expiry rollback, exact readiness/confirmation, and confirmed-service recovery. Each receipt
must report six Agent restarts, three rollbacks, every service observation, kind
`linux-service-v1`, and a sealed image. Accepted compact direct UDP `pair.pwpgv4si` and forced TCP
`pair.rntpawny` allocate 147,456 bytes each and independently pass the strict verifier. See
`evidence/2026-08-27-sandwurm-linux-service-update.md`; the cell does not simulate an abrupt VMM or
host power cut.

The qualification-only `provider-rolling` scenario uses
`tools/export-sandwurm-provider-rolling.py` and its matching strict verifier because it proves a
provider wire boundary rather than an IoTox authority session. Both identities and mutual friendships
originate under exact 0.2.22; the client remains on 0.2.22 and the device runs 0.2.23. The guest
receipts require bilateral fixed-message exchange, exact friend-route truth, live-provider rewrite,
and identical old/current semantic readback. Its 96 KiB compact allowlist preserves the two guest
receipts, Sandwurm chains, planned launches, and bound manifest while omitting provider savedata and
all other private classes (ADR 0153).

The optional `relay-restart` scenario is valid only for forced TCP. Both guests must first report a
confirmed TCP session and exchange text. The runner then kills the complete relay process group and
will not restore it until both guests independently report the application session and transport
peer offline. It restarts the fixture from the same private state, requires the public relay key to
remain identical, and accepts recovery only when both sessions are confirmed over TCP at a strictly
higher online epoch and fresh text crosses in both directions. A live relay process, successful
bootstrap call, or one-sided reconnect is insufficient evidence.

The `daemon-restart` scenario keeps both VMs and the bootstrap/relay fixture live. After both guests
confirm and exchange text, it cleanly stops only the device IoTox process. The stable client must
observe both its application session and transport peer offline before the runner starts a new IoTox
process from the same savedata. The exact device Tox address must survive, the client epoch must
strictly advance, both sides must establish a fresh confirmed session on the requested route, and
fresh text must cross in both directions. The restarted process's local epoch begins independently;
only the continuously running client's epoch supplies cross-incarnation ordering. This gate does not
claim that a Ratox PTY or local terminal controller survives daemon replacement.

The `link-interruption` scenario keeps both TAP carriers and every process live while replacing each
task-owned TAP's root qdisc with `netem loss 100%`. Only after both guests report transport and
application-session offline does the runner delete the impairment and restore the host's default
qdisc. Both peers must then confirm on the requested route at strictly higher online epochs and
exchange fresh text. A rejected preliminary mechanism lowered and raised the TAP carriers; Cloud
Hypervisor did not recover guest reachability after carrier restoration, so carrier toggling is not
the laboratory's link-loss primitive. The accepted packet-blackhole mechanism is also the foundation
for later seeded partial-loss, delay, reorder, and queue profiles.

The `packet-loss` scenario is the continuity complement to that outage gate. After both sessions are
confirmed, the runner installs independent random 5% `netem` loss on the two task-owned TAP egress
paths with fixed seeds. Each guest concurrently emits 128 exact 1,200-byte lossy custom probes at
5 ms spacing, retains every result row, and exchanges ordinary text before impairment removal.
Acceptance requires positive packet and drop counters on both qdiscs, no locally rejected probe, a
complete unique ordinal inventory, at least one delivery per role, an unchanged confirmed online
epoch, and fresh text after the default qdiscs are restored. Direct UDP must expose at least one
application-level lossy-carrier miss per role. Forced TCP may expose none only because its qdisc still
proves lower-layer drops; TCP retransmission is part of the observation. This custom echo remains
laboratory traffic, not Ratox framing or a latency SLA. See ADR 0151 and the retained 2026-08-24
evidence record.

The `ratox-route-impairment` scenario measures the actual terminal path rather than the custom echo.
After one authority-bound Ratox OPEN it records 20 baseline, 80 impaired, and 20 recovered samples.
Every sample completes one exact Ratox PING/PONG followed by one PTY byte echo; separate captures
retain the timestamps, byte sequences, stable session identity, and Agent queue/render observations.
During the middle phase both TAP egress paths carry independent seeded
`netem delay 75ms 15ms loss 2%`; acceptance requires positive packet/drop counts and exact qdisc
removal before recovery. Direct UDP, forced TCP, and strict generic SOCKS compact proofs are
`pair.tscy1yrt`, `pair.gf5mxexc`, and `pair.p3dt6g9c`. The last also requires packet containment and
proxy audits. `tools/analyze-ratox-route-impairment.py` independently rechecks the measurement schema
and computes phase statistics. See ADR 0196 and
`evidence/2026-08-27-sandwurm-ratox-route-impairment.md`. This gate freezes partial impairment as
warning-only; it does not exercise total loss, resume, migration, or actual Tor.

The `ratox-route-loss` scenario is the mutation-policy complement. It opens one authority-bound
Ratox PTY, proves one heartbeat and byte echo, then applies independently seeded `netem loss 100%`
to both task-owned TAP egress paths. A two-second PING deadline must expire while the controller
still observes the original confirmed carrier and epoch. The gate then waits for c-toxcore's
authoritative peer-offline transition and exact local `unavailable` outcome. Before restoring the
route, it asks the device guest to capture one live/running, zero-attached PTY and the matching
`peer-detached` event.

After exact qdisc removal, the controller must observe the same peer confirmed and authority-capable
at a higher epoch. It uses `resume_only` for the prior session and accepts only the same session ID
and process incarnation, generation one-to-two, exact byte position two, then a new PONG and byte
echo. The strict-SOCKS row retains the same zero-bypass packet and proxy-audit requirements as the
impairment row. Accepted compact proofs are `pair.0cnril1l`, `pair.qoty7j1x`, and `pair.8jjawnwp`;
`tools/analyze-ratox-route-loss.py` rechecks their joined measurements. ADR 0197 freezes explicit
higher-epoch resume and rejects automatic mutation from a heartbeat miss. Generic SOCKS is not Tor.

The `ratox-cli-reconnect` scenario composes that fault seam with the public production client. One
pseudo-terminal executes the real `iotox terminal PEER --reconnect`; the probe never speaks the
private terminal socket. It binds one PID plus process start ticks, one session/incarnation, exact
input/output sequences, healthy production heartbeats, the warning-before-authoritative-offline
split, retained zero-attached host state, retry attempts, higher authenticated epoch, generation
1-to-2, local `~d`, and exit status zero. Direct-UDP compact proof `pair.h3wylill` and forced-TCP
proof `pair.6bf75b_4` pass independent export verification. See ADR 0300 and
`evidence/2026-09-02-sandwurm-ratox-cli-reconnect.md`. This is one-loss route continuity, not Agent-
restart persistence or a repeated-loss soak.

The additive `ratox-cli-reconnect-repeated` scenario retains that legacy receipt and performs two
ordered 100% loss intervals in one production CLI process. It requires terminal progress and a
healthy heartbeat between faults, distinct seeds and positive drops on both TAPs, the same retained
session/incarnation, and generations 1-to-2-to-3. Accepted native-carrier evidence is in
`evidence/2026-09-03-sandwurm-ratox-cli-reconnect-repeated.md`. It is bounded repeated-loss evidence,
not a duration or overlay-route claim.

The `guest-restart` scenario asks the device guest to reboot after a clean IoTox stop and durable
phase checkpoint. Cloud Hypervisor cannot reconnect this profile's virtiofs backend in place, so the
first VMM exits with a bounded, verifier-bound failure. The runner starts a second Sandwurm chain from
the exact first prelaunch/runtime-root receipt: the persisted writable disk is reused and host identity
injection is not repeated. Acceptance requires a changed device boot-ID hash, unchanged client boot-ID
hash, exact device Tox identity, stable-client offline observation and epoch advancement, a fresh
confirmed route, and post-restart text both ways. Both Sandwurm epochs enter compact evidence.

The `sync-file` scenario is the first genuine synchronization S3 cell. Each guest creates a local v3
authority ledger with only the opposite one-way synchronization capability, while both strict
namespace records pin the stable publisher and subscriber principals. The device publishes a
canonical range-v1 index for a deterministic 4 MiB file and the client pulls the artifact and index
through request-selected Tox FileIds. Acceptance requires exact artifact, index, and signed-HEAD
identity on both guests, accepted-HEAD-last ordering, no implicit activation, and an explicit
exact-token activation. The independently reverified compact direct-UDP and forced-TCP observations
are `.sandwurm/exports/pairs/pair.uppm28y8` and `.sandwurm/exports/pairs/pair.7ufrcjtg`; exact digests
and nonclaims live in `evidence/2026-08-21-sandwurm-sync-file.md`.

The `sync-tree` scenario uses the same authority, object, HEAD, transfer, and explicit-activation
ordering for signed engine `treepack-v1`. The device publishes a deterministic owner-only tree with
three directories and three files, including a 4 MiB payload, an executable probe, nested content,
and an empty directory. Both roles require the same canonical treepack/index/HEAD identities. The
client additionally verifies exact contents, entry counts, no symlinks, frozen file/directory modes,
an atomic relative `materialized-trees/current`, and an idempotent exact retry. Independently verified
compact direct-UDP and forced-TCP observations are `.sandwurm/exports/pairs/pair.qf7x57c7` and
`.sandwurm/exports/pairs/pair.kjr7ksxw`; exact bindings, one disclosed pre-product VM startup flake,
and nonclaims live in `evidence/2026-08-24-sandwurm-sync-tree.md`.

The `sync-content` scenario moves one 4 MiB paged content-v2 revision from one complete source over
both direct UDP and forced TCP. `sync-content-same-source-lanes` keeps that one-source topology,
sets the signed namespace lane cap to two, starts the client with `--max-sync-content-lanes 2`, and
requires a live snapshot with two admitted non-root object lanes, distinct request IDs/FileIds, and
one exact source before ordinary convergence and activation. Accepted compact proofs are
`.sandwurm/exports/pairs/pair.895m5lwy` for direct UDP and
`.sandwurm/exports/pairs/pair.bcecui0l` for forced TCP. The first forced-TCP attempt reached no
content work because the new scenario inherited the generic 240-second host authority deadline;
the accepted rerun uses the same 480-second bound as the established forced-TCP content gate. See
ADR 0262 and `evidence/2026-08-30-sandwurm-sync-content-same-source-lanes.md`.

This lane scenario proves independent object concurrency on one Tox session. It does not prove byte
striping, multiple carriers, physical-path diversity, or better throughput.

## Same-source exact-carrier content gate

`sync-content-same-source-multi-route-actual-tor` holds one stable principal, native primary
authority/HEAD session, signed revision, and default-one content lane constant while repeating that
source selector in one `sync-pull-multi-route` request. The client must atomically bind the two
occurrences to distinct ready `tox/tor` route keys and worker incarnations before HEAD dispatch.
Both paths must complete availability, commit positive immutable-object bytes, converge the exact
artifact/HEAD, and activate explicitly. Equal route-local friend numbers are expected and must not
alias the paths.

Run and replay the accepted construction with:

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-same-source-multi-route-actual-tor \
  205.185.115.131:33445:3091C6BEB2A993F1C6300C16549FABA67098FF3D62C6D253828B531470B53D68

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.iiuhmhy0 \
  sync-content-same-source-multi-route-actual-tor
```

The accepted compact proof allocates 14,811,136 bytes. Its custom record binds one principal and
authority tuple, two source-path IDs, two route keys, two worker IDs, two local `friend=0` values,
four answered availability requests, and path contributions of 272 and 4,194,560 bytes. Both TAP
captures retain zero unexpected-context packets. The verifier recomputes the carrier-set digest and
requires positive contribution on both paths.

Each guest has one Tor process and both worker identities target the same public Tox relay. The
scenario therefore qualifies logical whole-object distribution, not byte striping, equal placement,
throughput gain, independent circuits/exits/physical links, transparent failover, or automatic
carrier policy. Exact path loss remains whole-job failure. See ADR 0269 and
`evidence/2026-08-31-sandwurm-sync-content-same-source-multi-route.md`.

`sync-content-lane-science` measures that missing single-session throughput boundary. It keeps one
cap-8 client process and one authenticated Tox session stable, publishes the same deterministic
8 MiB/24-chunk graph into one base and three isolated namespace roots, and signs the effective lane
and outstanding-request ceilings to `1`, `2`, `4`, and `8`. The client-side 4 Mbit/s shaping is unchanged.
Each compact proof retains a summary TSV plus four fresh process-resource intervals. Accepted proofs
are `.sandwurm/exports/pairs/pair.amcrp0_3` (direct UDP) and
`.sandwurm/exports/pairs/pair.805kzu4a` (forced TCP). The forced-TCP cell peaks at cap 4; the direct
cell is non-monotonic. ADR 0263 therefore retains default one and treats cap 4 only as a candidate
bulk setting pending repeated and competing Ratox-latency evidence. See
`evidence/2026-08-30-sandwurm-sync-content-lane-science.md`.

`sync-content-lane-science-reverse` is the exact order counterbalance. Its base namespace is signed
to cap 8 and its retained summary order is `8,4,2,1`; the ordinary scenario remains `1,2,4,8` with
base cap 1. The already-signed base HEAD supplies the initial-cap publication record, so both cells
pack only the three counterphase roots. Accepted current-code pairs are `pair.t6b6exf1` and
`pair.ku2fxml0` for direct UDP, plus `pair.70p2plez` and `pair.o_6q_m1n` for forced TCP.
`tools/analyze-content-lane-counterbalance.py` strictly verifies and aggregates an equal number of
both orders per carrier into `artifacts/rev0045/content-lane-counterbalance.json`. ADR 0266 keeps
default one, recommends explicit cap 2 for efficient mixed/relay-heavy bulk, cap 4 for fixed direct
UDP, and cap 8 only for stress qualification. See
`evidence/2026-08-31-sandwurm-sync-content-lane-counterbalance.md`.

`sync-content-restart-cap-2` and `sync-content-restart-cap-4` stop only the subscriber Agent with
`SIGKILL` after the exact number of non-root lanes is live and every c-toxcore transport temporary
has positive bytes. On startup the client must preserve the exact complete CAS inventory, remove
all exact private transport temporaries, retain no canonical partial, accept no old HEAD, and
activate nothing. After both roles report independently recovered application authority, a host
barrier permits one distinct pull to converge and activate. Accepted compact proofs are
`.sandwurm/exports/pairs/pair.8j7v2irm` and `.sandwurm/exports/pairs/pair.9q9hsx40` for direct UDP,
plus `.sandwurm/exports/pairs/pair.8ulddb9t` and `.sandwurm/exports/pairs/pair.ol5goyug` for forced
TCP. ADR 0267 qualifies complete-object reuse and fail-closed fencing, not partial-prefix resume,
same-job continuation, power loss, I2P, or byte striping. See
`evidence/2026-08-31-sandwurm-sync-content-restart.md`.

`sync-content-ratox-latency-science` composes that lane gate with one persistent terminal rather
than opening a new session per phase. One 720-sample attachment spans caps 1, 4, and 8 with exact
240-row segments and pauses while the cap-2 transfer-only control runs. Every measured segment
contains a completed pre-transfer echo and at least 20 genuinely overlapping samples. Accepted
compact proofs are `.sandwurm/exports/pairs/pair.af873531` (direct UDP) and
`.sandwurm/exports/pairs/pair.a3nglkh3` (forced TCP). They bind one session, one Tox epoch, the exact
carrier, all content/resource evidence, and independently reproduced latency percentiles. ADR 0264
keeps default one and rejects cap 8 as a latency-sensitive default candidate on this evidence. The
counterbalance and fresh post-bulk OPEN gates are now closed separately by ADRs 0266 and 0265. See
`evidence/2026-08-30-sandwurm-sync-content-ratox-latency.md`.

`sync-content-ratox-cap-2-sla` closes the missing measured phase with one 960-sample attachment over
ordered caps `1/2/4/8`. Before either carrier run, ADR 0268 freezes cap-two requirements of at least
40 exact-overlap rows, p50/p95/p99/max no greater than 250/500/1,000/1,500 ms, and owner-queue p95
no greater than 10 ms. The guest and host verifier independently enforce those exact constants.
Compact proofs `.sandwurm/exports/pairs/pair.rpblreul` (direct UDP) and
`.sandwurm/exports/pairs/pair.rwiyixfh` (forced TCP) pass. Cap four and cap eight miss the p95
ceiling in both cells, so default one remains and explicit cap two alone becomes the bounded native
interactive-bulk construction profile under the existing 4 Mbit/s shaping. See
`evidence/2026-08-31-sandwurm-sync-content-ratox-cap-2-sla.md`.

`sync-content-ratox-post-bulk-admission` closes the distinct fresh-controller question. It samples
authenticated readiness before the cap-8 transfer, records exact reliable-completion monotonic time,
then makes a new OPEN the next terminal operation. OPEN must be sent within one second and OPENED must
return within five seconds without carrier or epoch change; the fresh session must then complete 40
ordered echo/render/ACK samples. Accepted compact proofs are
`.sandwurm/exports/pairs/pair.614f4nje` (direct UDP) and
`.sandwurm/exports/pairs/pair.oengulmm` (forced TCP). See ADR 0265 and
`evidence/2026-08-30-sandwurm-sync-content-ratox-post-bulk-admission.md`.

`sync-content-multi-source` adds a third IoTox agent in the device VM,
independently authorizes both publishers, and partitions distinct physical chunk digests between
them. The direct-UDP cell passes only when both sources answer exact availability and contribute
objects before reconstruction, HEAD-last acceptance, and explicit activation; its compact proof is
`.sandwurm/exports/pairs/pair.u80_yp7r`. Four logical chunk positions contain only two distinct
physical digests, so the fixture derives inventory from the authenticated paged graph and records a
3/1 logical-source split rather than assuming four CAS files.

The same multi-source scenario remains a deliberate fail-closed forced-TCP research gate. Its host
runner starts a second independently keyed c-toxcore fixture on port 33446. The retained strongest
harness registers the subscriber on relays A+B, the primary publisher on A, and the secondary
publisher with bootstrap A plus relay B. Admission is primary-before-secondary; the device
pre-accepts each reviewed reusable key while the client supplies the corresponding complete Tox
address for rendezvous. Thirteen bounded cells established that relay count/order, isolated pending
requests, mutual known-key pre-provision, and A/B placement do not keep the secondary usable. The
strongest hybrid briefly passed exact TCP/session confirmation, then stayed offline for the full
300-second authority window before content transfer. A failure is not an accepted pair manifest or
compact proof. Do not replace session/authority assertions with host socket counts. See ADR 0255 and
`evidence/2026-08-30-sandwurm-sync-content-multi-source.md` before changing this topology or its
deadlines.

`sync-content-multi-source-loss` is the destructive direct-UDP companion. The client begins with
`sync-pull-multi`, which authenticates and registers both publishers before dispatching the primary
HEAD. After the secondary receives at least one object request, the host stops that exact Agent. The
old job must fail whole, clean transient staging/CTA1 state, and retain neither accepted HEAD nor
activation. The same secondary Tox/signing identity then restarts, advances from authenticated epoch
1 to 2, and participates in a distinct explicit atomic pull. Both publishers must answer availability
and contribute objects before reconstruction and explicit activation.

The complementary-store fixture copies one valid stable-device-signed revision to the secondary,
but the secondary is not that revision's local writer. `sync-replica-import` verifies the original
signature and complete manifest graph, then places a fixed device-custody envelope only under
`replica-heads`; `published-heads` must remain absent. After selected-source failure the secondary
cold-starts directly from that partial store, and `sync-gc sandwurm-file dry-run` must report complete
traversal, consistency, and zero candidates before network recovery. There is no post-start HEAD
injection. Exact import and restart checkpoints are retained in raw and compact proof
`.sandwurm/exports/pairs/pair.w_ws202c`. ADRs 0256 and 0257 plus
`evidence/2026-08-30-sandwurm-sync-content-replica-restart.md` preserve the boundary.

`sync-content-multi-route-actual-tor-loss` is the routed destructive companion to ADR 0259. It
retains both native publisher authority sessions and both exact Tor workers, then starts the client
with `--qualify-route-stop-after-bytes 65536 --qualify-route-stop-worker KEY`, where `KEY` is the
second signed bulk member. The first job must report positive committed/fetched progress and exact
auxiliary-carrier loss, then clean transient staging without accepting HEAD or activation. The same
job may not downgrade, reassign, or rebind. The exact route must return under a different worker
incarnation after one restart while both native session epochs remain unchanged; only a distinct
explicit `sync-pull-multi-route` may converge. The host kills no Agent, Tor process, or VM in this
cell. Accepted compact proof `.sandwurm/exports/pairs/pair.w31xqgd_` and its nonclaims are recorded in
ADR 0260 and `evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss.md`.

ADR 0261 repeats the identical cell through a second compiled public relay record as accepted compact
proof `.sandwurm/exports/pairs/pair.i8ar90tx`. The strict verifier initially rejected the derived
host manifest because one copied scenario allowlist emitted a zero head-fenced role count while both
guest receipts recorded true. Every common loss field now uses one frozen
`CONTENT_MULTI_SOURCE_LOSS_SCENARIOS` set; only that derived count was rebuilt, after which both raw
and compact roots verified. See
`evidence/2026-08-30-sandwurm-sync-content-actual-tor-loss-second-relay.md`. This is bounded relay-
record repetition, not independent exit/time-window/physical-path or long-running qualification.

The `sync-file-range` scenario advances that baseline through a real successor. The client first
pulls and explicitly activates the complete deterministic 4 MiB generation 1. The publisher changes
one bounded region and signs a parent-linked generation 2. The client must negotiate
`state-sync-ranges-v1`, verify the new manifest before planning, fetch fewer bytes than the artifact,
reconstruct the exact target from its accepted basis plus the range bundle, accept the HEAD last, and
activate only the exact generation-2 token. Both guest receipts must agree that reused plus fetched
bytes equals the target size. The retained direct-UDP and forced-TCP exports are
`.sandwurm/exports/pairs/pair.b2l3yof_` and `.sandwurm/exports/pairs/pair.uketizc_`; exact bindings and
nonclaims live in `evidence/2026-08-22-sandwurm-sync-range.md`.

The `sync-file-corrupt-basis` scenario repeats the two-generation sequence but corrupts the client's
exact generation-1 basis in place before the successor pull. It preserves file shape, proves the
digest mismatch, requires `range-fallback=1` with zero claimed range reuse, fully verifies and
activates generation 2, and proves the corrupt old path was not silently deleted or replaced. The
independently reverified direct-UDP and forced-TCP exports are
`.sandwurm/exports/pairs/pair.1fyi5byu` and `.sandwurm/exports/pairs/pair.9tkvsybe`; exact bindings and
nonclaims live in `evidence/2026-08-22-sandwurm-sync-corrupt-basis.md`.

The `sync-file-range-retry` scenario uses a 1 MiB changed region and rate shaping so the client can
cancel the first range attempt through the public generic file-control entrance after positive
progress. It requires exact cleanup/fencing before the unchanged range plan is issued under a fresh
FileId, then requires 3 MiB local reuse, a complete new 1 MiB fetch, exact reconstruction,
accepted-HEAD-last ordering, and explicit activation. Failed-prefix bytes are counted separately and
never reused. The independently reverified direct-UDP and forced-TCP exports are
`.sandwurm/exports/pairs/pair.phkpgx90` and `.sandwurm/exports/pairs/pair.4r5xzja_`; exact bindings and
nonclaims live in `evidence/2026-08-22-sandwurm-sync-range-retry.md`.

The `sync-file-repair` scenario starts from an explicitly activated deterministic 4 MiB revision.
The client overwrites and fsyncs the first 4 KiB of the exact artifact object, proves its digest no
longer matches its strict filename, and invokes the public `sync-repair` command. Only that object may
move into private quarantine; the accepted-HEAD and activation records must remain byte-identical.
An explicit pull of the same signed revision must restore the exact digest path while retaining the
quarantine copy. A second repair scan must verify both final objects and report no new quarantine
effect. Independently reverified direct-UDP and forced-TCP exports are
`.sandwurm/exports/pairs/pair.gzgjsiqq` and `.sandwurm/exports/pairs/pair.hkwzsf05`; exact bindings and
nonclaims live in `evidence/2026-08-23-sandwurm-sync-repair.md`.

The same scenario now appends the quarantine-only GC acceptance gate after repair recovery. Both
guests independently refuse a real bind mount over `objects`, preserve two outside-root sentinels,
dry-run one valid 32 KiB unreachable object, move that exact inode with both directory fsyncs, and
observe an empty retry. `purge=disabled` is required in every successful response. The accepted
compact observation is `.sandwurm/exports/pairs/pair.ci0p3t6f`; exact bindings and nonclaims live in
`evidence/2026-08-24-sandwurm-sync-gc-quarantine.md`.

The `sync-file-restart` scenario is the first genuine synchronization fault cell. It publishes a
deterministic 8 MiB revision, rate-shapes the client TAP, and waits for authoritative c-toxcore
receive position before killing the client IoTox daemon with `SIGKILL`. Before restart it requires
exit status 137, two exact private transport temporaries, a signed active-attempt journal, and no
accepted or activated HEAD. Startup must preserve both stable identities, recover the attempt without
reviving lost Tox handles, and leave staging empty before a fresh exact-revision pull. Acceptance then
requires the ordinary two-object verification, accepted-HEAD-last transition, and explicit exact-token
activation. The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.xf1soga1` and `.sandwurm/exports/pairs/pair.mxahczbv`; exact digests,
the defect the gate exposed, and nonclaims live in
`evidence/2026-08-21-sandwurm-sync-restart.md`.

The `sync-file-guest-restart` scenario is the persisted-publisher fault cell. It rate-shapes the
same deterministic 8 MiB revision and reboots the publisher guest only after positive subscriber
provider position. The stable subscriber must observe offline, terminally fail the old pull, remove
all live receives, staging, and signed attempt truth, and retain no accepted or activated HEAD. The
initial Cloud Hypervisor chain records a bounded reboot exit; a successor Sandwurm chain consumes the
exact initial prelaunch receipt and writable runtime-root disk without new identity injection.
Acceptance requires a changed publisher boot-ID digest, unchanged subscriber boot-ID digest, exact
Tox/stable identity, policy, source, immutable-object, and signed-HEAD preservation, plus a fresh
explicit pull only after 50 consecutive confirmed, authorized, route-correct samples at a higher
subscriber epoch. The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.x3h41g9b` and `.sandwurm/exports/pairs/pair.9wfzoss6`; exact bindings,
scientific failures, and nonclaims live in
`evidence/2026-08-22-sandwurm-sync-guest-restart.md`.

The `sync-file-pause` scenario is the live flow-control cell. It rate-shapes the same deterministic
8 MiB revision, waits for positive provider progress, records one active incoming transfer's exact
file number and request-selected FileId, and invokes the ordinary `file-control` pause. Acceptance
requires that same transfer to remain locally paused at one unchanged positive partial position for
20 consecutive 100 ms samples with no accepted or activated HEAD. Resume must retain its FileId,
clear only the local pause, and converge through the ordinary accepted-HEAD-last and exact-token
activation path. The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.5qa1ubwd` and `.sandwurm/exports/pairs/pair.hd71hqag`; exact digest
bindings and nonclaims are in `evidence/2026-08-21-sandwurm-sync-pause.md`.

The `sync-file-cancel` scenario is the explicit live-withdrawal cell. It rate-shapes the same
deterministic 8 MiB revision, captures the process-local job ID returned by `sync-pull`, and waits for
positive c-toxcore receive position plus at least one admitted FileId before issuing
`sync-cancel JOB_ID`. Acceptance requires terminal `cancelled` status under the same ID, no live
incoming receive, empty staging within a bounded polled tail, and no accepted or activated HEAD. Both
guest receipts bind the cancellation to the exact published artifact, manifest, and HEAD. It proves
local fencing after observed progress; it does not prove the publisher received a CANCEL packet or
byte-range resumption. The independently reverified compact direct-UDP and forced-TCP observations
are `.sandwurm/exports/pairs/pair.kfpfl6pz` and `.sandwurm/exports/pairs/pair.6x5cujaj`; exact
digests and nonclaims live in `evidence/2026-08-21-sandwurm-sync-cancel.md`.

`sync-tree-route-cancel` is the authenticated auxiliary-withdrawal cell. It uses one protected
primary and two ready bulk workers, selects one auxiliary route in adaptive mode, and waits for a
positive receive position joined through the pull's process-private FileIds to that exact worker
incarnation. Ordinary `sync-cancel` must terminal-fence the same job within 5,000 ms, remove every
incoming transfer and staging file, release signed route work from a positive value to zero, avoid
reassignment, preserve both ready bulk routes, and create neither accepted HEAD nor activation. The
post-cancel protected Ratox probe must still pass. Accepted compact direct UDP `pair.fpkne1pg` and
forced TCP `pair.r_4luysy` observed 70 ms and 80 ms tails; exact bindings and nonclaims live in
`evidence/2026-08-25-sandwurm-sync-route-cancel.md`.

`sync-tree-route-loss` additionally qualifies ADR 0224's whole-object suffix continuation. The
subscriber stops one authenticated bulk carrier only after positive object progress. Every positive
whole-object attempt on that carrier must move to a fresh attempt/FileId on the survivor, seek to its
exact private prefix length, and finish with the complete digest. Acceptance requires bounded equal
retained/resumed attempt counts, exact aggregate retained/resumed byte equality, zero retention
fallbacks and residual partials, the existing loss/reassignment/stale/recovery lifecycle, full
activation, and the 40-sample protected Ratox tail. Accepted compact direct UDP `pair.jlcr7zms` and
forced TCP `pair.okks1io5` are documented in
`evidence/2026-08-28-sandwurm-sync-byte-resume.md`. Historical proofs without the new observation
retain only their original whole-object-reassignment meaning.

`sync-tree-route-private-actual-tor-loss` applies the same resume contract to a real Tor process
fault. The host authenticates the pre-loss circuit/process, kills only the client Tor process after
positive progress, and requires exact prefix continuation through the native auxiliary with zero
IoTox worker restart. It then restarts the same Tor data directory and binds the recovered member and
circuit plus TCP-only local-endpoint containment. Accepted compact proof `pair.3u5cjbci` is documented
in `evidence/2026-08-28-sandwurm-actual-tor-sync-byte-resume.md`.

`sync-tree-route-population` is the bounded scheduler-population cell. It uses the same protected
primary and two ready eight-work-unit bulk workers, then starts eight independent two-object tree
pulls under adaptive policy and, after a clean same-identity Agent restart, under fixed policy.
Adaptive must alternate the normalized bulk keys as `01010101`; fixed must fill then spill as
`00001111`. All eight jobs per phase must show either a positive live receive position or a committed
object, commit both objects, explicitly activate their exact HEADs, leave staging empty, and drain
signed route work. The observation timestamp is deliberately named progress observation because a
131 KiB object may complete between status samples; it is not exact first-byte latency. Each phase
retains a client resource interval, and protected Ratox must pass after both. Accepted compact direct
UDP `pair.slx3x0kb` and forced TCP `pair.rrizbuky` are documented in
`evidence/2026-08-25-sandwurm-sync-route-population.md`.

`sync-tree-route-population-loss` turns that placement row into a bounded route-failure experiment.
Fixed policy fills two four-job routes as `00001111`, with two immutable objects per job. After at
least 65,536 aggregate receive bytes and a 750 ms hold, the Agent stops one exact worker and freezes
the four nonterminal job IDs assigned to it. All four must move as complete remaining work sets;
every stale terminal from the old incarnation must be fenced; all eight revisions must commit and
activate; signed work must drain 16-to-zero; and the stopped savedata identity may recover exactly
once only after all four affected jobs are terminal. Forty protected Ratox renders must each remain
below 250 ms. Accepted compact direct UDP `pair.j19_uhjj` and forced TCP `pair.rfnsjtqb` are
documented in `evidence/2026-08-26-sandwurm-sync-route-population-loss.md` and ADR 0180.

`sync-tree-route-loss-admission` proves work created during the degraded interval. Two fixed-policy
jobs begin on one four-job carrier; after at least 65,536 bytes and a one-millisecond hold, that
worker stops and both jobs reassign. Only then does the fixture create two further jobs. It requires
exactly one ready bulk route and both late jobs bound to that survivor before recovery. All four
revisions must commit and activate, signed work drains four-to-zero, stale terminals remain fenced,
the stopped savedata identity recovers once, and protected Ratox remains below 250 ms. Accepted
compact direct UDP `pair.v3qc2kld` and forced TCP `pair.djhqe3we` are documented in
`evidence/2026-08-26-sandwurm-sync-route-loss-admission.md` and ADR 0181.

`sync-tree-route-startup-admission` qualifies controlled degraded readiness after a clean
same-state Agent restart. It holds one exact authenticated auxiliary route for 20,000 ms, requires
ten stable sole-ready observations, then admits two independent 16 MiB tree jobs to that carrier.
Both must remain live and retain their carrier when the delayed route joins; both exact revisions
must activate; adaptive selections remain two; reassignment remains zero; and work drains
four-to-zero before protected Ratox. Accepted compact direct UDP `pair.46f6td4j` and forced TCP
`pair.2gvkqs6b` are documented in
`evidence/2026-08-26-sandwurm-sync-route-startup-admission.md` and ADR 0182. This fixture does not
remove a physical interface or reboot a guest.

`sync-tree-route-throughput` is the larger-object ABBA cell. It starts a fresh same-state subscriber
Agent for each `fixed-a,adaptive-a,adaptive-b,fixed-b` phase, holds it stopped for at least 5,000 ms,
and bounds full session/authority/two-route readiness at 180 seconds. Each phase starts two
independent 16,777,283-byte-artifact jobs. Fixed must select normalized carriers `00`; adaptive must
select `01`. All eight revisions must explicitly activate, reassignment stays zero, peak signed work
is four, final work is zero, and each phase retains a process-resource interval. Protected Ratox runs
after convergence. Accepted compact direct UDP `pair.pw3ogf7q` and forced TCP `pair.7zsdwj15` are
documented in `evidence/2026-08-26-sandwurm-sync-route-throughput.md` and ADR 0183. Both logical
routes share the same shaped 4 Mbit/s TAP; this is not physical bonding or an interactive-under-bulk
cell.

`sync-tree-route-concurrent-cancel` composes population with simultaneous withdrawal. It starts
eight independent 262,211-byte-artifact adaptive jobs and requires normalized carrier pattern
`01010101`. Four concurrent `sync-cancel` clients target indices 0, 1, 4, and 5, exactly two jobs per
bulk route. All four must retain their carrier/worker identity through terminal cancellation within
5,000 ms; the remaining four must commit two objects and explicitly activate. Cancelled namespaces
must have no accepted HEAD, activation, or staging; both routes must remain ready; signed work must
drain 16-to-zero; and reassignment must remain zero. One client process-resource interval and the
post-sync 40-sample protected Ratox probe are required. Accepted compact direct UDP
`pair.2laq038h` and forced TCP `pair.rlpuyjth` are documented in
`evidence/2026-08-25-sandwurm-sync-route-concurrent-cancel.md`.

Before the Ratox `OPEN`, the controller requires three consecutive local observations of the remote
Ratox capability, authority, and expected carrier. The `OPEN` deadline remains five seconds. Do not
increase the custom payload casually: two 1 MiB/job direct-UDP cells completed cancellation and
survivor convergence but then exposed a common shaped-TAP FIFO interference boundary. That is a
separate physical-QoS experiment, not a concurrent-cancellation failure.

`sync-tree-route-loss-cancel` composes the exact live-loss seam with ordinary withdrawal. It starts
one adaptive 4,194,601-byte tree pull, stops the active bulk incarnation after at least 65,536
incoming artifact bytes, requires exactly one loss/reassignment plus positive progress on the
replacement carrier, and only then issues `sync-cancel`. The job must remain bound to that
replacement through terminal cancellation within 5,000 ms, add no reassignment, drain work
two-to-zero, and leave no accepted HEAD, activation, incoming transfer, or staging. The stopped
savedata identity must then consume one restart-budget unit and return under a fresh authenticated
worker before the 40-sample protected Ratox probe. Accepted compact direct UDP
`pair._0jwjfe6` and forced TCP `pair.o0ozmdw1` are documented in
`evidence/2026-08-25-sandwurm-sync-route-loss-cancel.md`.

`sync-tree-route-cancel-loss` reverses that deterministic order. It first binds positive incoming
progress, the exact auxiliary key/incarnation, and signed admitted work. Ordinary `sync-cancel` must
then reach a terminal cancelled tombstone, remove incoming and staging state, and drain all route
work. A default-off seam subsequently stops only the tombstone's retained carrier. The guest
requires one carrier loss, zero reassignment, positive retired-terminal fencing, one signed-budget
recovery, the same key ready under a new worker incarnation, and both bulk routes ready before the
40-sample protected Ratox probe. Accepted compact direct UDP `pair.yv4txv1r` and forced TCP
`pair.m2396itk` are documented in
`evidence/2026-08-26-sandwurm-sync-route-cancel-loss.md`.

`sync-tree-route-cancel-race` starts from the same protected-primary/two-bulk topology but uses one
shared progress arm edge. At ≥65,536 incoming bytes the Agent freezes the exact carrier for a stop
500 ms later and reports it armed; the client independently waits 500 ms from that observation and
issues ordinary `sync-cancel`. Strict evidence permits either cancel-first with zero reassignment and
the retained stopped carrier, or loss-first with one reassignment and a distinct retained carrier.
One cleanup retry is allowed only after a typed unavailable result from the first cancellation; the
retry must settle the same tombstone. Both outcomes require one loss, one recovery, no live/staging
state, work two-to-zero, no HEAD/activation, both bulk routes ready, and protected Ratox. Accepted
compact direct UDP `pair.h6kg4fcr` and forced TCP `pair.z9egqd57` both observed cancel-first with one
cleanup retry and are documented in
`evidence/2026-08-26-sandwurm-sync-route-cancel-race.md`.

`sync-tree-route-cancel-race-loss-first` is the required-outcome companion. It arms identically,
stops the exact worker at 250 ms, and issues ordinary cancellation at 1,000 ms without waiting for a
loss/reassignment observation. The terminal pull must retain one distinct replacement carrier, with
one loss, one reassignment, two adaptive selections, zero cleanup retries in the accepted cells,
one recovery, empty state/work, and protected Ratox. Accepted compact direct UDP `pair.5gvh__p1`
and forced TCP `pair.rxb2dsge` are documented in
`evidence/2026-08-26-sandwurm-sync-route-race-linearizations.md`.

`sync-tree-route-startup-order` is the exact readiness-permutation cell. It uses one protected
primary and two signed bulk workers, but initially services only one exact named auxiliary identity.
The other worker remains held until the selected route has a confirmed application session and
reciprocal route binding; a 20-second observation delay begins only then. The guest requires the
selected public key to be the sole `lifecycle=ready` bulk route for ten consecutive samples, waits
for both routes to become ready, then repeats with the opposite exact key after a savedata-preserving
rolling Agent restart. Host release barriers restart client before device so simultaneous protected
primary replacement cannot masquerade as route-order failure. Both phases precede ordinary signed
tree convergence and protected Ratox. Accepted compact direct UDP `pair.nyiqwm8t` and forced TCP
`pair.mdacri5e` are documented in
`evidence/2026-08-25-sandwurm-sync-route-startup-order.md`.

The `sync-file-disconnect` scenario is the authenticated-epoch retirement cell. It rate-shapes the
same deterministic 8 MiB revision and waits for positive receive position plus admitted FileIds.
The host then replaces both TAP qdiscs with `netem loss 100%` until both guests report transport and
application-session offline. The subscriber must expose its old job as terminal `failed`, clear all
live incoming state and private staging, and retain neither accepted HEAD nor activation. After the
host restores both TAPs, both guests must confirm a strictly higher online epoch; only then does the
client issue a fresh pull, converge, and explicitly activate the exact HEAD token. Both peers must
retain the same recovered epoch and authority for 50 consecutive 100 ms samples before that retry;
the first scientific cell exposed a second connection flap after an immediate first-confirmed retry.
After convergence an explicit evidence-release barrier keeps the client online until the publisher's
stability checkpoint and bound completion record are secured.
The independently reverified compact direct-UDP and forced-TCP observations are
`.sandwurm/exports/pairs/pair.ip8h7ud4` and `.sandwurm/exports/pairs/pair.xi96v2re`; exact digests,
scientific failures, and nonclaims live in
`evidence/2026-08-21-sandwurm-sync-disconnect.md`. This is safe whole-object retry across disconnect,
not byte-range resume or implicit epoch rebinding.

The `ratox-idle` scenario is the first complete-service R7 cell. It reuses the immutable test
identities, exchanges their stable public principals through the same private rendezvous, and keeps a
fixed RecallRoot fixture only inside the disposable device guest. The device creates a local v2
authority ledger, grants the client only `interactive.terminal`, binds that principal to a fixed
raw/no-echo byte profile, and restarts the daemon with the default-off host gate explicitly enabled.
The client enables only the controller gate and collects 40 serialized INPUT-to-PTY-to-render
samples through the production terminal socket. Acceptance requires exact one-byte input/output
spans, monotonic controller timestamps, one exact owner-queue delta per INPUT, and 40 joined host
stage/commit/output event triples. This is an idle construction cell, not the 1,000-sample release
cell and not evidence for any bulk-load condition.

The separately named `ratox-matrix-idle` and
`ratox-matrix-bulk-{1,8,16,32,64}` scenarios run the same complete-service path for 1,000 serialized
inputs. They retain both generations of a rotated Ratox host journal and bind the sample count in
the pair manifest and receipts. Each scenario is one ordered cell, not the canonical randomized,
two-role-signed twelve-cell R7 bundle. Use the fast names above for construction regressions and the
`ratox-matrix-*` names only when collecting qualification-scale evidence.

ADR 0161 makes paced workload state explicit. New bulk progress checkpoints use v2 and retained
observations use v6: `present` is exactly `active + paused`, both populations are published, and the
gate requires the full expected present population plus positive progress for every transfer.
Scheduler PAUSE is a live workload phase, not a missing lane. Historical v1--v5 observations keep
their original active-only verification contract.

The first clean v6 direct-UDP `bulk-8` cell is retained at
`.sandwurm/exports/pairs/pair.y0d97_ng`. It completes lifecycle and strict verification but fails
performance: render p95 144.120 ms and one 250 ms miss despite owner p99 0.420 ms, event high-water
134/138, and zero required waits. Its active/paused split proves why state accounting matters; its
long bilateral pacing holds select resume fairness/shared-carrier burst science next.

ADR 0162 supplies that experiment with oldest-eligible selection and a default one-resume batch per
owner iteration. New Agent status and strict proofs bind batch limit/count/maximum; the existing
`pair.y0d97_ng` comparison legitimately lacks those later fields. Exact commit `dbcba87` produced
two strictly retained outcomes. `pair.xs9phpya` activates 3,167/2,658 singleton batches and improves
p95/p99/max to 124.811/161.242/188.401 ms without a lifecycle regression or 250 ms miss, but remains
above the direct p95 gate. `pair.dwo77gs0` never activates pacing, advances only 375,654 aggregate
file bytes, and reaches p95 504.428 ms at about 5% CPU while remote service remains healthy. This
variance is itself evidence: the next gate needs proactive carrier admission, not another event
queue threshold.

ADR 0163 implements that next gate at the receiver: one locally resumed incoming file per peer by
default, oldest-first bounded rotation, and complete admission/rotation/wait telemetry. The reactive
64/16 pacer remains the semantic reserve for the currently runnable transfer. A new `bulk-8` proof
must show positive carrier rotation and progress for every file; zero activation is explicitly not a
treatment result.

The first exact ADR 0163 proof is the rejected near-pass `pair.qrggya8w`: all eight files progress,
owner p99 is 1.488 ms, and render p95 falls to 56.247 ms, but does not cross the strict 50 ms gate.
Its 1,454 rotations in about 32 seconds and 141 reactive pause collisions select ADR 0164. Current
defaults use a 50 ms quantum, publish `transport-file-pacing-external-pause-count`, require zero true
control failures in new proofs, and discard only bounded events already queued after accepted local
cancellation. The next run must have no terminal file-transfer diagnostic.

That exact rerun is accepted as compact proof `pair.bo6l0der`. It progresses all eight files by
170,498,931 aggregate bytes, records 507 fair rotations and 77 typed external-owner handoffs with
zero true failures, and lowers event high-water to 228/168 with zero required waits. Render p95 is
39.634 ms and owner p99 is 1.917 ms, so both strict direct-route gates pass; no render reaches 100 or
250 ms. The next matrix cell is forced-TCP `bulk-8` from a clean commit.

Forced-TCP `bulk-8` also passes as compact proof `pair.pitcu1pk`: all eight files progress by
139,548,606 bytes, 739 rotations and 58 typed handoffs have zero true failures, event high-water is
141/139 with zero required waits, owner p99 is 1.525 ms, and no render reaches 250 ms. Its independent
route distribution is p50/p95/p99/max 24.636/76.249/98.314/119.607 ms. Both eight-stream route cells
are complete; advance to direct-UDP `bulk-16` before forced TCP.

Direct-UDP `bulk-16` passes as compact proof `pair.xphist_e`. All 16 files progress by 169,803,834
aggregate bytes; 524 rotations and 60 typed handoffs have zero true failures. Maximum fair wait grows
to 890.887 ms, consistent with a 16-file round, while the minimum file still advances 9,614,823
bytes. Event high-water is 203/183 with zero required waits, render p95 is 40.591 ms, owner p99 is
1.894 ms, and no render reaches 100 or 250 ms.

Forced-TCP `bulk-16` passes as compact proof `pair.qk3d51k6` with the identical binary. All 16 files
progress by 140,818,152 bytes; 782 rotations and 84 typed handoffs have zero true failures. Maximum
fair wait is 885.574 ms and the minimum file advances 7,896,960 bytes. Event high-water is 190/136
with zero required waits, render p95/p99/max is 75.704/87.867/106.025 ms, owner p99 is 1.013 ms, and
no render reaches 250 ms. The balanced 16-stream row is complete.

Direct-UDP `bulk-32` passes as compact proof `pair.ktcwivx_`. All 32 files progress by 147,315,321
aggregate bytes; 590 rotations and 78 typed handoffs have zero true failures. Maximum fair wait is
1.744 seconds, consistent with doubling the 16-file round, while the minimum file still advances
4,097,919 bytes. Event high-water is 162/152 with zero required waits, render p95 is 47.765 ms,
owner p99 is 1.811 ms, and no render reaches 100 or 250 ms.

Forced-TCP `bulk-32` passes as compact proof `pair.lanpv3u7` with the identical binary. All 32 files
progress by 122,955,393 bytes; 670 rotations and 56 typed handoffs have zero true failures. Maximum
fair wait is 1.736 seconds and the minimum file advances 3,175,236 bytes. Event high-water is 185/147
with zero required waits, render p95/p99/max is 76.331/95.608/163.533 ms, owner p99 is 0.798 ms, and
no render reaches 250 ms. The balanced 32-stream row is complete.

Direct-UDP `bulk-64` is a valid but rejected compact proof `pair.t736zqqh`. All 64 files progress by
1,549,230 aggregate bytes and cancel cleanly; 4,624 rotations have zero true failures, maximum fair
wait is 3.837 seconds, owner p99 is 0.118 ms, remote stage-to-output p95 is 10.293 ms, queues peak at
only 50/50, and reactive pacing never activates. Nevertheless render p50/p95/p99 is
220.897/331.081/446.692 ms and 108 samples reach 250 ms. This is a single-carrier transport cliff,
not an owner/PTY/CPU limit.

Forced-TCP `bulk-64` is independently rejected as compact proof `pair.swij6mj9`. All 64 files progress
by 168,951,072 aggregate bytes and cancel cleanly, but client event high-water reaches 711, owner p99
is 2.199 ms, and one render reaches 560.528 ms. The forced route remains high-throughput rather than
repeating direct UDP's low-use stall, so no one queue/quantum tweak is selected. ADR 0165 preserves
32 accepted sends/receives as the qualified single-Agent ceiling and labels larger CLI values
experimental. The complete matrix is measured; its frozen 64-stream R7 row remains unqualified.

The first matrix idle attempt found a protocol lifetime rather than a latency miss: all 1,000
direct-UDP renders completed, but per-ACK permanent replay retention exhausted the 128-entry control
cache before `CLOSE`. ADR 0154 replaces that duration-dependent allocation with one cumulative
attachment fence. A corrected dirty-tree construction run completed and verified the full cell;
it is diagnostic only. Qualification results must be rerun after the fix is committed so source
revision and binary provenance describe the exact tested tree.

The first loaded matrix attempt found a separate measurement defect after 457 exact renders. The
stopped client had executed all 914 expected INPUT/ACK owner operations with a 1.047 ms p99 bound,
but the probe was waiting on the deliberately coalesced runtime `status` file. ADR 0155 makes
authenticated control inspection return live transport counters and moves local PTY render before
all evidence work. A loaded failure now also publishes probe stderr and terminates the host wait
immediately. This changes only local measurement and inspection; Ratox v1 framing remains frozen.

The corrected clean idle cell then delivered 1,000/1,000 but missed the direct p95 target at
83.115 ms while owner queue p99 stayed at 0.511 ms. A transport-only 5 ms diagnostic left p95 at
59.230 ms; a combined transport/Agent-service 5 ms diagnostic reached p95 32.000 ms and p99
47.643 ms. ADR 0156 turns that seam into active-only policy: local terminal work wakes the event
consumer, live Ratox state uses configurable 5 ms transport/service defaults, and idle restores the
ordinary cadence. New cells retain and compact a process-incarnation-fenced resource interval for
both roles. The diagnostics are not accepted proof; the exact committed implementation must generate
the route/load matrix evidence.

The accepted direct-UDP construction observation is compacted at
`.sandwurm/exports/pairs/pair.b8y5m37j` and documented in
`evidence/2026-08-20-sandwurm-ratox-idle.md`. It rendered 40/40 exact inputs with p50 45.442 ms,
p95 63.941 ms, p99/max 67.435 ms, no 250 ms miss, and owner interactive queue p99 0.115 ms. Those
figures guide the next bulk cells; they are not release qualification.

The matched forced-TCP construction observation is compacted at
`.sandwurm/exports/pairs/pair.9dw2uul1`. It also rendered 40/40 exactly, with p50 65.454 ms, p95
104.139 ms, p99/max 109.183 ms, zero 250 ms misses, and owner queue p99 0.081 ms. Remote
stage-to-output p95 stayed near 27.4 ms on both routes, so the added TCP tail is outside remote queue
and PTY execution. Both cells remain construction-sized.

The accepted direct-UDP bulk construction ladder is documented in
`evidence/2026-08-20-sandwurm-ratox-bulk.md`. Its 1/8/16/32/64 cells kept every named transfer active,
rendered 40/40 exact inputs, proved every lane advanced, and canceled to an empty transfer set. The
64 cell explicitly raises both active-transfer limits to 64; normal guests retain the deliberate
default of 32. These are construction cells, not the 1,000-sample release matrix.

Forced TCP accepts 1 and 8 streams on upstream 0.2.23 and 16 streams on the source-tracked
`iotox-file-rr1-tcp-connect120` provider variant. Its scheduler patch rotates c-toxcore file
chunk-request service instead of
restarting at slot zero; the unchanged gate moved from 4/16 progressed lanes to 16/16. At 32,
all RESUME controls and sender chunk admissions completed but only 17 data lanes reached the client
inside the outer completion bound. Four independently keyed forced-TCP routes now pass 32 aggregate
streams (eight per route) twice, including 40 exact terminal samples and cancel-to-empty. A
40-stream cell completed one full client workload but did not repeat cancellation; 48/56/64 crossed
terminal or lifecycle deadlines. The qualified construction point is therefore eight bulk streams
per route, not the largest admitted population. One repeated 32 attempt also stopped at three
confirmed routes before an identical pass. Auxiliary establishment now uses bounded staggered
process restarts from unchanged savedata and refuses to release work with fewer than four routes. A
deliberate one-sided fourth-route restart passed the same 32-stream gate. Live lane loss after
transfer admission remains open. Exact measurements and nonclaims live in the bulk evidence note.

The named provider's direct-UDP rerun passes 1, 8, 16, and the ordinary 32-stream limit. Its explicit
64-stream opt-in completed all 40 terminal samples but not the all-lanes-progress gate. The guest now
publishes terminal-captured and changing progressed-lane checkpoints separately, so a failed private
run can be localized before bounded cleanup without treating a partial capture as proof.

Striped scenarios additionally publish content-free per-guest convergence counts and stop at an
evidence barrier. Both guests must snapshot all four live TCP routes before either auxiliary agent
may stop; this prevents teardown order from turning valid workload evidence into a one-sided route
receipt. The accepted compact steady-state 32-stream proof is
`.sandwurm/exports/pairs/pair.hb491hc_`. The accepted establishment-recovery proof is
`.sandwurm/exports/pairs/pair.fmf8pynz`; its receipts bind one injected and two automatic
route-process restarts before four-route convergence.

Both guests use a temporary host-side c-toxcore 0.2.23 bootstrap/TCP-relay fixture through the
prepared bridge address. The upstream sample binds wildcard UDP/TCP 33445 while alive, so the host
firewall is its outer exposure boundary. The fixture is built from the same pinned source and
libsodium as the IoTox binary, has a fresh key per run, and is terminated with the pair. It removes public
bootstrap timing and peer-as-its-own-relay asymmetry from the controlled experiment; it does not
represent an IoTox production service. Direct-UDP guests permit c-toxcore's ephemeral UDP socket
inside the disposable VM. Forced-TCP guests disable UDP, discovery, DHT announcements, and hole
punching and do not open that guest UDP range.

The remaining command surface is reserved, not implemented:

```text
./tools/iotox-sandwurm-lab.sh exec client -- COMMAND...
./tools/iotox-sandwurm-lab.sh exec device -- COMMAND...
./tools/iotox-sandwurm-lab.sh route direct-udp|forced-tcp
./tools/iotox-sandwurm-lab.sh impair PROFILE
./tools/iotox-sandwurm-lab.sh run ratox-r7|sync-s3
./tools/iotox-sandwurm-lab.sh collect OUTPUT_DIRECTORY
./tools/iotox-sandwurm-lab.sh down
```

`preflight` delegates substrate truth to Sandwurm and evaluates the IoTox flake. `build` realizes an
exact source-addressed role closure without launching. `down` will request bounded shutdown and
record forced termination for future persistent modes.

`route` and `impair` are mutually serialized experiment mutations. Named impairment profiles freeze
loss, duplication, reorder, delay, jitter, bandwidth, queue, and seed. `run` randomizes the frozen
matrix and records every phase rather than letting shell call order become evidence. `collect` verifies
the manifest and copies only declared content-free/digest-bound evidence.

## Initial guest roles

- `client`: IoTox controller, local terminal renderer, synchronization subscriber, and capture role A.
- `device`: IoTox Ratox host, synchronization publisher, delegated cgroup-v2 owner, and capture role B.
- `relay`: initially a bounded service in the controlled network role; it may become a small third
  guest only when separate-kernel fault injection materially improves the experiment.

Each IoTox guest receives a copied reusable test identity by default and otherwise fresh authority,
command, runtime, transfer, profile, namespace, and activation state. A separate gate generates fresh
identities. Secrets never enter receipts or repository artifacts.

## First acceptance gates

1. [x] Independent client and device closures boot under stock Cloud Hypervisor, report the expected
   dirty source identity and exact current binary digest, observe KVM/cgroup v2, emit complete
   content-free receipts, and exit cleanly with networking absent.
2. [x] Keep both guests live simultaneously and establish genuine source-linked Tox friendship
   through the controlled network.
3. [x] Direct UDP and forced TCP are positively observed rather than inferred from requested flags.
4. Fault/restart behavior produces typed bounded outcomes and no stale epoch effect:
   - [x] persisted-disk device guest restart across two bounded Sandwurm VMM epochs;
   - [x] forced-TCP packet-blackhole interruption and bilateral recovery;
   - [x] forced-TCP relay interruption and same-key recovery;
   - [x] daemon replacement with saved identity and stable-client epoch advancement.
5. The device guest owns a writable delegated cgroup-v2 root and positively exercises lifecycle,
   resource, PSI admission, and PSI trigger routes that skip in the current host shell.
6. Synchronization qualification:
   - [x] `sync-file` proves byte-identical signed one-source revision convergence and exact-token
     explicit activation over direct UDP and forced TCP;
   - [x] `sync-file-range` proves manifest-first signed-successor reconstruction with one bounded
     range and exact-token activation over direct UDP and forced TCP;
   - [x] `sync-file-corrupt-basis` proves a corrupt accepted basis selects exact whole-successor
     recovery without deleting that prior object over direct UDP and forced TCP;
   - [x] `sync-file-range-retry` proves one fully cleared same-epoch range-plan retry under fresh
     durable and transport identities without prefix reuse over direct UDP and forced TCP;
   - [x] `sync-file-restart` proves unclean receiver-process recovery and whole-object retry over
     direct UDP and forced TCP;
   - [x] `sync-file-cancel` proves terminal local withdrawal after positive provider progress over
     direct UDP and forced TCP;
   - [x] `sync-tree-route-cancel` proves exact-worker positive progress, bounded terminal withdrawal,
     signed work release without reassignment, ready-route preservation, and protected Ratox over
     direct UDP and forced TCP;
   - [x] `sync-tree-route-throughput` proves four bounded Agent replacements, fixed `00` versus
     adaptive `01` placement for two concurrent 16 MiB trees, exact activation/work drainage,
     phase-resource capture, and post-convergence protected Ratox over both carriers;
   - [x] `sync-file-disconnect` proves old-epoch retirement and explicit stabilized whole-object retry
     after bilateral live-link loss over direct UDP and forced TCP;
   - [x] `sync-file-pause` proves stable same-FileId local flow control and convergence after resume
     over direct UDP and forced TCP;
   - [x] `sync-file-guest-restart` proves persisted publisher identity/publication recovery, old-job
     cleanup, and stabilized explicit whole-object retry over direct UDP and forced TCP;
   - [x] `sync-file-repair` proves explicit corrupt target-object quarantine, signed-state
     preservation, same-revision recovery, retained quarantine evidence, and a clean second scan over
     direct UDP and forced TCP;
   - [x] `sync-tree` proves bounded deterministic-directory convergence, post-commit atomic
     activation projection, frozen contents/modes, and exact retry over direct UDP and forced TCP;
   - [x] dedicated directory cells prove rollback/fork refusal, ENOSPC recovery, queue saturation,
     byte/object quota refusal, real read-only recovery, and maximum-entry process high-water over
     direct UDP and forced TCP;
   - [x] `sync-tree-source-corrupt` proves publisher request-time verification, zero-admission
     refusal, exact two-object quarantine, same-revision reconstruction, and explicit retry over both
     carriers;
   - [x] `sync-tree-destination-corrupt` proves complete staged SHA-256 refusal after positive
     transport progress, predecessor preservation, valid sibling retention, selective explicit retry,
     and separate activation over both carriers;
   - [x] `sync-tree-control-replay` proves retained exact HEAD/object results, duplicate file-offer
     suppression, results reordered behind admitted file lanes, no duplicate-HEAD request cascade,
     same-ID conflict refusal, and separate activation over both carriers.
   - [x] `sync-tree-admission` proves the smallest real full-ledger boundary: one accepted receive,
     one exact paused excess offer, bounded fair retry to two-object convergence, and zero pending at
     completion over both carriers.
   - [x] `mutable-profile-status` grants both stable principals exactly `write.settings`, issues one
     durable `profile.status.set busy` in each direction, and proves exact outgoing/incoming success,
     provider readback convergence, and ownership epoch 1 over both carriers.
7. `ratox-r7` runs idle and 1/8/16/32/64 bulk cells under both route classes with at least 1,000 input
   observations per cell and the frozen analyzer targets.
8. Collection binds Sandwurm launch receipts, IoTox source/build identity, network profile, phase
   schedule, raw evidence digests, and both capture signatures into one verifiable report.

## Non-goals

The lab does not change IoTox into a Sandwurm-dependent product. Sandwurm is construction and
qualification infrastructure; shipped IoTox remains one binary with its own ordinary Unix surface.
