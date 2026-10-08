# rev0022 ranker blends

rev0021 proved that a frozen linear action-ranker can be loaded as a public-safe policy. It did not prove that imitation alone is a good pilot. rev0022 therefore adds a small family of **ranker + readable prior** policies.

New public-agent names:

```text
ranker_blend_threat_rev0022
ranker_blend_counter_rev0022
ranker_blend_patient_rev0022
```

Each policy computes:

```text
score(action) = ranker_weight * linear_ranker_score(action)
              + profile_weight * public_profile_score(action)
```

The default profile weight is intentionally small (`0.08`). The point is not to hand-feed expert play. The point is to test whether a weak supervised action-ranker becomes more useful when nudged by an interpretable style prior.

## Leak boundary

The blend policy receives only:

```text
DecisionFrame.observation
DecisionFrame.legal_actions
```

The profile scorer also consumes only the public observation and the legal action. It never receives `GameState`, opponent hand, opponent library, or future draws.

## Why this is worth testing before bigger neural policies

The linear ranker is easy to audit, but it mostly imitates weak/readable policies. A tiny blend family gives three cheap hypotheses:

```text
H1: ranker + threat prior becomes better at closing games.
H2: ranker + counter prior becomes better in stack-heavy mirrors.
H3: ranker + patient prior becomes better in 40-life / long-game settings.
```

If all three fail under promotion/statistical/replay gates, a bigger MLP may still be useful, but the failure will tell us that imitation data quality or state features are probably the bottleneck.
