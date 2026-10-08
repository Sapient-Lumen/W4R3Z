# 21 — Experiment Matrix (v0.19)

You do not know slice distribution; you must measure it.

## Core measurements
- time_to_ctrl distribution per agent
- ctrl_parse_rate + repair_success_rate
- truncation_rate (did outputs cut mid-packet?)
- WS churn vs progress (evidence per cursor)
- collision rate (lease violations, conflicting patches)
- discovery/random utility (how often it mattered)

## A/B experiments
- Budgets: default vs emergency
- Discovery: off vs controlled vs controlled+random
- Leases: none vs soft always-on vs reactive
- Voting: bounded upvotes vs sparse STAR/QV budgets
- PatchOnly frequency: never vs on collision spike

## Exploration experiments
- Explore off vs DISCOVERY-only vs DISCOVERY+RANDOM
- Log exploration win_rate (see 48_exploration_metrics_and_tuning.md)

## View budgeting experiments
- Enforce line caps only vs line+token guard (see 47_view_assembly_and_token_budgeting_contract.md)

MetaLLM-run experiments via forked threads: see 80_experiment_runner_and_ab_testing.md.
