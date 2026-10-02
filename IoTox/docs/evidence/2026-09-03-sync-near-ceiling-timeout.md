# Sync near-ceiling direct diagnostics

- Date: 2026-09-03
- Host: IoTox founding x86_64 machine
- Source revision: `7ac443b86f62702816c59e9124ca05eb9f40a744`
- Version: IoTox 0.46.0 rev0046
- Status: mixed direct diagnostics; not Sandwurm qualification evidence

## Attempted gate

The diagnostic attempted to push the existing three-writer harness from the accepted 512-file
persistent cell toward the source quota ceiling:

```sh
nix develop --command python3 tools/run-sync-three-writer.py \
  --iotox /nix/store/9hm0y747zivc5wp100148d67lqmsfidc-iotox-source-linked-0.46.0-rev0046/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --state-root /tmp/iotox-near-ceiling.p0UjRH/state \
  --evidence .sandwurm/three-writer-near-ceiling/run.20260903T-near-ceiling.json \
  --fresh-state \
  --capacity-files 3500 \
  --capacity-file-bytes 16384 \
  --timeout 1800
```

The source-linked IoTox binary SHA-256 was
`492df73d8cb50e474ad5f70b6486b3ea4ff674dcb0b5892d55071e3fa5e1c5b5`.
The private bootstrap binary SHA-256 was
`f4086096804253839c932ee68c05af5b75a127d1a3dfa9884d66d51ba900505d`.

The synthetic population was 3,500 files of 16,384 bytes, or 57,344,000 logical bytes. The run used
fresh generated identities and state. It was a direct host diagnostic, not a Sandwurm/KVM proof.

The harness failed exactly here:

```text
three-writer qualification failed: timeout waiting for capacity population on all three writers
```

No accepted receipt was emitted.

## Retained samples

The setup and graph phases completed before the timeout:

- local control sockets ready at 0.2 seconds;
- distinct identities and authority ledgers ready at 1.3 seconds;
- three friendship edges confirmed at 16.2 seconds;
- all six read-write shares committed by 16.7 seconds; and
- three signed branches converged at 23.7 seconds.

The capacity phase then made partial object-store progress but did not project the capacity tree onto
either follower before the 1,800-second wait expired.

| Approximate elapsed | Node 1 objects | Node 2 objects | Node 3 objects | Node 1 capacity files | Node 2 capacity files | Node 3 capacity files |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5.5 min | 3,501 | 789 | 785 | 3,500 | 0 | 0 |
| 11.6 min | 3,501 | 894 | 887 | 3,500 | 0 | 0 |
| 14.6 min | 3,501 | 1,041 | 1,033 | 3,500 | 0 | 0 |
| 17.5 min | 3,501 | 1,230 | 1,225 | 3,500 | 0 | 0 |
| 24.8 min | 3,501 | 1,655 | 1,662 | 3,500 | 0 | 0 |
| 28.7 min | 3,501 | 1,979 | 1,988 | 3,500 | 0 | 0 |
| final sample | 3,501 | 2,124 | 2,139 | 3,500 | 0 | 0 |

All three nodes held three branch files at the final sample. The discarded state root occupied about
196 MiB. The generated temp roots were moved to the user's Trash as
`$XDG_DATA_HOME/Trash/files/iotox-near-ceiling.p0UjRH-20260903` and
`$XDG_DATA_HOME/Trash/files/iotox-near-ceiling.PcN7Lp-20260903`.

## Interpretation

This diagnostic narrows the near-ceiling bottleneck. Authority, friendship, sharing, and branch
frontier propagation completed quickly. Follower object stores advanced slowly, and follower
worktrees did not project because full object custody had not arrived. The next scale work should
therefore start with bounded parallel object transfer, incremental branch/build work, incremental
projection, and less intrusive progress polling before repeating a Sandwurm near-ceiling gate.

The run also exposed observer interference in the direct harness. The capacity predicate checked node
1 first and rehashed the complete 57,344,000-byte source tree every 100 ms even though the follower
trees were still empty or partial. `tools/run-sync-three-writer.py` now checks per-node shape
(regular-file count and total byte count) before hashing full contents. A fresh 16-file/16-KiB smoke
after that change passed in 45.937 seconds, with capacity convergence and repair complete by 26.6
seconds.

