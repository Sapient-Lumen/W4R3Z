# Sandwurm cancellation-before-route-loss evidence

Date: 2026-08-26

Status: accepted Gate 4 opposite deterministic loss/cancellation order

## Claim

One source-linked IoTox client and one simultaneous device guest used a signed protected primary and
two separately keyed, reciprocally authenticated bulk workers. The client bound positive incoming
immutable-object progress and two units of admitted signed work to one exact auxiliary incarnation.
It then completed ordinary local cancellation: the job became terminal, incoming transfer and
staging state disappeared, and admitted route work reached zero.

Only after that settled boundary did the Agent stop the cancelled pull's retained exact carrier. The
late loss produced no reassignment and no renewed object request. One signed restart-budget unit
reconstructed the same route identity under a new worker incarnation; both bulk routes returned
ready before the pair completed 40 protected Ratox samples below 250 ms.

## Accepted compact cells

| Route | Compact proof | Cancelled staging | Cancel tail | Work | Loss / reassignment / stale / recovery | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.yv4txv1r` | 12,339 bytes | 80 ms | 2 → 0 | 1 / 0 / 2 / 1 | 17.686 / 18.244 ms | 502,581,699,787 ns | `c62c0d5a2916617093bccbaca42b8521123ab6204344698c3244388709788d1c` | `5d2a49e0a01e0228d7aab555906612f2373ba02abb15fe5b9c809355b7afddd3` |
| forced TCP | `.sandwurm/exports/pairs/pair.m2396itk` | 6,855 bytes | 70 ms | 2 → 0 | 1 / 0 / 2 / 1 | 129.344 / 133.915 ms | 538,480,419,783 ns | `709d1444bc05ec323ae2c269d03750928d625e514d6eac74bc626ee0b7e7863c` | `eab5292660b5988a347a4f3b36110eb443150d4c33e8e3969956ab69d7ee2e41` |

Each compact export allocates 241,664 bytes and excludes private guest disks, identities, bootstrap
secrets, mutable runtime state, FileIds, content paths, and content. Both bind source revision
`10871f9098adb68936ed8a7bd4287e097b613cf4-dirty`, rev0039, and binary
`184cef5e5dcf86f10c9ff1024d118e063ccc40ecebc3d7c59a305ee10f842284`.

The direct-UDP client/device receipt hashes are
`941b1d52f76a8f4c2935a3a0d6a1467b3375743e58847367ebbfd34d507b244a` and
`24be02537d5bbc4725da8161bf5b5b704ce0541583430fc41822f47aa0892824`.
The forced-TCP hashes are
`c4978057145007f8d330fed1caa655e49f2d9f6c5e1a1b67131bd4237eac440c` and
`9f871ddfa63f3ba72a3cdafae3f2ef6bbf32d0624e61efbe56499f1898af7b58`.

Both cells bind the same source artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and signed HEAD
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.

## Causal evidence

Before cancellation, the retained job and route status agree on one auxiliary route key, one
nonzero worker incarnation, positive receive progress, and admitted work of two. `sync-cancel`
returns only after the subscriber fences the job, closes transport and scheduler state, removes
staging, and settles durable attempts. The guest then observes the cancelled tombstone and zero
total admitted work.

The new Agent seam is conditional on that settled cancelled state. Status subsequently records
`qualification-fault=1`, `qualification-fault-position=0`, and
`qualification-fault-after-cancel=1`. The exact stopped key equals the cancelled carrier and the
post-recovery key; its worker incarnation changes. Both accepted cells report exactly one carrier
loss, zero reassignment, two late terminals rejected against the retired incarnation, and one route
recovery.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-cancel-loss

./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.yv4txv1r \
  sync-tree-route-cancel-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.m2396itk \
  sync-tree-route-cancel-loss
```

Both raw roots passed independently before export. Both compact roots passed independently after
export. The verifier binds the same cancelled, final, and stopped carrier key; zero fault position;
one loss; zero reassignment; positive stale-terminal fencing; one recovery; final two-route
readiness; native carrier class; receipt hashes; binary hash; protected Ratox; and every compact-file
digest. Its self-test rejects a synthetic post-cancellation reassignment.

## Exact nonclaims

This qualifies one deterministic `cancellation → route loss → recovery` order after positive
progress and complete local cleanup. It does not qualify a simultaneous race, random inter-event
delays, multiple cancelled pulls sharing a carrier, automatic production restart, larger-object
throughput, physical common-link priority, independent relays, multi-source download, byte striping,
transparent bonding, or long-running fleet policy. ADR 0177 freezes this interpretation.
