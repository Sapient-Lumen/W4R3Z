# latest migration guide head is operational but not citation ready

This scenario proves the pack should distinguish **operational guidance head** from **citation-ready frozen head**.

The maintainer has one current migration-guide page that people can read right now, but the exact release-pair anchor is still floating through a docs `latest` route instead of a version/tag/content-pinned locator.

Expected outcome:
- the guide may remain the **operational head**,
- the **citation head** stays missing,
- and the pack emits an explicit freeze warning instead of pretending the latest docs page is already a citation-ready source.