## Corrected observer retry

After the harness predicate fix, the same 3,500-file population was repeated with the same
source-linked product binary and a fresh state root:

```sh
nix develop --command python3 tools/run-sync-three-writer.py \
  --iotox /nix/store/9hm0y747zivc5wp100148d67lqmsfidc-iotox-source-linked-0.46.0-rev0046/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --state-root /tmp/iotox-near-ceiling-retry.0pTnWP/state \
  --evidence .sandwurm/three-writer-near-ceiling/run.20260903T-near-ceiling-retry.json \
  --fresh-state \
  --capacity-files 3500 \
  --capacity-file-bytes 16384 \
  --timeout 1800
```

The retry reached local control sockets at 0.2 seconds, distinct identities and authority ledgers at
1.1 seconds, three friendship edges at 15.3 seconds, all six read-write shares at 15.7 seconds, and
three signed branches at 18.9 seconds. The Python observer process stayed around 24--31% CPU instead
of the earlier roughly 76% sample, but the one-lane object path still timed out:

```text
three-writer qualification failed: timeout waiting for capacity population on all three writers
```

The final captured state had three branch files on every node, node 1 at 3,501 objects and 3,500
capacity files, node 2 at 2,559 objects and zero capacity files, and node 3 at 2,569 objects and zero
capacity files. No accepted receipt was emitted. The 208 MiB temp root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-near-ceiling-retry.0pTnWP-20260903`.

This confirms the first timeout was not primarily a harness observer artifact. It remains rejected
direct-host evidence, and it motivated ADR 0329's bounded tree-v2 exact-object lane pipeline.

## Four-lane tree-v2 retry

ADR 0329 then replaced the one-active-lane tree-v2 subscriber with a bounded exact-object lane
window and added a separate Agent process cap:

```sh
nix build .#iotoxSourceLinked -L

nix develop --command python3 tools/run-sync-three-writer.py \
  --iotox /nix/store/zc4avwk0gs94hfnafsrbrm37qwrx21an-iotox-source-linked-0.46.0-rev0046/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --state-root /tmp/iotox-near-ceiling-lanes.ZumHux/state \
  --evidence .sandwurm/three-writer-near-ceiling/run.20260903T-tree-lanes.json \
  --fresh-state \
  --capacity-files 3500 \
  --capacity-file-bytes 16384 \
  --timeout 1800
```

The resulting source-linked IoTox binary SHA-256 was
`5cdc1e1ced100c72355b50fbbfd41fe8ca004853fd2534b55fcee367222822ea`. The bootstrap binary SHA-256
remained `f4086096804253839c932ee68c05af5b75a127d1a3dfa9884d66d51ba900505d`.

Live `sync-status` on a follower confirmed the new scheduling boundary during the run:

```text
tree-lane-cap=4
tree-job=... state=awaiting-object ... active-lanes=4 requested=2718 committed=2714 ...
tree-lane-job=... kind=3 bytes=16384 ... admitted=1
```

The direct run passed and emitted
`.sandwurm/three-writer-near-ceiling/run.20260903T-tree-lanes.json`, SHA-256
`d96b571ca31b12448a026db8a52316f8daf1d19da5143b8bf69727330f2fa1e2`.

Retained receipt fields:

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 1,050,374 |
| `capacity_catchup_ms` | 960,696 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `capacity_repair_ms_per_node` | 552 / 1,822 / 686 |
| `capacity_agent_high_water_kib` | 36,524 / 33,236 / 37,312 |
| `capacity_allocated_delta_bytes_per_node` | 123,564,032 / 120,295,424 / 120,274,944 |
| `periodic_attempts_per_node` | 45 / 35 / 36 |
| `stalled_cycle_restarts` | 0 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |

The run also completed the offline three-way conflict and explicit resolution phases. The temp state
root occupied 344 MiB and was moved to
`$XDG_DATA_HOME/Trash/files/iotox-near-ceiling-lanes.ZumHux-20260903`.

This result demonstrates that bounded same-source tree-v2 object pipelining buys the near-ceiling
gate something material: the corrected one-lane baseline failed with followers around 2,560 objects
after 1,800 seconds, while the four-lane build reached full object custody, projection, repair, and
the retained conflict lifecycle in 1,050.374 seconds. The next question is not whether the lane
window helps; it is whether the same behavior survives the Sandwurm VM gate and whether projection
or route scheduling becomes the next scale limit.

## Sandwurm near-ceiling comparison

After the three-writer Sandwurm guest was parameterized, the near-ceiling profiles repeated the same
3,500-file/57,344,000-byte population in a networkless 2-vCPU/2-GiB Cloud Hypervisor guest. These
profiles intentionally omit the 24-cycle shadow, recovery, and storage-fault follow-ups; those remain
covered by the 512-file gate. This gate isolates scale behavior for capacity catch-up plus the
ordinary three-way conflict/resolution path.

The cap-1 baseline used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-1` and proof
root `.sandwurm/lab/three-writer-near-ceiling-cap-1/run.2JGNcbs5`. Console evidence reached local
control sockets at 0.3 seconds, distinct identities and authority ledgers at 1.5 seconds, three
friendship edges at 16.4 seconds, all six read/write shares at 17.4 seconds, and three signed
branches at 20.5 seconds. It then failed at guest timestamp 1,824.009214 with:

