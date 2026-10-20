# Current-tree Sandwurm repeated Ratox reconnect recheck

Date: 2026-09-09

Status: accepted current-tree recheck on direct UDP and forced TCP

## Claim

The current IoTox tree still passes the bounded production-CLI repeated reconnect gate. One real
`iotox terminal PEER --reconnect` process crossed two sequential seeded total-loss intervals and
resumed the same retained device PTY afterward.

This is a regression/qualification recheck for the current binary, not a new latency target and not
a replacement for the detailed 2026-09-03 repeated-loss measurement table.

## Evidence

| Route | Compact proof | Expected/observed carrier | Status | Samples | Interruptions | Binary SHA-256 |
|---|---|---|---|---:|---:|---|
| direct UDP | `.sandwurm/exports/pairs/pair.h25zpony` | UDP / UDP | passed | 3 | 2 | `b447f6fd0445f16b3bb9acca76bc413faf12b9b779ba7d20f5c8d95a128ed6b7` |
| forced TCP | `.sandwurm/exports/pairs/pair.sduwsbg8` | TCP / TCP | passed | 3 | 2 | `b447f6fd0445f16b3bb9acca76bc413faf12b9b779ba7d20f5c8d95a128ed6b7` |

Both route-loss receipts report `controller_kind=production-cli-reconnect` and
`detached_host_snapshot=true`.

| Route | Manifest SHA-256 | Compact-export SHA-256 | Route-loss SHA-256 |
|---|---|---|---|
| direct UDP | `4d330c619fa4e385066bf25c206ce77a5b14e2f6c43710bed3e10da5fdc43d75` | `f1c903b1494be3b5c3b63951fb6b02daee0f2977b0c6a4ce8b5413dccbe7897d` | `cafeaa5a60a2dc533847e967812c0d8e4e3858eb9d5f8fa19259e9984f65b7a8` |
| forced TCP | `2520c34be228dfe1d97fc022e1224a97b60a113c8e158d6cf94cbc4a1e878f04` | `4673ccf1841586f9e06dafc868ab899a18839605ea1eb75ee83a11aeb4536458` | `866da35993c22a2a6b763f0f855001a378659db306244e692656f34f54055516` |

## Commands

```sh
./tools/iotox-sandwurm-lab.sh preflight
./tools/iotox-sandwurm-lab.sh up-pair direct-udp ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/pair.h25zpony
./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/pair.sduwsbg8
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.h25zpony ratox-cli-reconnect-repeated
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.sduwsbg8 ratox-cli-reconnect-repeated
```

## Notes and nonclaims

The direct-UDP pair was launched after the Sandwurm wrapper fix was present in the working tree; the
fix was then committed as `b8e9ceb` before the forced-TCP pair was launched. Both pair manifests bind
the same product binary hash.

This proves the current bounded reconnect mechanism still works in two same-host Sandwurm/KVM
guests over native UDP and relay-only TCP. It does not prove hours-long retention, actual Tor or I2P
continuity, daemon-death PTY survival, physical-machine independence, every PAM/sudo policy, every
cgroup controller deployment, or production activation.
