# rev0017 priority reconsideration

Current priority order:

```text
1. Expand C++ transition microcases, especially stack resolution and choice continuations.
2. Add C++ differential coverage for Overlord trigger discard and Jace +2 / Brainstorm choices.
3. Use meta-rank and statistical gates to select population slices worth deeper evaluation.
4. Add a small action-feature imitation/ranker only after payoff/replay gates stay stable.
5. Delay full C++ rollout engine until transition coverage is much broader.
```

## Why not full C++ engine now?

The Python engine still changes as we discover edge cases. A full C++ port would create two drifting rules engines. The staged plan is safer:

```text
numeric probes → legal menu → deterministic transitions → stack/choice transitions → random rollout kernel → full tournament core
```

rev0017 completes the first deterministic-transition slice.

## What looks newly valuable?

Meta-rank is now useful enough to keep. Mean score and lower-confidence-bound standings answer “who scored well?” Meta-rank asks “who has population mass under pairwise replacement?” Those can disagree, and that disagreement is exactly the kind of thing worth investigating in a tiny metagame.
