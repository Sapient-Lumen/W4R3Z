# rev0008 payoff-table scaffold

rev0008 adds the first explicit population-payoff surface for MUC-5.

The strategy key is deliberately stable:

```text
strategy = deck construction + mulligan policy + pilot/controller
```

This lets later methods compare against the same table shape whether the pilot is heuristic, evolutionary, neural, CFR-like, PSRO-generated, or externally chosen through the gametable.

## New code

```text
src/muc5/payoff.py
scripts/run_rev0008_payoff_table.py
```

Important objects/functions:

```text
StrategyBundle
load_seed_decks(...)
default_strategy_bundles(...)
play_strategy_pair(...)
build_payoff_rows(...)
aggregate_payoff_rows(...)
```

## rev0008 default population

The smoke population contains eight strategy bundles. It intentionally mixes deck shapes and pilot personalities; it is not a claim about good MUC-5 play.

```text
fjace_bal          forty_force_jace_pressure           heuristic
fovr_threat        forty_overlord_impending            threat_rush
flight_counter     forty_land_light_force_comboish     counter_happy
sibig_bal          sixty_drawless_control_big          heuristic
siovr_threat       sixty_overlord_heavy                threat_rush
sicounter_counter  sixty_counterwall_jace              counter_happy
gambit_counter     forty_minimal_threat_decking_gambit counter_happy
jaceonly_bal       sixty_no_overlord_jace_only         heuristic
```

Every bundle currently uses `land_band` London mulligan policy. That is a limitation, not a principle. The next table should vary mulligan policy as part of the bundle.

## Generated artifacts

```text
data/rev0008_payoff_games.csv
  256 game rows

data/rev0008_payoff_aggregate.csv
  128 aggregate strategy0 × strategy1 × life-total rows

data/rev0008_payoff_summary.json
  compact metadata and outcome summary
```

The current smoke grid is:

```text
8 strategies × 8 strategies × 2 life totals × 2 starting-player settings × 1 rep = 256 games
```

## Current smoke output

From `data/rev0008_payoff_summary.json`:

```text
games: 256
aggregate rows: 128
life totals: 20, 40
mean decisions: 273.8945
```

Outcome reasons in this heuristic-only smoke table:

```text
player_0_attempted_to_draw_from_empty_library: 97
player_1_attempted_to_draw_from_empty_library: 96
player_0_life_total_zero_or_less: 32
player_1_life_total_zero_or_less: 29
max_decisions_reached: 2
```

This is a useful warning: MUC-5 is currently ending a lot of games by decking. That may be real for a five-card Jace/Overlord environment, or it may reflect weak pilots overusing draw/Brainstorm/Overlord triggers. Do not treat this table as strategic truth yet.

## Why this matters

This is the bridge to PSRO-style work. PSRO needs a population of policies, a way to evaluate pairwise payoffs, and an oracle that can add new best responses. rev0008 gives us the first crude version of the population/payoff pieces. The oracle can later be:

```text
evolved deck constructor
learned pilot
CFR-ish best response
assistant-written code policy
human/external-seat policy trace
```

## Known limitations

- Only one repetition per ordered pair/start/life in the generated artifact.
- The pilots are still hand-coded heuristics.
- All bundles use the same `land_band` mulligan policy.
- The table currently uses deterministic seed scheduling, not confidence intervals.
- The engine logs are disabled during payoff generation for speed, so per-game `log_events` is zero.

## Next useful changes

1. Add `mulligan_policy` variation to the bundle grid.
2. Add Wilson/binomial confidence intervals for payoff means.
3. Add a `best_response_candidate` script that samples/evolves decks against a target mixture.
4. Add exploitability-ish smoke metrics for small populations.
5. Keep payoff generation reproducible and cheap before trying neural training.
