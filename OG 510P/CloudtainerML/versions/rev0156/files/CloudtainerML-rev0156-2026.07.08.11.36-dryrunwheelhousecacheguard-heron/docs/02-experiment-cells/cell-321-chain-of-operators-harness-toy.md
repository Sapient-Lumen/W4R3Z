# CELL-321 — Chain-of-Operators Harness Toy

Priority: P2

Status: planned-symbolic

Question: Can explicit operator chains beat learned operator routing when the base model is frozen or tiny?

Cheap first run: Build simple operator-family toy only if operator routing remains a core lane.

Metrics: relative_error, ood_error, chain_length, cost, interpretability_score

Required baselines: direct_operator, explicit_chain, router_chain, oracle_chain

Stop condition: Drop if unrelated to performance-core architecture questions.
