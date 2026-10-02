# Sandwurm actual-I2P bounded-range evidence

Date: 2026-08-28

Status: accepted positive authenticated-auxiliary range evidence

## Claim

Two simultaneous source-linked Sandwurm/KVM guests ran clean revision
`38081157378597f61a86444a2f5fd1264348f0ae` and identical IoTox binary SHA-256
`8a919501363fe3987806116843088744017e653f3877e7bca989a6e22888a726`. Both authenticated the signed
native/native/construction-I2P private-v2 route set and negotiated `state-sync-ranges-v1` on the
primary authority edge and exact auxiliary worker.

The subscriber first pulled and explicitly activated a deterministic 4 MiB generation-1 basis over
native. The publisher then changed one 128-byte region and signed parent-linked generation 2. A new
per-job `fail-closed tox/i2p-construction` pull selected the exact signed I2P member, received one
bounded range, reused the verified remainder of the basis, checked the complete successor digest,
accepted its HEAD last, and explicitly activated it. The selected member never changed.

```text
product revision                    rev0045
artifact bytes                      4,194,304
range count                         1
artifact bytes fetched              128
verified basis bytes reused         4,194,176
generation                          2
reassignments                       0
client router restarts              0
service-front restarts              0
initial pull attempts               1
initial pull failures               0
```

The exact carrier is represented only by domain-separated SHA-256 commitment
`0a1530b0f9486da2d6dd96855c92357b30d38594a52a4ecfcc889b0e0b2f606c`.
The accepted immutable identities are:

```text
HEAD record       dead8d7be3834b7d06128ae25a6b343168c48e154ac3af60a605944c7a85b31d
artifact SHA-256  0e2590fa6bcc290f7307cb0c0a34cc807934895293f4be25aafb102383075411
manifest SHA-256  322dd3fffdda3747ca592f2627138d8ae32fd064680b34aa4dd238b01804e032
```

The 128-byte count is the fetched artifact range. It deliberately does not describe total network
traffic: range index/manifest bytes, protocol messages, Tox/I2P overhead, and background carrier
traffic are outside that counter.

## Route and packet containment

The host constructed two distinct i2pd 2.60.0 routers and three persistent address-preserving service
fronts. The topology rehashes binary `d5e89b4c2520ae5e3776a9c134b54200061b477f8b388bea60f60b07865753b5`,
the 315-file source tree, and the 21-file certificate tree, and confirms signed reseed verification.
Neither router nor any service front restarted during the transfer.

Both guests intentionally retain native routes, so the TAP captures contain mixed native and strict
adapter traffic. Every TCP packet is confined to the configured local proxy/relay endpoints and each
capture reports zero unexpected network-context packets.

| Role | IPv4 egress | Native UDP | Native TCP relay | I2P adapter packets | Unexpected | Capture SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| client | 5,700 | 4,268 | 58 | 1,359 | 0 | `755f2a97321b03d8fe46f4572394d958f9961b4a3c82715856098a63fc2254ea` |
| device | 8,990 | 7,380 | 66 | 1,528 | 0 | `752856a3cd9e9082f467f4a4d34b68e576cf9427d91df12e262e784613d84849` |

## Proof and reproduction

The accepted compact proof is `.sandwurm/exports/pairs/pair.ej_4507n`. It allocates 17,563,648 bytes
across 17 files, reports `contains_secrets=false`, and omits bootstrap secret state, guest disks,
injected identities, and runtime state. The source-private proof allocated 2,483,073,024 bytes. Both
independently return `passed` from the strict verifier.

```text
source-private manifest SHA-256  ce79844804e13a638088e7315fe4114afe0254f0b18818e5aaecb38fa453ce11
compact pair manifest SHA-256    3a3e5fca0f04022a79e3d4aeb5bc27f230935c3210a80a220a5a55c76c9f479b
compact-export SHA-256           f226633f156f2c98fbd1b6e415d4543b9b6f6b91989bd2dfa05684dd7e3b0a9f
topology-final SHA-256           8095c34dad57755af44542819dbcb92686af8948f2af32d0a73cc4e955797987
client receipt SHA-256           b0732f1ba90fa73eb68480f5c70148139648e1c96f503c8482564f643a022d5a
device receipt SHA-256           17d9a9e8bb37e0c46ebd694e44074dea9bc0fde202892e78f4e7e49654a3f0b2
```

Use three explicitly reviewed, currently reachable public numeric Tox TCP records:

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-file-range-actual-i2p \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY \
  IPV4:TCP_PORT:64_HEX_PUBLIC_KEY
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/lab/pairs/PAIR_ID sync-file-range-actual-i2p
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR_ID
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/PAIR_ID sync-file-range-actual-i2p
```

## Exact nonclaims and next gate

This is one bounded time window on one physical host, two local VMs, two local I2P routers, three
public Tox records, and one router implementation/version. It proves positive range-v1 transport on
an authenticated signed-class auxiliary and exact final reconstruction. It proves neither anonymity,
unlinkability, timing resistance, independent administration, performance, total byte savings, nor
fleet behavior. It does not exercise router loss during a range, partial-range continuation, process
restart, repeated or very-late loss, or automatic cross-class replacement. Production `tox/i2p`
therefore remains unsupported. The subsequent ADR 0228 proof closes bounded live-range loss plus
explicit fresh same-carrier recovery while still excluding partial-prefix reuse; see
`2026-08-29-sandwurm-actual-i2p-range-loss.md`.
