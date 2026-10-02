# Network model

## Taxonomy

IoTox represents peer semantics and route separately:

```text
Tox/native
Tox/Tor
Tox/I2P

Tor/direct-future
I2P/direct-future
```

A route selection is privacy and reachability policy. `Tox/native` remains the default. Unsupported
explicit routes fail; they never silently use native sockets.

## Operator readiness surface

Use the binary, not memory, for the current operator-facing route posture:

```sh
iotox readiness routes
iotox readiness privacy
iotox overview
```

The route report intentionally separates lanes that are easy to conflate:

- `routes-native=accepted` means ordinary c-toxcore through the isolated runtime adapter remains
  the default reachable Tox path.
- `routes-tor=actual-route-bounded` means strict `tox/tor` has actual Tor route evidence, with
  stronger current coverage for Ratox route loss/soak/adversary and sync tree/range/content gates.
- `routes-i2p=vm-qualified-strict` means canonical `tox/i2p` is a strict numeric SOCKS-to-SAM route
  with retained VM-qualified evidence, but it is not yet Tor-equivalent across every product lane.
- `routes-toxic-native=default-qualified-forced-tcp-degraded` means the normal-Tox compatibility
  bridge is strongly proven against stock Toxic on the default native route, while forced TCP has
  founding and long-loop evidence but remains degraded until a follow-up soak is boring.
  `routes-toxic-tor` and `routes-toxic-i2p` are evidence-gated: they need explicit bridge/route
  proof labels before any operator claims them.
- `routes-policy-cards=not-carried-by-self-roster-or-person-card` means private self rosters and
  public person cards publish membership/delivery keys, not a route-class downgrade policy. Use
  route-set v2 and explicit runtime configuration for route class policy.

`iotox readiness privacy` repeats the safety boundary: direct Tor/I2P IoTox transports are not
implemented, no signed roster or public card authorizes silent native fallback, and none of these
routes by itself certifies anonymity against timing, traffic shape, peer, relay, or host observation.

The evidence-gated route porch is:

```sh
iotox route-qualification-check --scope all
iotox route-qualification-check --scope toxic
iotox route-qualification-check --scope ratox
iotox route-qualification-check --scope sync
iotox route-qualification-check --scope privacy
```

With no labels it fails closed and prints the actual route science commands:
operator Tor smoke and verifier, I2P SAM/front construction, Toxic default and
forced-TCP labs, route-set v2 creation, and the bridge graduation command.
With labels it reports `route-qualification=operator-attested` for that
scope, while still printing `silent-fallback-authorized=0` and
`anonymity-certified=0`. Route qualification is host/lane/operator evidence,
not a universal network privacy certificate.

## Tox/I2P — VM-qualified strict route

`tox/i2p` applies the same strict numeric SOCKS/bootstrap/relay and TCP-only option contract
described below for Tor, reports `Tox/I2P`, and uses
`device.tox-i2p.toxsave`. The SOCKS endpoint must be the ADR 0211 exact-record SAM adapter, not an
ambient I2P SOCKS proxy or clearnet outproxy. ADR 0213 provides the matching persistent
SAM-to-loopback service boundary. ADRs 0214–0215 add the bounded establishment budget and require at
least three address-preserving node fronts for fresh-key qualification. A same-host two-peer
application E2E passes. ADR 0216 adds two-guest Sandwurm TAP containment, and ADR 0217 replaces the
client router across listener-positive/SAM-negative loss before bilateral higher-epoch text
recovery. ADR 0218 replaces all three service fronts over stable private Destinations. ADR 0219 then
binds one exact 131,369-byte signed sync tree to the authenticated I2P member with zero reassignment
while native fallback remains ready. Larger diagnostic objects exposed whole-object cross-class
failover. ADRs 0221–0222 now freeze owner-local failover and constructed-network class per job; the
I2P guest requests `fail-closed tox/i2p`, so it cannot initially select or later replace
onto native. ADR 0225 now signs that coarse class in route-set v2 and enforces it at primary,
worker, and coordinator admission. ADR 0226 accepts one genuine mid-object router-loss gate: the
class-pinned job remains blocked with native ready, the same member recovers without a worker
restart, and only an explicit fresh pull completes. ADR 0227 then reuses the frozen range-v1 frames
on that authenticated member: a native 4 MiB basis plus I2P-pinned successor fetches one changed
128-byte artifact range and reuses the remaining verified bytes with zero reassignment. Live I2P
range loss/resume and broader time/record qualification remain open. ADR 0253 promotes this exact
qualified construction to the canonical product spelling without changing its numeric signed class,
savedata, framing, or provider policy. `tox/i2p-construction` remains a deprecated reproduction
alias and old evidence retains that historical label. Production-spelling compact proof
`pair.btm5vwr9` independently passes two-guest actual-I2P containment. See
`docs/i2p-route-construction.md` and
`docs/evidence/2026-08-29-sandwurm-tox-i2p-production.md`.

