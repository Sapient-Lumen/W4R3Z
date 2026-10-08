# Track-header CSV size refactor audit

**Track:** Shared / Release engineering / Size budget
**Status:** v857 generated audit

The track-header CSV now carries actionable failure rows only; the JSON/Markdown audit retains total numbered-doc counts. This preserves the release-gate invariant without spending size budget on duplicate all-success listings.
