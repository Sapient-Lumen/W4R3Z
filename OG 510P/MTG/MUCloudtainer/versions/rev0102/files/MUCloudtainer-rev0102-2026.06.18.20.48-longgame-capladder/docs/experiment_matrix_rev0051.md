# rev0051 experiment matrix

| Axis | rev0051 setting |
|---|---|
| Strategy population | rev0049/rev0050 terminal-clean yield panel |
| Focus targets | claim-ledger robust/life-sensitive rows |
| Target count | 3 |
| Pair schedule | every ordered pair where either seat is a target |
| Life totals | 20, 40 |
| Starting player | 0, 1 |
| Reps | 2 |
| Max decisions | 900 |
| Gameplay interface | public DecisionFrame |
| Mulligan interface | strategy-bundle mulligan agent/policy |
| Reward convention | draw-half reporting, terminal-only training |
| Promotion use | diagnostic/claim triage, no new policy promotion |
| C++ use | transition shadow check on live rollout traffic |

Primary outputs:

```text
rev0051_deep_claim_target_summary.csv
rev0051_deep_claim_target_pairs.csv
rev0051_deep_claim_claim_ledger.csv
rev0051_deep_claim_summary.json
```
