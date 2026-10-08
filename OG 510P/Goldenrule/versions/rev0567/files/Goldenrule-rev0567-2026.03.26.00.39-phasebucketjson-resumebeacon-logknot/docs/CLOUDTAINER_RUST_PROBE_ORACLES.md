# Cloudtainer Rust Probe Oracles

This card gives the blocked cloudtainer a compact semantic oracle surface for the current Rust comeback queue: exact path witnesses where the preferred probe seed is deterministic, and exact finite-horizon expectation witnesses where the preferred probe seed is stochastic.

## Summary

- queue rows covered: `14` from `artifacts/reports/rust_external_test_queue.json`
- unique preferred probe seeds: `10`
- exact path witnesses: `8` rows
- exact expectation witnesses: `6` rows
- rows with inert `initial_standing` warning: `3`

## Why this exists

- the archive already had the comeback queue, patch plan, and execution card, but a blocked session still lacked one compact place to see the expected semantics of the preferred probe seeds without `cargo`
- `ReputationModelSpec::SimpleStanding` declares `initial_standing`, but `TaskSpec::new(...)` still seeds `standing_a`/`standing_b` from a fixed `1.0`, probe expansion calls `TaskSpec::new(...)` directly, and `run_match(...)` bootstraps the live standing state from those task fields rather than from the world declaration: `crates/gr_engine/src/spec.rs:133-145`, `crates/gr_engine/src/spec.rs:300-314`, `crates/gr_engine/src/probe.rs:379-391`, `crates/gr_engine/src/sim.rs:488-489,527-528`, `crates/gr_engine/src/sim.rs:647-664`

## Row-by-row witness table

| Family | Variant | Lane | Oracle | Preferred seed | Witness headline |
| --- | --- | --- | --- | --- | --- |
| `assertion_kind` | `coop_rate_a_at_least` | `probe_run` | `exact_path` | `examples/probes/ipd_c_vs_d_smoke.json` | avg_a=0; avg_b=5; coop_a=1; coop_b=0; observed=1 |
| `assertion_kind` | `coop_rate_b_at_least` | `probe_run` | `exact_path` | `examples/probes/ipd_c_vs_d_smoke.json` | avg_a=0; avg_b=5; coop_a=1; coop_b=0; observed=0 |
| `assertion_kind` | `mutual_defect_rate_at_most` | `probe_run` | `exact_path` | `examples/probes/mutual_defect_rate_guardrail_probe.json` | avg_a=3; avg_b=3; coop_a=1; coop_b=1; observed=0 |
| `reputation_kind` | `simple_standing` | `probe_run` | `exact_path` | `examples/probes/simple_standing_image_scoring_probe.json` | avg_a=3; avg_b=3; coop_a=1; coop_b=1; declared initial_standing currently inert |
| `standing_update_rule` | `image_scoring` | `probe_run` | `exact_path` | `examples/probes/simple_standing_image_scoring_probe.json` | avg_a=3; avg_b=3; coop_a=1; coop_b=1; declared initial_standing currently inert |
| `standing_update_rule` | `standing_norm` | `probe_run` | `exact_path` | `examples/probes/simple_standing_standing_norm_probe.json` | avg_a=0.916667; avg_b=1.333333; coop_a=0.083333; coop_b=0; declared initial_standing currently inert |
| `strategy_family` | `fsm` | `probe_run` | `exact_path` | `examples/probes/fsm_grim_trigger_probe.json` | avg_a=0.875; avg_b=1.5; coop_a=0.125; coop_b=0 |
| `strategy_family` | `memory_one_exit` | `probe_run` | `exact_path` | `examples/probes/memory_one_exit_after_break_probe.json` | avg_a=0; avg_b=2.5; coop_a=0.5; coop_b=0 |
| `noise_kind` | `observation_flip` | `probe_run` | `exact_expectation` | `examples/probes/noisy_adversarial_probe.json` | avg_a=3.799924; avg_b=1.800114; coop_a=0.600038; coop_b=1 |
| `assertion_kind` | `avg_payoff_b_at_least` | `probe_run` | `exact_expectation` | `examples/probes/ipd_asymmetric_noise_c_vs_d_smoke.json` | avg_a=0.6; avg_b=4.6; coop_a=1; coop_b=0.2; observed=4.6 |
| `noise_kind` | `iid` | `probe_run` | `exact_expectation` | `examples/probes/scaling_prefix_stability_probe_seed.json` | avg_a=2.310283; avg_b=2.086795; coop_a=0.452; coop_b=0.496698 |
| `noise_kind` | `implementation_flip` | `probe_run` | `exact_expectation` | `examples/probes/implementation_flip_probe.json` | avg_a=3.031594; avg_b=2.815969; coop_a=0.906875; coop_b=0.95 |
| `strategy_family` | `memory_one` | `probe_run` | `exact_expectation` | `examples/probes/noisy_adversarial_probe.json` | avg_a=3.799924; avg_b=1.800114; coop_a=0.600038; coop_b=1 |
| `metamorphic_kind` | `scaling_prefix_stability` | `metamorphic_suite` | `exact_expectation` | `examples/probes/scaling_prefix_stability_probe_seed.json` | avg_a=2.310283; avg_b=2.086795; coop_a=0.452; coop_b=0.496698; same-seed prefix pass is exact here |

