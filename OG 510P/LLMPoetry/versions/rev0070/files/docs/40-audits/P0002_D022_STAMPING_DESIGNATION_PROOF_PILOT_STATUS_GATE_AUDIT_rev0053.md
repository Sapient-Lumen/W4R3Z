# P0002-D022 stamping/designation reanchor and proof/pilot status gate audit — rev0053

Current head: `P0002-D022` — **Stamping or Designation**.  
Previous head: `P0002-D021`.  
Verdict on previous head: `revise_not_promote`.

## Literary move

D021 removed D020's datum lesson but softened into rain/weather metaphor. D022 cuts rain from the body and reanchors to the NOAA table phrase `Stamping or Designation`: the source gives the same primary benchmark both a stamped mark (`NO 7 1975`) and a designation (`851 8750 TIDAL 7`).

The new bet is not the weather crossing the disk. It is whether a dry official name can let a table call the same disk from two waters without becoming the water it names.

This is not a promotion. D022 can fail by becoming a tidy naming conceit.

## Audit/refactor

The concrete drift fault was compact and practical: `registries/proof_status.json` and `registries/pilot_queue.json` could carry fresh current-head fields while their top-level `status`, `current_summary`, or `note` still named older drafts. In rev0052, `proof_status.status` still contained meters-above wording, and `pilot_queue.status` still pointed to an older D017-era pilot posture.

`tools/check_surface_freshness.py` now blocks that class of drift by checking proof-status and pilot-queue top-level prose fields against the actual current head.

These are orientation/provenance guards, not poem-quality claims.

## Current non-claim

P0002-D022 is same-turn unjudged; not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA value claim.
