# Sandwurm late bounded-range carrier-loss evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two simultaneous source-linked IoTox guests preserved and resumed one exact private prefix after an
authenticated native auxiliary carrier died beyond 15/16 of a live 1 MiB bounded range. Both route
modes received only the small suffix under fresh attempt/FileId identities and converged on the exact
signed generation without discard or fallback.

## Accepted cells

The gate binds `--qualify-route-stop-after-bytes 983040`,
`--qualify-route-stop-file-bytes 1048576`, and 256-kbit/s selected-range shaping in its manifest.
The 4 MiB basis remains on the ordinary 4-Mbit/s prerequisite path.

| Route | Compact proof | Fault/retained/resumed | Remaining | Pair span |
|---|---|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.tev4u3rs` | 984,378 | 64,198 | 438,453,698,922 ns |
| forced TCP | `.sandwurm/exports/pairs/pair.1z7_d0jn` | 995,346 | 53,230 | 498,230,171,154 ns |

Both use source revision `5d6358aa23f96cf146aaa18411bfe9b685683df2`, product revision
`rev0045`, and binary SHA-256
`88093a006d9a9e0bedb7af6be5ed3efb47399279a289c7b7c44eb86748257bca`.
Each reports one loss/reassignment/stale terminal/recovery/retained attempt/resumed attempt, zero
discard/fallback/final retained partials, one 1 MiB range fetched, and 3 MiB verified basis reused.

The common final artifact, manifest, and signed HEAD identities are the same as the earlier range
cells. Direct client/device receipt digests are
`501dec0c3ad3ce0a8cb5dd749d90cf9dfffabeec7bc4ebda546d9be52893e7cd` and
`310085f4a73fb2525469022418c5389361c2cc692c41c90a5e8b22e254b303b5`;
forced-TCP digests are
`1b802499defc8d477dff8d0cbf3ac3b97095079cfef87234e7fd939d9c2930c3` and
`dcb985bad9d380a835ea0445df89330d4e5f1d561bdbbbeb3e0b6fac8fd1b03b`.

Direct pair-manifest/compact-export SHA-256 values are
`45b5fa55a93d99544e7bc8be9ddc070a549122b6a869a4257e2c798e7f27dfa3` and
`e1926fff9dc6322664e9cdf545dbfa18289e7b00e24fc32187f2d2ab782b167c`.
Forced-TCP values are
`0f94254dc7a9f21f6cdfc302645b5ce95688a0e609ca727e71d230f64e3cdb8a` and
`e71587254cf7373040f81f329bc16841087dd29be174848f7b3040b5c8945888`.

## Rejected calibration

Initial direct root `pair.6ki1hscj` used the same 983,040-byte threshold at 4 Mbit/s. The range
completed with zero qualification faults before the service loop could observe the final 64 KiB
window, and the runner rejected it after the exact successor budget. No loss/resume claim is drawn
from that root. Shaping only the selected range made the event observable; it did not change IoTox
framing, route policy, or prefix semantics.

## Reproduction

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-late-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-late-route-loss

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.tev4u3rs sync-file-range-late-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.1z7_d0jn sync-file-range-late-route-loss
```

## Exact nonclaims

This does not prove final-chunk/post-completion races, repeated late faults, three-plus losses,
random thresholds, process/guest restart, explicit-new-job prefix reuse, I2P/Tor continuation,
cross-class migration, concurrent multi-source striping, two physical hosts, or performance gains.
