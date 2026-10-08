# rev0027 experiment matrix update

New axis:

```text
mulligan policy:
  keep_always
  land_band
  land_band_business
  mulligan_ranker_rev0024
  mulligan_outcome_ranker_rev0027
```

New evaluation panel:

```text
3 fixed deck/pilot shells
5 mulligan policies per shell
20 and 40 life
both starting-player settings
900 public payoff games
```

Shells:

```text
fjace_code
  forty_force_jace_pressure + code_jace_lock_rev0013

overlord_threat
  forty_overlord_impending + threat_rush

wall_counter
  sixty_counterwall_jace + counter_happy
```

Core question:

```text
Can terminal-outcome weighted pregame learning improve over deterministic rule mulligans and pseudo-oracle hand-quality mulligans?
```

Smoke answer:

```text
not yet reliably
```

This points toward paired counterfactual mulligan probes rather than more imitation-only training.