## Tox/native — enabled

The ordinary native configuration may enable UDP, local discovery, DHT announcements, and hole
punching and installs configured bootstrap/TCP-relay endpoints. `--native-tcp-only` disables every
UDP discovery seam without claiming a privacy overlay. Disconnected agents retry configured
bootstrap and relay records on a bounded cadence.

The compiled node catalog is a dated, frozen build input, not a sovereign service. Users may replace
it completely with repeated CLI options. Endpoint operators receive no ownership or authorization
power. Native direct-UDP and forced-TCP behavior is qualified inside the controlled two-guest
Sandwurm laboratory; public DHT, NAT variety, and Internet relay reliability remain separate claims.

Owners may explicitly contribute a source-pinned bootstrap and TCP relay with the exported
`nixosModules.toxBootstrap` NixOS module. Module import is inert, enablement requires a reviewed
package, and the firewall remains closed unless separately requested. The service retains a private
node identity, not an IoTox principal or reassignment key. Its KVM gate proves local TCP/UDP
listeners, identity retention across restart, systemd resource bounds, and exact firewall rules;
public reachability and operation remain external responsibilities. See
`bootstrap-relay-operations.md` and ADR 0240.

## Tox/Tor — construction-enabled and bounded operator-route-qualified

The first strict routed mode is explicit:

```sh
iotox run \
  --state /absolute/device.toxsave \
  --runtime /absolute/private-runtime \
  --network tox/tor \
  --socks5-proxy 127.0.0.1:9050 \
  --bootstrap 203.0.113.10:33445:64_HEX_DIGITS \
  --tcp-relay 203.0.113.10:33445:64_HEX_DIGITS
```

Route selection automatically suppresses the compiled native bootstrap/relay catalogs and forces
these c-toxcore options:

```text
UDP                         off
local discovery             off
DHT announcements           off
hole punching               off
proxy                       SOCKS5, one explicit numeric IP:port
native DNS                  off
bootstrap/relay records     explicit, nonempty, numeric IPs only
native fallback             absent
```

Both bootstrap and relay records are required deliberately. In c-toxcore 0.2.23, TCP-only
`tox_bootstrap()` installs onion path nodes while its DHT datagram branch remains disabled;
`tox_add_tcp_relay()` installs the TCP carrier. That provider's SOCKS5 request carries relay
destinations as IPv4/IPv6 bytes rather than proxy-resolved domain names. Accepting a name would
therefore require local resolution, contradicting disabled native DNS. IPv6 proxy syntax is
`[ADDRESS]:PORT`; scope identifiers and credentials are not supported.

Missing or repeated proxy options, hostnames, bootstrap omission, relay omission, zero ports, any
compiled default catalog, a proxy paired with `tox/native`, and a signed auxiliary route that
requires UDP all fail before durable/runtime mutation. Status projects `Tox/Tor`; connection truth
still reports `tcp` or `offline` independently.

