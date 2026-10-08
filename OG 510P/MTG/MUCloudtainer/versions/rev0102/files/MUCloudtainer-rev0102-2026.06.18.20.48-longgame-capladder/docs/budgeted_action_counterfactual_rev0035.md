# rev0035 budgeted gameplay action counterfactuals

rev0033 and rev0034 established the right learning shape for gameplay improvement:
branch legal actions from an identical referee state, roll each branch forward,
and label the public action candidates by observed outcome.  The weakness was
that high-branching frames were skipped.  That silently biased the dataset toward
small menus.

rev0035 adds a budgeted selector.  Small legal menus are still fully branched.
Large menus can enter the label corpus through a diverse subset.

The selector always includes the behavior policy's chosen action, then attempts
to keep anchors like `PASS` and `PLAY_ISLAND`, plus one representative from broad
action families such as Force pitch choices, Jace modes, attack/block shapes, and
choice-effect variants.  Remaining slots are filled by deterministic-random
leftovers.  All rows keep the original legal-action index.

New fields in candidate and branch rows:

```text
action_count              full legal-menu size
branched_action_count     number of actions actually rolled out
branched_subset           1 if the row came from a budgeted subset
budget_reason             behavior_chosen / anchor_pass / diversity_representative / ...
```

This matters for epistemic hygiene.  A row from a budgeted subset says:

```text
among the branched candidates, this action looked best
```

It does **not** say:

```text
this action was best in the entire legal menu
```

The rev0035 model downweights subset rows slightly during fitting.  That is only
a smoke choice, not a proof.  The right long-run version should allocate more
rollouts to frames whose branch labels remain unstable or whose high-action menus
look strategically important.

## Archived smoke result

```text
sampled situations:              26
full-menu situations:            17
budgeted-path situations:         9
subset situations:                5
candidate actions:               86
branch games:                   172
branch rollouts per action:       2
branch terminal games:          172
branch truncations:               0
branch C++ checked transitions: 35104
branch C++ mismatches:            0
max full action count:           21
max branched action count:        6
```

The labels were still mostly ties in this smoke run.  Only two collection
situations were decisive by the raw summary, and the label audit saw one decisive
situation after grouping.  That is useful pushback: the selector works, but the
label budget and rollout policy are still the limiting factors.
