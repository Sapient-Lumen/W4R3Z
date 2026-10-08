# rev0010 simulator readiness

## Short answer

The simulator is **already working for automated beta play**. It can start MUC-5 games, run London-mulligan baselines, expose hidden-information-correct DecisionFrames, accept legal macro-actions, play full automated games, write payoff tables, and pass invariant/leakage checks.

It is **not yet ready for strong learning or tournament conclusions**. The remaining gap is not “make it run.” The remaining gap is “make it hard for wrong rules, hidden leaks, truncation incentives, or aggregation shortcuts to contaminate learning results.”

## Readiness levels

| Level | Status | Meaning |
|---|---|---|
| A. Automated-play smoke simulator | green | Random/scripted/public agents can play end-to-end games with invariants checked. |
| B. Learning-loop beta simulator | yellow | The DecisionFrame/action-mask boundary exists, but the scenario suite should expand before trusting learned results. |
| C. Research-claim tournament simulator | red | Payoff tables need higher reps, truncation policy stress tests, and frozen simplification notes before strategic claims. |

## Evidence generated in this revision

```text
rules scenarios: 5/5 passed
public-frame fuzz games: 300
fuzz decisions: 63667
fuzz failures: 0
card-conservation checks: 63857
observation-shape checks: 1538243
public DecisionFrame decisions/sec: 59047.86
```

## The honest answer to “how far away?”

Working enough to play: **yes, now**.

Working enough to start tiny training experiments: **almost**. The public DecisionFrame path and action mask are the correct learning boundary, but every new learning method should run behind rev0010-style scenario/fuzz/audit gates.

Working enough to believe a claim like “deck X is better than deck Y”: **not yet**. That needs more payoff reps, no-silent-truncation conventions, and a larger rules-scenario suite.

## Remaining simulator risks

- London mulligans are agent-facing, but the exact simultaneous/turn-order public-declaration nuance is still simplified.
- Overlord triggers are now sequential, but more multi-trigger regression cases should be added.
- Jace -1 now targets Overlord creature state, but more Jace top-card and Brainstorm putback scenarios should be audited.
- Random fuzzing finds broad crashes/leaks; it does not prove rules correctness.
- Public DecisionFrame speed is adequate, but observation construction is still a likely hotspot before compiled tools matter.
