# Scenario — virtualized list recycles node identity and breaks diff

A scrolling virtualized list reuses widget instances aggressively.
The authoring-side semantic tree still has the right broad shape, but row node ids churn between snapshots.

The doctor should not pretend that a name/role diff is trustworthy when the underlying identity linkage collapsed.
The right output is a **baseline-drift report** that elevates node-identity churn and keeps part of the review in `manual-review-required` territory.
