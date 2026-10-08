# Audit — rev0169

## Scope

The audit asked whether rev0168's release could be sent as-is after a documented acceptance command stalled in a checkpoint-heavy test group, a generated scenario template could be started without editing placeholder text, and the archive lacked an explicit top-level license.

## Finding A169-01 — close-time truncating WAL checkpoint could stall teardown

**Risk.** `PRAGMA wal_checkpoint(TRUNCATE)` during connection close can wait behind another reader connection or subprocess fixture after useful story work has completed. That turns a passing checkpoint test into an ambiguous timeout.

**Repair.** Close-time cleanup now sets a short busy timeout, attempts `PRAGMA wal_checkpoint(PASSIVE)`, swallows cleanup-only SQLite operational/closed-database errors, and closes the connection. Durability still comes from committed WAL state and normal SQLite recovery.

## Finding A169-02 — generated scenario templates were accepted as runnable capsules

**Risk.** A research run could be created with literal placeholder player inputs or undeclared model-policy placeholders, making a nominally valid experiment meaningless.

**Repair.** Scenario capsule validation now raises `scenario-capsule-template-not-edited` when generated player-input placeholders or generated model-policy placeholders remain. Tests and CLI fixtures explicitly edit generated templates before beginning runs.

## Finding A169-03 — recipient acceptance was too monolithic

**Risk.** A single `unittest discover` command gives little diagnostic value if one module stalls or exhausts a wall-clock budget.

**Repair.** Added `tools/run_acceptance.py`, which runs each `tests/test_*.py` module in a fresh interpreter with a per-module timeout and reports the exact failing or timed-out module. Standard discovery remains available for development.

## Finding A169-04 — licensing was ambiguous

**Risk.** A gift artifact without a top-level license leaves reuse, redistribution, and patching unclear.

**Repair.** Added a top-level MIT `LICENSE` and project metadata pointing to it.

## Residual risks

- Passing tests and artifact checks do not prove provider identity, context isolation, narrative quality, or empirical efficacy.
- Passive close-time checkpointing can leave WAL files for normal SQLite recovery rather than forcing truncation at teardown.
- The template gate catches generated Lacuna placeholders, not every low-quality or scientifically weak scenario script.

## Acceptance disposition

The revision is acceptable when source compile, bounded acceptance, targeted checkpoint and scenario-template regressions, manifest verification, and strict artifact audit pass in the packaged tree.
