# Specimen flow 77 — residue sidecar, flattening refusal, and egress survival

Goal: keep Foundry honest when a query result, support-card table, dashboard tile, chart, CSV, JSON export, markdown summary, cache-served object, or SlopOS-facing operator artifact leaves the cube and would otherwise shed the residue that made it meaningful.

## Scenario

A SlopOS support workspace asks for a tidy weekly table:

```text
week, boundary_family, mediation_class, outcome_class, redaction_reason, profile, status, count
```

The table is then reused as:

- a dashboard tile;
- a CSV export;
- a chart;
- a JSON API response;
- a markdown support summary;
- a cached materialized result; and
- a balance/reconciliation support card.

The tempting but wrong move is to let the tidy surface stand alone.

That surface has lost the reasons it was safe or unsafe to read: query contract, result envelope, hierarchy scope, rollup path, materialization cut, refresh witness, disclosure cut, suppression witness, observation-status card, adjustment witness, control-total card, reconciliation witness, classification pin, crosswalk witness, and code-drift fence.

Foundry should not ban tidy surfaces. It should require every tidy surface to carry its meaning, link to it by digest, or refuse to leave.

## Small seam to prove

### 1) residue sidecar

A residue sidecar is a compact digest-linked carrier for semantic residue that an egress surface cannot carry in-band.

Example:

```text
semantic_sidecar:
  sidecar_family: foundry_semantic_sidecar_v0
  sidecar_digest: sha256:...
  attached_surface:
    kind: chart
    surface_digest: sha256:...
  source_cut: foundry_cut_2026_05_21T06_10Z
  query_contract_digest: sha256:...
  result_envelope_digest: sha256:...
  grain_cards: [grain_credential_presentation_observation_v0]
  classification_pins: [pin_boundary_browser_federation_v0]
  crosswalk_witnesses: [cw_boundary_browser_federation_to_browser_mediation_v0]
  materialization_cuts: [mat_weekly_support_summary_2026_05_21]
  refresh_witnesses: [refresh_weekly_support_summary_2026_05_21]
  disclosure_cuts: [disc_support_agent_masked_v0]
  suppression_witnesses: [suppression_small_cell_redaction_reason_v0]
  observation_status_cards: [status_as_observed_or_adjusted_v0]
  control_total_cards: [control_total_weekly_support_v0]
  reconciliation_witnesses: [recon_weekly_support_v0]
  fences:
    - no_label_join
    - no_bare_code_join
    - same_cut_only
    - export_sidecar_required
    - suppression_blocks_subtraction
    - stale_cut_refused
  loss_profile:
    row_preserving: false
    drill_through: sidecar_only
    irreversible_losses:
      - chart_bins_drop_row_identity
```

This is smaller than a universal datacube schema. It is an egress truth wrapper.

### 2) flattening refusal

A flattening refusal is the explicit decision that a surface may not be emitted in a requested shape unless residue survives elsewhere.

Example refusals:

```text
flattening_refusal:
  requested_surface: csv_export
  refused_reason: classification_pins_would_be_dropped
  required_escape:
    - emit_semantic_sidecar
    - keep_native_lens_export
    - request_row_preserving_json
  refusal_fence: export_sidecar_required
```

This keeps CSV, chart, markdown, and BI surfaces useful without letting them become semantic keys.

### 3) egress survival check

An egress survival check is a deterministic fixture/checker posture, not a global proof system.

Example:

```text
egress_survival_check:
  fixture_id: specimen_76_classification_drift_golden
  surface_under_test: weekly_support_chart
  expected_failures:
    - label_only_export
    - bare_code_join
    - balance_reuse_across_classification_cut
    - unmapped_code_coerced_to_other
  expected_passes:
    - chart_with_sidecar
    - old_lens_display_with_native_pin
    - one_to_one_rename_with_reviewed_crosswalk
```

This makes the prose seams falsifiable.

## What this specimen proves

Foundry can let useful SlopOS-facing surfaces leave the cube without inventing:

- one universal semantic layer;
- one warehouse/lakehouse runtime;
- one terminology server;
- one validation DSL;
- one privacy engine;
- one accounting/statistics engine;
- one mandatory JSON shape for all future results.

The cube only needs to say:

1. which residue the surface still carries;
2. which residue moved to a digest-linked sidecar;
3. which losses are irreversible;
4. and which requested flattenings must be refused.

## What this specimen must keep separate

- sidecar attachment versus source truth;
- export digest versus result identity;
- in-band metadata versus sidecar metadata;
- sidecar availability versus policy approval;
- row-preserving export versus lossy chart;
- old-lens display versus current-label rewrite;
- validation check pass versus Ward-style verdict;
- materialized result reuse versus same-cut meaning;
- suppression witness versus zero/null export;
- balance pass versus truth or force-balancing authority.

## Promotion gate for these nouns

Do not widen residue sidecars beyond egress surfaces until all of the following survive fixtures without collapse:

- one result envelope and validation witness attached to a JSON result;
- one hierarchy/rollup/aggregation guard attached to a parent-row table;
- one materialization cut and refresh witness attached to a cached support card;
- one disclosure cut and suppression witness attached to a CSV/chart export;
- one observation-status/adjustment/as-observed fence attached to an adjusted value export;
- one control-total/reconciliation/balance fence attached to a support-card total;
- one classification pin/crosswalk/code-drift fence attached to a label-heavy chart;
- one requested export that is refused because residue would be lost.

## Why this matters

Datacubes become dangerous at the edges. Inside the cube, a row may be carefully pinned and witnessed. Outside the cube, a tidy chart or CSV can erase the pins and still look authoritative.

Specimen 77 gives Foundry a small rule: egress either preserves meaning, points to meaning, or refuses to pretend.
