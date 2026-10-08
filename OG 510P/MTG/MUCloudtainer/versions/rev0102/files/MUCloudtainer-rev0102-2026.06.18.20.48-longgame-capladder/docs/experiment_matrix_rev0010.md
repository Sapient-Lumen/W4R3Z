# rev0010 experiment matrix update

The simulator now has explicit readiness gates.

| Experiment family | Current status | Gate before trusting results |
|---|---|---|
| Random/heuristic smoke games | usable | rev0010 scenario + fuzz + audit pass |
| Payoff table smoke | usable as plumbing | label as smoke; report truncations |
| Evolutionary constructor | next plausible target | DecisionFrame-only pilot or audited trusted baseline |
| Learned policy/value | not started | DecisionFrame/SlotEnv only; no full GameState |
| PSRO/population loop | scaffolded conceptually | payoff reps + best-response generator |
| CFR/NFSP/ReBeL-style branch | later | clearer imperfect-information abstraction and exploitability proxy |
| Human/assistant gametable | usable after mulligan stage | add optional external mulligan decisions later |

## New axis to record

Every result table should include:

```text
simulator_revision
audit_gate
rules_scenario_version
fuzz_seed_base
max_decisions
truncation_policy
```

That makes old rows legible when the simulator improves.
