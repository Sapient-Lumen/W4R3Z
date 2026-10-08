# MUC-5 Spec

> **rev0091 status note:** for the current policy-facing information-state contract, see `docs/CURRENT_SPEC.md`. This historical file is no longer the normative source for hidden-information semantics.
> **rev0068 status note:** this file is a historical rev0002-through-rev0010 specification, not a complete current normative spec. See `docs/current_spec_conformance_plan_rev0068.md` for the consolidation plan.

## Card universe

Only five cards exist:

```text
Island
Counterspell
ForceOfWill
JaceTheMindSculptor
OverlordOfTheFloodpits
```

A deck is a five-count vector:

```text
(size, island, counterspell, force, jace, overlord)
```

where `size` is either 40 or 60 and the five card counts sum to `size`. There is no four-of rule.

## Rev0002 game assumptions

The rev0002 engine implements a compressed but card-specific referee:

- two players;
- starting life 20;
- opening hand size 7;
- first player skips the first draw;
- one Island may be played during the active player's main frame;
- Islands are represented as tapped/untapped counts, not individual objects;
- Counterspell and Force of Will are the only instants;
- stack decisions are only exposed when a spell can be countered;
- Jace is represented as a single optional planeswalker with loyalty;
- Overlords are aggregated by state: ready, sick, tapped, or impending counters;
- hidden hands and libraries remain private to the owning player.

## Referee versus learner

The engine does not try to teach MUC theory. It only answers:

```text
Given this state, which macro-actions are legal?
```

The learner eventually answers:

```text
Which legal macro-action is best?
```

That keeps the project pointed at ML: deck construction, timing, Force pitch valuation, Jace valuation, Overlord mode choice, and counter-war behavior are supposed to be learned.

## Legal macro-action families

rev0002 uses the following compact families:

```text
PASS
PLAY_ISLAND
CAST(card, mode, target_index, pitch_card)
ACTIVATE_JACE(mode, target)
ATTACK(to_player, to_jace)
BLOCK(blocks_player, blocks_jace)
CHOOSE(kind, parameters)
```

Nested choices are explicit decision frames rather than hidden automation:

```text
Overlord discard
Jace Brainstorm putbacks
Jace +2 top/bottom choice
Jace legend keep-old/keep-new choice
cleanup discard
Force pitch-card choice
```

## Simplifications intentionally preserved

These simplifications are project features, not bugs:

- no generic Magic parser;
- no layer system;
- no arbitrary target system beyond the five cards;
- no manual Island tapping;
- no continuous-effect engine except Overlord's creature/noncreature impending state;
- no priority prompts when neither player can cast a counterspell.

## Strategic things not simplified away

These should remain real because they define the project:

- hidden hand/library information;
- exact Force of Will pitch identity and life payment;
- Counterspell/Force stack fights;
- Jace Brainstorm putback order;
- Jace +2 top/bottom information asymmetry;
- Jace ultimate as library pressure;
- Overlord full-cost versus impending mode;
- Overlord enter/attack draw-two-discard-one;
- 40-card consistency versus 60-card endurance;
- no four-of construction limit.

## Known rev0002 incompleteness

The rev0002 engine is suitable for tests and random-game smoke trajectories, not yet for trusted strategic results.

Known areas for later audit:

- response priority is compressed after spells and counterspells;
- Overlords are aggregated, which is safe only while all Overlords remain indistinguishable;
- Jace +2 currently exposes a choice frame, but a future version should represent who knows the top card more carefully;
- Jace Brainstorm currently uses indexed hand choices and should later receive a cleaner combinatorial choice generator;
- no mulligan system yet;
- no draw/play evaluation split yet.

## rev0004 addition: life total dial

Supported starting life totals are now exactly:

```text
20
40
```

Gameplay observations always include the actual `starting_life` and current public life totals. Construction may be run in a known-life context or an unknown-life context:

```text
known_life_20
known_life_40
unknown_life_actual_20
unknown_life_actual_40
```

The unknown-life constructor is not gameplay-blind. It simply commits to a deck before it knows which of the two life totals the match will use.

## rev0005 pregame and audit additions

MUC-5 now has an optional London-mulligan scaffold. This does not add new cards or change legal deck construction. It adds a pregame procedure and public metadata:

```text
mulligans_taken
opening hand after bottoming
bottomed cards in mulligan log
```

The current baseline policies are deterministic placeholders:

```text
keep_always
land_band
land_band_business
```

Future learned agents should replace these with explicit pregame decision frames.

rev0005 also adds a five-card conservation invariant. The invariant is part of the spec now: after any legal action, the total number of each actual MUC-5 card owned by each player should equal that player's registered deck counts, accounting for stack spells, pending combat attackers, and Jace legend-rule limbo.

## rev0006 addendum: mulligan agency

Mulligans are now treated as pregame legal-action decisions, not only as a deterministic setup helper.

The pregame action grammar is:

```text
MULLIGAN_KEEP
MULLIGAN_TAKE
MULLIGAN_BOTTOM(card)
```

`start_game` accepts `mulligan_agents=(agent0, agent1)`. Each agent receives a `MulliganObservation` and a legal action list. This mirrors the core gameplay contract: the referee generates legal choices and the model/agent chooses among them.

The engine records both a per-player summary in `state.mulligan_log` and event-level choices in `state.mulligan_decision_log`.

## rev0007: assistant-facing gametable

rev0007 adds an external-seat table protocol. The MUC-5 referee still produces exact legal macro-actions. The table can now stop at an external player's decision frame, render public/hidden-information-correct state, list numbered legal actions, accept an action index, apply it, and auto-play named agents until the next external frame.

New agent names:

```text
random
heuristic
counter_happy
threat_rush
external
```

The external table does not yet expose interactive mulligan menus; it starts after explicit rule-agent London mulligans have been applied and logged.

## rev0008 addition: payoff/speed seam

rev0008 does not change the five-card rules. It adds two infrastructure seams:

```text
strategy bundle = deck + mulligan policy + pilot
payoff table = ordered bundle matchups across life totals and starting players
```

The simulator also exposes a trusted hot path:

```python
apply_action(..., validate=False)
```

for actions already emitted by `legal_actions(state)`, while retaining validation as the default for external callers.


## rev0010 note: simulator readiness

rev0010 fixes two correctness shortcuts: multiple Overlord attack triggers now resolve sequentially, and Jace -1 chooses a specific Overlord creature state rather than an internal default. It also adds directed rules scenarios, public DecisionFrame fuzzing, and a readiness report distinguishing automated beta play from learning-grade and tournament-claim readiness.
