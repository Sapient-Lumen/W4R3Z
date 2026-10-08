# Replay-helper and generated-audit compression refactor audit

Revision: `rev0352`.

## Scope

This pass targets the highest-risk seam left after note-key extinction and initial event replay: frontier-source freshness could still pass on row-level `source_refs` for bridge-local public records whose typed denominator, route-local handoff, or acquired-evidence exclusion custody was not replayed. The pass also removes duplicated helper logic and compresses one generated audit that had become a large all-pass table.

## Substantive changes

- `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` moves to schema version `1.6`.
- Typed event replay is enabled for seven additional assertions: Family-C subregion portability, Family-B thermodynamic/relative-entropy scope, String/M observed-sector atlas pressure, QRF frame-transport pressure, Family-B nonequilibrium horizon calibration, Family-C finite-N/QEC/island source role, and Lab-GIE protocol/noise/classical-split pressure.
- The replayed assertion set grows from 8 to 15 assertions.
- The replayed event-row checks grow from 320 to 394.
- Twenty-one missing `source_role_events` are added to rows that previously relied on bare `source_refs` for the selected bridge assertions.
- New events are capped at `S0` and use only denominator-pressure roles with one of three dispositions: `retained_on_denominator_row_only`, `route_local_handoff_only`, or `excluded_from_acquired_source_refs`.

## Helper refactor

`tools/source_role_event_utils.py` now owns the repeated source-role event constants and row-local helper checks used by freshness replay, negative replay, and lint. This is deliberately a small utility layer, not a route or source registry. Family-local policy files still own their substantive scientific boundaries.

## Generated-audit compression

`docs/30-program/cosmology-source-role-audit.generated.md` previously displayed a long all-pass row table. The evaluator still executes all 140 checks, but the generated artifact now shows a compact check-family summary plus failure details only. `tools/lint_archive.py` rejects regrowth of the old all-pass table or a line-count breach.

## No-promotion boundary

No route score, authority state, promotion ceiling, evidence-unit source credit, empirical-delta effect, forecast realization state, decision-experiment outcome, or observed-sector recovery state is improved. Freshness/event replay is source-custody control only.

## Remaining risk

The remaining useful work is narrower: extend typed event replay only to assertions where the event semantics are clear, avoid turning the helper layer into a registry, and continue compressing generated audits that display failure-free empty rows rather than restart-relevant failures.
