# rev0094 PSRO stress panel

rev0094 attacks the highest-risk loose end after rev0092 and rev0093: the first admitted PSRO response looked dominant in a low-resolution expanded matrix, but the project had not yet asked whether a second oracle could immediately exploit it.

## Why this matters

A PSRO expansion is useful only if the population keeps being attacked. The rev0092 admitted response should not become a de facto answer just because it received nearly all mass in a small expanded game. rev0094 therefore treats it as the effective sole opponent of the expanded meta-strategy and runs a second finite-oracle stress panel.

The expanded solver has tiny fictitious-play residue on the old eight strategies. rev0094 prunes that residue with an explicit bound:

```text
included support: oracle_map_08_60_mixed_threats_counter_wall
included weight: 0.999920007199352
omitted weight: 0.00007999280064796555
maximum possible weighted-score error from pruning: 0.00007999280064796555
```

Because all scores lie in `[0, 1]`, the omitted normalized mass bounds the change in any weighted response estimate.

## What ran

`python scripts/run_rev0094_psro_stress.py`

The panel evaluates:

- 8 existing population strategies as pure-response controls;
- 7 information-state upgrades after excluding the already admitted response;
- 8 static MAP-Elites proposals after excluding the already admitted response.

It uses disjoint deterministic seed namespaces for:

- challenge selection: 368 game rows;
- top-four holdout: 192 game rows;
- incumbent stress: 384 game rows.

Total: **944** balanced game rows, zero truncations.

## Result

No nonduplicate static-catalog challenger clears the holdout screen. The best holdout challenger is `oracle_map_04_40_mixed_threats_counter_wall`:

```text
mean score vs admitted response: 0.3958333333333333
95% interval: [0.2560222166610398, 0.5356444500056268]
```

The incumbent pure-response stress panel also finds no incumbent with mean score above 0.5 against the admitted response. The admitted response's weakest mean result is against `pub_threat60_pressure`:

```text
admitted mean score vs pub_threat60_pressure: 0.5833333333333333
admitted 95% lower bound vs pub_threat60_pressure: 0.4423850085470937
```

That is not a promotion claim. The confidence lower bound is below 0.5. The correct interpretation is narrower: the admitted response survived a second finite-catalog stress panel and should now be challenged by a genuinely generative oracle.

## Refactor delivered

`src/muc5/psro_catalog.py` now owns:

- the frozen response-population reconstruction;
- information-state upgrade candidates;
- MAP-Elites proposal reconstruction;
- incumbent pure-response controls;
- duplicate signature detection.

This prevents future PSRO, evolutionary, and neural runners from copying the same fragile strategy-order and candidate-construction literals.

## Files

- `src/muc5/psro.py`
- `src/muc5/psro_catalog.py`
- `scripts/run_rev0094_psro_stress.py`
- `tests/test_rev0094_psro_stress.py`
- `data/rev0094_psro_stress_summary.json`
- `data/rev0094_psro_stress_audit.json`
- `data/rev0094_psro_challenge_games.csv`
- `data/rev0094_psro_challenge_scores.csv`
- `data/rev0094_psro_challenge_catalog.csv`
- `data/rev0094_psro_incumbent_stress.csv`
