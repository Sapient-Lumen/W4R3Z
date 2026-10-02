# 0403 — Accept fresh precious-data-era sync long-soak proof

Date: 2026-09-25

Status: accepted; custody terminology superseded by ADR 0405

## Context

ADR 0397 retained a hard final-restart rejection after the accepted
`run.9nqvO8B2` long-soak proof. ADRs 0400--0402 then clarified the
precious-data boundary: IoTox no longer seeks storage-media certification,
native backup/retention/evidence/signoff porches exist, and the remaining
operator-specific gate is versioned recovery custody plus restore/runbook
discipline.

After those boundaries were in place, a new 24-hour Sandwurm three-writer
soak was started from commit `f8c006d` to refresh the `sync.long-soak`
evidence used by precious-data signoff and stable evidence planning.

## Decision

Accept compact proof `.sandwurm/exports/three-writer/run.2nPKtCoX` as the
current sync long-soak evidence for this repository.

The verifier report produced by `tools/verify-sync-three-writer-sandwurm.py`
reports:

- schema `iotox.sync-three-writer-sandwurm-verification.v1`;
- `status=passed`;
- `contains_secrets=false`;
- `soak_campaign=true`;
- `shadow_cycles=24`;
- `soak_cycles=288`;
- `soak_elapsed_ms=97453767` (`27h04m13s`);
- `soak_restart_settle_passes=11`;
- `soak_stalled_cycle_recoveries=0`;
- `stalled_cycle_restarts=0`;
- `recovery_rehearsal=true`;
- `storage_fault_rehearsal=true`;
- `maintenance_lifecycle=true`;
- `read_only_start_refused=true`;
- `enospc_live_observed=true`;
- `final_boundary_restarts_skipped=1`; and
- final stage `maintenance lifecycle and writer cutoff converged`.

The compact export is content-free and small:

- proof root: `.sandwurm/exports/three-writer/run.2nPKtCoX`;
- source proof root: `.sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX`;
- exported file count: `5`;
- total exported bytes: `96980`;
- compact manifest SHA-256:
  `e7e42344883152e5dde264c3b6fab0c0df5e601a56334e2c2e344754d30318f9`;
- raw guest sync receipt SHA-256:
  `687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b`.

The raw guest receipt schema is `iotox.sync-three-writer.v1`. The native
stable-evidence checker expects the verifier schema
`iotox.sync-three-writer-sandwurm-verification.v1`, so operators should mint
the stable `sync.long-soak` receipt with:

```sh
tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json
```

That deterministic receipt currently has SHA-256
`6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0`.

`tools/iotox-repo.sh stable-evidence-plan` now names this current proof,
helper command, verifier receipt hash, raw guest receipt hash, and compact
manifest hash so operators do not have to reconstruct the accepted long-soak
path from chat or historical notes.

## Consequences

The sync long-soak gate is current and accepted for same-host Sandwurm
evidence. This strengthens the operator path to `iotox sync precious-status`
and `iotox sync precious-signoff`, but it does not complete recovery
custody, restore-runbook custody, terminal long-soak evidence, or
stable/no-concern release evidence by itself.

Operators may generate the native receipt and use it as the `--long-soak`
input when collecting evidence for a real dataset:

```sh
tools/iotox-repo.sh current-sync-long-soak-receipt --out /proof/long-soak.json

iotox evidence collect sync /dataset read-write 30 \
  --out /proof/sync \
  --storage-readiness /proof/storage-readiness.json \
  --long-soak /proof/long-soak.json \
  --backup-custody /proof/sync-backup/backup-custody.json \
  --restore-drill /proof/sync-backup/restore-drill.json \
  --recovery-runbook /proof/recovery-runbook.receipt \
  --retention-policy /proof/sync-retention-policy.receipt
```

## Validation

```sh
tools/iotox-sandwurm-lab.sh status-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX

tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX

tools/iotox-sandwurm-lab.sh export-three-writer \
  .sandwurm/lab/three-writer-soak-24h/run.2nPKtCoX

tools/iotox-sandwurm-lab.sh verify-three-writer \
  .sandwurm/exports/three-writer/run.2nPKtCoX
```
