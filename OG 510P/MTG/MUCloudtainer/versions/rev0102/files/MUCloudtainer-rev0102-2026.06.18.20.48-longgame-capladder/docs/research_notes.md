# Research Notes for rev0002

rev0002 research focused on two things:

1. how to shape the simulator so learning code can attach cleanly;
2. what online precedents matter for hidden-information card-game learning.

## Game-environment API shape

OpenSpiel is the main conceptual reference for general game research infrastructure. It supports reinforcement learning and search/planning across sequential and simultaneous games, perfect and imperfect information games, and multi-agent settings.

Project implication:

```text
MUC-5 should be a game environment, not a bot script.
```

That means reproducible states, legal actions, observations, transition functions, and logs should be first-class objects.

PettingZoo's AEC API is the closest Python API-shape reference for a sequential two-player environment. Its docs explicitly discuss action masks for marking valid and invalid actions.

Project implication:

```text
MUC-5 should expose observation + legal action mask from the beginning.
```

That matches the core project principle: the referee determines legality; ML ranks legal options.

## Card-game RL precedents

RLCard is directly relevant because it is an RL toolkit for card games and explicitly frames its goal as bridging reinforcement learning and imperfect-information games.

Project implication:

```text
MUC-5 should keep hidden information explicit and avoid leaking opponent hand/library into normal observations.
```

Deep CFR remains relevant because CFR is a major family for imperfect-information games, and Deep CFR uses neural networks to approximate CFR behavior in large games.

Project implication:

```text
MUC-5 can eventually support a CFR-ish branch, but only after legal-action/state transitions are stable.
```

## Exact card/rule sources used for rev0002

The five-card rules were checked against online card/rule references:

- Force of Will: alternative cost can pay 1 life and exile a blue card rather than pay mana cost; counters target spell.
- Jace, the Mind Sculptor: four loyalty abilities, including +2 top-card decision, 0 Brainstorm, -1 bounce creature, and -12 library/hand effect.
- Overlord of the Floodpits: impending 4 for `1UU`, flying 5/3, and enter/attack draw-two-discard-one.
- Impending: if cast for impending, the spell is still cast and can be countered; when it resolves it enters with time counters and is not a creature until the last is removed.
- Planeswalker loyalty abilities: can be activated at sorcery timing and only once per permanent per turn.

## Design decisions from the research

### 1. Do not implement generic Magic

The relevant precedent is not “build a universal card engine.” It is “build a stable closed-world research environment.” MUC-5 is tiny enough that every card can have executable logic.

### 2. Keep legality and strategy separate

PettingZoo-style masks and OpenSpiel-style game abstractions both push toward the same split:

```text
engine: legal actions + transitions
learner: action ranking + value estimation
```

### 3. Prioritize imperfect-information compatibility

Even when early pilots are random or heuristic, the state representation should already separate:

```text
true state
player observation
public information
private hand/library
```

This prevents future rewrites when we add belief sampling, information-set search, or CFR-ish learners.

### 4. Use probes before simulation is trusted

The full construction space is small enough to enumerate. Exact probability probes let us compare construction methods before matchup simulation is strategically meaningful.

### 5. Keep logs from the start

The older MUC plan aimed toward self-play logs, human review, and later transcript/theory models. rev0002's engine log is primitive, but it starts the trail.

## Links consulted

- OpenSpiel GitHub and paper: https://github.com/google-deepmind/open_spiel and https://arxiv.org/abs/1908.09453
- PettingZoo AEC and action masking docs: https://pettingzoo.farama.org/api/aec/ and https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- RLCard GitHub and paper: https://github.com/datamllab/rlcard and https://arxiv.org/abs/1910.04376
- Deep CFR: https://arxiv.org/abs/1811.00164
- Force of Will card text: https://scryfall.com/search?as=text&q=%2B%2Bo%3A%22counter+target+spell.%22
- Jace search/rules references: https://scryfall.com/search?q=%2B%2B%21%22jace%2C+the+mind+sculptor%22
- Overlord of the Floodpits: https://mtg.wtf/card/dsk/373/Overlord-of-the-Floodpits
- Overlord official Gatherer page: https://gatherer.wizards.com/DSK/en-us/399/overlord-of-the-floodpits

## rev0006 research note: mulligan as pregame policy

The London mulligan creates a compact imperfect-information-adjacent decision surface: repeated seven-card looks followed by bottom choices. In MUC-5, it directly interacts with Island density, Force pitch density, threat density, deck size, and starting life. This makes mulligan policy a useful benchmark before full pilot learning.

Near-term learning candidates:

```text
contextual bandit over keep/take
supervised hand-value model from rollout outcomes
small action-masked policy over keep/take/bottom
joint constructor + mulligan + pilot population evaluation
```

Do not add more mulligan rules yet. One rule system with multiple policies is enough.

## rev0007 online research additions

The external gametable is aligned with three research directions:

1. PettingZoo-style sequential environment/action-mask interfaces.
2. OpenSpiel-style game environment plus algorithms/evaluation framing for imperfect-information games.
3. Code-space / programmatic response-oracle work, where LLMs generate interpretable policy code instead of opaque neural policies.

For MUC-5, the immediate implication is to keep the table thin and legal-action-driven, then use transcripts and payoff tables to evaluate either learned policies or generated code policies.
