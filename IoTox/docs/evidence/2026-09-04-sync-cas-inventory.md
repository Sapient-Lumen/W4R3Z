# Effect-fenced tree-v2 CAS inventory evidence

- Date: 2026-09-04
- Source revision: `a0a0eba4acd87f80a433931e5f194108ff28a7df`
- Version: IoTox 0.47.0 rev0047
- Status: accepted direct diagnostic and exact Sandwurm qualification

## Question

ADR 0330 changed tree-v2 file admission from one complete CAS inventory per file to one per bounded
lane window. At cap 16, each 3,500-file follower still committed 219 windows and therefore paid for
219 growing full-store digest walks. ADR 0331 asks whether one strictly verified pull-private view,
plus a fresh strict scan at the final branch/projection effect boundary, can remove that amplification
without weakening quota, corruption, or concurrent-job behavior.

## Owned gates

The new worktree check performs two cached imports and requires both to report zero repeated full
inventory work. Final revalidation must inspect the exact two-object store. A separate normal
serialized importer then adds a third valid immutable object; final revalidation accepts and accounts
that addition. Replacing one cached object with corrupt bytes must fail with `protocol_error`.

The existing four-lane subscriber gate now additionally requires exactly two full scans around its
single successful file-bearing pull and four total objects observed by the final scan. GCC's
warnings-as-errors build passed the complete `834/834` owned registry. The complete GCC CTest surface
passed `55/55`; the five delegated-cgroup process tests were correctly skipped outside their VM
service fixture. The three-writer receipt verifier self-test and `nix flake check --no-build` passed.

## Clean source-linked direct run

The final additive-safe implementation was committed before construction. The source-linked binary
was built from that clean commit and the full cap-16 near-ceiling gate ran from new state:

```sh
nix develop -c python3 tools/run-sync-three-writer.py \
  --iotox /nix/store/8p73x4f1438l03rblybh589vwpp7hdv9-iotox-source-linked-0.47.0-rev0047/bin/iotox \
  --bootstrap /nix/store/jgy3lf9w65yllk5zyx5q1gxbajjhw125-iotox-tox-bootstrap-33445-0.2.23/bin/DHT_bootstrap \
  --state-root /var/tmp/iotox-cas-inventory-rev0047-cap16.519x45S9/state \
  --evidence .sandwurm/three-writer-near-ceiling/run.20260904T-rev0047-cas-inventory-cap16-direct.json \
  --fresh-state --capacity-files 3500 --capacity-file-bytes 16384 \
  --max-sync-tree-lanes 16 --namespace-maximum-lanes 16 --timeout 1800
```

The source-linked binary SHA-256 was
`8e62c38c7a042e6f5f1be4126dd20d9b9c5b5d697fcf25efd6b404022157a81e`.
The content-free receipt SHA-256 was
`6e6c9697bed3512e73ca47a744866bf7570d57bca774ba06169533b61d257ed6`.

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 478,979 |
| `capacity_catchup_ms` | 379,948 |
| `capacity_file_commit_batches_per_node` | 0 / 219 / 219 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 16 / 16 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 7 / 5 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 12,131 / 5,921 |
| `capacity_repair_ms_per_node` | 236 / 317 / 251 |
| `capacity_agent_high_water_kib` | 37,256 / 42,136 / 48,360 |
| `capacity_allocated_delta_bytes_per_node` | 123,449,344 / 121,208,832 / 121,061,376 |
| `capacity_staged_file_objects_per_node` | 0 / 0 / 0 |
| `capacity_retired_offer_ids_per_node` | 0 / 0 / 0 |
| `capacity_retired_offer_evictions_per_node` | 0 / 0 / 0 |
| `periodic_attempts_per_node` | 48 / 58 / 59 |

Every node retained three branches, both losing conflict alternatives, common explicit resolution,
and a clean repair. No watchdog restart fired. The followers' 7 and 5 scans include multiple
automation pull jobs created while the source population was being written; a successful
file-bearing job has an initial scan and a final effect-fence scan, while a still-active or failed job
may have only its initial scan.

