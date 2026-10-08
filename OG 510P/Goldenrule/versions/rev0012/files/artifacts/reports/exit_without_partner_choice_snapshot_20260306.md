# Exit Without Partner Choice Snapshot (2026-03-06)

Method:
- evaluated all `243` deterministic `memory_one_exit` policies in `ipd_core_v1`
- scorecard opponents: extortion, self-play, Always-Cooperate, Generous TFT
- coarse screen with fixed seeds, then high-rep reevaluation of finalists

Main finding:
- In this deterministic exit-enabled family, a near-fair balanced candidate exists, but it achieves that only by defecting on the first move and then using exit as a trap.
- Once we impose a minimal nice-start filter, the best balanced candidate no longer uses exit and fairness stays negative.
- This is a local warning that `memory_one_exit` without rematching/outside-option mechanics is not the same as partner choice.

Best fairness-only candidate:
- code: `DCCEC`
- uses exit: `true`
- fairness vs extortion: 2.500000
- self-play payoff: 2.960000
- exploit gain vs Always-Cooperate: 2.500000

Best balanced candidate (self-play >= 2.5, exploit gain <= 0.1):
- code: `DCECC`
- uses exit: `true`
- fairness vs extortion: 0.000016
- self-play payoff: 2.960000
- exploit gain vs Always-Cooperate: 0.100000

Best balanced nice-start candidate (same thresholds, plus first move = cooperate):
- code: `CCDDD`
- uses exit: `false`
- fairness vs extortion: -0.045458
- self-play payoff: 3.000000
- exploit gain vs Always-Cooperate: 0.000000

Balanced frontier witnesses:

| code | uses exit | fairness vs extortion | self-play | exploit gain vs allC |
|---|---:|---:|---:|---:|
| `DCECC` | true | 0.000016 | 2.960000 | 0.100000 |
| `CCDDD` | false | -0.045458 | 3.000000 | 0.000000 |
| `CCDED` | true | -0.073184 | 3.000000 | 0.000000 |
| `CCDCD` | false | -0.099832 | 3.000000 | 0.000000 |
| `CCDDE` | true | -0.393605 | 3.000000 | 0.000000 |

Interpretation:
- If a policy gets fairness by defecting first and cashing out, the scorecard should reject it as non-Golden-Rule-like.
- The nice-start filter is a minimal proxy for Golden-Rule shape. Under that filter, exit does not rescue the deterministic frontier.
- That points back to the missing **world mechanic** (leave-and-rematch / outside option), not merely the action alphabet.

Immediate implementor implication:
- Do not treat `memory_one_exit` as a substitute for partner choice. Add one explicit rematch / outside-option world before expanding exit-heavy search.