## Witness details

### `lift_coop_rate_a_at_least_assertion_kind_lift_first_seed`

- seed: `examples/probes/ipd_c_vs_d_smoke.json` line `23` (`ipd_c_vs_d_smoke_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `ipd_c_vs_d_smoke_v1` / matchup `always_c_vs_always_d`
- witness stats: `avg_payoff_a=0`, `avg_payoff_b=5`, `coop_rate_a=1`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r1; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r2; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r3; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)

### `lift_coop_rate_b_at_least_assertion_kind_lift_first_seed`

- seed: `examples/probes/ipd_c_vs_d_smoke.json` line `24` (`ipd_c_vs_d_smoke_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `ipd_c_vs_d_smoke_v1` / matchup `always_c_vs_always_d`
- witness stats: `avg_payoff_a=0`, `avg_payoff_b=5`, `coop_rate_a=1`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r1; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r2; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r3; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)

### `lift_mutual_defect_rate_at_most_assertion_kind_lift_first_seed`

- seed: `examples/probes/mutual_defect_rate_guardrail_probe.json` line `4` (`mutual_defect_rate_guardrail_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `mutual_defect_rate_guardrail_probe_v1` / matchup `always_c_vs_always_c_zero_mutual_defect`
- witness stats: `avg_payoff_a=3`, `avg_payoff_b=3`, `coop_rate_a=1`, `coop_rate_b=1`, `mutual_coop_rate=1`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3)
  - r1; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3)
  - r2; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3)
  - r3; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3)

### `lift_simple_standing_reputation_kind_lift_first_seed`

- seed: `examples/probes/simple_standing_image_scoring_probe.json` line `3` (`simple_standing_image_scoring_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `simple_standing_image_scoring_probe_v1` / matchup `always_c_vs_tft_under_image_scoring`
- witness stats: `avg_payoff_a=3`, `avg_payoff_b=3`, `coop_rate_a=1`, `coop_rate_b=1`, `mutual_coop_rate=1`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r1; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r2; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r3; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
- standing bootstrap warning: declared `initial_standing=0.5` but effective task start is `1` under the current probe-expansion path
- note: current probe expansion seeds TaskSpec standing_a/standing_b at 1.0, so declared world.reputation.initial_standing is inert for these probe seeds

### `lift_image_scoring_standing_update_rule_lift_first_seed`

- seed: `examples/probes/simple_standing_image_scoring_probe.json` line `3` (`simple_standing_image_scoring_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `simple_standing_image_scoring_probe_v1` / matchup `always_c_vs_tft_under_image_scoring`
- witness stats: `avg_payoff_a=3`, `avg_payoff_b=3`, `coop_rate_a=1`, `coop_rate_b=1`, `mutual_coop_rate=1`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r1; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r2; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
  - r3; pre=(1,1); intend=(c,c); exec=(c,c); obs=(c,c); pay=(3,3); post=(1,1)
- standing bootstrap warning: declared `initial_standing=0.5` but effective task start is `1` under the current probe-expansion path
- note: current probe expansion seeds TaskSpec standing_a/standing_b at 1.0, so declared world.reputation.initial_standing is inert for these probe seeds

### `lift_standing_norm_standing_update_rule_lift_first_seed`

- seed: `examples/probes/simple_standing_standing_norm_probe.json` line `3` (`simple_standing_standing_norm_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `simple_standing_standing_norm_probe_v1` / matchup `tft_vs_always_d_under_standing_norm`
- witness stats: `avg_payoff_a=0.916667`, `avg_payoff_b=1.333333`, `coop_rate_a=0.083333`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0.916667`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5); post=(1,0.8)
  - r1; pre=(1,0.8); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1); post=(0.8,0.6)
  - r2; pre=(0.8,0.6); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1); post=(0.6,0.4)
  - r3; pre=(0.6,0.4); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1); post=(0.6,0.2)
- standing bootstrap warning: declared `initial_standing=0.7` but effective task start is `1` under the current probe-expansion path
- note: current probe expansion seeds TaskSpec standing_a/standing_b at 1.0, so declared world.reputation.initial_standing is inert for these probe seeds

### `lift_fsm_strategy_family_lift_first_seed`

- seed: `examples/probes/fsm_grim_trigger_probe.json` line `3` (`fsm_grim_trigger_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `fsm_grim_trigger_probe_v1` / matchup `grim_trigger_vs_always_d`
- witness stats: `avg_payoff_a=0.875`, `avg_payoff_b=1.5`, `coop_rate_a=0.125`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0.875`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r1; pre=(1,1); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1)
  - r2; pre=(1,1); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1)
  - r3; pre=(1,1); intend=(d,d); exec=(d,d); obs=(d,d); pay=(1,1)

### `lift_memory_one_exit_strategy_family_lift_first_seed`

- seed: `examples/probes/memory_one_exit_after_break_probe.json` line `3` (`memory_one_exit_after_break_probe_v1`)
- lane: `probe_run`
- oracle: `exact_path` on probe `memory_one_exit_after_break_probe_v1` / matchup `memory_one_exit_vs_always_d`
- witness stats: `avg_payoff_a=0`, `avg_payoff_b=2.5`, `coop_rate_a=0.5`, `coop_rate_b=0`, `mutual_coop_rate=0`, `mutual_defect_rate=0`
- exact path excerpt (first recorded rounds):
  - r0; pre=(1,1); intend=(c,d); exec=(c,d); obs=(d,c); pay=(0,5)
  - r1; pre=(1,1); intend=(exit,d); exec=(exit,d); obs=(d,exit); pay=(0,0)

### `lift_observation_flip_noise_kind_externalize_now_seed`

- seed: `examples/probes/noisy_adversarial_probe.json` line `17` (`noisy_extortion_chi3_v1`)
- lane: `probe_run`
- oracle: `exact_expectation` on probe `noisy_extortion_chi3_v1` / matchup `extortion_vs_always_c_noisy`
- witness stats: `avg_payoff_a=3.799924`, `avg_payoff_b=1.800114`, `coop_rate_a=0.600038`, `coop_rate_b=1`, `mutual_coop_rate=0.600038`, `mutual_defect_rate=0`
- expectation support: `8` terminal states with probability mass `1`

### `lift_avg_payoff_b_at_least_assertion_kind_broaden_after_lift_seed`

- seed: `examples/probes/ipd_asymmetric_noise_c_vs_d_smoke.json` line `28` (`ipd_asymmetric_noise_c_vs_d_smoke_v1`)
- lane: `probe_run`
- oracle: `exact_expectation` on probe `ipd_asymmetric_noise_c_vs_d_smoke_v1` / matchup `always_c_vs_always_d`
- witness stats: `avg_payoff_a=0.6`, `avg_payoff_b=4.6`, `coop_rate_a=1`, `coop_rate_b=0.2`, `mutual_coop_rate=0.2`, `mutual_defect_rate=0`
- expectation support: `2` terminal states with probability mass `1`

### `lift_iid_noise_kind_broaden_after_lift_seed`

- seed: `examples/probes/scaling_prefix_stability_probe_seed.json` line `4` (`scaling_prefix_stability_probe_seed_v1`)
- lane: `probe_run`
- oracle: `exact_expectation` on probe `scaling_prefix_stability_probe_seed_v1` / matchup `random_vs_memory_one_scaling_prefix_stability_seed`
- witness stats: `avg_payoff_a=2.310283`, `avg_payoff_b=2.086795`, `coop_rate_a=0.452`, `coop_rate_b=0.496698`, `mutual_coop_rate=0.224507`, `mutual_defect_rate=0.27581`
- expectation support: `16` terminal states with probability mass `1`

### `lift_implementation_flip_noise_kind_broaden_after_lift_seed`

- seed: `examples/probes/implementation_flip_probe.json` line `3` (`implementation_flip_probe_v1`)
- lane: `probe_run`
- oracle: `exact_expectation` on probe `implementation_flip_probe_v1` / matchup `tft_vs_always_c_under_implementation_flip`
- witness stats: `avg_payoff_a=3.031594`, `avg_payoff_b=2.815969`, `coop_rate_a=0.906875`, `coop_rate_b=0.95`, `mutual_coop_rate=0.861531`, `mutual_defect_rate=0.004656`
- expectation support: `8` terminal states with probability mass `1`

### `lift_memory_one_strategy_family_broaden_after_lift_seed`

- seed: `examples/probes/noisy_adversarial_probe.json` line `30` (`noisy_extortion_chi3_v1`)
- lane: `probe_run`
- oracle: `exact_expectation` on probe `noisy_extortion_chi3_v1` / matchup `extortion_vs_always_c_noisy`
- witness stats: `avg_payoff_a=3.799924`, `avg_payoff_b=1.800114`, `coop_rate_a=0.600038`, `coop_rate_b=1`, `mutual_coop_rate=0.600038`, `mutual_defect_rate=0`
- expectation support: `8` terminal states with probability mass `1`

### `lift_scaling_prefix_stability_metamorphic_kind_broaden_after_lift_seed`

- seed: `examples/probes/scaling_prefix_stability_probe_seed.json` line `3` (`scaling_prefix_stability_probe_seed_v1`)
- lane: `metamorphic_suite`
- oracle: `exact_expectation` on probe `scaling_prefix_stability_probe_seed_v1` / matchup `random_vs_memory_one_scaling_prefix_stability_seed`
- witness stats: `avg_payoff_a=2.310283`, `avg_payoff_b=2.086795`, `coop_rate_a=0.452`, `coop_rate_b=0.496698`, `mutual_coop_rate=0.224507`, `mutual_defect_rate=0.27581`
- expectation support: `16` terminal states with probability mass `1`
- scaling-prefix witness: base `20` vs extended `60` is an exact pass here because both tasks reuse the same `match_seed`, both traces request the same first `20` rounds, and neither strategy family can exit; anchors: `crates/gr_engine/src/sim.rs:505-522`, `crates/gr_engine/src/metamorphic.rs:457-483,498-521`
- note: same-seed fixed-horizon prefix coupling is exact here because neither side can exit and both tasks replay the same per-round RNG stream prefixes

## Practical use

- while Rust is still blocked, use this card to decide whether a future external test should be asserting an exact path, an exact mean statistic, or an exact same-seed prefix property before the first Rust-capable inheritor touches `probe_run.rs` or `metamorphic_suite.rs`
- once `cargo` exists again, the highest-value follow-up is still to land the queued external tests and then compare their live outputs to the witnesses recorded here rather than reopening the full code surface first
