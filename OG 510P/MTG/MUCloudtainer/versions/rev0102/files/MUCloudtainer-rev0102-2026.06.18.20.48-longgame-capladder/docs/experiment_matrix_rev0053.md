# Experiment Matrix rev0053

| Axis | rev0053 setting |
|---|---|
| Card pool | Island, Counterspell, Force of Will, Jace, Overlord |
| Deck sizes | 40 / 60 as defined by strategy bundles |
| Starting life | 20 and 40 |
| Mulligans | strategy-bundle mulligan agents |
| Interface | public DecisionFrame |
| Payoff | draw-half reporting, terminal-only training convention |
| Max decisions | 900 |
| C++ status | transition shadow gate, not authoritative rollout engine |
| Replay | 8 sampled public traces |
| Evaluation focus | concrete target/opponent cells selected from rev0052 retest confluence |

rev0053 is a claim-hygiene revision.  It does not train or promote a new gameplay policy.
