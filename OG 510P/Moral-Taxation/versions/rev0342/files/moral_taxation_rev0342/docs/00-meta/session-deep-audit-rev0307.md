# Session deep audit — rev0307

Focus: public-finance-core memo compactness without deleting substantive ladders.

## What was risky

After rev0301 through rev0306, the archive had concrete accountability profiles, compressed live axes, and compact accountability capsules. The next risk was duplicated route-local prose: public-finance-core memos still maintained local anti-pattern lists and recommendation-change lists even though `anti_pattern` and `review_trigger` are now controlled cube axes with audit gates.

## What changed

Rev0307 rewrites public-finance `Anti-patterns` sections into `Failure-mode capsule` sections and `What would change the recommendation` sections into `Recalibration trigger capsule` sections. The new capsules name the route's cube axes and preserve source continuity, while leaving option scans, ladders, default tables, and provisional recommendations in place.

## Audit/refactor performed

`tools/audit_prose_bloat.py` now has a public-finance family gate: public-finance-core route memos cannot reintroduce legacy anti-pattern or change-trigger headings, and the family must stay under the compactness ceiling recorded in `cube-index.json`.

## Remaining risk

The next bloat surface is not the public-finance failure/trigger taxonomy. It is the long option-scan/provisional-recommendation scaffold in the largest legal-enforcement, tax-administration, labor/care, and controller-AI memos. Those should be pruned by family and by route semantics, not with a global rewrite.
