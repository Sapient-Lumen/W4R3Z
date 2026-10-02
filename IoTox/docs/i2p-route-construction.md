# Tox/I2P route boundary

## Current status

`Tox/I2P` is a VM-qualified strict IoTox product route. ADR 0213 originally added the separately
named laboratory route `tox/i2p-construction` so exact experiments did not falsely report I2P
traffic as Tor. ADRs 0211–0215 construct both sides of the route: exact numeric c-toxcore
targets map to an exact I2P Destination, and that persistent Destination forwards raw streams to one
numeric-loopback TCP service without DNS, an address book, or a clearnet outproxy.

```text
c-toxcore TCP-only
  -> exact numeric SOCKS5 CONNECT
  -> IoTox SAM adapter allowlist
  -> exact canonical 52-character b32 destination
  -> numeric loopback SAM v3.1
  -> I2P STREAM
  -> exact loopback egress shim or operator-exposed Tox TCP service
  -> same numeric Tox node named in the original record
```

ADR 0212 live-qualifies the adapter-to-I2P-STREAM edges through two distinct i2pd processes on this
host. ADR 0213 process-qualifies the stable service boundary and live-checks it through two routers.
ADRs 0214–0215 add the bounded relay-establishment budget and address-preserving three-front
topology. Two actual c-toxcore peers pass the complete friendship/authority/application/restart
lifecycle through that topology. ADRs 0216–0219 and 0225–0229 add Sandwurm containment,
router/front recovery, signed route classes, fail-closed sync loss, and range payloads. ADR 0253
promotes that exact policy to canonical `tox/i2p`; `tox/i2p-construction` remains a deprecated
reproduction alias, not a separate provider configuration.

## Frozen server contract

```sh
python3 tools/run-i2p-sam-forward.py \
  --sam 127.0.0.1:7656 \
  --target 127.0.0.1:33445 \
  --destination-key /absolute/private/service.destination \
  --audit /new/private/service-forward.audit.jsonl
```

The immediate key parent must be owner-owned and deny group/world access. A new key is written once
with mode 0600, fsynced with its directory, and never overwritten. An existing key must be a bounded
owner-owned regular single-link 0600 file opened without following a final symlink. Canonical padded
I2P Base64 is decoded; the private record must contain the exact public Destination prefix. The
traditional b32 address printed on readiness is public route configuration. The private record is
never printed or audited.

The process requests exact SAM 3.1 `DEST GENERATE`, a persistent STREAM session with
`i2p.streaming.profile=2`, and
`STREAM FORWARD ... HOST=<numeric-loopback> PORT=<exact-port> SILENT=true`. Both long-lived control
sockets define one readiness generation. Loss of either creates one content-free `lost` record;
only a newly formed pair produces a higher ready generation. The router—not this process—opens the
loopback service socket and relays bytes.

## Frozen client contract

The command is deliberately explicit:

```sh
python3 tools/run-i2p-sam-socks.py \
  --listen 127.0.0.1:39051 \
  --sam 127.0.0.1:7656 \
  --map 205.185.115.131:53=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.b32.i2p \
  --audit i2p-sam-audit.jsonl
```

The numeric record must be the exact real c-toxcore node endpoint present in the frozen
bootstrap/TCP-relay catalogs. It is never connected natively by IoTox or the adapter. Tox embeds
bootstrap addresses inside its encrypted onion paths, so a documentation alias such as
`192.0.2.17` produces an unroutable remote path even though the SOCKS and encrypted relay handshakes
succeed. The right side is a traditional 52-character b32 name, which commits the I2P Destination
without using the locally mutable human-readable address book. Extended blinded names, full base64
Destinations, and per-client secrets need separate syntax and policy before they may be accepted.

A fresh TCP-only gate uses at least three explicit bootstrap and three explicit relay records, each
with its own exact map and current single-target persistent service front. This is a c-toxcore
population requirement, not an I2P naming rule. No records or Destinations are compiled defaults.

The adapter requires the SAM bridge on a numeric loopback address because SAM 3.1 provides no
mandatory transport authentication. It requests exactly:

```text
HELLO VERSION MIN=3.1 MAX=3.1
SESSION CREATE ID=<random-process-id> STYLE=STREAM DESTINATION=TRANSIENT SIGNATURE_TYPE=7 i2cp.leaseSetEncType=4 inbound.quantity=2 outbound.quantity=2 i2p.streaming.profile=2
STREAM CONNECT ID=<same-id> DESTINATION=<exact-b32> SILENT=false
```

The session stays alive on its control socket. Every application stream uses a separate SAM socket.
The adapter answers SOCKS success only after explicit SAM stream success. If the control socket
dies, the listener may remain reachable but new mapped requests fail until a new transient session
reaches a higher adapter generation. None of these observations changes c-toxcore carrier or IoTox
Ratox/sync state.

Each route-decision audit record includes content-free `setup_us` from accepted local SOCKS
connection through its SAM outcome. It separates local/SAM setup from later Tox and application
convergence without labeling either as carrier truth.

## Identity and evidence policy

The SAM session is outgoing-only and transient. Its returned private Destination is discarded and
never logged. The process-local random session ID is reused only across router reconnection within
that adapter process. IoTox's stable device principal and authority ledger remain above the route;
the separately stored `device.tox-i2p.toxsave` remains the future Tox route identity. That Tox key is
observable to the remote peer and may link traffic inside the I2P route; no anonymity claim follows
from transient SAM identity.

Audit records contain target records, local generations, outcomes, setup microseconds, monotonic
timestamps, and a
domain-separated SHA-256 commitment to the mapped b32 destination. They contain no payload, SAM
private Destination, or raw b32 mapping. Denial decisions enter the audit while holding the state
lock before the corresponding SOCKS failure reply, so a returned denial cannot race behind a later
SAM-loss record.

## Process qualification

```sh
python3 tests/test_i2p_sam_socks.py tools/run-i2p-sam-socks.py
```

An independent SAM process double verifies exact SAM 3.1 protocol bytes, eight
simultaneous streams plus two sequential streams, byte identity, strict target mapping, domain-name
denial, admission closure during SAM loss, generation-two recovery, stable process-local session ID,
and content-free audit output. It separately injects a SAM 3.2 PING to freeze a defensive PONG
response; that extension is not claimed as part of the negotiated 3.1 protocol.

The independent server-side process test is:

```sh
python3 tests/test_i2p_sam_forward.py tools/run-i2p-sam-forward.py
```

It freezes exact DEST/SESSION/FORWARD commands, stable key reuse, padded Base64, `SILENT=true`, raw
target bytes, generation-two recovery, mode-0600 key policy, audit no-clobber, loopback-only target
selection, and content-free audit records. A separate live construction passed exact echo bytes
through the client adapter, two distinct i2pd processes, the persistent Destination, and the
forwarded local service. This is still below c-toxcore.

The bounded live construction runner is:

```sh
python3 tools/run-i2p-sam-smoke.py \
  --server-sam 127.0.0.1:SERVER_PORT \
  --client-sam 127.0.0.1:CLIENT_PORT \
  --server-router-pid SERVER_PID \
  --client-router-pid CLIENT_PID \
  --router-binary /absolute/path/to/i2pd \
  --router-source /absolute/path/to/immutable/i2pd-source \
  --output /new/path/to/receipt.json
```

It refuses a dirty source tree, shared router processes/endpoints, non-loopback SAM, a mismatched
router executable or command line, and routers without both their exact SAM listener and at least one
public TCP peer. It commits the complete immutable router source tree and creates an unencrypted
LeaseSet2 server Destination on one router. It keeps exactly one pending server-side SAM accept while
dispatching accepted streams concurrently, avoiding dependence on router-specific accept-queue
semantics. It sends four simultaneous 64 KiB byte-verified streams through the strict adapter and
the other router only after one bounded byte-verified warm-up stream has established that the new
LeaseSet is discoverable. Expected pre-discovery `denied-stream` outcomes remain counted in the
receipt. A client barrier must release all four measured attempts within 50 ms. The
content-free receipt binds both processes and binaries, exact payload and remote-Destination sets,
adapter audit records, and timings. The server and adapter use the same domain-separated b32
commitment so an independent verifier can join the exact mapped Destination without retaining its
raw name. This same-host router smoke is intentionally below the full live
gate: it is neither Tox traffic nor guest packet-containment evidence.

## Accepted actual-I2P seam