The source-linked local gate uses the pinned c-toxcore bootstrap/TCP-relay fixture through a strict
numeric-only allowlisted SOCKS5 forwarder. It observes TCP self-connectivity, no IoTox UDP socket,
no direct IoTox-to-relay TCP socket, offline state after proxy loss, and recovery only through the
same proxy endpoint. Run it with:

```sh
python3 tools/run-tox-tor-smoke.py
```

The accepted rev0045 construction receipt measured 8.038 seconds to initial TCP, 77.993 seconds
from proxy loss to authoritative `offline`, and 4.921 seconds from exact-endpoint restart to TCP.
Pinned c-toxcore's 30-second TCP ping cadence and 10-second outstanding-ping timeout explain the
coarse detection timescale; relay/onion recovery adds state beyond those constants. IoTox will keep
that provider truth intact. The separate local observation surface is:

```sh
iotox route-health
iotox route-health FRIEND
iotox --sample-ms 250 --failure-samples 3 --recovery-samples 2 \
  route-health-watch FRIEND
iotox --timeout-ms 2000 route-target-health
```

The first form copies the exact c-toxcore carrier state and, for `Tox/Tor`, opens and closes one
bounded numeric TCP connection to the configured local SOCKS listener. It sends no SOCKS request,
so a reachable listener leaves an offline upstream `unresolved`. The optional friend form also sends
the existing transcript-confirmed lossless echo and reports only responsive/unresponsive, RTT, and
a numeric error code; pre-send failure reports `unavailable`, not a fabricated timeout. Neither form
exposes endpoint/peer/nonce content, changes the carrier label,
or advances a session epoch (ADR 0192).

The watch strictly reparses each canonical report and keeps independent process-local latches for
the local boundary and remote application. Defaults require three decisive failures and two decisive
successes; thresholds are bounded to 1..64. Unmeasured/pre-send results are inconclusive, clear the
current streak, and cannot fabricate a transition. The monitor persists nothing in the Agent and
cannot detach, resume, relabel, or advance an epoch.

The separate terminal heartbeat uses the frozen Ratox PING/PONG frames. One exact PING identity is
reused for the current attachment so indefinite sampling consumes one never-evicted replay record,
not one per interval. The terminal CLI samples every second and warns after three unanswered
deadlines while retaining the session. A PONG proves current remote Ratox route/replay reachability,
not PTY-child progress or terminal output latency. ADR 0196's two-guest bounded-impairment matrix now
measures that heartbeat separately from PTY input-to-output over direct UDP, forced TCP, and strict
generic SOCKS. It keeps one session alive through 75 ms +/- 15 ms delay plus 2% loss and recovery;
partial impairment remains warning-only because the signals and their tails differ. ADR 0197 then
qualifies complete bilateral loss on those same three route classes. A two-second heartbeat miss
leaves carrier/session truth unchanged; authoritative offline at about 30–31 seconds detaches the
controller with typed `unavailable` while the device retains one live PTY. Only a higher
authenticated epoch followed by explicit exact-session resume advances the attachment generation.
Automatic migration and actual-Tor terminal behavior remain separate gates. The operator gate binds
one-shot SOCKS-target observations to authenticated Tor control without changing that policy
(ADRs 0193/0195/0196/0197).

`route-target-health` is deliberately separate and one-shot. For `Tox/Tor` the Agent—not the
request—selects the first already validated explicit numeric TCP relay, negotiates SOCKS5 no-auth,
sends one numeric CONNECT, consumes the bounded reply, sends no application data, and closes. Its
content-free stage/result distinguishes local proxy failure from configured-target refusal or
success while copying carrier truth unchanged. It accepts no endpoint and is not part of the 250 ms
watch. A successful CONNECT is not a Tox handshake, circuit identity, or anonymity claim (ADR 0194).
See `docs/evidence/2026-08-27-source-linked-tox-tor-route.md`.

The included forwarder is auditable laboratory plumbing, not Tor. IoTox cannot determine from a
SOCKS endpoint alone that it is a Tor client, that it built a circuit, or that its upstream route is
anonymous.

