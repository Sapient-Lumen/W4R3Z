# rev0027 mulligan outcome results

Key artifacts:

```text
data/rev0027_mulligan_outcome_keep_training.csv
data/rev0027_mulligan_outcome_bottom_training.csv
data/rev0027_mulligan_outcome_ranker_model.json
data/rev0027_mulligan_outcome_games.csv
data/rev0027_mulligan_outcome_same_shell.csv
data/rev0027_mulligan_outcome_summary.json
```

Same-shell smoke means:

```text
fjace_code:
  land_band            0.533
  keep_always          0.517
  pseudo               0.517
  land_band_business   0.500
  outcome              0.450

overlord_threat:
  land_band            0.417
  keep_always          0.408
  land_band_business   0.400
  pseudo               0.383
  outcome              0.358

wall_counter:
  pseudo               0.667
  land_band            0.650
  land_band_business   0.567
  keep_always          0.567
  outcome              0.567
```

These are smoke-scale, not theory.  The meaningful result is methodological: terminal-outcome weighted mulligan learning is now in the same audited strategy-bundle pipeline as every other policy.

The negative result is also useful: simply weighting behavior-policy mulligans by terminal outcome does not automatically beat a transparent hand-quality pseudo-oracle or even simple rule policies.
