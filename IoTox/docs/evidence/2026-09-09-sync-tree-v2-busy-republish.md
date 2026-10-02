# Tree-v2 busy republish throttle and lane-width evidence

- Date: 2026-09-09
- Product version: IoTox 0.51.0 rev0051
- Status: accepted current-tree Sandwurm comparison

## Question

After ADR 0352, current rev0051 could report preservation counts but had not remeasured the
near-ceiling lane-width sweet spot. The specific question was whether wider tree-v2 object lanes
still helped once source-watch wakeups, debounce, no-op skips, digest reuse, grouped path work, and
preservation counters were all present.

## Pre-throttle current-tree baseline

Source revision `f0f0145ddab85e3a28dd92426b0be4b68d43f0f7` was tested in the 2-vCPU/2-GiB
networkless Sandwurm three-writer near-ceiling profile. Both runs used the same source-linked binary
SHA-256: `935d899ae055956bb05655a883b882f593ec26fac0182ab90fa36df853bc8711`.

| Field | cap 4 `.sandwurm/exports/three-writer/run.602ALtud` | cap 8 `.sandwurm/exports/three-writer/run.XC8lKbgg` |
| --- | ---: | ---: |
| `elapsed_ms` | 466,085 | 1,256,792 |
| `capacity_catchup_ms` | 386,718 | 1,084,185 |
| `capacity_file_commit_batches_per_node` | 0 / 875 / 875 | 0 / 438 / 438 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 4 / 4 | 0 / 8 / 8 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 7 / 11 | 0 / 74 / 81 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 9,643 / 13,503 | 0 / 160,198 / 158,813 |
| `capacity_late_offers_cancelled_per_node` | 0 / 2 / 3 | 0 / 9 / 15 |
| `periodic_attempts_per_node` | 49 / 41 / 54 | 118 / 101 / 103 |

The cap-8 run cut batch count roughly in half but became 2.80x slower on capacity catch-up. Because
there were no watchdog restarts, no retained offer IDs, and no eviction pressure, the leading cause
was intermediate publication churn causing too many sequential follower pulls and repeated strict
CAS inventories.

The compact-export SHA-256 values were:

- cap 4: `494296b266b944c3941b8982770f61df3a7f3f7fa640a0c04d82a342e94b45b9`;
- cap 8: `4a27984c3356b36bbd84c758db4cf10bd860746815e812222df3d68d7eb548fa`.

## Implemented change

Commit `5203d7bd43a404682c6770fed282f29640fb0342` implements ADR 0353. Tree-v2 source-watch changes
that arrive while a publish is active keep a pending local-source publish, but that pending publish
is delayed by 5 seconds after the active publish completes. For publish-only and writable policies,
the delayed pending source publish also suppresses an earlier normal periodic local publish. For
bidirectional policies, remote peer pulls can still run while the local source republish cools down.

Local verification before VM work:

```text
nix develop -c bash -lc 'cmake --build build -j2 && ctest --test-dir build -R "^(iotox\.unit-and-integration)$" --output-on-failure'
nix develop -c bash -lc 'ctest --test-dir build -R "^(iotox\.sync-three-writer-sandwurm-verifier|iotox\.sync-tree-process|iotox\.sync-publication-process)$" --output-on-failure'
```

The post-change source-linked binary SHA-256 was
`a7fc1ca6d468410620b29ceb38a420a0c7f74f25d1de0bc49448a23de505be2b`.

## Post-throttle Sandwurm comparison

