# rev0046 experiment matrix addition

| Axis | rev0046 setting |
|---|---|
| Frame selector | hard_screen, margin_screen, yield_screen |
| Matched candidate pool | yes |
| Branching | union of selected situations |
| Branch allocation | online adaptive/racing |
| Training target | decisive labels per rollout |
| Hidden-state use | offline branch referee only |
| C++ role | transition shadow checker |
| Gameplay policy promoted | no |

Future runs should compare yield-screen selected frames against larger branch budgets and then evaluate whether a ranker trained from those labels improves in promoted, nontruncated payoff tables.
