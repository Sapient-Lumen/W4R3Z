# rev0011 Research Notes: What Looks Worth Attempting Next

The online scan continues to point toward environment-first, population-first methods rather than a single giant neural policy.

## 1. Action masks stay central

PettingZoo's AEC API and action-masking tutorials are a good external reference: sequential turn-based games often expose valid/invalid action masks rather than teaching legality through penalties.  MUC-5's DecisionFrame interface is the local version of that pattern.

Sources:
- https://pettingzoo.farama.org/api/aec/
- https://pettingzoo.farama.org/tutorials/custom_environment/3-action-masking/

## 2. OpenSpiel remains the north-star library, not necessarily a dependency

OpenSpiel describes itself as a collection of environments and algorithms for reinforcement learning and search/planning in games, including perfect/imperfect information games.  Its algorithm list includes CFR, NFSP, PSRO, AlphaZero, and Alpha-Rank-style evaluation.  We do not need to import it yet; the design lesson is that the game environment and algorithm experiments should stay cleanly separated.

Sources:
- https://github.com/google-deepmind/open_spiel
- https://openspiel.readthedocs.io/en/latest/algorithms.html

## 3. Payoff tables make Alpha-Rank / PSRO natural later

OpenSpiel's Alpha-Rank docs note that games can be specified through payoff tables or heuristic payoff tables.  This exactly matches our strategy-bundle payoff table direction:

```text
deck + mulligan policy + pilot -> payoff table -> population analysis
```

PSRO surveys frame the method as a scalable game-reasoning framework that grows a useful subset of strategies via response oracles.  That is probably a better fit for MUC-5 than chasing one champion bot too early.

Sources:
- https://openspiel.readthedocs.io/en/latest/alpha_rank.html
- https://arxiv.org/html/2403.02227v1

## 4. CFR / Deep CFR are still later, not immediate

CFR is the classic imperfect-information-game tool.  Deep CFR approximates CFR with neural networks to avoid manual abstraction in large games.  MUC-5 is small in card vocabulary but still large in hidden libraries/hands, so CFR-like ideas remain interesting.  The near-term issue is not algorithm sophistication; it is simulator trust and information-set representation.

Sources:
- https://poker.cs.ualberta.ca/publications/NIPS07-cfr.pdf
- https://proceedings.mlr.press/v97/brown19b.html

## 5. Reward hacking is not optional to think about

Recent reward-hacking/specification-gaming work reinforces the basic lesson: when systems optimize a proxy, they may satisfy the literal objective without doing the intended thing.  For MUC-5, the immediate proxy risks are much smaller and more concrete: truncation score, speed score, open-state leakage, and construction-context leakage.

Sources:
- https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/
- https://arxiv.org/html/2507.05619v1

## New question priorities

The generated question bank is in:

```text
data/rev0011_question_bank.json
```

Top three questions after rev0011:

1. Can every surprising result be replayed exactly?
2. Can agents exploit truncation/draw-half scoring?
3. Does population analysis reveal multiple strategic species rather than a single champion?
