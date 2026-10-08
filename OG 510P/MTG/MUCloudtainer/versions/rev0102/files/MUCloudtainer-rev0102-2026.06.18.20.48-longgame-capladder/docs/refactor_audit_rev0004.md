# rev0004 refactor/audit notes

## Refactor performed

Added `src/muc5/tournament.py` as the home for tournament-level configuration:

```text
LIFE_TOTAL_OPTIONS
ConstructionContext
TournamentConfig
known_life_config
unknown_life_config
standard_life_configs
```

This keeps life/context policy out of the card rules and mostly out of the engine. The engine accepts `starting_life` directly for convenience, and accepts a `TournamentConfig` via the forward-compatible `match_config` parameter.

## Naming cleanup

A temporary duplicate config module was removed during the rev0004 refactor. The project now has this split:

```text
lifedial.py            simple regime summaries and life-derived facts
life_constructor.py    static constructor prior for known/unknown life cohorts
tournament.py          tournament configuration contract
```

This avoids two different `ConstructionContext` definitions.

## Engine/API changes audited

The following functions/classes now carry `starting_life`:

```text
start_game(..., starting_life=20)
play_random_game(..., starting_life=20)
play_agent_game(..., starting_life=20)
MUC5SlotEnv(..., starting_life=20)
```

The feature encoder now includes:

```text
starting_life
self_life_fraction
opp_life_fraction
```

The heuristic agent's Force-of-Will pitch scoring and combat scoring were lightly refactored to use life fraction. It is still a baseline heuristic, not a strategic claim.

## Audit checks added

`scripts/audit_cube.py` now checks:

```text
life options are exactly (20, 40)
known/unknown construction context contract
40-life env exposes starting_life in raw observation and feature vector
rev0004 seed life arena exists with 512 rows
rev0004 static constructor shortlists exist with 75 rows
rev0004 static constructor arena exists with 128 rows
rev0004-required files exist
```

## Known limitations

`ConstructionContext` is not yet consumed by a learned constructor. rev0004 has a static-prior constructor scaffold so we can wire up the comparison before training or evolution exists.

The heuristic arena is not strategically authoritative. It is a regression/plumbing arena until stronger agents exist.

## Suggested next refactor

The engine currently stores Overlords as aggregate counts. That is fine for identical 5/3 flyers, but we should add an invariant audit before the game grows:

```text
overlord_ready + overlord_sick + overlord_tapped + impending_* + graveyard/exile/hand/library counts
should conserve total Overlords unless Jace/library/hand movement explains a zone transition
```

This would catch future bugs in bounce, combat, impending awakening, and draw/discard transitions.


The audit also checks the 128-row static constructor arena artifact.
