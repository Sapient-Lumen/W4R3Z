# Probability Probes

`src/muc5/probability.py` adds exact hypergeometric probes for construction screening.

These are not matchup evaluations. They are cheap constructor diagnostics.

## Probe metrics

For a deck vector, `deck_probe(deck)` returns:

```text
p_keepable_2_to_5_islands
p_force_plus_pitch_open7
p_counterspell_online_turn2_play
p_overlord_impending_turn3_play
p_jace_turn4_play
p_overlord_full_turn5_play
crude_probe_score
```

The turn windows assume the player is on the play in a two-player game:

```text
opening hand = 7 cards
turn 2 = 8 cards seen
turn 3 = 9 cards seen
turn 4 = 10 cards seen
turn 5 = 11 cards seen
```

The first player skips the first draw.

## Why exact probes now

The full raw deck space is only 771,127 deck vectors. That is small enough to enumerate. Exact probes let us cheaply rank every deck before we have game outcomes.

This gives later methods something to beat:

```text
enumerative/probe baseline
  vs evolutionary constructor
  vs neural constructor
  vs hybrid constructor
```

## Generated data

`scripts/build_probe_tables.py` enumerates the raw deck space, applies a plausibility filter, and writes:

```text
data/probe_rankings_top100.csv
data/probe_summary.json
```

The rev0002 plausibility filter keeps decks with:

```text
35% <= Island fraction <= 75%
at least one interaction card
at least one threat card
at least 12 blue nonland cards
```

This filter is intentionally not strategic. It only removes obvious non-games.

## Seed deck example

The seed deck used in smoke tests is:

```text
40 cards: 24 Island, 6 Counterspell, 4 Force, 3 Jace, 3 Overlord
```

At rev0002 creation its crude probe score was:

```text
0.6661702922375548
```

That number is now part of the audit to catch accidental probability drift.
