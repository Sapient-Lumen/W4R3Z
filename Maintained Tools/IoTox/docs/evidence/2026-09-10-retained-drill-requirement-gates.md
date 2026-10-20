# Retained drill requirement gates — 2026-09-10

## Scope

This note records validation for ADR 0366.

The pass hardened retained recovery and witness custody wrappers so operators can require local
evidence prerequisites without promoting same-host drills into independence claims.

It does not claim a completed 24-hour soak, backup independence, restore provenance,
operational witness independence, immutable custody, off-machine custody, or precious-data
suitability.

## Validated behavior

`tools/run-sync-retained-recovery-drill.py` now:

- validates the production CLI's exact label-hex bindings;
- writes command-rejected receipts without raw stdout/stderr text;
- records failure kind, return code, stdout/stderr byte counts, and failure hash;
- preserves nonzero structured `decision=mismatch` reports with manifest/count evidence;
- supports `--require-operator-provenance`; and
- supports `--require-different-device`.

`tools/run-witness-checkpoint-custody-drill.py` now:

- supports `--require-custody-labels`; and
- supports `--require-different-device`.

`tools/iotox-repo.sh` now exposes:

```sh
tools/iotox-repo.sh sync-recovery-drill [drill options] BACKUP_ROOT RESTORED_ROOT
tools/iotox-repo.sh witness-custody [drill options] SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX
```

## Validation commands

```sh
python3 -m py_compile \
  tools/run-sync-retained-recovery-drill.py \
  tools/run-witness-checkpoint-custody-drill.py

python3 tools/run-sync-retained-recovery-drill.py --self-test
python3 tools/run-witness-checkpoint-custody-drill.py --self-test
tools/iotox-repo.sh sync-recovery-drill --self-test
tools/iotox-repo.sh witness-custody --self-test
```

The self-tests cover a passing labeled receipt and a rejected missing-label receipt for both
wrappers.

Under `nix develop`, the real source-linked `build/iotox` also passed these focused checks:

- a matching same-device `sync-recovery-verify` drill with required operator provenance;
- a mismatching same-device `sync-recovery-verify` drill retained as a structured rejected receipt
  with distinct manifest digests;
- a matching same-device recovery drill that correctly rejected when `--require-different-device`
  was requested; and
- a fake witness checkpoint that the production custody command rejected while the wrapper retained
  only content-free failure metadata.

The same-device rejection matters: it proves the wrapper can distinguish “the data matched” from
“the requested local independence prerequisite was satisfied.”

## Result

The wrappers now make local drill requirements explicit and machine-checkable. They still require
operator-retained evidence to prove any real backup or witness independence claim.
