# Sandwurm actual-Tor Ratox circuit-churn evidence

Date: 2026-08-28

Status: accepted bounded two-IoTox actual-Tor terminal duration and circuit-churn evidence across
two public relay records

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean commit
`77a020003c717e886f26b02efea5afe65d3b0fdb` and identical IoTox binary SHA-256
`70cd90ce57c2d0f69555e3a3f8d116664c47684e517ff33909b9dd68568b2c1a`. Both primary agents used
strict `Tox/Tor` through independent Tor 0.4.8.11 processes and the one operator-supplied current
public numeric Tox TCP record `205.185.115.131:33445`. The private bootstrap fixture was used only
for deterministic identity handoff; neither guest TAP contains traffic to it.

One authority-bound echo PTY completed 120 paired heartbeat and terminal exchanges at a one-second
inter-sample interval. After samples 20 and 100, authenticated Tor control sent `CLOSECIRCUIT` to
the exact application circuit carrying the client and device stream respectively. Tor, IoTox, both
guests, the Ratox session, its host-process incarnation, and its accepted byte positions remained
under one continuous evidence timeline. The active probe wall time was 476.708 seconds.

The two checkpoints exercised both accepted protocol branches:

| Checkpoint | Tor transition | Tor recovery | Ratox outcome |
|---|---|---:|---|
| client after sample 20 | same stream reattached to a distinct three-hop `CONFLUX_LINKED` circuit | 123.813 ms | attachment-continuous; epoch 2 and generation 1 unchanged; byte positions advance through 21 |
| device after sample 100 | new stream opened on a distinct three-hop `CONFLUX_LINKED` circuit | 30.220 s | authoritative loss followed by explicit resume; epoch 2 to 3 and generation 1 to 2; byte positions advance through 101 |

Both closes have raw `REASON=REQUESTED` evidence. The v3 churn envelope binds authenticated
before/after `stream-status` and `circuit-status` snapshots to exact path and digest commitments.
The same-stream branch additionally joins the eventual raw STREAM close to the replacement circuit;
it does not fabricate a second `SUCCEEDED` event that Tor's Conflux reattachment did not emit.

All 120 input and output sequences reached their exact next positions, and the lifecycle records one
resume only. Tor process restart count, IoTox daemon restart count, and guest restart count are all
zero. The greatest observed terminal round trip was 5.912 seconds at sample 23; the greatest
heartbeat round trip was 6.407 seconds at sample 105. These are one public-network observation, not
protocol deadlines or a latency SLO.

## Packet and Tor containment

The exact Tor binary SHA-256 was
`63055c572ff1ec2cb96b9ea4855804a06d06d26558609a028fa4d492e199c2b2`. Both authenticated control
planes reached bootstrap 100. Final attribution bound guest-source streams to the configured Tox
target and qualifying three-hop linked-Conflux application circuits. Every captured guest IPv4
egress packet was TCP to its role-specific Tor listener; both captures contain zero native UDP,
direct bootstrap, direct relay, or direct peer packets.

| Role | IPv4 egress | Sole destination | Capture SHA-256 |
|---|---:|---|---|
| client | 2,862 | `10.0.0.1:39051` | `63c61959e1e7a9e115148e77b387a356d0efb0999839d48dfe71eea51b19433f` |
| device | 2,961 | `10.0.0.1:39052` | `5040737ae28b19bb7d3ebeaafaca00de44254fc0e209c2e35962ce92fba3711a` |

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.k8o54n2v`. It allocates 3,129,344
bytes, reports `contains_secrets=false`, and omits guest disks, injected identities, runtime state,
the bootstrap secret, and Tor data directories. The source-private manifest, compact pair manifest,
churn record, lifecycle record, and compact-export SHA-256 values are respectively:

```text
63298d08f071aad51840bf7ba534650054e837daf29a64eaa950e1df1f083017
9d14f7b24d45a397d6505baadf1cb337f7995e76d6f93b12b661daa3ef2b4229
28fdd6c3b2ba5890e6ce52114835110ce117ca3d4456e260fbe8690a9f0b00cb
198a75218766a62fbe00aeaa9f3b76096a156c44af4612523f6eb56937870221
af06619a895bece5d8b10898644ae07d3311992db5d5e51a13fdd43c51266125
```

```sh
./tools/iotox-sandwurm-lab.sh up-pair tox-tor \
  ratox-route-actual-tor-soak \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/lab/pairs/PAIR_ID ratox-route-actual-tor-soak
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair tox-tor \
  .sandwurm/exports/pairs/PAIR_ID ratox-route-actual-tor-soak
