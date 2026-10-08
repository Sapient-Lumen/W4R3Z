# rev0045 — matched margin-screen vs hard-screen queue audit

rev0044 added a tiny public-feature margin screen for choosing which hard public decision frames deserve expensive branch rollouts. rev0045 makes the next audit stricter: compare that margin-screen queue against the older public hard-frame queue on the same candidate pool.

The comparison is deliberately matched:

```text
same public behavior games
  -> same public hard-frame candidate pool
  -> hard-screen selects top K
  -> margin-screen selects top K
  -> branch only the union of selected frames
  -> score both queues from the same branch outcomes
```

That isolates queue quality from branch rollout noise. It also keeps hidden information isolated: public agents and screeners see only `DecisionFrame` observations and legal actions; the hidden true state is used only inside the offline counterfactual labeler/referee after the public frame has already been selected.

## Smoke result

Archived summary: `data/rev0045_margin_match_summary.json`.

```text
behavior games:             24
behavior decisions:       4,717
choice frames seen:       2,142
candidate pool rows:         34
hard selected:               10
margin selected:             10
union selected:              15
overlap selected:             5
hard-only selected:           5
margin-only selected:         5
branch games:               131
branch truncations:           0
C++ checked transitions: 17,432
C++ skipped transitions:      0
C++ mismatches:               0
```

Method-level smoke comparison:

```text
hard-screen decisive labels:   1 / 86 branch rollouts
margin-screen decisive labels: 1 / 90 branch rollouts
hard-screen mean margin:       0.1000
margin-screen mean margin:     0.0333
```

## Interpretation

This is a useful negative/neutral result. In this smoke run, the rev0044 margin screen did not improve label yield over the simpler hard-frame queue. It selected higher-action frames on average, but those frames were not more decisive under the current branch/racing budget.

That does not invalidate margin screening. It says the current target/model is too weak or the features are insufficient. The next queueing model should likely optimize for **observed decisive labels per rollout**, not predicted raw margin alone.

## New files

```text
src/muc5/action_margin_compare.py
scripts/run_rev0045_margin_match_queue.py
tests/test_rev0045_margin_match.py

data/rev0045_margin_match_pool.csv
data/rev0045_margin_match_hard_rank.csv
data/rev0045_margin_match_margin_rank.csv
data/rev0045_margin_match_selected.csv
data/rev0045_margin_match_methods.csv
data/rev0045_margin_match_method_summary.csv
data/rev0045_margin_match_candidates.csv
data/rev0045_margin_match_branch_games.csv
data/rev0045_margin_match_allocations.csv
data/rev0045_margin_match_votes.csv
data/rev0045_margin_match_cpp_transitions.csv
data/rev0045_margin_match_situation_summary.csv
data/rev0045_margin_match_summary.json
```
