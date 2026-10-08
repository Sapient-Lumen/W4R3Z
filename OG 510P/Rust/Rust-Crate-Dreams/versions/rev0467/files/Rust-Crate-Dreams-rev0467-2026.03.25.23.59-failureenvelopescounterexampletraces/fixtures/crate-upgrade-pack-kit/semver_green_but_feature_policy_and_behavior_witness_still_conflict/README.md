# Scenario — SemVer/public-API stays green, but feature policy and behavior witness still conflict

This scenario captures a release where public API diffs remain compatible, yet the default-feature/runtime lane changed and the checked recipe still forces human review.

The fixture should prove that:
- SemVer/public-API evidence is a slice, not the whole migration story,
- feature-policy and behavior witnesses can remain live at the same time,
- and the honest output can still be `manual_review_required` rather than a synthetic “all clear”.
