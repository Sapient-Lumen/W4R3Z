# Sandwurm cancellation/route-loss race evidence

Date: 2026-08-26

Status: accepted Gate 4 shared-arm cancellation/loss race cell

## Claim

One source-linked IoTox client and one simultaneous device guest used a signed protected primary and
two independently keyed, reciprocally authenticated bulk workers. The client observed a live
immutable-object receive above 65,536 bytes, at which point the Agent armed one exact route/worker
stop for 500 ms later. From that same observable arm edge the client delayed 500 ms and issued the
ordinary local `sync-cancel` command.

On both native carrier classes cancellation won the authority-state serialization point while the
worker independently disappeared. The pull became terminal with no reassignment, but the first
control response exposed typed transport unavailability. One exact retry settled already-fenced
cleanup without repeating the transport effect. Signed work drained from two to zero, incoming and
staging state disappeared, no HEAD or activation was created, the stopped route consumed one restart
budget unit and returned ready, and 40 protected Ratox samples completed below 250 ms.

## Accepted compact cells

| Route | Compact proof | Fault / cancelled staging | Cancel tail | Outcome / cleanup retries | Loss / reassignment / stale / recovery | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.h6kg4fcr` | 175,488 / 198,795 bytes | 60 ms | cancel-first / 1 | 1 / 0 / 2 / 1 | 17.598 / 18.938 ms | 316,464,192,988 ns | `40f5d3e66b4c2ce53e1b9d5802b2f637fbaa64dda932002d2b3b4fc1bcb5b4ca` | `cb03446313c283504c226a3cfd0fda975e6e96114257bc532a6fc907af34ffe6` |
| forced TCP | `.sandwurm/exports/pairs/pair.z9egqd57` | 154,923 / 115,164 bytes | 90 ms | cancel-first / 1 | 1 / 0 / 2 / 1 | 95.707 / 121.089 ms | 444,856,304,651 ns | `78c1615fb1b208cbc74c607b1fa2903879bf5afe8a188f60acbc8e52cb1a5955` | `f457e6996315402846899454a9bc160f56e0e4352ad3379a44a34d34b38fdcba` |

Each compact export allocates 241,664 bytes and excludes private guest disks, identities, bootstrap
secrets, mutable runtime state, FileIds, content paths, and content. Both bind source revision
`1c85180c42f350d0a0fe3c7f80e7ecc67f03087f-dirty`, rev0039, and binary
`881d3abd90374bff8be8ec03191d3d632363a0bfb565677ede9efae807df2615`.

The direct-UDP client/device receipt hashes are
`61133d0e5344fe0892cfc106b631f38e39ef6e5bb3a11bbfa3d9679bb560dc71` and
`b53903b59bf27e26ac5da93f5d6ecf7c5ce9743c0543bc8962955867cd5bf55d`.
The forced-TCP hashes are
`6d9166c981116b8ef1dea5027bd5f277071cfbe0ab60cd94190f637e3023ac3f` and
`146a72dbd93331a12204f9e9c87aa6556058f328c4ca3b34d4d7b9a0eea2ac09`.

Both cells bind source artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and signed HEAD
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.

## Causal evidence

Before the race, status binds the pull's positive position, random worker incarnation, exact carrier,
and two units of admitted work. It then exposes `qualification-fault=0` and
`qualification-fault-armed=1` while carrier-loss and reassignment counters are still zero. The
armed record freezes that route key, worker ID, position, and monotonic deadline; it cannot silently
retarget another transfer.

Both 500 ms contenders then run independently. Each cell records `qualification-fault=1`, one
carrier loss, zero reassignment, two retired-incarnation terminals, and one route recovery. The
cancelled tombstone's final carrier equals its initial and stopped carrier, which strictly defines
the recorded `cancel-first` outcome. The first local command returned status 4 with typed
`error=unavailable`; its single exact retry returned the ordinary `sync-cancelled` result. Final
status has cancellation settled, no incoming transfer or staging, signed work zero, and both bulk
routes ready with exactly one restart on the stopped identity.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-cancel-race

./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.h6kg4fcr \
  sync-tree-route-cancel-race
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.z9egqd57 \
  sync-tree-route-cancel-race
python3 tools/verify-sandwurm-pair.py --self-test
```

Both raw roots passed independently before export, and both compact roots passed independently after
export. The verifier self-test accepts internally consistent cancel-first and loss-first records and
rejects a mismatched outcome. Strict pair replay additionally binds the common receipt outcome and
cleanup count, role ownership of observation, native Tox carrier, exact binary and receipt hashes,
protected Ratox capture, and every compact artifact digest.

## Exact nonclaims

This qualifies one deliberately colliding 500/500 ms shared-arm cell on each native carrier. Both
observed the same cancel-first linearization; that is not evidence about its probability. It does not
qualify a randomized delay sweep, startup during a route fault, multiple simultaneous affected jobs
sharing the failed carrier, automatic production restart, larger-object throughput, physical
common-link priority, independent relays, multi-source download, byte striping, transparent bonding,
or long-running fleet policy. ADR 0178 freezes this interpretation.
