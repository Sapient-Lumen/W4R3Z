
# Priority-0 burden gate audit — 2026-06-15

## Decision

`rev0362` resolves `OQ-0253` by spending the first Priority-0 smoke-slice result on one concrete burden reduction rather than another doctrine pass. The hot-path `Current additions` cue is compacted from `48` broadly touched/generated surfaces to `18` true current supports, while `REVISION-RECEIPT.json#touched_surfaces` keeps the fuller trace.

The gate is deliberately reversible. It is not deletion authority, a review court, a benchmark court, or a proof of archive minimality. It records a bounded consequence of one non-independent smoke slice and opens `OQ-0254` for a position/filler-rotated challenge.

## Evidence being spent

The rev0361 smoke slice compared four packets on the same continuation problem:

| Packet | Score | Operator cost | Use in this revision |
|---|---:|---:|---|
| No archive | 2 / 16 | 1 minute | Safe behavior mostly abstains. |
| Minimal core | 14 / 16 | 8 minutes | Carries the mission heart, missing assay, OQ routing, anti-review-court boundary, and next action. |
| Full archive | 15 / 16 | 18 minutes | Adds small contradiction/coldstore context at more than twice the operator cost. |
| Sham / decoy core | 4 / 16 | 5 minutes | Proves fluent false continuity remains a real hazard. |

The actionable result is not “delete the archive.” The actionable result is that the hot cue should stop making every touched/generated surface part of default reentry when the first measured continuation task was mostly carried by the minimal core.

## Audit target

The waste target was the first-line landing cue in `START_HERE.md`, `README.md`, `AGENTS.md`, and `docs/README.md`. It had become an oversized list of `48` current additions. That list mixed true current support with generated derivatives, ledger tails, and touched surfaces. The result was a high-salience cue that taught future sessions to read mass as continuity.

`REVISION-RECEIPT.json#canon_additions` now carries only the `18` surfaces that must be visible to continue the current turn:

- `docs/40-session/priority-zero-burden-gate-audit-2026-06-15.md`
- `assays/priority-zero-burden-gate-2026-06-15.json`
- `tools/check_priority_zero_burden_gate_contract.py`
- `tools/check_priority_zero_smoke_slice_contract.py`
- `tools/validation_toolchain_lib.py`
- `docs/10-method/archive-economy-audit-witnesses.md`
- `tools/check_archive_economy_witness_contract.py`
- `tools/check_current_witness_receipt_slot.py`
- `START_HERE.md`
- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `REVISION-RECEIPT.json`
- `SURFACE-STATUS.json`
- `SELF-SUFFICIENCY-LEDGER.json`
- `FRONTIER-BACKLOG.json`
- `docs/20-constitution/open-question-registry.md`
- `docs/00-meta/trajectory-map.md`


The fuller audit trail remains in `REVISION-RECEIPT.json#touched_surfaces`, generated indexes, ledgers, coldstores, and release integrity files. The change is a hot-path gate, not a history purge.

## Trigger-gated full archive use

The full archive remains required when a future session needs contradiction recovery, coldstore restoration, receipt restoration, generated-surface drift diagnosis, or a rotated smoke slice shows material lift from archive depth. It is no longer justified as the default first cue for every continuation when the live problem is to recover mission posture and next action.

The trigger gate is:

1. Start with the landing cue, current receipt, frontier ticket, context pack, self-sufficiency tail, current method surface, and current burden-gate fixture.
2. Escalate to full archive when any cue contradicts another cue, a cited source surface is missing, a coldstore/restoration claim is under test, or the next smoke slice shows the compact packet underperforms by more than two points.
3. Treat any deletion, irreversible demotion, or authority claim as out of scope unless separately supported by public restoration evidence and ordinary revision review.

## Refactor performed

`tools/check_priority_zero_smoke_slice_contract.py` was refactored so the rev0361 smoke fixture remains valid historical evidence after `rev0362` becomes the current tail. The previous checker over-bound the smoke fixture to the current receipt, which would have forced either fossilized routing or inflated claims that the smoke slice was still the latest self-sufficiency row. The refactor now checks the fixture against its own historical ledger row while `tools/check_priority_zero_burden_gate_contract.py` checks the current burden-gate tail.

`tools/check_priority_zero_burden_gate_contract.py` is the new fail-closed guard. It rejects missing source-smoke evidence, missing hot cue compaction, missing full-archive triggers, deletion-authority creep, lost touched-surface trace, stale successor routing, and missing self-sufficiency alignment for `OQ-0254`.

## What is still risky

The remaining risk is overfitting this gate to one same-session position. `OQ-0254` must run a second slice with decisive evidence moved away from the first and last pages of the packet, plausible filler inserted, the task wording changed, and no-archive / sham / abstention controls preserved. If full archive support materially improves that slice, this gate should narrow or reverse.

## Resolution

`RS-0261` closes `OQ-0253` because the first smoke-slice result now caused an actual burden gate and a validator, not only a report. `OQ-0254` is the live successor: test whether the gate survives a position/filler-rotated slice or must be reversed.
