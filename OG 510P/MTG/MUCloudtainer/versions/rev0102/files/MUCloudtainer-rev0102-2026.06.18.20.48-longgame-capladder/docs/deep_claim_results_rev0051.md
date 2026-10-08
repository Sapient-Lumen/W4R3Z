# rev0051 results — focused terminal-clean deep claim panel

The selected targets were:

```text
code_jace60
cf34_counter_wall
cf49_fjace
```

The panel produced:

```text
games: 312
aggregate rows: 78
target pair rows: 48
max_decisions: 900
truncations: 0
replay samples: 8 / 8 passed
C++ shadow events: 89,750
C++ skipped events: 0
C++ mismatches: 0
```

All gates passed:

```text
promotion gate
statistical gate
terminal-meta gate
deep-claim gate
C++ shadow gate
replay trace gate
```

Target summaries:

```text
code_jace60
  games: 120
  mean score: 0.625
  score LCB: 0.501
  life20 score: 0.550
  life40 score: 0.700
  deep label: deep_field_signal

cf34_counter_wall
  games: 120
  mean score: 0.625
  score LCB: 0.501
  life20 score: 0.700
  life40 score: 0.550
  deep label: deep_field_signal

cf49_fjace
  games: 120
  mean score: 0.325
  score LCB: 0.201
  life20 score: 0.283
  life40 score: 0.367
  deep label: deep_watchlist
```

Interpretation:

`code_jace60` and `cf34_counter_wall` both retained positive field signals under deeper terminal-clean sampling, but each now shows a meaningful life bias.  `cf49_fjace`, previously selected because it was life-sensitive in the claim ledger, did not survive deeper sampling as a strong candidate.

This is still not final MUC theory.  The pair/life cells remain thin for matchup claims.  The revision’s value is better triage: future repetitions should probably spend more on `code_jace60` and `cf34_counter_wall` life-split matchups, and less on `cf49_fjace` unless a specific counter-meta reason appears.
