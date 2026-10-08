# Manual review required under conflicting signals

Simulates a lane where adoption/popularity signals, docs quality, and task/interop fit point in different directions.
The pathfinder crate should stop at reviewable ambiguity rather than pretending the ranking engine solved a political choice.

Why this matters:
- some of the most damaging curation tools are the ones that always emit a winner even when the honest output is “two plausible stacks remain”;
- historical Rust platform discussions already showed that global blessing can create real downsides.

What this scenario should force:
- an explicit `manual_review_required` verdict
- manual-review reasons such as `conflicting_teaching_vs_production_defaults` or `adoption_signal_disagrees_with_lockin_cost`
- a summary that names the unresolved trade-off instead of hiding it behind a numeric rank
