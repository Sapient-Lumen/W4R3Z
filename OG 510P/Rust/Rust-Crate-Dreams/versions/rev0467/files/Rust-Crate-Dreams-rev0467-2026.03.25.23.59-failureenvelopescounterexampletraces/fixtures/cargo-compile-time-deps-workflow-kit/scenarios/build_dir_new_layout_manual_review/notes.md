# Scenario: build-dir new layout manual review

A custom wrapper or local process touches build-dir assumptions during the `-Zbuild-dir-new-layout` transition. The bundle should keep root-lane facts explicit and prefer `manual_review_required` when support for the new layout is not proven.
