# Sandwurm exact route-readiness-order evidence

Date: 2026-08-25

Status: accepted Gate 4 exact corresponding-readiness-order qualification

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two separately
keyed, reciprocally authenticated bulk workers. In phase one, each role allowed its exact lane-1
identity to advance while holding lane 2. In phase two, a savedata-preserving rolling Agent restart
allowed the exact lane-2 identity first and held lane 1. The hold began only after the selected worker
was confirmed and reciprocally bound.

Every phase observed exactly one expected `lifecycle=ready` bulk route for ten consecutive samples
inside a 20,000 ms post-readiness window, then observed both bulk routes ready. Only after both orders
passed did the pair converge and explicitly activate the same signed 4 MiB tree and complete 40
protected Ratox samples below 250 ms.

## Accepted compact cells

| Route | Compact proof | Client phase 1 / 2 | Device phase 1 / 2 | Minimum stable samples | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.nyiqwm8t` | 2,161 / 1,916 ms | 2,108 / 1,658 ms | 10 | 29.742 / 31.876 ms | 467,147,300,693 ns | `160640d34072c2b3a274006b08754cbfb4d20272c4d819faefe56459401f5c8e` | `e68b50ce027c9ebc0e448b5a3a5610179c4815c1a370bb8b385e5bfa8fbfec89` |
| forced TCP | `.sandwurm/exports/pairs/pair.mdacri5e` | 9,676 / 1,832 ms | 8,732 / 2,193 ms | 10 | 110.380 / 129.896 ms | 329,334,999,866 ns | `3590a59f8801a0048c3f5edca0c971612a72c57f5e31129a48414800ff924798` | `6cb35185279340239b6a5836faa33010680899b94314e07fac2cea759a0481c0` |

Each compact export allocates 241,664 bytes and excludes guest disks, private identities, bootstrap
secrets, mutable runtime state, FileIds, paths, and content. Both bind source revision
`1a1e7e03aa0dbf031792600c233314776eb9a835-dirty`, rev0039, pinned c-toxcore 0.2.23 with
`iotox-file-rr1`, and binary
`6bc197c81ee26a70a206d749d7d67c6c442abfab3f6330a2467d81cad97016a7`.

The direct-UDP client/device receipt hashes are
`7473e084f0ed422dc6ee76ab1508dead560fec0aa114291bfa03378236e6f831` and
`d4ec3d65362164009e1a4c8714f2a00dc6cfce7a7474b61287ab763df0e9a28a`.
The forced-TCP hashes are
`e44b41dd851069f028eb5b13d23bf2fbac5f2ef6915d68adefc4a4069f9e8327` and
`55d49549b9e255b09536b48644b6889ed2d63512e91a4e525c1ea8aa74ccc97e`.

Both cells bind the same artifact
`a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`, manifest
`f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`, and signed HEAD
`ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`.

## Scientific corrections retained

The first three development attempts restarted both protected primary Agents simultaneously and then
timed out waiting for bilateral v3 synchronization authority. Read-only disk inspection showed the
same savedata identities had restarted, but the primary sessions remained offline. The accepted cell
therefore uses explicit host-controlled client-then-device barriers for both primary restart phases.
Those failures are not evidence about auxiliary route order.

The first forced-TCP route-order attempt to clear protected control exposed a second flaw: a
20,000 ms deadline measured from worker construction could expire while primary authority recovered.
Both routes could therefore become eligible before sampling. The production qualification seam now
arms the delay only when the selected worker is application-ready and reciprocally authenticated.
One later corrected forced-TCP attempt failed the initial protected-control barrier; a clean cached
retry passed. This remains a local single-relay startup-variance observation, not a product SLA.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-startup-order

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.nyiqwm8t \
  sync-tree-route-startup-order
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.mdacri5e \
  sync-tree-route-startup-order
```

The guest derives each expected key from its signed local route inventory and refuses any sole-ready
key mismatch before writing a receipt. The verifier requires two valid, distinct exact keys, ten
stable observations, positive times below the hold, and matching two-role aggregates, then binds tree
convergence, two final ready routes, protected Ratox, receipt hashes, native carrier class, and every
compact-file digest. Its self-test rejects mutated scenario fields and nonzero startup-order fields in
other cells.

## Exact nonclaims

This qualifies the two corresponding exact orders `lane 1 → lane 2` and `lane 2 → lane 1` on each
role. It does not qualify random delay distributions, more-than-two-worker partial orders, startup
during link loss, simultaneous protected-primary replacement, public relay startup reliability,
larger-object throughput, physical common-link priority, independent relays, multi-source download,
byte striping, transparent bonding, or long-running fleet policy. ADR 0176 freezes this interpretation.
