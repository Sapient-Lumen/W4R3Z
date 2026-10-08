# Meta 0443 — Subnational AI local-pilot repair and matrix-registry refactor

This revision adds the subnational / local digital-government AI case lane and keeps the work concrete: municipal algorithmic-tool reports, state ADS inventories, state AI statutes, court and school guidance, public-records retention, procurement, vendor features, local pilots, affected-person routes, and no accountability by local pilot.

The maintenance change is a small build refactor: recent common test matrices now have a registry-driven builder path, so future case packets do not require another copy-pasted build step and lint list. The older individual builders remain usable, but `build_all` can now build the common matrices through one registry surface.

Deferred: the next substantive gap should be a non-English / Global South official-source packet, preferably one where source-health and translation risk are as important as doctrine.
