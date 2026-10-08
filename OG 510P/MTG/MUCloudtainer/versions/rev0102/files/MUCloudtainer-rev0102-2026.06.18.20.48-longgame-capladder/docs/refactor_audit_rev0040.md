# rev0040 refactor/audit notes

## New modules

```text
src/muc5/action_hybrid_selector.py
src/muc5/action_hybrid_compare.py
```

`action_hybrid_selector.py` isolates branch-budget selection logic from branch rollout collection. This prevents the counterfactual collector from becoming a pile of one-off selector rules.

`action_hybrid_compare.py` mirrors the matched comparison pattern from rev0039 but adds a third method. The collector branches the union of all three methods' selected action sets, then evaluates each selector against the same branch outcomes.

## Audit intent

The audit checks that:

```text
three methods are present for every sampled situation
branch outcomes are C++ shadow-checked
no branch truncations occurred
hybrid selector outputs remain legal and budgeted
required rev0040 docs/scripts/tests exist
```

## No promotion

No ranker or policy is promoted in rev0040. The hybrid selector is an offline label-budget tool.