```text
three-writer qualification failed: timeout waiting for capacity population on all three writers
```

Sandwurm returned `launched-without-guest-evidence`; no accepted IoTox receipt or vm-smoke receipt
was emitted. The rejected live-chain SHA-256 was
`ac8b38a5f3314c3f557b9acefd2d7dbca3d19e85beba2a3b30071ce74a14aeb0`; the preserved console-log
SHA-256 was `e397b5d9b6ac3724f47e56dc96f41ec3933af16ecd6b67712a63ddc074b73f1f`. The raw proof root
was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-1-run.2JGNcbs5-20260903`.
Later harness work adds direct `status=rejected` receipts for failures, but this specific VM
baseline remains console/live-chain evidence because the guest service exited before that receipt
mode existed.

The cap-4 default profile used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-4` on
clean source revision `4dceed1aef80e7690d71868d763d872b07959539`. It passed and emitted a compact
proof at `.sandwurm/exports/three-writer/run.f3q2rjxM` (104 KiB, 90,093 evidence bytes). Both
verifiers accept it independently. The compact-export SHA-256 is
`b7d5143b6060427766afd09e2601985e007f12f575d4e985604e9bd4ed876834`; the sync receipt SHA-256 is
`d393b1667fe8db5c3cc646c7d1e140ddc88d25e6c7bf1858b3c2d0d5c2bc3fce`.

Retained cap-4 receipt fields:

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 1,361,936 |
| `tree_lane_cap` | 4 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `capacity_catchup_ms` | 1,277,048 |
| `capacity_repair_ms_per_node` | 820 / 300 / 323 |
| `capacity_agent_high_water_kib` | 33,892 / 33,920 / 27,144 |
| `capacity_allocated_delta_bytes_per_node` | 123,195,392 / 121,282,560 / 121,397,248 |
| `periodic_attempts_per_node` | 44 / 41 / 36 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |
| `shadow_cycles` | 0 |
| `stalled_cycle_restarts` | 0 |

The cap-4 raw proof root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-4-run.f3q2rjxM-20260903`
after compact export.

The cap-8 science profile used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-8`
after the helper grew a fresh-state-only namespace quota override. This keeps the product
`sync-create` default unchanged while letting the VM gate raise both the Agent process cap and the
signed namespace `maximum-lanes` quota. The accepted proof used source revision
`ddda30733d42e7e7ff12411f59ffb4212a421102` and binary SHA-256
`5cdc1e1ced100c72355b50fbbfd41fe8ca004853fd2534b55fcee367222822ea`. It emitted a compact proof at
`.sandwurm/exports/three-writer/run.fEPzg6G1` (104 KiB, 90,155 evidence bytes). Both verifiers accept
it independently. The compact-export manifest SHA-256 is
`8939f8b84fb2f80622c3a8873172f7d752af1110fc6e7dbd7f55b846453fc64a`; the sync receipt SHA-256 is
`a6ce0206d22ab824e7251d5defa56cc31758159db3b70e4f86ad5d7c9639c15f`.