The separate `tox-tor proxy-restart` Sandwurm gate runs two source-linked guests without a direct
peer ping. Accepted proof `pair.zyy913jf` establishes a confirmed session, proxy-loss offline state,
epoch-advancing exact-endpoint recovery, post-recovery text, and 913 captured guest-egress IPv4
packets exclusively to the SOCKS endpoint over TCP. It observes no native UDP, direct bootstrap, or
direct peer packet and no denied proxy target. This qualifies the generic SOCKS route, not Tor.

The separate opt-in operator gate uses an actual Tor daemon and current public numeric Tox TCP relay:

```sh
python3 tools/run-tox-operator-tor-smoke.py \
  --node IP:TCP_PORT:64_HEX_PUBLIC_KEY \
  --output operator-tor-receipt.json
python3 tools/verify-tox-operator-tor-smoke.py \
  operator-tor-receipt.json \
  --runner tools/run-tox-operator-tor-smoke.py
```

The operator obtains and reviews current numeric records; the tool downloads no catalog and has no
fallback node. It binds the exact Tor binary and normalized loopback SOCKS/control policy. Tor
control must attach the Tox relay stream to a built three-hop `GENERAL` or `CONFLUX_LINKED`
application circuit, Linux socket
ownership must show only IoTox-to-loopback-SOCKS TCP and no IoTox UDP/direct relay socket, and the
Tor process must own public TCP connections. The gate kills Tor, waits for authoritative offline,
holds and samples the no-bypass state, restarts the exact endpoint, and requires a second qualifying
circuit.

Tor must use explicit `SafeSocks 0` with this provider contract. c-toxcore sends already numeric
SOCKS destinations and IoTox prohibits native resolution; `SafeSocks 1` rejects those numeric
requests because Tor cannot know that the operator supplied them. This does not relax IoTox's
numeric-only/native-DNS-disabled policy.

The accepted rev0045 sample used Tor 0.4.8.11 and one public relay. It reached initial TCP in 9.120
seconds, bound initial/recovered configured-target success to distinct three-hop `CONFLUX_LINKED`
circuits, observed local refusal after 35 ms while c-toxcore still reported TCP, became
authoritatively offline after 74.602 seconds, stayed absent for 30.290 seconds and 30 socket checks,
and recovered in 3.913 seconds. See `docs/evidence/2026-08-27-operator-tor-public-route.md` and
ADRs 0191/0195.

This is a bounded actual-Tor public-route claim, not anonymity, censorship resistance, or a public
relay SLA. Accepted compact Sandwurm proof `pair.2mycvy9n` separately binds two exact Tor
auxiliaries to distinct three-hop circuits and private-v2 readiness inside one converged sync
topology. Accepted compact proof `pair.lzsyitvy` then binds the complete signed 4,194,389-byte tree
job to the exact Tor auxiliary with zero reassignment, alongside separate Tor-control and TAP
containment evidence. This is scheduler-level payload attribution, not an anonymity claim or a
packet-by-packet content classifier. ADR 0205 adds a separate external process-loss cell: it
kills the client Tor process after positive exact-carrier object progress, requires native-member
reassignment, and counts Tor's actual return without restarting the IoTox worker. Accepted compact
proof `pair.iompvehf` records one loss, one reassignment, one recovery, two stale terminals, zero
worker restarts, and zero unexpected-context packets. Long-running multi-relay/exit capture and
adversarial proxy tests remain qualification work.

ADR 0206 qualifies a separate Ratox primary-route cell rather than inferring terminal behavior
from immutable sync failover. Both peers use actual Tor; after initial PTY progress the host kills
only client Tor, preserves the device's detached session through authoritative offline, restarts the
same Tor instance, and requires explicit higher-epoch resume of the exact session/incarnation. The
strict evidence joins heartbeat/carrier separation, byte positions, host PTY retention, three Tor
phases, and TCP-only TAP containment. Accepted compact proof `pair.2waqdpgk` binds those facts to a
real client Tor `SIGKILL`, distinct recovered process/control identities, zero IoTox daemon
restarts, and exact-session generation-2 resume.