```

Both the 2,583,646,208-byte private root and compact export independently returned `passed` from
the strict verifier. The verifier reparses raw Tor events, authenticated inventories, both pcaps,
terminal and heartbeat captures, the controller lifecycle, process identities, source/target
attribution, replacement ordering, session/incarnation/generation/sequence continuity, and VMM
chains. The complete rendezvous span, including realization and public-network waits, was
849,254,938,108 ns.

## Second relay-record repetition

The unchanged gate was repeated against distinct operator-supplied record `3.0.24.15:33445` as
compact proof `pair.9cx0jels`. Two simultaneous guests ran clean commit
`e33b4bd72aee912f0ad8d94640e0ea473912ae18` and the same product binary SHA-256 as the first proof.
All 120 samples completed in 468.286 seconds of active probe time. Both requested circuit closes
produced new stream IDs and distinct qualifying three-hop circuits, in 17.273 seconds on the client
and 17.174 seconds on the device, while both application checkpoints returned a canonical PONG at
unchanged online epoch 2 and generation 1. The lifecycle records zero resumes and exact byte
positions 21 and 101.

This is a useful cross-layer result: `stream-reopened` does not imply authoritative Tox carrier loss.
The first proof's device reopened a Tor stream and required explicit Ratox resume; the second proof
reopened both Tor streams while the attachment remained continuous. Tor stream/circuit evidence
therefore cannot predict, fabricate, or authorize a session transition. The frozen post-churn PING,
c-toxcore carrier truth, and authenticated explicit-resume rules remain necessary.

The greatest observed terminal and heartbeat round trips in the repetition were 2.525 seconds and
3.144 seconds respectively. The TAPs captured 2,924 client and 2,966 device IPv4 egress packets,
all TCP to the exact role-local Tor listeners with zero native UDP or direct bootstrap/relay/peer
traffic. The raw proof allocated 2,547,585,024 bytes; its secret-free compact form allocates
3,297,280 bytes. Raw and compact forms independently pass strict verification. Their source-private
manifest, compact pair manifest, churn record, lifecycle record, and compact-export SHA-256 values
are respectively:

```text
52df8ebbac33133cfb973266060f2c5cec04c28ffacec2bdb8cbbbaf0584dc99
8f87ff5dffbfc85707a8e3bff1f4ce45680d549af3cf70995ca02cbd730c1b91
ac6cb603a8dc69e102f4ff60950725b1ef83e1b39f017b6d401a473904751b03
0c02ae97d76e82a853c003d8c532fb925db6c71e8aea66c02de6e8aeb41264a2
ba01548ed1af6be85c6b66c3881ad085e746514c172b568172a8b70245c1a91a
```

| Proof | Public Tox record | Tor transitions | Ratox outcomes | Resume count |
|---|---|---|---|---:|
| `pair.k8o54n2v` | `205.185.115.131:33445` | client reattached; device reopened | continuous; explicit resume | 1 |
| `pair.9cx0jels` | `3.0.24.15:33445` | client reopened; device reopened | continuous; continuous | 0 |

## Exact nonclaims and next gate

This proves one bounded terminal duration and two controlled circuit replacements with continuous
Tor and IoTox processes. It does not claim anonymity, unlinkability, timing-correlation resistance,
physical-path independence, automatic migration, transparent recovery in every churn, relay or exit
diversity, adversarial-proxy resistance, fleet behavior, a public-relay availability SLA, or a
latency SLO. It is one physical host, two local VMs per run, two public Tox records, one Tor build,
one echo profile, four deliberate circuit closes, and two sequential runs in one date/time window.

ADR 0209's later `pair.vx6z0csh` closes the first adversarial local-proxy cell. The remaining M8
evidence frontier is more repetition across reviewed relays, independently separated time windows,
and observed exit populations. Those experiments must retain the frozen distinction between Tor
observations, c-toxcore carrier authority, and explicit Ratox attachment transitions.
