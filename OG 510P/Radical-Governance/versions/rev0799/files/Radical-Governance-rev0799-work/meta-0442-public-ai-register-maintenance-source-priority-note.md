# meta-0442 — Public AI register maintenance and source-priority refactor note

This release adds the public AI register maintenance docket and applied public-register case packet as the next substantive risk repair after watchlist / border automation. The point is not to celebrate more registers; it is to prevent public inventories, algorithmic transparency records, high-risk AI database rows, COTS rollups, late inventory publications, and missing rows from being used as substitutes for lifecycle state, authority, procurement, model/data/vendor lineage, monitoring, incidents, redress, and retirement evidence.

The release also tightens source-health maintenance. `generated/SOURCE_HEALTH.*` now reports manual health coverage and lists unchecked priority sources by dependent surface, so future cleanup can start with the source keys that carry the most notes, claims, and case packets instead of expanding the registry uniformly.

Operational rule: use `917`, `918`, and `generated/PUBLIC_AI_REGISTER_TESTS.*` whenever a public AI inventory or register row is cited as proof that a tool is live, paused, retired, governed, high-impact, exempt, or absent.
