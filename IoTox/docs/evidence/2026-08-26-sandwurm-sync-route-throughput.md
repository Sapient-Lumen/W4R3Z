# Sandwurm multi-route throughput and application-restart evidence

Date: 2026-08-26

Status: accepted Gate 4 larger-object ABBA row

## Claim

After each bounded clean subscriber Agent replacement, the primary and both auxiliary application
sessions re-confirm and re-authorize even if the underlying Tox transport epoch remains continuous.
Two concurrent 16 MiB tree jobs then select `00` under fixed policy and `01` under adaptive policy.
Across the counterbalanced `fixed-a,adaptive-a,adaptive-b,fixed-b` order, adaptive placement has
higher aggregate artifact throughput in one direct-UDP and one forced-TCP cell. All eight revisions
activate, route work drains four-to-zero, no job is reassigned, and 40 protected Ratox probes remain
below 250 ms after the transfer experiment.

## Accepted compact cells

| Route | Compact proof | Fixed A / B | Adaptive A / B | Fixed / adaptive B/s | Adaptive ratio | Completion skew fixed A/B; adaptive A/B | Ratox p50 / p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.pw3ogf7q` | 87,710 / 92,230 ms | 76,900 / 77,160 ms | 372,952 / 435,603 | 1.167986 (16.80%) | 720/570; 3,160/2,570 ms | 12.256 / 17.740 / 21.810 ms | 909,134,012,196 ns | `e93a1bc3e31a6dd0b8ce4ecee8bc9b56d5ef83ee9a2235728e39923005665663` | `e76b03e07797a45f13c72d6ba911fdd820b2216b37306099e949dd7cc6aecefe` |
| forced TCP | `.sandwurm/exports/pairs/pair.7zsdwj15` | 86,820 / 81,590 ms | 79,490 / 78,550 ms | 398,486 / 424,633 | 1.065616 (6.56%) | 10,250/2,490; 19,020/14,650 ms | 88.640 / 128.307 / 131.101 ms | 1,248,778,906,332 ns | `1b314586e44c0f2e96df8a4ea3fafee3c73034380e3d5c86fe8b0b9da8900a71` | `146d018791d8528523721eb7727c206c9cd0f4b84c94036efca46219ff1f67f7` |

Both cells bind source revision `848ae4e982351b0a3212d3e2bb6370b8ddfda630-dirty` and binary
`e23b5ca2fe020e476c4a49f10f188d3d73638b4fb9d2230e267f7c58a4a5ff2d`. Each phase binds two
16,777,283-byte artifacts, two exact selections, two activations, zero reassignment, peak signed
work four, final work zero, and a 5,000 ms stopped-Agent hold. Fixed patterns are `00,00`; adaptive
patterns are `01,01`.

The direct-UDP client/device receipt hashes are
`08480559a1de9b62402208b5a9b66500d58c097b7031db078fbf48ed60afa8ac` and
`93e476e59f59bed1186db9b6cec4248db3281d662028a126b59ab04a1b9c819c`.
The forced-TCP hashes are
`892905c3c86478cc9d415c567cf41de4d73f8dc64c55900b93aa0bdf7a0bf1b1` and
`0a033f97722403b4f214a7a2847debfe18a2f1cbb4de09038b7f8df2c049a050`.
The protected Ratox resource digests are
`0141f75b191565a5fb10f1532002fed44cad8a6619103a076709fa9d66cb279d` for UDP and
`a5794af9b93be513d9a086b7a936154e512e7191b2f90d87c22d9e0052e620c3` for TCP. Each phase also
retains a separate process-incarnation-fenced resource interval and digest in the compact proof.

## Defect observations and superseded cells

The first direct-UDP experiment `pair.ofjwtams` completed before the stopped-Agent hold was frozen;
it is pre-contract and supports no accepted claim. Forced-TCP `pair.6ygambi7` then remained live
after a fast restart while all six relay sockets stayed established. The runner was manually stopped
and its exact orphan process groups were cleaned. This identified the missing application epoch but
is not an accepted proof.

After adding the 5,000 ms hold and bounded readiness diagnostics, direct-UDP `pair.r1oqk7fn`
completed under the old HELLO rule. Forced-TCP `pair.3cx6zuu2` recovered two phases only after long
delays and failed the third at the exact 180-second readiness bound:

```text
phase=adaptive-b-readiness-timeout
session-confirmed=1
authority-authorized=1
ready-bulk=1
```

The protected primary and authority gate were healthy while exactly one auxiliary application
session remained frozen. This root is rejected. `pair.r1oqk7fn` remains a useful pre-fix observation
but is superseded and is not the accepted same-binary comparison.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-throughput

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.pw3ogf7q \
  sync-tree-route-throughput
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.7zsdwj15 \
  sync-tree-route-throughput
python3 tools/verify-sandwurm-pair.py --self-test
```

Each raw root passed strict verification before export. Each compact root passed independently after
export. The compact allowlist retains only content-free receipts, launch chains, phase and Ratox
status/timestamps, process-resource intervals, and their exact hashes. After that two-stage
verification, the six accepted, rejected, and superseded raw lab roots were pruned with the bounded
workspace cleaner, reclaiming 17.5 GiB. The two accepted compact roots above are the retained proof.

## Interpretation and exact nonclaims

The two logical bulk routes use independent Tox identities and file-manager domains but share the
same remote device, host bridge, and shaped 4 Mbit/s client TAP. The gain therefore says that routing
two jobs away from one busy logical path removes an internal bottleneck on this topology. It does not
show two physical links, doubled link capacity, transparent byte striping, proportional scaling,
independent relays, or cross-client behavior.

These are two cells, not a throughput distribution. The ABBA order reduces one simple ordering bias
but does not cover randomized phase order, repeated days, background workloads, route-quality
estimation, per-route weighting, or fairness guarantees. Forced TCP's adaptive completion skew is
worse than its fixed skew even while aggregate throughput improves. Protected Ratox runs after bulk
convergence, not simultaneously with these transfers, so no live bulk-interference latency claim is
made. Physical QoS, independent bottlenecks, relay diversity, and simultaneous interactive/bulk
qualification remain separate gates.