Retained cap-8 receipt fields:

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 1,198,824 |
| `tree_lane_cap` | 8 |
| `tree_lane_process_cap` | 8 |
| `tree_lane_namespace_cap` | 8 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `capacity_catchup_ms` | 1,106,351 |
| `capacity_repair_ms_per_node` | 612 / 339 / 420 |
| `capacity_agent_high_water_kib` | 32,836 / 36,152 / 27,144 |
| `capacity_allocated_delta_bytes_per_node` | 123,109,376 / 121,155,584 / 121,147,392 |
| `periodic_attempts_per_node` | 36 / 48 / 38 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |
| `shadow_cycles` | 0 |
| `stalled_cycle_restarts` | 0 |

The cap-8 raw proof root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-8-run.fEPzg6G1-20260903`
after compact export.

The cap-16 science profile used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-16`
with the same fresh-state-only namespace quota override. The accepted proof used source revision
`50670899ba4dc244c30fb8666b65a13e27a8d309` and the same binary SHA-256
`5cdc1e1ced100c72355b50fbbfd41fe8ca004853fd2534b55fcee367222822ea`. It emitted a compact proof at
`.sandwurm/exports/three-writer/run.LFDsNpxz` (104 KiB, 90,302 evidence bytes). Both verifiers accept
it independently. The compact-export SHA-256 is
`7fb4ca8a43d3ad60a9434eaca60d186e6f3bbde586bfe77aafb9be523c966a9d`; the sync receipt SHA-256 is
`e65843b19cddd4bc7877621f5a2b7f61f93694f271ea8f6a6a6b46f7da89ac95`.

Retained cap-16 receipt fields:

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 1,138,904 |
| `tree_lane_cap` | 16 |
| `tree_lane_process_cap` | 16 |
| `tree_lane_namespace_cap` | 16 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `capacity_catchup_ms` | 1,059,715 |
| `capacity_repair_ms_per_node` | 1,328 / 331 / 304 |
| `capacity_agent_high_water_kib` | 32,660 / 36,660 / 34,524 |
| `capacity_allocated_delta_bytes_per_node` | 122,937,344 / 121,303,040 / 121,094,144 |
| `periodic_attempts_per_node` | 42 / 33 / 37 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |
| `shadow_cycles` | 0 |
| `stalled_cycle_restarts` | 0 |

The cap-16 raw proof root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-16-run.LFDsNpxz-20260903`
after compact export.

The cap-32 science profile used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-32`
on source revision `097fd7698411cb607bb58929e2f984a634062d9b`. It reached the same graph setup,
but timed out after 1,823.048 seconds waiting for capacity population on all three writers. The
guest wrote a content-free `status=rejected` IoTox receipt, but because the normal vm-smoke receipt
was not emitted before the manual VMM shutdown, Sandwurm's live-chain status is
`launched-without-guest-evidence`. The three-writer verifier now accepts this narrower rejected-proof
shape without treating it as an accepted VM qualification. The compact rejected proof is retained at
`.sandwurm/exports/three-writer/run.RTfmt0r2` (72 KiB, 63,424 evidence bytes). The compact-export
SHA-256 is `b68d7d407ea19c4e4746e1390f55ef726a3b7d767b1bec6f5f1d1b9e1132ce43`; the sync receipt
SHA-256 is `eab5aa63941d94cec3064b3516d38cb66c6c77494da86019801f89acf4724999`.

Retained cap-32 rejected receipt fields:

| Field | Value |
| --- | ---: |
| `status` | `rejected` |
| `elapsed_ms` | 1,823,048 |
| `tree_lane_cap` | 32 |
| `tree_lane_process_cap` | 32 |
| `tree_lane_namespace_cap` | 32 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `failure_sha256` | `40af54f64141b99f36e57017fd3e9299264390cd2e28616c8a12979b138e3cf4` |
| `partial_agent_high_water_kib` | 30,968 / 31,680 / 31,452 |
| `partial_capacity_shape_per_node.files` | 3,500 / 0 / 0 |
| `partial_tree_v2_store_shape_per_node.objects` | 3,501 / 132 / 158 |
| `partial_tree_v2_store_shape_per_node.object_bytes` | 57,344,016 / 2,146,320 / 2,572,304 |
| `partial_branch_count_per_node` | 3 / 3 / 3 |
| `partial_conflict_alternatives_per_node` | 0 / 0 / 0 |
| `shadow_cycles` | 0 |

The cap-32 raw proof root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-32-run.RTfmt0r2-20260903`
after compact export.

The cap-64 science profile used `./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-64`
on source revision `cb6415eb0668b39bc7d78872b252818fb5cc4e1a`. It reached graph setup, timed out
after 1,822.462 seconds, emitted a content-free `status=rejected` IoTox receipt, and followed the
same vm-smoke-missing host wrapper shape as cap 32 after manual VMM shutdown. The compact rejected
proof is retained at `.sandwurm/exports/three-writer/run.kM0Wu7VQ` (72 KiB, 63,410 evidence bytes).
The compact-export SHA-256 is `fdb0d714e833539b9f1e4ac11606ed3428e914cee871336e43ab8f86008461c0`;
the sync receipt SHA-256 is `98d0c6d00fe8e764b9a88945c3cf71e3691b58aba01660cfff3e62f762f25c42`.

Retained cap-64 rejected receipt fields:

| Field | Value |
| --- | ---: |
| `status` | `rejected` |
| `elapsed_ms` | 1,822,462 |
| `tree_lane_cap` | 64 |
| `tree_lane_process_cap` | 64 |
| `tree_lane_namespace_cap` | 64 |
| `capacity_files` | 3,500 |
| `capacity_file_bytes` | 16,384 |
| `capacity_logical_bytes` | 57,344,000 |
| `failure_sha256` | `40af54f64141b99f36e57017fd3e9299264390cd2e28616c8a12979b138e3cf4` |
| `partial_agent_high_water_kib` | 31,032 / 17,152 / 16,896 |
| `partial_capacity_shape_per_node.files` | 3,500 / 0 / 0 |
| `partial_tree_v2_store_shape_per_node.objects` | 3,501 / 1 / 1 |
| `partial_tree_v2_store_shape_per_node.object_bytes` | 57,344,016 / 16 / 16 |
| `partial_branch_count_per_node` | 3 / 3 / 3 |
| `partial_conflict_alternatives_per_node` | 0 / 0 / 0 |
| `shadow_cycles` | 0 |

The cap-64 raw proof root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-near-ceiling-cap-64-run.kM0Wu7VQ-20260903`
after compact export.

The comparison changes the scale claim. At this ceiling, single-lane transfer still fails to reach
full object custody before the timeout, while cap 4 reaches full custody, projection, repair,
conflict convergence, and explicit resolution inside the same VM class. Cap 8 buys another measured
step, but not linear scaling: catch-up improved from 1,277.048 seconds to 1,106.351 seconds
(170.697 seconds, 13.4%), and total elapsed improved from 1,361.936 seconds to 1,198.824 seconds
(163.112 seconds, 12.0%). Cap 16 buys a smaller additional step over cap 8: catch-up improved by
46.636 seconds (4.2%) and total elapsed by 59.920 seconds (5.0%). From cap 4 to cap 16, catch-up
improved by 217.333 seconds (17.0%) and total elapsed by 223.032 seconds (16.4%). Memory high-water
and allocated-byte deltas stayed in the same range across all accepted lane widths. Cap 32 then
regressed into timeout with followers still below 200 received objects and no follower projection.
Cap 64 also timed out, with followers receiving only the 16-byte empty-file object. For this guest
shape, cap 16 is the measured lane-width sweet spot. The next bottleneck is still the per-object
transfer/projection path, not the conflict/resolution tail. The cap 1/4/8/16/32/64 series is now
complete enough to stop widening lane count as the primary optimization strategy; product work should
prioritize projection batching, tree-v2 range or bundle transfer, and route-aware auxiliary
distribution.

