# rev0020 experiment matrix additions

## C++ parity experiments

| Experiment | Status | Output |
|---|---:|---|
| C++ deck probability probes | done | `rev0015` |
| C++ legal menu diff | done | `rev0016` |
| C++ transition directed/sampled diff | done | `rev0017` / `rev0018` |
| C++ recorded trace checker | done | `rev0019` |
| Jace ultimate shuffle transport | done | `rev0020_cpp_trace_summary.json` |
| C++ batch transition benchmark | next | not built |
| Full C++ rollout core | later | not built |

## Learning experiments

| Experiment | Status | Output |
|---|---:|---|
| Public heuristic/code policies | done | `src/muc5/public_agents.py`, `src/muc5/code_policy.py` |
| Action feature vectors | done | `src/muc5/action_features.py` |
| Public imitation dataset | done | `rev0020_action_ranker_dataset.csv` |
| Logistic action-ranker smoke model | done | `rev0020_action_ranker_summary.json` |
| Frozen action-ranker public agent | next/later | not built |
| PPO/CFR/neural best response | later | not built |

## Evaluation experiments

| Experiment | Status | Comment |
|---|---:|---|
| Reward/truncation adversary | done | stall gate catches draw-hacking pressure |
| Statistical gate | done | refuses smoke-scale overclaiming |
| MAP-Elites candidate eval | started | candidates now reach real games |
| Meta-rank adapter | started | useful as population lens, not final truth |
