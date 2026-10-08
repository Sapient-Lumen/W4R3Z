# rev0043 experiment matrix additions

| Axis | rev0043 value |
|---|---|
| Frame source | public hard-frame queue |
| Branch selector | hybrid vote + diversity + ranker prior |
| Branch allocation | online adaptive/racing |
| Base rollouts | 1 per selected legal action |
| Extra budget | up to 4 per situation in archived run |
| Hidden-state access | offline labeler only |
| C++ role | transition shadow checker |
| Policy promotion | none |

Future comparison rows should include:

```text
hard_frame_score_version
branch_selector_version
allocation_version
base_rollouts_per_action
max_extra_rollouts_per_situation
decisive_per_100_rollouts
branch_truncation_rate
cpp_mismatch_count
```
