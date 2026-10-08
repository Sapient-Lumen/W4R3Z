# rev0033 refactor and audit notes

New code:

```text
src/muc5/action_counterfactual.py
scripts/run_rev0033_action_counterfactual.py
tests/test_rev0033_action_counterfactual.py
```

Updated code:

```text
src/muc5/ranker_policy.py
src/muc5/public_agents.py
src/muc5/strategy_sets.py
cpp/muc5_transition_micro.cpp
scripts/audit_cube.py
```

Main refactors:

```text
1. Added an offline gameplay-action counterfactual collector.
2. Added JSON-backed counterfactual linear ranker loader/factory aliases.
3. Added a strategy-bundle panel for counterfactual ranker evaluation.
4. Fixed the C++ combat/Jace sentinel collision.
5. Added a directed C++ parity test for the sentinel case.
```

Audit requirements for rev0033:

```text
action-counterfactual candidate rows exist
branch rollout rows exist
branch collection C++ transitions have zero skipped events and zero mismatches
counterfactual ranker model JSON exists
counterfactual ranker can load as a public agent
payoff evaluation passed promotion and statistical gates
replay samples passed
C++ shadow rollout has zero skipped events and zero mismatches
required docs/scripts/tests exist
```
