# Should we compare enumerative, evolutionary, neural, and hybrid constructors?

Yes. MUC-5 is small enough that comparison is one of the cleanest things about it.

## Why construction is special here

There are only five card-count variables, and deck size is either 40 or 60.

```text
40-card construction count = C(44, 4) = 135,751
60-card construction count = C(64, 4) = 635,376
total = 771,127
```

This means deck construction can be enumerated. That is unusual for a card-game ML environment and gives us a baseline most projects do not have.

## The methods to compare

### 1. Enumerative

Definition:

```text
Evaluate all deck vectors, or a filtered/stratified subset, under one or more pilot policies.
```

Why it matters:

```text
- ground truth-ish baseline for construction
- exposes global deck-space geometry
- lets us produce heatmaps and Pareto frontiers
- gives labels for learned constructors
```

Limitations:

```text
- only as good as the pilot used during evaluation
- expensive once pilot/search is slow
- can overfit to one opponent pool
```

### 2. Evolutionary

Definition:

```text
Population of deck+pilot genomes -> simulated games -> selection -> mutation/crossover -> new population
```

Why it matters:

```text
- natural for deck counts
- easy to keep a bot personality zoo
- robust to non-differentiable game outcomes
- can co-adapt construction and play style
```

Limitations:

```text
- noisy fitness estimates
- can collapse into local metagame quirks
- needs opponent-pool discipline
```

### 3. Neural

Definition:

```text
A network maps observation + legal action mask to policy/value, trained from self-play, imitation, PPO-like RL, Deep CFR/NFSP-like imperfect-information learning, or generated labels.
```

Why it matters:

```text
- learns hidden state valuation and action timing
- can generalize across deck vectors
- can produce a reusable position evaluator
- can later support MCTS/search rollouts
```

Limitations:

```text
- more machinery than the first engine needs
- action masks are mandatory
- hidden-information training is trickier than perfect-information AlphaZero
```

### 4. Hybrid

Definition:

```text
Any combination of enumeration/search/evolution/neural value or policy.
```

Examples:

```text
- enumerate decks, but use neural value for fast evaluation
- evolutionary deck search, but learned masked policy for pilot
- MCTS or determinized search using a neural value leaf evaluator
- use enumerated deck results to train a constructor prior
- Deep CFR-ish regret learner for pilot, evolutionary constructor above it
```

Why it matters:

```text
Hybrid is probably where MUC-5 gets strongest, because construction is small but piloting is sequential, stochastic, and hidden-information.
```

## Comparison metrics

```text
match win rate
confidence interval / uncertainty
sample efficiency: games needed to find strong decks
exploitability proxy: performance against diverse bot zoo
robustness across 40-vs-60, play/draw, open/closed decklists
pilot dependence: deck ranking changes under different pilots
human judgment: does the bot feel strategically real?
strategy diversity: does it find more than one viable school?
```

## First comparison plan

The baby version should not train a big net. It should compare:

```text
A. random deck sampling
B. stratified enumeration by land/blue/threat bands
C. simple evolutionary search over deck vectors
D. neural surrogate regressor trained to predict deck fitness after partial enumeration
E. hybrid active learner: sample decks where the surrogate is uncertain or optimistic
```

This lets us learn the construction landscape before piloting is strong.
