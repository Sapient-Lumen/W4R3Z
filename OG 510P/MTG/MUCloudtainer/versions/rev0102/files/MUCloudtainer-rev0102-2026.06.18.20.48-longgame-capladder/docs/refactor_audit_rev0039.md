# rev0039 refactor/audit note

New module:

```text
src/muc5/action_screen_compare.py
```

The module separates three concerns that were tangled across earlier action-counterfactual collectors:

```text
screen public-policy votes
select branch candidates
compare label selectors on shared branch outcomes
```

New audit checks verify:

```text
rev0039 output row counts match the JSON summary
sampled situations all came from disagreement frames
branch truncations are zero
C++ transition shadow has zero skipped events and zero mismatches
method rows exist for both unscreened_budget and screened_vote_budget
```

No gameplay engine semantics changed in this revision.
