# Cloudtainer Standing Bootstrap Delta

This card answers one narrow but useful blocked-session question: if a future Rust-capable inheritor fixes the current `simple_standing.initial_standing` bootstrap seam, which of the current comeback witnesses actually move?

## Summary

- affected queue rows: `3` from `artifacts/reports/cloudtainer_rust_probe_oracles.json`
- affected unique seeds: `2`
- rows whose mean stats stay invariant under the bootstrap repair: `3`
- rows currently classified as trace-only drift: `3`
- rows with action-stream drift: `0`
- rows with payoff-stream drift: `0`
- earliest standing-trace divergence round: `r0`

## Why the current delta is trace-only

- probe expansion still builds each `TaskSpec` via `TaskSpec::new(...)`, which seeds `standing_a` and `standing_b` from a fixed `1.0` rather than from `world.reputation.initial_standing`: `crates/gr_engine/src/probe.rs:379-391`, `crates/gr_engine/src/spec.rs:300-314`
- `run_match(...)` bootstraps its live reputation state from those task fields, then updates standing each round using the active simple-standing rule: `crates/gr_engine/src/sim.rs:488-489,527-528`, `crates/gr_engine/src/sim.rs:647-664`
- for the current affected probe seeds, the active strategy selectors consult prior observed actions/signals but do not branch on `opponent_standing`, so bootstrap repair changes the recorded standing trajectory without changing the executed action/payoff stream: `crates/gr_engine/src/sim.rs:55-290`

## Seed table

| Preferred seed | Queue rows | Declared start | Current task start | Mean stats move? | Action stream moves? | First standing diff | Classification |
| --- | ---: | ---: | ---: | --- | --- | --- | --- |
| `examples/probes/simple_standing_image_scoring_probe.json` | `2` | `0.5` | `1` | `no` | `no` | `r0` | `trace_only` |
| `examples/probes/simple_standing_standing_norm_probe.json` | `1` | `0.7` | `1` | `no` | `no` | `r0` | `trace_only` |

## Seed details

### `examples/probes/simple_standing_image_scoring_probe.json`

- probe/matchup: `simple_standing_image_scoring_probe_v1` / `always_c_vs_tft_under_image_scoring`
- declared vs current bootstrap: `0.5` vs `1`
- classification: `trace_only`
- implementor note: current strategy selectors in these seeds do not branch on opponent_standing, so honoring declared initial_standing changes only the carried standing trace and standing-update bookkeeping, not the executed action/payoff stream
- queue rows carried by this seed:
  - `reputation_kind` / `simple_standing` -> `lift_simple_standing_reputation_kind_lift_first_seed` in `probe_run`
  - `standing_update_rule` / `image_scoring` -> `lift_image_scoring_standing_update_rule_lift_first_seed` in `probe_run`
- mean stats under current bootstrap: `avg_payoff_a=3`, `avg_payoff_b=3`, `coop_rate_a=1`, `coop_rate_b=1`, `mutual_coop_rate=1`, `mutual_defect_rate=0`
- mean stats under declared bootstrap: `avg_payoff_a=3`, `avg_payoff_b=3`, `coop_rate_a=1`, `coop_rate_b=1`, `mutual_coop_rate=1`, `mutual_defect_rate=0`
- trace delta: first standing diff at `r0`, action-stream changed=`false`, payoff-stream changed=`false`, changed fields=`standing_a_post_update`, `standing_a_pre_update`, `standing_b_post_update`, `standing_b_pre_update`
- current bootstrap trace excerpt:
  - `r0` pre=(`1`, `1`) exec=(`c`, `c`) post=(`1`, `1`)
  - `r1` pre=(`1`, `1`) exec=(`c`, `c`) post=(`1`, `1`)
  - `r2` pre=(`1`, `1`) exec=(`c`, `c`) post=(`1`, `1`)
  - `r3` pre=(`1`, `1`) exec=(`c`, `c`) post=(`1`, `1`)
- declared-bootstrap trace excerpt:
  - `r0` pre=(`0.5`, `0.5`) exec=(`c`, `c`) post=(`0.55`, `0.55`)
  - `r1` pre=(`0.55`, `0.55`) exec=(`c`, `c`) post=(`0.595`, `0.595`)
  - `r2` pre=(`0.595`, `0.595`) exec=(`c`, `c`) post=(`0.6355`, `0.6355`)
  - `r3` pre=(`0.6355`, `0.6355`) exec=(`c`, `c`) post=(`0.67195`, `0.67195`)

### `examples/probes/simple_standing_standing_norm_probe.json`

- probe/matchup: `simple_standing_standing_norm_probe_v1` / `tft_vs_always_d_under_standing_norm`
- declared vs current bootstrap: `0.7` vs `1`
- classification: `trace_only`
- implementor note: current strategy selectors in these seeds do not branch on opponent_standing, so honoring declared initial_standing changes only the carried standing trace and standing-update bookkeeping, not the executed action/payoff stream
- queue rows carried by this seed:
  - `standing_update_rule` / `standing_norm` -> `lift_standing_norm_standing_update_rule_lift_first_seed` in `probe_run`
- mean stats under current bootstrap: `avg_payoff_a=0.916667`, `avg_payoff_b=1.333333`, `coop_rate_a=0.083333`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0.916667`
- mean stats under declared bootstrap: `avg_payoff_a=0.916667`, `avg_payoff_b=1.333333`, `coop_rate_a=0.083333`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0.916667`
- trace delta: first standing diff at `r0`, action-stream changed=`false`, payoff-stream changed=`false`, changed fields=`standing_a_post_update`, `standing_a_pre_update`, `standing_b_post_update`, `standing_b_pre_update`
- current bootstrap trace excerpt:
  - `r0` pre=(`1`, `1`) exec=(`c`, `d`) post=(`1`, `0.8`)
  - `r1` pre=(`1`, `0.8`) exec=(`d`, `d`) post=(`0.8`, `0.6`)
  - `r2` pre=(`0.8`, `0.6`) exec=(`d`, `d`) post=(`0.6`, `0.4`)
  - `r3` pre=(`0.6`, `0.4`) exec=(`d`, `d`) post=(`0.6`, `0.2`)
- declared-bootstrap trace excerpt:
  - `r0` pre=(`0.7`, `0.7`) exec=(`c`, `d`) post=(`0.8`, `0.5`)
  - `r1` pre=(`0.8`, `0.5`) exec=(`d`, `d`) post=(`0.8`, `0.3`)
  - `r2` pre=(`0.8`, `0.3`) exec=(`d`, `d`) post=(`0.8`, `0.1`)
  - `r3` pre=(`0.8`, `0.1`) exec=(`d`, `d`) post=(`0.8`, `0`)

## Implementor guidance

1. A future bootstrap repair can keep the current payoff/cooperation witness headlines for these three queue rows; the current delta surface says the risk is trace-only, not mean-stat drift.
2. Once Cargo returns, apply the narrow source repair from `docs/RUST_STANDING_BOOTSTRAP_REPAIR_PATCH.md`, then land the standalone guard from `docs/RUST_STANDING_BOOTSTRAP_GUARD.md` so the first recorded standing values equal the declared `world.reputation.initial_standing` for a simple-standing probe seed. That closes the blind spot directly without turning this trace seam into a vague engine-wide default change.
3. Re-run this card whenever a strategy starts consulting `opponent_standing`; at that point the same seam can become action-sensitive instead of remaining trace-only.