The accepted rev0045 receipt was produced from clean IoTox commit `a1f3b53`, i2pd 2.60.0, one
executable digest, and one 315-entry immutable source-tree commitment. The two long-lived router
processes owned distinct SAM endpoints and retained 12 and 49 public TCP peer sockets at capture.
The server session formed in 9.018 seconds; a 4 KiB warm-up completed in 2.526 seconds without a
discovery denial. A barrier then released four measured clients within 0.083 ms. All four distinct
64 KiB payloads echoed exactly, with end-to-end latencies from 23.689 to 25.390 seconds.

The first construction attempt exposed a defect in i2pd 2.60.0 rather than an IoTox framing rule:
its `SAM.cpp` queued-accept expiry loop removes entries whose deadline is still in the future. Two
of four accepts survived the race. The accepted runner therefore keeps exactly one pending SAM
`STREAM ACCEPT`, dispatches an established stream to its own worker, and only then creates the next
pending accept. Client attempts remain simultaneous. This is an implementation compatibility rule,
not a claim that SAM itself permits only one pending accept.

Verify the retained receipt and, when the exact Nix inputs are present, its router bits:

```sh
python3 tools/verify-i2p-sam-smoke.py \
  artifacts/rev0045/i2p-sam-two-router-smoke.json

python3 tools/verify-i2p-sam-smoke.py \
  artifacts/rev0045/i2p-sam-two-router-smoke.json \
  --router-binary /nix/store/...-i2pd-2.60.0/bin/i2pd \
  --router-source /nix/store/...-source
```

## Accepted actual-I2P Tox/application gate

ADR 0215 records the successful three-front cell. Two fresh source-linked IoTox peers each opened
three streams to the loopback adapter and reached `self-connection=tcp` through two distinct i2pd
2.60.0 processes. The unchanged genuine real-peer harness then passed canonical protocol sessions,
owner recovery and delegation, revocation across restart, ownership epoch transition, text, durable
commands, an exact finite file, a second restart, and friendship removal/re-add.

The falsification ladder matters: one record was insufficient; three direct records passed; three
fake-address I2P maps failed after completing relay handshakes; and the same maps keyed by the real
numeric Tox addresses passed. Repeating the carrier check with only the 120-second TCP establishment
patch also passed, so the proposed onion-state timeout patch was removed. See
`docs/evidence/2026-08-28-actual-i2p-real-peer-e2e.md`.

## Accepted Sandwurm baseline and recovery gates

ADR 0216 accepts compact proof `pair.k_vopzf5`. Two source-linked Sandwurm/KVM guests used the
bridge adapter, the same exact three-record commitment, two pinned i2pd 2.60.0 routers, and three
persistent service fronts. Both reached TCP friendship, canonical session confirmation, and
bidirectional text. Their TAP captures contain 1,054 and 1,164 IPv4 egress packets respectively,
all TCP to `10.0.0.1:39053`, with zero UDP, direct bootstrap, direct peer, or other IPv4 destination.
The raw 2.44 GB proof and 1.59 MB secret-free compact proof independently pass the strict verifier.

ADR 0217 accepts the router-loss companion as compact proof `pair.v_11i2me`. The exact source-matched
21-file certificate bundle is selected and signed reseed verification is enabled. Both guests prove
an authenticated pre-fault session; the host kills only the client i2pd while the bridge listener
stays reachable and SAM becomes absent; both guests independently observe c-toxcore offline. A
distinct router PID reuses the same private datadir, the adapter advances to generation two, both
guest epochs advance from 1 to 2, and fresh text arrives bilaterally. The TAPs retain zero UDP,
direct-bootstrap, direct-peer, or alternate-destination traffic. Raw 2.46 GB and 1.76 MB secret-free
compact forms independently pass the strict verifier.

ADR 0218 accepts the server-front companion as compact proof `pair.6rrdsdc_`. Both source-attributed
router PIDs remain live, retain their SAM listeners, and own established public TCP remote sets while
all three persistent forward processes are terminated. Both guests independently observe offline.
Three distinct processes then load the exact same owner-private Destination keys; all three b32
identities remain stable, the adapter remains on SAM generation one, both guest epochs advance from
1 to 2, and fresh text arrives bilaterally. The 68.615-second replacement interval and both TAPs
retain zero native fallback. Raw 2.46 GB and 1.61 MB secret-free compact forms independently pass.

