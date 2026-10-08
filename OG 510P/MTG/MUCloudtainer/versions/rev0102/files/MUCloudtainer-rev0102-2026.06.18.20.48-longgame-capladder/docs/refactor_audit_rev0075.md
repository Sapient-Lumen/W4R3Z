# rev0075 refactor audit

rev0075 made two small but high-leverage refactors because both could distort promotion accounting.

## 1. CSV-safe gate booleans

`summary_population_precision_gate` previously counted passed cells with `bool(row.get("gate_passed"))`.  That is safe for live Python booleans but unsafe after a CSV round trip, because the string `"False"` is truthy.

The new `population_gate_bool` parser treats `"False"`, `"0"`, `"no"`, empty strings, and unknown text as false.  The new test `test_gate_bool_does_not_treat_false_csv_strings_as_passed` protects the failure mode.

## 2. Context normalization before population grouping

The first stratum-challenge run exposed a grouping bug: pooled old CSV rows used `starting_life="40"`, while fresh in-memory summary rows used `starting_life=40`.  The post-stress gate therefore produced six rows instead of three.

`population_frontier` now normalizes numeric context axes such as `starting_life`, `target_deck_size`, and `opponent_deck_size` before both cell construction and weighted aggregation.  The new regression test verifies that string/int `starting_life` rows merge into one complete population cell.

## 3. Reused core C++ sampler

`run_rev0070_population_precision.py` no longer carries its own copy of the sampled-prepared-rollout helper.  It imports `sample_prepared_cpp_shadow_rollout` from `src/muc5/cpp_rollout.py`, reducing divergence between heavy population scripts.

## Remaining risk

The targeted strata are no longer underpowered under the rev0075 gate, but one cell still has a high point floor and a low conservative LCB.  The next substantive move is not another registry; it is either more seed-disjoint games for `counter60_vs_threat40` at life 40, or a new adversarial threat column that directly attacks the guarded counter's apparent strengths.