## Batched cap-16 direct retry

ADR 0330 inspected the subscriber behind that lane-width plateau and found that every completed file
called the general strict CAS importer separately. Because the importer inventories and
digest-verifies the complete existing object store, a 3,500-small-file pull repeated a growing full
store walk for every object. The subscriber now holds only the completed objects in its current
bounded lane window and submits that window through one importer call. It also retains exact retired
FileIds so cancellation cannot race a late Tox file offer into the generic paused-file lane.

A first direct diagnostic of the batching implementation exposed that late-offer race and was
stopped without a receipt after followers stalled with leaked paused offers. Its private state was
moved recoverably to
`$XDG_DATA_HOME/Trash/files/iotox-tree-batch-cap16-first-diagnostic-20260903`.
After the exact late-offer fence and its owned regression test were added, a fresh source-linked
cap-16 retry used:

```sh
nix develop --command python3 tools/run-sync-three-writer.py \
  --iotox /nix/store/a2nha554kpwivmnh4xsr9xzw6j311ca0-iotox-source-linked-0.46.0-rev0046/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --state-root /tmp/iotox-tree-batch-cap16-retry.8TgIq59U/state \
  --evidence .sandwurm/three-writer-near-ceiling/run.20260903T-batched-cap16-retry.json \
  --fresh-state --capacity-files 3500 --capacity-file-bytes 16384 \
  --max-sync-tree-lanes 16 --namespace-maximum-lanes 16 --timeout 1800
```

The binary SHA-256 was
`18c3a9f1f9b7ca402e5a741ae6438f44cf18d202776ff5a743cb4055af2544e8`; the content-free receipt
SHA-256 is `6c728948f1634e5a47adbe73c5609df29ef13cc7564c0ca77866507131aefb7d`.

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 478,624 |
| `capacity_catchup_ms` | 387,085 |
| `capacity_file_commit_batches_per_node` | 0 / 219 / 219 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 16 / 16 |
| `capacity_staged_file_objects_per_node` | 0 / 0 / 0 |
| `capacity_repair_ms_per_node` | 232 / 232 / 1,034 |
| `capacity_agent_high_water_kib` | 35,068 / 46,204 / 46,320 |
| `capacity_allocated_delta_bytes_per_node` | 123,478,016 / 119,083,008 / 119,218,176 |
| `periodic_attempts_per_node` | 38 / 51 / 44 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |

Every node completed repair, three-way conflict convergence, and explicit resolution. Each follower
committed all 3,500 transferred files in 219 CAS batches; 218 full batches of 16 plus one batch of 12
account exactly for that total. Compared with the prior cap-16 Sandwurm receipt, catch-up is 672.630
seconds (63.5%) shorter and total elapsed is 660.280 seconds (58.0%) shorter. The environments differ,
so those percentages are diagnostic rather than accepted VM performance evidence. A fresh
networkless Sandwurm cap-16 run is the apples-to-apples gate.

The direct receipt predates the final three late-offer counter fields in the harness. The owned test
proves cancel-before-offer retirement and the live retry observed the fence making progress, but the
next Sandwurm receipt must bind zero retained IDs/evictions at convergence. The direct private state
was moved recoverably to
`$XDG_DATA_HOME/Trash/files/iotox-tree-batch-cap16-direct-passed-20260903` after the
content-free receipt was retained.

## Batched cap-16 Sandwurm qualification

The batching implementation then repeated the exact prior cap-16 profile on committed source
revision `defd492e00162e5a59bdcc8982c97b0c085f3d0f`:

```sh
./tools/iotox-sandwurm-lab.sh up-three-writer near-ceiling-cap-16
./tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer-near-ceiling-cap-16/run.WoveT4SE
./tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/exports/three-writer/run.WoveT4SE
```

The first launch attempt, `run.EOrYCs8G`, did not boot a VM because the host's 48-GiB `/tmp` tmpfs
had only about 3 GiB free while Nix finalized the sparse 25-GiB qualification image. Sandwurm
correctly recorded `status=blocked` and no IoTox receipt. The exact image was instead prebuilt with a
temporary build directory on the ordinary host filesystem; no unrelated `/tmp` data or NixOS host
configuration was changed. The second proof root booted normally with fixed 2 vCPUs, 2 GiB RAM, a
private writable ext4 image, no network device, and the committed source-linked binary.

