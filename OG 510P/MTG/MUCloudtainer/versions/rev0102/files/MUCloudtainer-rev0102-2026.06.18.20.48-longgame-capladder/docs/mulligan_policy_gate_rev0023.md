# rev0023 — mulligan policy gate

Mulligans are now treated as a strategy-bundle component, not a quiet simulator default.

The new gate evaluates the same deck/pilot shells under all three current mulligan policies:

```text
keep_always
land_band
land_band_business
```

This matters because a deck/pilot can look strong because it gets better opening-hand treatment, not because the pilot plays better or the construction is better.

## Same-shell comparison

The script groups results by shell:

```text
fjace_code
overlord_threat
wall_counter
```

and compares the policy suffix:

```text
keep
band
business
```

Generated summary:

```text
data/rev0023_mulligan_policy_gate_same_shell.csv
```

This is not a learned mulligan policy yet. It is a guardrail: future learned or evolved mulligan agents must be visible in payoff rows and promotion gates.

## Generated artifacts

```text
data/rev0023_mulligan_policy_gate_games.csv
data/rev0023_mulligan_policy_gate_aggregate.csv
data/rev0023_mulligan_policy_gate_standings.csv
data/rev0023_mulligan_policy_gate_same_shell.csv
data/rev0023_mulligan_policy_gate_pairwise.csv
data/rev0023_mulligan_policy_gate_stat_standings.csv
data/rev0023_mulligan_policy_gate_replay_traces.jsonl
data/rev0023_mulligan_policy_gate_cpp_trace_summary.json
data/rev0023_mulligan_policy_gate_summary.json
```

## Next mulligan step

A learned mulligan policy should use the same legal pregame action surface already exposed by `MulliganObservation` and `MULLIGAN_KEEP` / `MULLIGAN_TAKE` / `MULLIGAN_BOTTOM(card)`. It should be evaluated as:

```text
deck + mulligan agent + gameplay pilot
```

not merely as a hidden parameter to the game engine.
