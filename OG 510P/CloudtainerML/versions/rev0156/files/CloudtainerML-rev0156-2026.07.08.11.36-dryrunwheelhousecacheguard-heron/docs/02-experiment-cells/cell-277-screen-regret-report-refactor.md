# CELL-277 — Screen Regret Report Refactor

- priority: P0
- status: implemented-audit-rev0025
- idea: IDEA-0276
- sources: SRC-0296, SRC-0300

## Cheap first run

Generate a current-revision audit over regret/cost/kernel fields in smoke outputs.

## Metrics

- screen_audited_artifacts
- guard_ready_count
- fields_present

## Required baselines

- probe_metric_index
- native_family_report
- manual_notes

## Stop condition

Keep if it catches probes lacking reversal surfaces.
