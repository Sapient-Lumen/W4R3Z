# rev0004 — Life-total dial

## Decision

MUC-5 now has exactly two supported starting life totals:

```text
20
40
```

Gameplay always knows the actual starting life total. The uncertainty dial is only for **construction**:

```text
known construction:
  constructor is told actual starting_life before choosing a deck

unknown construction:
  constructor is told possible_starting_life_totals = [20, 40]
  constructor must choose a robust deck before the actual life total is sampled/chosen
```

This is represented in code by `src/muc5/tournament.py`:

```python
ConstructionContext(known_starting_life=20)
ConstructionContext(known_starting_life=40)
ConstructionContext(known_starting_life=None, possible_starting_life_totals=(20, 40))
```

## Pushback / why this might be a bad dial

The life-total dial is interesting, but it is not automatically important in MUC-5.

The five-card universe has only one damage source: `OverlordOfTheFloodpits`, a 5-power flyer. Jace and decking are alternate long-game pressure points, and repeated Overlord triggers draw so many cards that decking may matter even when life is high.

So 40 life may not create a clean "control mirror gets slower" result. It may instead create one of these outcomes:

1. **Real construction shift.** More Force of Will and fewer pure damage clocks become correct because life is more spendable.
2. **Mostly no shift.** Jace/library pressure dominates enough that life total is a weak tournament dial.
3. **Degenerate shift.** High life creates more time for loops/timeouts or excessive draw/discard, making the heuristic arena less trustworthy.

Therefore rev0004 adds the dial as a **configuration variable and measurement axis**, not as a permanent claim about the game.

## What changed in the engine/API

`start_game`, `MUC5SlotEnv`, `play_agent_game`, and `play_random_game` now accept `starting_life`.

The observation includes:

```text
starting_life
public_self.life
public_opponent.life
```

The numeric feature encoder adds:

```text
starting_life
self_life_fraction
opp_life_fraction
```

This matters because a neural or heuristic policy should not treat 10 life the same way in 20-life and 40-life games.

## Static constructor scaffold

rev0004 adds `src/muc5/life_constructor.py` and `scripts/build_life_constructor_shortlists.py`.

This is a deliberately weak static constructor prior, not a learned constructor. It creates three named deck cohorts:

```text
known_life20
known_life40
unknown_robust
```

The current top static-prior decks are stored in:

```text
data/rev0004_life_constructor_shortlists.csv
data/rev0004_life_constructor_shortlists_summary.json
```

The scorer intentionally pushes in different directions:

```text
known_life20:
  more willing to value Overlord as a fast damage clock
  more tolerant of 40-card consistency pressure

known_life40:
  more willing to value Jace, interaction, and 60-card library cushion

unknown_robust:
  averages 20/40 static scores and penalizes over-specialization
```

This gives us something to test now while keeping the learned-constructor slot open.

## Arena artifacts

`data/rev0004_life_dial_arena.csv` runs the original eight seed decks through four tournament contexts:

```text
known_life_20
known_life_40
unknown_life_actual_20
unknown_life_actual_40
```

For fixed seed decks, known-vs-unknown construction is metadata, not a real adaptive constructor yet. The summary still computes two useful rankings:

```text
known_best_by_actual_life:
  best seed deck at 20
  best seed deck at 40

robust_unknown_ranking:
  best seed deck by mean performance across 20 and 40
```

`data/rev0004_life_constructor_arena.csv` is the more construction-shaped smoke test. It takes the top four static-prior decks from the correct cohort for each context and runs those through the heuristic arena:

```text
known_life_20 uses known_life20 decks
known_life_40 uses known_life40 decks
unknown_life_actual_20 uses unknown_robust decks
unknown_life_actual_40 uses unknown_robust decks
```

This is still not strategic proof. It is a wiring test for the future constructor comparison.

## Testing questions

The dial creates clean questions:

```text
Does 40 life increase the value of Force of Will because the life payment is cheaper?
Does 40 life reduce the value of Overlord as a damage clock?
Does 40 life increase the value of Jace because games last longer?
Does a robust unknown-life constructor choose 60 cards more often than a known-20 constructor?
Does 40 life increase timeouts/max_decisions in heuristic arenas?
```

## Simplification retained

The dial does **not** require new card rules. It is only a scalar in the initial player state plus features. That makes it cheap to keep even if it later turns out to be strategically weak.


## Static constructor arena

rev0004 also includes a tiny follow-up arena over the static-prior shortlist:

```text
scripts/run_life_constructor_arena.py
data/rev0004_life_constructor_arena.csv
data/rev0004_life_constructor_arena_summary.json
```

It plays the top four decks for each construction label against one another under the appropriate life/config context. This is still not learned construction, but it is the first bridge from "static context prior" to "arena fitness."
