# Research notes folded into rev0003

The goal of the research pass was not to chase a single algorithm. It was to clarify which comparison axes belong in the cube while MUC-5 is still small enough to audit.

## Environment/API references

OpenSpiel is a useful north star because it explicitly targets reinforcement learning and search/planning in games, including sequential, simultaneous, perfect-information, and imperfect-information games. That reinforces the idea that MUC-5 should be a clean game environment first, not a pile of bot scripts.

PettingZoo's AEC API is relevant because MUC-5 is turn/decision sequential. PettingZoo also documents action masking as a natural way to mark valid/invalid actions rather than letting invalid actions become no-ops.

RLCard is relevant because it focuses specifically on reinforcement learning in card games and frames itself around imperfect-information games with large state/action spaces and sparse rewards.

## Algorithms worth comparing later

### Enumerative construction

Because the construction space is only 771,127 raw decks, enumeration remains the baseline. Search methods need to beat it on sample efficiency, adaptation, or pilot/deck co-training, not on raw possibility coverage.

### Evolutionary construction / pilot populations

Evolutionary and population methods are attractive because the MUC-5 metagame may be non-transitive. A deck that beats Jace-heavy piles may lose to Overlord-heavy piles, and vice versa. This makes permanent policy/deck pools more useful than one champion.

### Alpha-Rank / empirical metagame ranking

OpenSpiel supports Alpha-Rank for ranking policy profiles from payoff tables / heuristic payoff tables. This is a good future match for MUC-5 once we have a pool of deck+pilot pairs and a matchup table.

### PSRO

Policy Space Response Oracles iteratively grow a policy population by adding approximate best responses. That looks like a natural later form of "constructor + pilot ecology": maintain a pool of deck/pilot agents, estimate the payoff matrix, add a new response, repeat.

### NFSP / CFR / Deep CFR

MUC-5 is imperfect-information because hands and libraries are hidden. NFSP and CFR-family methods are therefore more directly relevant than pure AlphaZero. Deep CFR is especially relevant once tabular traversal becomes impossible, though rev0003 is not there yet.

### ReBeL / search in imperfect-information games

ReBeL combines self-play RL and search for imperfect-information games. The full method is too ambitious for now, but its framing suggests a useful later split: public belief state + value/policy + search.

### AlphaZero-like imperfect-information baselines

AlphaZero-style baselines have been tested in imperfect-information games like Stratego/DarkHex and can be surprisingly strong, though not necessarily state of the art. This argues for keeping a simple AlphaZero-ish baseline in the comparison stack rather than dismissing it.

### Generic policy gradients with masking

Recent work has argued that generic policy-gradient methods may be more competitive in imperfect-information games than expected. That makes masked PPO/A2C a reasonable experimental branch once the slot/action representation is stable.

## rev0003 decision

The cube should compare construction/pilot families, but not all immediately. The recommended order is:

```text
1. legal referee + random/heuristic smoke agents
2. probe-filtered enumeration
3. heuristic-vs-heuristic arena data
4. evolutionary deck search against named pilots
5. population/meta ranking over deck+pilot pairs
6. masked neural policy baseline
7. CFR/NFSP/PSRO-style branches
```

rev0003 implements steps 1 and part of 3.

## Source URLs reviewed

- OpenSpiel documentation / repository: https://openspiel.readthedocs.io/ and https://github.com/google-deepmind/open_spiel
- PettingZoo AEC/action masking docs: https://pettingzoo.farama.org/api/aec/ and https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/
- RLCard docs / paper: https://rlcard.org/ and https://arxiv.org/abs/1910.04376
- Deep CFR: https://arxiv.org/abs/1811.00164
- NFSP: https://arxiv.org/abs/1603.01121
- ReBeL: https://arxiv.org/abs/2007.13544
- PSRO survey: https://arxiv.org/html/2403.02227
- AlphaZero-like imperfect-information baseline: https://www.frontiersin.org/articles/10.3389/frai.2023.1014561/full
- Neural Replicator Dynamics / DeepNash family context: https://arxiv.org/abs/1906.00190 and https://arxiv.org/abs/2206.15378