The baseline and two recovery companions close the router/source/certificate pin, three-front topology,
two-guest source-linked lifecycle, listener-positive/SAM-negative fault, exact client-router
replacement, exact stable-Destination front replacement, initial exact-router public-socket
attribution, authoritative interruption, higher-epoch recovery, TAP containment, and raw/compact
evidence portions of the larger gate.

## Accepted private-member payload and size boundary

ADR 0219 accepts compact proof `pair.5xjf2n4d`. Both guests retain a native primary and fallback
while private route-binding v2 admits one exact `Tox/I2P-construction` auxiliary. Only after
`sync-status` reports both expected routes for the remote principal does fixed placement begin. One
131,369-byte signed tree is attributed to the I2P auxiliary, accepted, and explicitly activated with
zero reassignment. Both i2pd routers and all three fronts remain live; mixed-context TAP evidence
contains native and I2P endpoints with zero unexpected packets.

The bound is intentional. Diagnostic 512 KiB and 4 MiB objects initially selected I2P but outlived
an authoritative carrier epoch and were safely retried as complete objects through native. The
512 KiB capture's busiest client-to-adapter flow carried about 301 KiB across roughly 101 seconds.
The original auxiliary protocol carried complete object request/result records and intentionally
excluded range frames, so this was a 128 KiB accepted lower bound and 512 KiB rejected upper point for
one construction window—not an I2P throughput limit. ADR 0227 now closes that protocol omission by
carrying the unchanged range-v1 frames only after bilateral feature negotiation on both the primary
authority session and exact auxiliary worker.

ADR 0225 subsequently signs the member's exact construction-I2P class in route-set v2. ADR 0226 and
compact proof `pair.jbr89_gc` accept its destructive companion: after 69,921 object bytes, client
router loss leaves the class-pinned job blocked with native ready and zero reassignment; the same
member returns under a distinct router process with zero worker restart; only explicit cancellation
and a fresh class-pinned job complete the tree. Raw and 6.656 MB secret-free compact forms
independently pass. See `docs/evidence/2026-08-28-sandwurm-fail-closed-i2p-loss.md`.

ADR 0227 and compact proof `pair.ej_4507n` accept the positive large-successor path. Generation 1
installs a verified 4 MiB native basis; generation 2 is pinned to the signed construction-I2P member,
reuses 4,194,176 bytes from that basis, fetches its one changed 128-byte artifact range on the exact
I2P member, accepts the linked HEAD last, and activates explicitly with zero reassignment or
router/front restart. The range index/manifest and protocol overhead are not included in the
128-byte artifact-range count. See `docs/evidence/2026-08-28-sandwurm-actual-i2p-range.md`.

ADR 0228 and compact proof `pair.a9zwongf` accept its destructive companion. The host stops only the
client router after 86,373 bytes of a concrete 1 MiB range. IoTox retires the receive, removes all
staging, blocks the class-pinned job, and makes zero reassignment. The same signed member recovers
once over preserved router state with zero worker restart. Explicit cancellation plus a distinct
fresh job then refetches the complete 1 MiB range, reuses 3 MiB of verified basis, and activates the
exact 4 MiB target. See `docs/evidence/2026-08-29-sandwurm-actual-i2p-range-loss.md`.

The remaining hardening and availability work includes:

1. same-attempt or failed-prefix range resume without weakening the qualified signed route-class,
   fail-closed, attempt, and final-digest constraints;
2. larger exact-I2P object/range distributions after the fresh-recovery gate; and
3. repetition across later time windows and distinct records before any availability claim.

The canonical invocation is `--network tox/i2p` plus one numeric SOCKS endpoint and at least three
explicit address-preserving numeric bootstrap/relay records for fresh-key gates. The historical
`--network tox/i2p-construction` spelling remains accepted only for reproducing old evidence and
maps to the same numeric route classes, savedata, and strict provider options. See ADR 0253 and
compact proof `pair.btm5vwr9`. Selection still proves neither anonymity nor broad production
suitability.

## Protocol sources

- I2P SAM v3 specification: <https://i2p.net/en/docs/api/samv3/>
- I2P naming and traditional/extended b32 formats: <https://i2p.net/en/docs/overview/naming/>
