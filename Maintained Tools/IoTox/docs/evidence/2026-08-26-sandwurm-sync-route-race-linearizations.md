# Sandwurm shared-arm race linearization evidence

Date: 2026-08-26

Status: accepted Gate 4 completion of both shared-arm authority outcomes

## Claim

ADR 0178's equal 500/500 ms cells proved cancel-first on direct UDP and forced TCP. This companion
campaign starts from the identical observable armed-progress state but stops the exact worker at
250 ms and issues ordinary cancellation at 1,000 ms without waiting for any loss or reassignment
observation. Both native carrier classes produce the required loss-first outcome.

The old route is fenced once, the missing immutable object is assigned once to the other signed bulk
worker, and cancellation terminates that replacement. Work drains from two to zero; transfer and
staging state disappear; no signed HEAD is accepted or activated; the stopped identity recovers once;
and protected Ratox remains below 250 ms. Unlike the equal-deadline cancel-first cells, the ordinary
cancellation succeeds immediately and needs no cleanup retry.

## Accepted loss-first compact cells

| Route | Compact proof | Fault / cancelled staging | Cancel tail | Outcome / cleanup retries | Loss / reassignment / stale / recovery | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.5gvh__p1` | 200,166 / 139,842 bytes | 50 ms | loss-first / 0 | 1 / 1 / 2 / 1 | 24.955 / 32.603 ms | 488,106,562,971 ns | `0879c59e2f440cb07ea827593775fee80220945a6aaea3df7fc21f8cff3d5a80` | `5ba689d6a2299cbb9b5189a31da06eeb73273cd8160a98d62357793221669411` |
| forced TCP | `.sandwurm/exports/pairs/pair.rxb2dsge` | 164,520 / 100,083 bytes | 60 ms | loss-first / 0 | 1 / 1 / 2 / 1 | 97.949 / 131.836 ms | 468,441,708,022 ns | `98aa3884f18ab43dd265edb0bf7df592845dbe23ebfbaad15fa233ad065e19f5` | `6112adb344959f86a802b3e9f045192a8d4de56461d683b4415d1d67aa8ec605` |

Each compact export allocates 241,664 bytes and excludes private guest disks, identities, bootstrap
secrets, mutable runtime state, FileIds, content paths, and content. Both bind source revision
`5e280229cbb514fbd7cc7c4191d78a1d07571e12-dirty`, rev0039, and binary
`881d3abd90374bff8be8ec03191d3d632363a0bfb565677ede9efae807df2615`.

The direct-UDP client/device receipt hashes are
`9426129c61584745cca1bbdf9a94e85e1218dc7cf30702560022346004b25475` and
`7245ff37cfc5881012604822ffb594746c9085ca2bf26f3f2906ed552b956047`.
The forced-TCP hashes are
`4f32026e875963ec5cf8e81f7969c24c6783cfbe12863e01714d7409e42d43b3` and
`39d1749d741dc1fccbf02b0cba6939dbea2424b11e08e7165baf5e87e3db41ce`.

Both cells bind source artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and signed HEAD
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.

## Cross-outcome evidence

| Outcome | Delays (fault / cancel) | UDP proof | TCP proof | Reassignments | Cleanup retries |
|---|---:|---|---|---:|---:|
| cancel-first | 500 / 500 ms | `pair.h6kg4fcr` | `pair.z9egqd57` | 0 | 1 |
| loss-first | 250 / 1,000 ms | `pair.5gvh__p1` | `pair.rxb2dsge` | 1 | 0 |

Every cell starts from a positive position and `qualification-fault-armed=1` with zero prior loss or
reassignment. Outcome is never inferred from wall-clock intent alone. Cancel-first is bound by zero
reassignment and final carrier equality with the stopped carrier. Loss-first is bound by exactly one
reassignment, two adaptive selections, and final carrier inequality. All four cells end with one
loss, one recovery, zero signed work, terminal cancellation, no HEAD/activation, both bulk routes
ready, and protected Ratox.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-cancel-race-loss-first

./tools/iotox-sandwurm-lab.sh export-pair \
  .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.5gvh__p1 \
  sync-tree-route-cancel-race-loss-first
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rxb2dsge \
  sync-tree-route-cancel-race-loss-first
python3 tools/verify-sandwurm-pair.py --self-test
```

Both raw roots passed independently before export, and both compact roots passed independently after
export. Strict replay also continues to accept the two ADR 0178 cancel-first compact proofs under
their original scenario. This binds both branches without rewriting earlier evidence.

## Exact nonclaims

These four cells cover both outcome classes under two deliberate delay shapes and two native carrier
classes. They are not a random delay sweep, a probability estimate, or exhaustive thread scheduling.
They do not qualify startup during a route fault, multiple simultaneous affected jobs sharing the
failed carrier, automatic production restart, larger-object throughput, physical common-link
priority, independent relays, multi-source download, byte striping, transparent bonding, or
long-running fleet policy. ADR 0179 freezes this interpretation.
