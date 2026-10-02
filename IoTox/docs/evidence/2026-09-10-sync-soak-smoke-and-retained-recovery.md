# 2026-09-10 sync soak smoke and retained recovery evidence

This note records the first accepted same-host Sandwurm proof for ADRs 0361 and 0362. It is a
construction proof, not a precious-data recommendation.

## Commands

Focused local checks:

```sh
python3 -m py_compile \
  tools/run-sync-three-writer.py \
  tools/run-sync-recovery-rehearsal.py \
  tools/verify-sync-three-writer-sandwurm.py \
  tools/run-sync-retained-recovery-drill.py \
  tools/clean-workspace.py

python3 tools/verify-sync-three-writer-sandwurm.py --self-test
python3 tools/run-sync-retained-recovery-drill.py --self-test
python3 tools/clean-workspace.py --self-test
nix flake check --no-build --override-input sandwurm git+file:../sandwurm
nix develop --command cmake --build build/gcc-debug -j2 --target iotox iotox_tests
nix develop --command ctest --test-dir build/gcc-debug \
  -R '^(iotox\.unit-and-integration|iotox\.client-help)$' --output-on-failure
```

Sandwurm proof:

```sh
tools/iotox-sandwurm-lab.sh up-three-writer soak-smoke
tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer-soak-smoke/run.UFBCMzt9
python3 tools/verify-sync-three-writer-sandwurm.py \
  .sandwurm/exports/three-writer/run.UFBCMzt9
python3 tools/verify-sandwurm-vm-smoke.py \
  .sandwurm/exports/three-writer/run.UFBCMzt9 device
```

## Artifact identity

- Raw proof root: `.sandwurm/lab/three-writer-soak-smoke/run.UFBCMzt9`
- Compact proof root: `.sandwurm/exports/three-writer/run.UFBCMzt9`
- Compact manifest SHA-256: `5e641a29d3ab5c194f254be1ec923a44e4d371dd69e770806a8103cb70d498b6`
- Compact export size: 96,198 bytes across five files
- Compact receipt SHA-256:
  `f3136b5669da1651ae2f3a1e0921faeca4a7d6b78eb9f2f3879adf4c703111a8`
- Raw recovery receipt SHA-256:
  `73784712c1717c7ff24e9a33b0b4230af8fb3c7c06cec8c3d5358d4bf6ed8c01`
- Raw storage-fault receipt SHA-256:
  `ab9f9e034831c797efaac8c5ed6aed2e4e76f787cff701743f3a8c25250d855c`
- IoTox binary SHA-256:
  `1784a1a9fbca4cb89bf044636cd8659256c093ac4e391eecb4fe826414697c22`
- IoTox version: `IoTox 0.51.0 rev0051`
- Verified source revision in VM smoke receipt: `f0ce75deafb3ff3f01183bc1501e5173f9590a1c-dirty`
- Compact exporter `contains_secrets`: `false`

## Result summary

The compact proof verifier passed with:

- `node_count=3`
- `directed_read_write_share_count=6`
- `branch_count_per_node=[3,3,3]`
- `conflict_alternatives_per_node=[2,2,2]`
- `maintenance_lifecycle=true`
- `recovery_rehearsal=true`
- `storage_fault_rehearsal=true`
- `soak_campaign=true`
- `network_class=none`
- `vm_substrate=cloud-hypervisor`

The short writable soak used 128 files at 4,096 bytes each, requested at least 30 seconds and at
least 3 cycles, and completed:

- `capacity_logical_bytes=524288`
- `capacity_catchup_ms=6177`
- `shadow_cycles=4`
- `shadow_elapsed_ms=7141`
- `soak_cycles=4`
- `soak_elapsed_ms=34235`
- `soak_daemon_restarts=2`
- `soak_repair_passes=2`
- `soak_delete_cycles=2`
- `soak_cycle_ms_min=1010`
- `soak_cycle_ms_median=15810`
- `soak_cycle_ms_max=16101`
- `soak_agent_high_water_kib=[18432,15872,18388]`

The retained recovery follow-up completed:

- `recovery_files=33`
- `recovery_directories=1`
- `recovery_bytes=131099`
- `recovery_elapsed_ms=81910`
- `recovery_verifier_matches=4`
- `recovery_operator_provenance=present`
- `recovery_operator_provenance_bound=true`
- `recovery_restore_reports_with_provenance=4`
- `recovery_root_devices_differ=[0,0,0,0]`
- `recovery_one_node_branch_count=[3,3,3]`
- `recovery_replacement_branch_count=[3,3,3]`

The storage-fault follow-up completed:

- `storage_fault_disk_mib_per_node=192`
- `enospc_filler_bytes=178221056`
- `enospc_abrupt_exit=-9`
- `read_only_exit=3`
- `abrupt_exchange_observed=pending-workspace`
- `abrupt_exchange_exit=-9`
- `storage_fault_final_files=19`
- `storage_fault_final_directories=1`
- `storage_fault_final_bytes=33620017`
- `storage_fault_elapsed_ms=98246`
- `storage_fault_final_tree_sha256=444795f5a52d94a9301bececa30987cc907b650551f11b562f76ac6b4f360b93`

## Boundary

This proof buys a real mechanism upgrade and one same-host acceptance run: the harness can now run
wall-clock writable soaks, retained recovery receipts bind operator provenance labels, and exact
terminal cutoff replays cannot restore a retired writer to the live frontier.

It does not close the 24-hour writable soak. It does not prove independent immutable backup custody:
the recovery labels in this run intentionally describe same-VM synthetic provenance, and the verifier
reports `root-devices-differ=[0,0,0,0]`. It also does not turn synchronization into a backup or test
dishonest storage.