| Field | cap 4 `.sandwurm/exports/three-writer/run.Ed6ZvJvG` | cap 8 `.sandwurm/exports/three-writer/run.BKxk74nS` | cap 16 `.sandwurm/exports/three-writer/run.EFQ2DS2A` |
| --- | ---: | ---: | ---: |
| `elapsed_ms` | 612,381 | 570,450 | 1,362,544 |
| `capacity_catchup_ms` | 512,569 | 480,819 | 1,271,565 |
| `capacity_file_commit_batches_per_node` | 0 / 875 / 875 | 0 / 438 / 438 | 0 / 219 / 219 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 4 / 4 | 0 / 8 / 8 | 0 / 16 / 16 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 3 / 9 | 0 / 23 / 25 | 0 / 90 / 111 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 4,187 / 17,525 | 0 / 50,651 / 51,509 | 0 / 187,638 / 213,371 |
| `capacity_late_offers_cancelled_per_node` | 0 / 0 / 1 | 0 / 2 / 3 | 0 / 20 / 39 |
| `capacity_repair_ms_per_node` | 1,380 / 1,596 / 935 | 862 / 398 / 562 | 365 / 1,125 / 717 |
| `capacity_agent_high_water_kib` | 46,876 / 46,428 / 51,056 | 45,920 / 50,676 / 51,228 | 48,680 / 51,232 / 49,804 |
| `capacity_allocated_delta_bytes_per_node` | 123,170,816 / 121,356,288 / 121,520,128 | 124,715,008 / 120,344,576 / 120,659,968 | 124,723,200 / 120,516,608 / 121,409,536 |
| `periodic_attempts_per_node` | 44 / 53 / 47 | 36 / 39 / 39 | 45 / 37 / 38 |

Compact-export SHA-256 values:

- cap 4: `cf0b83df388c5bcb4a3077ab8d5f1a752ac7b6d579b6b071974307e61f3eb764`;
- cap 8: `b707f8b689a4bc256dc046ccc587f0adfbfc70c399eb5235c30e6fca56c9c3b1`;
- cap 16: `858837feb3be0dfb7163a5b2301b91d44032578b1760c5d3336ebe3f42591ee2`.

All three post-throttle compact proofs passed `verify-three-writer` and
`verify-sandwurm-vm-smoke.py`.

## Counter-retaining cap-8 repeat

After ADRs 0354--0357 landed, cap 8 was repeated to bind final pull/apply counters into the compact
Sandwurm receipt. Source revision `72cc76d8c4789c9ba877194be8aa9cc9fed372a9` produced binary
SHA-256 `facd385e4213e56bacd64790e245bef9e65944948a81aa7cb6aa3ef320bb9897`.

The run passed as `.sandwurm/exports/three-writer/run.cbiP45oS`. Its compact manifest SHA-256 is
`f93fc2c6d45a8ad2fab7b9f66c1ae8827a965955734b60674eea4f2e73e079af`; the sync receipt SHA-256 is
`1226170f1f5f57cd3abc3e22f229707fe76c19160e017fbe2b9a2ffd5163e9cf`.

| Field | cap 8 `.sandwurm/exports/three-writer/run.cbiP45oS` |
| --- | ---: |
| `capacity_catchup_ms` | 538,809 |
| `capacity_file_commit_batches_per_node` | 0 / 438 / 438 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 8 / 8 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 26 / 24 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 51,022 / 39,660 |
| `capacity_late_offers_cancelled_per_node` | 0 / 0 / 4 |
| follower `reconcile-projection-files` | 3,501 / 3,501 |
| follower `reconcile-projection-bytes` | 57,344,016 / 57,344,016 |
| `reconcile-cas-installed` | 0 / 0 / 0 |
| `reconcile-source-reused` | 0 / 0 / 0 |

This repeat is in-family with the prior post-throttle cap-8 proof, but it should not be treated as a
new speed record. It chiefly showed that final apply work was projection and source-hash dominated,
not CAS dominated. ADR 0358 follows from that evidence by adding a subscriber-owned volatile source
digest cache for repeated no-op pull/apply cycles.

## Post-cache cap-8 rejected repeat

The first Sandwurm cap-8 repeat after ADR 0358 did not pass. Source revision
`b34081e` produced compact rejected proof `.sandwurm/exports/three-writer/run.NhlrhpHW`, with compact
manifest SHA-256 `1b906657348f79d226e34337af71fe616ac7ce86d84751bd4bf42a96d73c7586`.

The three-writer verifier accepted the compact rejected receipt. The generic `vm-smoke` verifier is
not applicable to this compact proof because the run did not export `vm-smoke.json`.

