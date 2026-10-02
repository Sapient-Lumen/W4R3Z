# Sandwurm route-loss-before-cancellation evidence

Date: 2026-08-25

Status: accepted Gate 4 bounded loss→reassignment→cancellation qualification

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two
separately keyed, reciprocally authenticated bulk workers. The subscriber admitted one two-object,
4,194,601-byte tree pull under the adaptive selector. After the active auxiliary artifact crossed
65,536 bytes, the Agent stopped that exact worker incarnation, fenced its transfers, rejected its
late terminal truth, and reassigned the missing immutable objects to the other ready route.

The test waited for positive artifact progress on that replacement incarnation before issuing the
ordinary `sync-cancel` command. Cancellation retained the replacement carrier/worker identity,
released its signed work two-to-zero within 5,000 ms, and left no incoming transfer, staging file,
accepted HEAD, or activation. The originally stopped savedata identity then spent exactly one
restart-budget unit, returned under a fresh worker incarnation, reauthenticated, and restored two
ready bulk routes. The protected primary subsequently completed 40 Ratox samples below 250 ms.

## Accepted compact cells

| Route | Compact proof | Fault position | Replacement staging before cancel | Stale terminals | Cancel tail | Work | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair._0jwjfe6` | 116,535 bytes | 9,597 bytes | 2 | 80 ms | 2 → 0 | 20.406 / 22.621 ms | 481,561,600,312 ns | `db85bd041e59f715a0bc230a7b374cf9b40ccf76c3ad44039d65791fe2a72528` | `f66137e440cec862d0be3942f5bc9283f83fde9c452336f8991ab3e51927914c` |
| forced TCP | `.sandwurm/exports/pairs/pair.o0ozmdw1` | 174,117 bytes | 52,098 bytes | 2 | 80 ms | 2 → 0 | 129.511 / 131.769 ms | 478,807,598,820 ns | `ae709267ef232e8d29c5927ec008672cd188bc29c4a20cb1227643521b2c79e4` | `9819ea02539a74020e298eab97043377d5677a38f2f0af2105e1570368eb917d` |

Each compact export allocates 241,664 bytes and excludes guest disks, identities, bootstrap secrets,
mutable runtime state, FileIds, paths, and content. Both bind source revision
`c0476531292fa502340bed04ee7a5669038c54c8-dirty`, rev0039, c-toxcore 0.2.23 with
`iotox-file-rr1`, and binary
`7acb80b0058addd7868a370cab361e4e46b8581ac583c0b21b13d237c476f5d9`.

The direct-UDP client/device receipt hashes are
`66ff8554d6da8d80bc361452a81e10f67e4ebba46ad4d0e96e60f2c6ded83378` and
`a640d30e47fa31c1e6bdc89ad1ebb8467c58dd0baf9c06a5e08e3dc6b49c791c`.
The forced-TCP hashes are
`c836d46793e13883936400f879baf1af35af13e99d7b415dbe70983afc047c07` and
`af1b5ef5fbc3f0347f34b834a8b1661e24991115d6005de1e38fb970e84b74a0`.

## Recovery rule exercised

The qualification restart seam previously waited only for an auxiliary pull to become `complete`.
That made cancellation after reassignment terminal but prevented the deliberately stopped worker
from entering its bounded recovery path. The seam now treats `complete` and `cancelled` as terminal
recovery prerequisites. It still requires the injected fault, exactly one reassignment, at least one
stale old-worker terminal, a stopped bulk worker, an available signed restart-budget unit, and a
fresh worker incarnation. Failed or nonterminal pulls do not authorize recovery.

This change does not add automatic production worker restart. It makes the existing explicit
qualification seam able to finish the cancellation branch without weakening coordinator accounting.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-loss-cancel
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-loss-cancel

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair._0jwjfe6 \
  sync-tree-route-loss-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.o0ozmdw1 \
  sync-tree-route-loss-cancel
```

The verifier binds the exact cancellation outcome, ≥65,536-byte fault threshold, one loss, one
reassignment, at least one stale terminal, one recovery, two adaptive decisions, unchanged
replacement carrier across cancellation, distinct stopped carrier, zero post-cancel work, two ready
routes on both roles, native carrier class, protected Ratox evidence, receipt hashes, and every
compact-file digest. Its self-test mutates the final carrier back to the stopped carrier and requires
rejection.

## Exact nonclaims

This is one deterministic order per carrier: progress on route A, loss, reassignment and progress on
route B, cancellation, then recovery of A. It does not qualify simultaneous loss/cancel races,
cancellation before reassignment, cancellation during recovery failure, randomized startup or fault
timing, repeated restart-budget exhaustion, larger-object fair sharing, physical queue isolation,
independent relays, multi-source download, byte striping, or long-running fleet policy. ADR 0175
freezes this interpretation.