ADR 0207 accepts compact proof `pair.k8o54n2v` for the complementary continuous-process gate. Both
Tor instances and both IoTox agents stay alive while the exact client and device application circuits are deliberately closed at
separate points in one 120-sample Ratox attachment. The accepted proof shows distinct raw
replacement circuits with the attributed stream either reattached or reopened, unchanged process/control and session identities, contiguous terminal
bytes, paired heartbeats, and exact local-listener packet containment. The first close established
that the Tox TCP carrier can go authoritatively offline even while Tor stays alive, while another
attempt emitted no error. Acceptance now requires post-replacement PONG with unchanged epoch or
exact loss plus higher-epoch explicit resume rather than assuming either outcome. The accepted run
exercises both branches. It measures controlled
circuit churn, not anonymity, relay/exit diversity, or public-route availability.

ADR 0208 repeats the unchanged cell through a distinct public Tox record as compact proof
`pair.9cx0jels`. Both Tor streams reopen on distinct circuits, but both post-churn application PINGs
remain at the same epoch and generation. Compared with ADR 0207's reopened-stream explicit-resume
branch, this proves Tor transition type does not predict or authorize the Ratox lifecycle. The pair
of sequential runs begins relay-record sampling; it is not separated time/exit diversity.

ADR 0209 constructs and live-qualifies the adversarial local boundary with a separate numeric
SOCKS-over-SOCKS interposer. It can leave its listener and both established TCP sides open while
holding relay bytes, then release them exactly. Accepted compact proof `pair.vx6z0csh` joins every
exact chain to Tor control and process sockets, retains TCP-only TAP containment, observes Ratox
warning before authoritative offline and a detached PTY, then resumes exactly after removing only
the hold file. Listener reachability, fresh target admission, and Tor control remain observations,
not carrier or session authority.

ADR 0210 independently accounts the target-circuit population across all eight retained compact
two-IoTox actual-Tor proofs after ADR 0243's later operator-window repetition. The deterministic
analyzer first re-verifies every compact root, then resolves 30 exact-target role/phase and
before/after churn declarations against raw circuit paths. They form 24 normalized three-hop
identity paths with 20 first hops, 23 last hops, and no
cross-proof complete-path or last-hop reuse. Only domain-separated set commitments and counts are
published. A distinct last hop is population evidence, not independent exit/operator, geography,
anonymity, availability, or time-window evidence. See
`docs/evidence/2026-08-28-actual-tor-path-population.md`.

## Tox/I2P — qualification history and remaining nonclaims

ADR 0211 froze the client-side construction seam before enabling the route. The
`run-i2p-sam-socks.py` process maps explicit complete numeric Tox records to exact canonical
52-character b32 destinations, connects only to a numeric loopback SAM v3.1 bridge, owns one
long-lived transient STREAM session, denies new work during session loss, and recreates a higher
local generation. It accepts no domain target, address-book name, outproxy, wildcard, UDP, or native
fallback. Ten streams, including eight simultaneous streams, pass an independent process double
across exact framing and loss/recovery.

ADR 0212 now adds a bounded actual-I2P seam below the product: one byte-verified warm-up plus four
simultaneous 64 KiB streams pass through the strict adapter and two distinct live i2pd 2.60.0
processes on this host. The receipt binds router/process/socket attribution and the immutable router
source without retaining raw Destinations. ADRs 0213–0215 then add the persistent service and carry
two real peers through the full same-host application lifecycle. ADR 0216 accepts source-linked
two-guest TAP containment and a secret-free compact baseline. ADR 0217 keeps the adapter listener
up while its client SAM/router disappears, requires bilateral authoritative offline, replaces the
router over preserved state, and proves higher-epoch bilateral text with no native fallback.
ADR 0218 preserves both exact socket-attributed routers while replacing all three server fronts over
unchanged private Destination keys, then proves the same bilateral higher-epoch application
recovery. ADR 0219 adds private-v2 route membership and assigns one exact 131,369-byte signed tree to
the I2P member with zero reassignment while native fallback stays ready. It also records that 512 KiB
and 4 MiB diagnostic objects crossed a carrier epoch and safely fell back as complete objects.
Per-job constructed-network filtering and fail-closed loss are now locally enforced, and the next
guest run requests the I2P construction class explicitly (ADRs 0221–0222). Route-set v2 signs that
member class (ADR 0225), ADR 0226 qualifies genuine fail-closed loss/recovery, and ADR 0227 qualifies
the unchanged digest-bound range-v1 transport over that exact member. ADR 0228 qualifies a live
1 MiB range loss, strict no-downgrade cleanup, same-member recovery, and explicit distinct fresh
  pull; I2P carrier-loss prefix resume and broader repetition remain open.
