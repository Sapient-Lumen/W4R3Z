# Scenario — GitHub release note import floats instead of pinning exact release

This scenario captures a maintainer who imports a nearby GitHub release surface, but the fetch path uses a floating alias rather than a release-pinned anchor.

The fixture should prove that:
- source lineage matters independently of hazard authority,
- a floating `latest` page is not the same thing as a version-pinned release note,
- and the pack should keep the note advisory/manual-review-only until the release pair is pinned tightly enough.
