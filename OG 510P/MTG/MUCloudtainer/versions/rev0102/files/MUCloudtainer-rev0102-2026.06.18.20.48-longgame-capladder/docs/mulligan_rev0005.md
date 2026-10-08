# rev0005 Mulligan Scaffold

## Decision

Add a London-mulligan scaffold, but do **not** yet make mulligan style a tournament dial.

MUC-5 construction depends heavily on opening-hand quality. If we evaluate all decks with no mulligans forever, land-count and Force/pitch density conclusions can be distorted. The official London mulligan keeps the choice among seven-card hands while reducing final hand size by one card for each mulligan: after deciding to keep, the player bottoms a number of cards equal to mulligans taken.

Reference: https://magic.wizards.com/en/news/announcements/london-mulligan-2019-06-03

## Implementation

New file:

```text
src/muc5/mulligan.py
```

Supported baseline policies:

```text
keep_always
land_band
land_band_business
```

`keep_always` preserves previous behavior. `land_band` keeps hands with 2-5 Islands, with a max-mulligan cutoff. `land_band_business` also asks for at least one nonland spell. These are intentionally crude; they exist to expose the rule seam and produce data.

`start_game(...)`, `play_random_game(...)`, `play_agent_game(...)`, and `MUC5SlotEnv(...)` now accept a `mulligan_policy` argument. Gameplay observations expose public mulligan metadata through:

```text
public_self.mulligans_taken
public_opponent.mulligans_taken
self_mulligans_taken feature
opp_mulligans_taken feature
```

## Why this is not a strategic claim

The current bottom-card chooser is deterministic and simple:

```text
bottom excess Islands first, but try to keep two
then Overlord
then Jace
then Force
then Counterspell
then final Islands if forced
```

That is not optimal. It is an auditable placeholder. A future pilot should learn both keep/mulligan and bottom choices.

## Pushback

Mulligans can become a rabbit hole. MUC-5 already has deck size, life total, construction-known/unknown context, and pilot policy. Adding many mulligan policies as a tournament dial would multiply data demands. For now, use mulligans as a simulator capability and audit axis, not as a full metagame condition.

## Generated artifact

```text
data/rev0005_mulligan_probe.csv
data/rev0005_mulligan_probe_summary.json
```

Summary from rev0005 seed-deck probes, 1,000 samples per deck/policy:

```text
keep_always:          mean p(any mulligan) = 0.000000, mean kept size = 7.000000
land_band:            mean p(any mulligan) = 0.110875, mean kept size = 6.876625
land_band_business:   mean p(any mulligan) = 0.111250, mean kept size = 6.875750
```

The business condition barely differs from land-band for the current seed decks because the seed decks already contain high nonland density.

## Future ML seam

Eventually, pregame can become an explicit decision frame:

```text
MULLIGAN_DECISION: keep or mulligan
BOTTOM_DECISION: choose N cards to bottom
```

That would let the same masked-action machinery handle mulligans instead of relying on deterministic policy strings.
