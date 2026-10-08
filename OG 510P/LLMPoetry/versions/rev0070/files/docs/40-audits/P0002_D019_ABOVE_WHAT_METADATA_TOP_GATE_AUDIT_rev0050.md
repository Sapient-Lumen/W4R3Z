# P0002-D019 above-question reanchor and metadata top-gate audit — rev0050

Current head: `P0002-D019` — **Above What**.  
Previous head: `P0002-D018`.  
Verdict on previous head: `revise_not_promote`.

## Literary move

D018 found the right source pressure — the same NOAA benchmark disk listed at two official heights above two water datums — but it still displayed the table too directly. D019 moves `4.468 above MLLW` and `3.025 above MHW` out of the poem body and into packet/disclosure space. The poem body now tests the question that was latent in D018: **above what?**

This is not a promotion. It is a riskier subtraction. D019 can fail by becoming over-smoothed and less resistant than D018.

## Audit/refactor

The concrete drift fault was in compact current metadata. `poems/P0002/metadata.json` could carry fresh current-head fields while its top-level title and generation context still pointed to older drafts. `registries/proof_status.json` also had a nested `current_context` that could lag behind the actual current head.

`tools/check_release_surfaces.py` now blocks these classes of drift:

- P0002 metadata top-level title mismatch against the current draft H1;
- metadata current draft/packet mismatch;
- metadata generation-context prompt/packet/revision-basis mismatch;
- proof-status nested current-context head/draft/packet mismatch;
- dynamic stale-current prose for prior P0002 heads.

These checks are navigation/provenance guards, not quality claims.

## Current non-claim

P0002-D019 is same-turn unjudged; not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA value claim.
