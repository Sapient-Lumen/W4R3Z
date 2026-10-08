# Baby experiment matrix

## Phase 0: deck-space geometry, no gameplay

Questions:

```text
How many decklists exist?
What land fractions are possible?
How many decks have plausible Force support?
How many decks have at least one threat?
How much does 40 vs 60 change consistency bands?
```

Artifacts:

```text
data/deck_space_all.csv.gz
data/deck_space_summary.json
```

## Phase 1: opening-hand/mulligan Monte Carlo

Before full gameplay, we can test construction with direct probability probes.

Metrics:

```text
P(opening hand has >= 2 Island)
P(opening hand has Counterspell + UU by turn 2)
P(opening hand has Force + pitch card)
P(has Jace + 4 mana by turn 4)
P(has Overlord impending + 3 mana by turn 3)
P(has threat by turn N)
P(self-deck pressure under repeated Overlord/Jace draw)
```

This is the first place enumeration, random search, evolution, neural surrogate, and hybrid active search can be compared cheaply.

## Phase 2: partial rules engine

Implement:

```text
opening hand / draw / land play
main phase casts
Counterspell / Force stack fights
Jace resolve and simple loyalty actions
Overlord resolve and enter trigger
basic combat damage
library-empty loss
```

Bots:

```text
RandomLegalBot
CastThreatBot
CounterEverythingBot
ForceGreedyBot
JaceMaxBot
```

## Phase 3: construction comparison under weak pilots

Compare constructors under fixed weak pilots:

```text
enumerated top-K by simulated win rate
random search
evolutionary deck search
neural surrogate deck scorer
hybrid active search
```

Goal: discover whether method choice matters before pilot intelligence dominates.

## Phase 4: deck + pilot co-adaptation

Each candidate contains:

```text
deck vector
pilot weights or policy checkpoint
```

Run co-evolution / self-play leagues.

Track:

```text
metagame cycling
40-card vs 60-card prevalence
Force density shifts
Jace/Overlord ratios
counter density
human exploitability
```

## Phase 5: hidden-information learning

Add open vs closed decklist flags.

Potential methods:

```text
determinized MCTS
NFSP-style average/best-response split
Deep CFR-ish regret approximation
masked PPO/A2C
policy/value imitation from search
```

## Phase 6: theory generator

Generate empirical claims from logs:

```text
Decks with X-Y Islands and Z Force density win N% against the current field.
On turn 3, impending Overlord into 2 open Islands is good/bad under conditions C.
Jace Brainstorm vs fateseal inflection appears at library/hand state S.
```

## rev0004 life-total/context matrix

Add two axes:

```text
actual_starting_life ∈ {20, 40}
construction_life_knowledge ∈ {known, unknown_uniform_20_40}
```

Current seed-deck arena:

```text
8 seed decks × 8 seed decks × 2 start-player swaps × 4 life/context configs = 512 games
```

Future constructor experiment:

```text
known constructor chooses deck for 20
known constructor chooses deck for 40
unknown constructor chooses one robust deck for mixed 20/40
all decks cross-play under both actual life totals
```

Primary measurements:

```text
win rate by actual life
robust average across life totals
known-context advantage over robust-context choice
rate of max_decisions timeouts at 20 vs 40
Force pitch count and life-loss frequency once logs expose event counters
```

## rev0005 additional experiment axes

### Mulligan policy as evaluation condition, not yet a tournament dial

```text
none / keep_always
land_band
land_band_business
```

For now, use these to test whether construction conclusions are sensitive to opening-hand handling. Do not cross every method against every mulligan policy until payoff tables show the axis matters.

### Action-space stress audit

For every stronger pilot generation, run:

```bash
python scripts/audit_action_space.py
```

Record:

```text
max legal action count
p99 legal action count
max by frame
max by pending choice kind
card-conservation pass/fail
```

This protects the slot-action interface from silent blowups.

## rev0006 update: mulligan policy as a real axis

Mulligans are promoted from simulator option to experimental axis. Keep the rule system fixed to London mulligan, but compare policy quality:

```text
keep_always
land_band
land_band_business
future learned/contextual mulligan policies
```

The current cross-axis arena is:

```text
starting_life ∈ {20, 40}
mulligan_policy ∈ {keep_always, land_band, land_band_business}
seed_deck_pair ∈ 8 × 8
starting_player alternated
```

`data/rev0006_mulligan_life_arena_summary.json` stores the first 768-game plumbing run.

## rev0007 additions

Controller/pilot can now be a saved external table seat:

```text
controller ∈ {random, heuristic, counter_happy, threat_rush, external, future_neural, future_code_policy}
```

This means a future experiment can include moves chosen by the assistant or by generated Python policies in the same payoff matrix as normal agents.

## rev0008 matrix extension

Payoff-table evaluation is now a first-class experiment artifact.

Current smoke grid:

```text
8 strategy bundles × 8 strategy bundles × 2 life totals × 2 starting players × 1 rep = 256 games
```

A strategy bundle currently means:

```text
deck construction + London mulligan policy + pilot/controller
```

This gives enumerative/evolutionary/neural/hybrid constructors a shared output surface: add or compare bundles by their payoff rows.