ADR 0229 repeats the destructive gate with exact local manifest reuse: compact proof
`pair.ip5q0at9` requests only the fresh 1 MiB range while committing both objects. It removes a
786,496-byte redundant transfer but retains the I2P-loss-prefix nonclaim.
ADR 0230 qualifies prefix reuse only for one ordinary same-process/same-job/same-carrier retry:
compact proofs `pair.cj5y5vgt` and `pair.qeb99i4o` seek past exact private UDP/TCP prefixes under
fresh attempt and FileId identities. It does not retain the I2P carrier-loss prefix or change route
selection, class, failure, or fallback semantics.
ADR 0253 promotes the exact strict construction to canonical `tox/i2p` and accepts compact
production-spelling proof `pair.btm5vwr9`. Selection still fails closed on incomplete topology and
never falls back to `Tox/native`. The construction spelling is a deprecated reproduction alias.
See `docs/i2p-route-construction.md`.

## Identity linkability

Native, Tor, and I2P contexts use independent random Tox identities by default. The ordinary
native path is `device.toxsave`; Tor selects `device.tox-tor.toxsave`; I2P owns
`device.tox-i2p.toxsave`, all under the same state directory. The directory-scoped stable device
identity and authority ledger therefore remain common while the publicly observable Tox keys do
not. Supplying `--state` or `IOTOX_STATE_PATH` overrides that split and is an explicit linkability
decision.

No Tox key is derived from the stable principal, and no public lookup maps the principal to its
routes. A complete cross-route inventory is private authorization material. ADR 0198 requires it to
cross an already authority-authenticated primary association; an auxiliary path may prove only its
expected member. Route-binding v1 instead carries the full roster on the auxiliary
friendship and is qualified only for same-context construction. It must not be used to claim
native/Tor unlinkability. The negotiated v2 codec now exists: full inventory type 26 is authority-
primary-only, and auxiliary type 27 binds one expected member plus the full artifact digest. The
explicit `--enable-private-route-bindings` gate provides bounded primary replay/high-water, worker
handoff, member-only exchange, and authority-loss withdrawal (ADRs 0199/0200). Exact-key
`--route-worker-network KEY=tox/native|KEY=tox/tor@NUMERIC_PROXY|KEY=tox/i2p@NUMERIC_PROXY`
overrides are validated as one
complete topology before any worker starts. Nonempty exact-key `--route-worker-bootstrap` and
`--route-worker-tcp-relay` lists replace inherited primary catalogs, are bounded to 16 records each,
and keep mutable deployment reachability outside the signed inventory (ADR 0202). ADR 0201 and
compact proof `pair.z948jeii` qualify the
default-off v2 path in two Sandwurm guests with native primary/native bulk/strict generic-SOCKS bulk
contexts and one signed 4,194,389-byte tree. The forwarder is not Tor, so an actual-Tor two-peer
claim remains open.
Separate keys remove one direct identifier correlation; they do not prove
anonymity against timing, traffic-shape, peer, relay, or host observation.

## Direct overlays

Direct IoTox transports over Tor or I2P are not implemented and are not synonyms for Tox over those
routes. They would need their own session, delivery, identity, file, and peer semantics while still
carrying the IoTox application protocol.
