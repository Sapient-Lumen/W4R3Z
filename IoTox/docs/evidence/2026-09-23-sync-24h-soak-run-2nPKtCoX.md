# 2026-09-23 sync 24-hour soak: run.2nPKtCoX

Status: accepted same-host Sandwurm sync long-soak evidence; not independent
backup custody and not sole-copy precious-data approval.

The 24-hour three-writer soak started from commit `f8c006d` after the native
precious-data signoff porch landed. Its proof root was:

```text
.sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX
```

Early host watch confirmed the VM launched, completed 24 shadow cycles, entered
`soak-running`, and converged the first two writable soak cycles before the run
was left unattended. The final status later reported `health=passed`,
`phase=receipt-passed`, `receipt-status=passed`, and final stage
`maintenance lifecycle and writer cutoff converged`.

The dedicated verifier accepts both the raw proof and compact export. The
compact, content-free proof is:

```text
.sandwurm/exports/three-writer/run.2nPKtCoX
```

Important verifier receipt facts:

```text
schema=iotox.sync-three-writer-sandwurm-verification.v1
status=passed
contains_secrets=false
node_count=3
network_class=none
vm_substrate=cloud-hypervisor
shadow_cycles=24
soak_campaign=true
soak_cycles=288
soak_elapsed_ms=97453767
soak_restart_settle_passes=11
soak_stalled_cycle_recoveries=0
stalled_cycle_restarts=0
capacity_files=512
capacity_logical_bytes=8388608
tree_lane_cap=4
tree_lane_namespace_cap=4
tree_lane_process_cap=4
recovery_rehearsal=true
storage_fault_rehearsal=true
maintenance_lifecycle=true
read_only_start_refused=true
enospc_live_observed=true
```

The run also recorded `final_boundary_restarts_skipped=1` under the
`skip-if-floor-satisfied` policy. That is expected for ADR 0399's final-boundary
rule: after the wall-clock and cycle floors are already satisfied, the profile
does not create an artificial final restart just to punish a representative
already-long run.

Compact export facts:

```text
file_count=5
total_bytes=96980
compact_manifest_sha256=e7e42344883152e5dde264c3b6fab0c0df5e601a56334e2c2e344754d30318f9
raw_guest_sync_receipt_sha256=687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b
stable_verifier_receipt_sha256=6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0
```

The raw guest receipt inside the compact proof uses schema
`iotox.sync-three-writer.v1`. The native `sync.long-soak` stable evidence gate
expects the verifier schema above, so generate the receipt to pass to
`iotox evidence collect sync` with:

```sh
tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json
```

Validation commands:

```sh
tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX

tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX

tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/exports/three-writer/run.2nPKtCoX
```

This proof is suitable for minting the `sync.long-soak` verifier receipt for
`iotox evidence collect sync` on a real dataset. It does not create or verify
that dataset's independent immutable/versioned backup custody, restore drill,
recovery runbook, retention policy, or operator signoff.
