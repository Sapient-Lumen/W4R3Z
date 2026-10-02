# 0399: Plan precious-data gates and handle the final soak boundary honestly

Date: 2026-09-22

Status: accepted; storage-media planning portions superseded by ADR 0400 and
custody terminology superseded by ADR 0405

## Context

IoTox sync has strong same-host storage science, exact production
transaction-prefix replay, strict receipt verifiers for recovery custody, and a
stable gate that shape-checks those receipts.
It still must not imply that a human can trust precious data by default.

Two practical gaps remained:

- operators needed a safe porch before backup/restore custody work; and
- the 24-hour three-writer soak could reach the effective finish line, then
  start a scheduled restart-settle cell at the final cycle boundary and reject
  a representative run because local control repair timed out there.

## Decision

Add `tools/plan-sync-precious-data-gates.py` and expose it through:

```sh
tools/iotox-repo.sh sync-precious-data-gates-plan
```

The helper is read-only by default. After ADR 0400, it inventories only
content-free backup/restore capability, prints the next gate commands, and
optionally writes invalid-by-default backup-custody and recovery-runbook
templates to an explicit operator-selected directory. It does not plan or
invite storage-media certification.

Also add `--soak-final-boundary-restart-policy` to the three-writer soak
harness. The default is `allow`. The Sandwurm `soak-24h` profile selects
`skip-if-floor-satisfied`, which can skip a scheduled restart only when:

- a wall-clock soak floor exists;
- a minimum cycle floor exists;
- the next cycle is a scheduled restart boundary;
- the cycle floor would be satisfied by that cycle;
- the wall-clock floor is already satisfied before beginning that cycle; and
- no deferred repair is pending.

The receipt records:

- `soak_final_boundary_restart_policy`;
- `soak_restart_skipped_final_boundary`; and
- `soak_restart_skipped_cycles`.

The verifier rejects malformed skip claims, skip claims under `allow`, skips on
non-restart cycles, and skips before the minimum-cycle floor.

## Consequences

Precious-data readiness becomes easier to approach without becoming easier to
overclaim. The planner does not format, mount, unmount, or read file contents,
and its templates are intentionally rejected by the real verifiers until an
operator replaces placeholders with genuine receipt evidence.

The long-soak profile no longer has to punish a representative already-long run
for beginning a new disruptive restart cell after the acceptance floors are
already satisfied. Normal scheduled restart-settle evidence is still required
for every restart that actually runs, and short smoke soaks continue to exercise
the ordinary restart path.

This does not complete recovery custody or precious-data readiness. It makes
the next honest proof step safer and clearer.

## Validation

```sh
python3 tools/plan-sync-precious-data-gates.py --self-test
python3 -m py_compile \
  tools/plan-sync-precious-data-gates.py \
  tools/run-sync-three-writer.py \
  tools/verify-sync-three-writer-sandwurm.py \
  tools/inspect-sync-three-writer-soak.py \
  tools/watch-sync-three-writer-soak.py
ctest --test-dir build/gcc-debug -R \
  '^(iotox\.sync-precious-data-gates-plan|iotox\.storage-readiness|iotox\.sync-backup-custody-verifier|iotox\.sync-three-writer-sandwurm-verifier|iotox\.sync-three-writer-soak-status|iotox\.sync-three-writer-soak-watch|iotox\.repo-stable-evidence-plan|iotox\.docs-coherence)$' \
  --output-on-failure
```
