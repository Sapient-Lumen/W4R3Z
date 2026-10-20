# Sandwurm multi-route sync population evidence

Date: 2026-08-25

Status: accepted Gate 4 bounded population and resource qualification

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two
separately keyed, reciprocally authenticated bulk workers. The subscriber started eight independent
two-object tree pulls under each scheduling policy. Fixed filled the first route's eight work units
before spilling to the second (`00001111`); adaptive alternated jobs across equally loaded routes
(`01010101`). Every one of the 16 jobs per carrier made observed-or-committed progress, committed its
artifact and manifest, accepted its signed HEAD last, and activated only by exact local token.

Both routes returned to zero work, all private staging was empty, and each policy produced a bounded
process-resource interval. The same guests then completed 40 protected-primary Ratox samples with no
render at or above 250 ms.

## Accepted compact cells

| Route | Compact proof | Fixed / adaptive duration | Fixed / adaptive progress-observation spread | Patterns | Activations | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.slx3x0kb` | 5,675 / 4,998 ms | 1,342 / 1,371 ms | `00001111` / `01010101` | 16 | 31.953 / 46.039 ms | 412,951,134,678 ns | `05d9c5e4b289ac5edfc6253b8d585cc75a5fecf5007bc2e1b3483d0428fb1500` | `f5d2950f0582768f6e8bc1007d846a99c82f28796f3934b57606786c071c9640` |
| forced TCP | `.sandwurm/exports/pairs/pair.rrizbuky` | 5,267 / 4,841 ms | 1,744 / 2,139 ms | `00001111` / `01010101` | 16 | 95.700 / 130.776 ms | 535,192,650,844 ns | `47719bc312cca4ebbe1eb3baf475ace0deee4914e4d8fce4c485f7917b90989a` | `6d8f7bd5e052d9240526c85fbe8c680784c6df08a8a414b1726b299a1d7be256` |

Each compact export allocates 249,856 bytes and excludes guest disks, identities, bootstrap secrets,
mutable runtime state, FileIds, paths, and content. Both bind source revision
`9e7a5313390dbd4591f3bac6ff24301be752039d-dirty`, rev0039, c-toxcore 0.2.23 with
`iotox-file-rr1`, and binary
`1eb2c2cb71300252147de3da3d1a62d6d07231636f3bc2556ffa09292ae2920b`.

The direct-UDP client/device receipt hashes are
`bb338306af56451865c64f1c0c1eaaea4308e53b75a4157a9c13dfe4222e17aa` and
`2ac92acc0b5893d9b482fef2c02937e475ecf7f51abd41ae0054aa4653b3b04e`.
The forced-TCP hashes are
`16cfe6b5d986008476432ebce2c0eef021d309c4a2ebd1dc2df7c5dd88f0644a` and
`3027a019244dfc2c3592d92466f3b2ab943d913548058e9826b01149b80453a7`.

## Resource observations

| Route / policy | CPU ticks (user + system) | `VmHWM` start → end | Descriptor start → end | Context switches (voluntary + involuntary) | Major faults | Bytes written | Transport iterations |
|---|---:|---:|---:|---:|---:|---:|---:|
| UDP adaptive | 27 + 37 | 15,044 → 15,300 KiB | 36 → 36 | 251 + 0 | 0 | 8,974,336 | 264 |
| UDP fixed | 34 + 42 | 14,028 → 15,308 KiB | 36 → 36 | 284 + 1 | 0 | 9,138,176 | 289 |
| TCP adaptive | 29 + 30 | 14,976 → 15,232 KiB | 36 → 36 | 244 + 1 | 0 | 8,810,496 | 257 |
| TCP fixed | 29 + 34 | 13,952 → 15,232 KiB | 36 → 36 | 265 + 0 | 0 | 8,978,432 | 272 |

The exact TSVs are digest-bound compact-proof members. `VmHWM` is a process-lifetime high-water
mark, so its interval delta is not a working-set measurement and cannot be compared between ordered
phases as if each began from a fresh kernel history. Context switches and transport iterations are
bounded wakeup proxies, not scheduler-only attribution.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-route-population
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-route-population

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.slx3x0kb sync-tree-route-population
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rrizbuky sync-tree-route-population
```

The verifier binds two ready bulk routes on both roles, eight jobs per policy, exact 131,139-byte
artifacts, normalized carrier patterns and prefix bounds, eight progress observations and eight
activations per policy, object accounting, route drain, resource-file hashes, both native carrier
classes, all Ratox rows, exact receipt hashes, and every compact-file digest.

## Exact nonclaims

This is one adaptive-first run per carrier. The modest adaptive duration advantage is not a policy
performance claim, and the progress-observation timestamp is not exact first-byte latency. The cell
does not prove larger-object throughput, proportional route bandwidth, randomized startup or fault
order, concurrent cancellation fairness, cancellation during route loss, independent relay
diversity, multi-source download, byte striping, live migration, physical path diversity, or
long-running fleet policy. ADR 0173 freezes this interpretation.