Compact proof `.sandwurm/exports/three-writer/run.WoveT4SE` is 104 KiB. Its compact-export manifest
SHA-256 is `e6c28f2ceb28f31f822ba0a7771c223f52f48cf1cc96af571c001d979f689ba9`; its IoTox receipt
SHA-256 is `a0739336983b3d61a5327715232226fc77de1f5df1ea6106c8aa3f97c3303d6f`. Both the
three-writer verifier and generic VM-smoke verifier accept it independently. The product binary
SHA-256 is `04cf97c15fb26bb32d508860c312604aec2cbc1f038c1bb065b8af8afa7d2bca`.

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 788,317 |
| `capacity_catchup_ms` | 654,214 |
| `capacity_file_commit_batches_per_node` | 0 / 219 / 219 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 16 / 16 |
| `capacity_staged_file_objects_per_node` | 0 / 0 / 0 |
| `capacity_late_offers_cancelled_per_node` | 0 / 7 / 8 |
| `capacity_retired_offer_ids_per_node` | 0 / 0 / 0 |
| `capacity_retired_offer_evictions_per_node` | 0 / 0 / 0 |
| `capacity_repair_ms_per_node` | 362 / 319 / 526 |
| `capacity_agent_high_water_kib` | 47,036 / 46,180 / 46,408 |
| `capacity_allocated_delta_bytes_per_node` | 123,432,960 / 120,668,160 / 120,737,792 |
| `periodic_attempts_per_node` | 57 / 57 / 78 |
| `branch_count_per_node` | 3 / 3 / 3 |
| `conflict_alternatives_per_node` | 2 / 2 / 2 |

Against the earlier cap-16 result on the same VM profile, capacity catch-up fell from 1,059.715 to
654.214 seconds: 405.501 seconds or 38.3%. Full elapsed time fell from 1,138.904 to 788.317 seconds:
350.587 seconds or 30.8%. The conflict/resolution tail varied between runs, so catch-up remains the
cleaner measure of the CAS change. Peak Agent RSS rose into the 46--47-MiB range from the earlier
33--37-MiB range; a 16-object staging window accounts for at most 256 KiB of this workload, so the
larger observed delta must not be attributed to batching without profiling.

The late-offer fix is no longer supported only by a mock race: the two followers cancelled 7 and 8
late offers during the real gate. Both drained their retirement sets completely and recorded zero
bounded-set evictions. This is positive evidence that the first failed batching diagnostic found and
closed an actual scheduling race.

This result invalidates the old conclusion that cap 16 is necessarily the current sweet spot: the
cap-4/cap-8/cap-16 series measured the superseded per-file importer. It does validate bounded
batching at cap 16 and identifies the remaining work precisely: repeat smaller caps, profile the RSS
change, replace polling source scans, and decide whether a trustworthy durable inventory index or a
new negotiated bundle/range extension is warranted.

After compact export and independent verification, the 3.4-GiB accepted raw proof root was moved
recoverably to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-batched-cap16-run.WoveT4SE-20260903`.
The smaller prelaunch-blocked root was moved to
`$XDG_DATA_HOME/Trash/files/iotox-sandwurm-three-writer-batched-cap16-prelaunch-blocked-run.EOrYCs8G-20260903`.
The repository workspace retains only the independently verifiable compact proof.

## Evidence boundary

This file now contains mixed direct-host diagnostics, accepted near-ceiling Sandwurm cap-4/cap-8/
cap-16 VM gates before batching, the accepted batched cap-16 repeat, and compact retained
cap-32/cap-64 rejections. It is not production
synchronization qualification, not a data-loss finding, and not a precious-data recommendation. It
does not prove the exact ceiling, cold-cache behavior, physical storage durability, power-cut
recovery, dishonest storage behavior, independent backup safety, or multi-machine behavior outside
the same-computer VM substrate.
