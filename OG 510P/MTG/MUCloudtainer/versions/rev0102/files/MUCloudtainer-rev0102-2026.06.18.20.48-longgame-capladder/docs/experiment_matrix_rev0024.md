# rev0024 experiment matrix

New axis added:

```text
mulligan_agent_type:
  deterministic_rule
  pseudo_oracle_seeded_linear_ranker
```

Current learned-mulligan panel:

```text
shell: fjace_code
  deck: forty_force_jace_pressure
  pilot: code_jace_lock_rev0013
  mulligans: keep, band, business, learned

shell: overlord_threat
  deck: forty_overlord_impending
  pilot: threat_rush
  mulligans: keep, band, business, learned

shell: wall_counter
  deck: sixty_counterwall_jace
  pilot: counter_happy
  mulligans: keep, band, business, learned
```

Evaluation dimensions:

```text
life totals: 20, 40
starting players: 0, 1
all ordered strategy pairs
public DecisionFrame gameplay
promotion gate
statistical gate
replay gate
batched C++ trace gate
```

Generated table:

```text
12 strategies x 12 strategies x 2 life totals x 2 starting-player settings
= 576 games
```
