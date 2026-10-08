# rev0098 selection-bias audit and frontier retest

rev0098 addresses the most immediate methodological risk after rev0097: response-oracle screens can look better than they are. The cube had four post-rev0092 oracle branches attacking the same effective PSRO support, but their results lived in separate summaries. This revision adds a shared audit that treats training and selection rows as screens, holdout rows as evidence, and confirmation as the only admission path.

## Inputs

The audit reads the compact score tables from:

- rev0094 finite-catalog second-oracle stress;
- rev0095 gameplay MAP-Elites generator;
- rev0096 frozen rev0023 MLP oracle;
- rev0097 rollout-searched information-state learned response.

All four branches target the rev0092 admitted response, `oracle_map_08_60_mixed_threats_counter_wall`, after rev0094 effective-support pruning.

## Cross-oracle selection finding

Across the four branches, the audit sees 190 score rows and 19 candidates with both screen and holdout evidence. No branch clears the declared holdout lower-bound response threshold.

The largest within-candidate selection-to-holdout optimism occurs in the learned-response branch:

```text
candidate: learned_1_02_d1_m1_60_jace_heavy_counter_mid
selection mean: 0.7500
holdout mean:   0.28125
optimism gap:   0.46875
```

The largest branch-level screen-to-best-holdout gap is also learned-response:

```text
best screen mean:  0.8750
best holdout mean: 0.4375
gap:               0.4375
```

The gameplay MAP-Elites branch remains the best holdout branch from the inherited evidence, with mean 0.5625, but its lower bound is only 0.4207 and therefore does not justify confirmation.

## Common-target frontier retest

rev0098 then retests the best holdout challenger from each branch against the same admitted response, using one common retest configuration:

```text
life totals: 20 and 40
reps: 12
games per candidate: 96
max decisions: 700
total game rows: 480
truncations: 0
```

The retest result is stricter than the earlier per-branch point estimates:

```text
admitted self-control mean: 0.53125, CI [0.4309, 0.6316]
best challenger: learned_response_rev0097, mean 0.44792, CI [0.3479, 0.5479]
MAP-Elites challenger: mean 0.38542, CI [0.2875, 0.4833]
finite-catalog challenger: mean 0.33333, CI [0.2385, 0.4281]
frozen-MLP challenger: mean 0.06250, CI [0.0138, 0.1112]
```

No challenger has a confidence lower bound above 0.5. No population admission and no strategic promotion occur.

## Method consequence

The immediate priority should shift from “add another oracle family” to “improve oracle sample efficiency and admission discipline.” In particular:

1. Candidate screens should report selection-to-holdout optimism by default.
2. Every future PSRO round should include a common-target retest of branch winners before confirmation.
3. Learned/evolutionary generators need larger or sequentially valid screening budgets; tiny screens are useful for exploration but too optimistic for admission.
4. The current admitted response remains the empirical target to beat, not a promoted strategic answer.

## Files

- `src/muc5/oracle_selection_audit.py`
- `scripts/run_rev0098_selection_audit.py`
- `tests/test_rev0098_oracle_selection_audit.py`
- `data/rev0098_oracle_selection_audit_summary.json`
- `data/rev0098_oracle_selection_branch_summary.csv`
- `data/rev0098_oracle_selection_candidate_pairs.csv`
- `data/rev0098_frontier_retest_scores.csv`
- `data/rev0098_frontier_retest_games.csv`

Note: this is the winner's-curse audit for response-oracle screens.
