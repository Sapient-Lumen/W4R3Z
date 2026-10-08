# source_edit_reverse_dep_fanout

A locally private source edit still causes broader reverse-dependency rebuilds than a maintainer expects.

This scenario exists to keep the crate aligned with the upstream “relink don't rebuild” motivation.
The bundle must preserve two truths at once:

1. reverse dependencies really did rebuild;
2. the crate still cannot prove from stable surface data that the edit changed the public interface.

So the right 0.1 answer is a conservative bundle with `public_interface_change_possible` or `manual_review_required` rather than a fake proof chain.
