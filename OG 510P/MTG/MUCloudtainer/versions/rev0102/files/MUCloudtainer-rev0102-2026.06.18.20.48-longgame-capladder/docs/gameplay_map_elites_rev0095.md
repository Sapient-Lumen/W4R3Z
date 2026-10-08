# rev0095 gameplay-driven MAP-Elites oracle

rev0095 turns the next PSRO method priority into executable machinery. The old MAP-Elites archive was useful as a source of diverse proposals, but its cell quality was static deck-construction score. rev0095 keeps the illumination idea and replaces the quality function with actual rollout value against the current effective PSRO support.

## Target

The target is the rev0092 admitted response as isolated by rev0094 effective-support pruning:

```text
oracle_map_08_60_mixed_threats_counter_wall
included mass: 0.999920007199352
omitted mass / max score error from pruning: 0.00007999280064796555
```

The search asks whether a bounded generator can find a response to that target before the project moves to more expensive neural or full repeated-PSRO experiments.

## Method

`src/muc5/gameplay_map_elites.py` defines a small strategy-space illumination layer:

- deck descriptors from the existing MAP-Elites grid;
- pilot-family descriptors for counter, closure, pressure, surge, and balanced templates;
- mulligan-family descriptors;
- deterministic candidate de-duplication against the expanded PSRO population;
- archive replacement by actual mixture rollout mean, with truncation penalty;
- parent selection from gameplay elites rather than from static construction priors.

`scripts/run_rev0095_gameplay_map_elites.py` runs three bounded selection generations. Generation zero remeasures seed and static-catalog proposals under current gameplay. Later generations mutate elite decks, add random plausible decks, assign bounded pilot templates, and retain one elite per descriptor cell. The top archive elites then receive seed-disjoint holdout evaluation.

## Result

The run evaluated 44 nonduplicate candidates and filled 26 gameplay archive cells. It produced 592 balanced game rows with zero truncations and no seed overlap between selection and holdout stages.

The best holdout point estimate was:

```text
gme_g01_103_40_mixed_threats_counter_mid_business_pressure
40 cards: 16 Island, 12 Counterspell, 0 Force of Will, 7 Jace, 5 Overlord
pilot: infostate_threat_pressure
mulligan: land_band_business
holdout mean vs admitted response: 0.5625 over 48 rows
normal 95% interval: [0.4207, 0.7043]
```

That is only a point-estimate lead. Its lower confidence bound is below the challenge threshold of `0.520079992800648`, so rev0095 confirms no new response and promotes no strategy; it is not a promotion gate.

## Interpretation

This is real forward movement despite the negative gate result. The cube now has a gameplay-driven generative response oracle that can be repeated, budgeted, and compared against future neural/search oracles. The result also makes the admitted rev0092 response look less trivially vulnerable: a generator found an interesting 40-card pressure challenger, but did not confirm it.

The next high-substance step is either to run a second, larger generative PSRO round with preregistered budgets or to add the first small neural response oracle under the same selection/holdout/confirmation discipline.