ADR 0330's prior clean direct cap-16 sample completed catch-up in 387.085 seconds and the full gate in
478.624 seconds. The new run is 7.137 seconds (1.8%) faster in catch-up and 0.355 seconds (0.07%)
slower overall—effectively flat at whole-run scale. The old implementation and its 219 batch count
imply 219 full scans per follower; the new observed 7/5 counts are 96.8%/97.7% lower. That removes the
algorithmic amplification but falsifies the idea that it alone dominates elapsed time on this host.
Per-object Tox request/offer/terminal turnover, per-object durable installation, repeated full source
scans, and intermediate publication are now the leading candidates.

## Exact Sandwurm comparison

The same cap-16 campaign then ran from fresh state inside the established 2-vCPU/2-GiB networkless
Sandwurm Cloud Hypervisor guest. The VM used source revision
`03e0996fef3f9b5b73288806c720e411106cae3c` and the same source-linked binary SHA-256 as the direct
run. The raw 3.3-GiB proof verified before export. The independently verified compact proof is
`.sandwurm/exports/three-writer/run.yDPmVYg6`; `compact-export.json` has SHA-256
`1c758ea9188f4e786d53a9f0743912c52d5e01fc5b6cfff85c43268aa5052b06`, and the embedded
content-free sync receipt has SHA-256
`fba4d2803c012a01925463ff6ae675cccfce663968521f4805510ae74f3053e2`.

| Field | Value |
| --- | ---: |
| `elapsed_ms` | 634,194 |
| `capacity_catchup_ms` | 554,077 |
| `capacity_file_commit_batches_per_node` | 0 / 219 / 219 |
| `capacity_largest_file_commit_batch_per_node` | 0 / 16 / 16 |
| `capacity_cas_full_inventory_scans_per_node` | 0 / 21 / 15 |
| `capacity_cas_inventory_objects_inspected_per_node` | 0 / 42,977 / 25,099 |
| `capacity_repair_ms_per_node` | 573 / 1,269 / 826 |
| `capacity_agent_high_water_kib` | 40,912 / 47,596 / 47,028 |
| `capacity_allocated_delta_bytes_per_node` | 124,538,880 / 120,385,536 / 120,926,208 |
| `capacity_staged_file_objects_per_node` | 0 / 0 / 0 |
| `capacity_late_offers_cancelled_per_node` | 0 / 0 / 0 |
| `capacity_retired_offer_ids_per_node` | 0 / 0 / 0 |
| `capacity_retired_offer_evictions_per_node` | 0 / 0 / 0 |
| `periodic_attempts_per_node` | 34 / 40 / 33 |

All three nodes retained all three branches and both losing conflict alternatives, then converged on
the common explicit resolution. No watchdog restart fired. Against ADR 0330's exact 654.214-second
catch-up and 788.317-second total VM sample, this is 100.137 seconds (15.3%) faster in catch-up and
154.123 seconds (19.5%) faster overall. The 21/15 follower scans are 90.4%/93.2% below the old
implementation's batch-implied 219 scans. Unlike the effectively flat direct result, this constrained
guest shows a material elapsed-time win; complete-store hashing was therefore a real CPU/I/O
contention amplifier under guest limits, but not the only end-to-end bottleneck.

## Nonclaims and next gate

The exact constrained-VM scale comparison is closed. The result does not prove power-cut recovery,
dishonest storage, disk reservation, a 24-hour soak, physical hardware, backup suitability, or
precious-data readiness. The cache is process memory only and never replaces the mandatory final
strict scan. The next measured scale work should target repeated source scans and intermediate
publication first, then per-object Tox request/offer/terminal turnover and durability cadence. Any
bundle/range wire extension or weakened durability barrier requires its own explicit ADR and fault
evidence; neither follows automatically from this result.