| Field | cap 8 `.sandwurm/exports/three-writer/run.NhlrhpHW` |
| --- | ---: |
| `status` | rejected |
| `elapsed_ms` | 1,825,073 |
| `capacity_catchup_ms` | 0 |
| `partial_capacity_shape_per_node` | 3,500 / 194 / 194 files |
| `partial_tree_v2_store_shape_per_node.objects` | 195 / 195 / 195 |
| `partial_tree_v2_store_shape_per_node.incoming_files` | 0 / 0 / 0 |
| `partial_agent_high_water_kib` | 24,840 / 16,848 / 16,768 |

This is not evidence that the subscriber apply cache improves near-ceiling transfer time; the run
timed out before reaching the final apply phase where `source-reused` would matter. It is retained
as a negative scale sample pointing back at object-transfer/catch-up scheduling rather than local
projection apply. The next useful cap-8 work is to instrument the in-progress object request/offered/
committed frontier at timeout, then attack the remaining transfer churn or bundle/range overhead.
ADR 0359 implements that rejected-receipt frontier summary for future repeats.

## Post-cache cap-8 accepted repeat

After ADR 0359, cap 8 was repeated again at source revision
`11eafa2fa1a062030de82b41d2bd0830784fa9a1`. The run passed as
`.sandwurm/exports/three-writer/run.T6m7lxAN`; the compact export reported manifest SHA-256
`8f183ebb67a4748cc6c7307ba5618bfa4d704dd5c3593b0ce13711ca3df9830b`, and the sync receipt SHA-256
is `42f691ba1c9d28662c06088b199e808d15d20d09aa03783a5e4af7d186f155cc`.

| Field | cap 8 `.sandwurm/exports/three-writer/run.T6m7lxAN` |
| --- | ---: |
| `elapsed_ms` | 1,027,682 |
| `capacity_catchup_ms` | 940,891 |
| `capacity_file_commit_batches_per_node` | 0 / 438 / 438 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 8 / 8 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 92 / 94 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 140,152 / 161,762 |
| `capacity_late_offers_cancelled_per_node` | 0 / 14 / 11 |
| `reconcile-source-hashed` | 0 / 3,501 / 0 |
| `reconcile-source-reused` | 28,008 / 1 / 28,008 |
| `reconcile-projection-files` | 0 / 3,501 / 0 |
| `reconcile-cas-installed` | 0 / 0 / 0 |

This accepted repeat proves the subscriber apply cache is active in VM conditions: two nodes reused
28,008 stable file digests apiece across retained no-op applies. It also proves that the cache is not
the near-ceiling throughput fix. Catch-up was materially slower than the previous accepted cap-8
runs, with follower full-inventory scans back up to 92/94 and late-offer cancellations at 14/11.

## Interpretation

The throttle fixed the cap-8 regression without weakening sync semantics:

- cap 8 capacity catch-up dropped from 1,084.185 seconds to 480.819 seconds, a 55.7% reduction;
- cap 8 full follower scans dropped from 74/81 to 23/25;
- cap 8 total elapsed dropped from 1,256.792 seconds to 570.450 seconds;
- all accepted runs still converged three branches, retained two conflict alternatives per node,
  resolved to common content, ran repair, and ended with zero retained offer IDs and zero evictions.

Cap 8 is viable and has the best accepted sample in this exact VM profile, but the later
538.809-second and 940.891-second accepted repeats show enough variance that cap 4 versus cap 8 is
not closed as an operational default. Cap 16 remains negative: it reduces commit batches again, but
it increases full inventories, inspected objects, late-offer cancellations, and elapsed time. Wider
lane caps should not be the next primary optimization path. The next useful scale work is to reduce
intermediate head/follower-pull churn further, retain in-progress transfer-frontier data on any new
timeout, then implement selected incremental projection and eventually a negotiated tree-v2 object
bundle/range transfer if the measured per-object transfer overhead remains dominant.

This remains synchronization evidence, not backup qualification. It does not close the 24-hour soak,
independent-backup restore, dishonest-storage, remaining power-cut, or production hardware gates.
