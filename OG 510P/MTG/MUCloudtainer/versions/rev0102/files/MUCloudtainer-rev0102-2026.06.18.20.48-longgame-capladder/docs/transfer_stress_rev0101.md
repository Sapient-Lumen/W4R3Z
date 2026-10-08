# rev0101 transfer stress — OOD panel for admitted PSRO response

rev0101 asks whether the current admitted PSRO response still looks strong outside the original eight-incumbent ecology that rev0100 tested.

Target:

```text
oracle_map_08_60_mixed_threats_counter_wall
25 Island / 21 Counterspell / 4 Force of Will / 5 Jace / 5 Overlord
pilot: infostate_counter_guard
mulligan: mulligan_outcome_ranker_rev0027
```

## Why this revision exists

rev0100 produced a clean confidence floor against the original eight incumbents. That was useful but scoped: the eight incumbents are no longer the whole attack surface. Since rev0094-rev0098, the cube has generated branch-frontier challengers, learned candidates, degenerate deck shapes, and counter-control axes that were not in the original population.

The risk was that the admitted response would look dominant only because the test population had become too familiar.

## What changed

Added:

- `src/muc5/transfer_stress.py`
- `scripts/run_rev0101_transfer_stress.py`
- `tests/test_rev0101_transfer_stress.py`
- fixed OOD panel catalog, game rows, pair estimates, family summaries, symmetry rows, self-control rows, and truncation-rescue rows.

The panel has 13 nonduplicate opponents:

- 4 branch-frontier candidates from rev0094-rev0098;
- 3 degenerate threat-density stressors;
- 1 Force-heavy pressure stressor;
- 5 counter-control / Jace-control stressors.

Each OOD pair uses 160 balanced rows: two life totals × 20 reps × two physical orientations × two starting-player roles. The self-control diagnostic is separate.

## Result

The admitted response survives all panel opponents in mean, but the OOD audit does **not** clear a confidence floor.

```text
OOD opponents:                 13
OOD game rows:                 2,080
self-control rows:             160
weakest OOD mean:              0.528125
weakest OOD CI lower:          0.4507726356760219
weakest opponent:              ood_counter_jace40
truncations:                   1
truncation rescue cap:         1,600 decisions
rescue remaining truncations:  1
```

The weakest axis is not a fast Overlord deck. It is a 40-card no-Overlord counter/Jace control deck:

```text
ood_counter_jace40
15 Island / 20 Counterspell / 0 Force of Will / 5 Jace / 0 Overlord
pilot: infostate_counter_guard
mulligan: land_band_business
```

That opponent also produced the one persistent nonterminal cap hit. Raising the cap from 1,400 to 1,600 decisions did not resolve the same seed. This is a measurement finding, not just a runtime nuisance: hard counter-control mirrors can create long or unresolved games in exactly the area where the admitted response is weakest.

## Interpretation

rev0101 weakens the story in a useful way. The admitted response remains the current target to beat, but its rev0100 confidence-floor result should be read as **fixed-incumbent evidence**, not broad transfer evidence.

The branch-frontier subset is reassuring: its weakest lower bound is above 0.5. The open axes are counter-control/Jace-control and high mixed-threat density. Future oracles should target those axes directly rather than spending more budget on branch winners already shown to be weak.

This is not a strategic promotion. It is a transfer/falsification audit that narrows the next attack surface.
