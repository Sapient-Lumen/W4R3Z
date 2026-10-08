# P0002-D021 no-column-for-rain reanchor and STATE status gate audit — rev0052

Current head: `P0002-D021` — **No Column for Rain**.  
Previous head: `P0002-D020`.  
Verdict on previous head: `revise_not_promote`.

## Literary move

D020 restored source resistance by naming the datum waters, but the cold review found that it still explained the mechanism too directly. D021 keeps the official NOAA benchmark table and exact MLLW/MHW elevation values in packet/disclosure space and moves the poem body to a smaller pressure: the table has official columns, while rain crossing the dock has no column.

The bet is now physical and negative: not `Mean Lower Low Water` versus `Mean High Water` in the body, but rain crossing the disk and leaving no height behind.

This is not a promotion. D021 can fail by becoming a softer table lyric rather than a poem.

## Audit/refactor

The concrete drift fault was in `STATE.json`: rev0051 had a fresh `current_head` of `P0002-D020`, but `status` and `next_action` still described `P0002-D018`. The main validation path passed anyway.

`tools/check_surface_freshness.py` now blocks that class of compact-orientation drift by requiring these STATE prose fields to mention the actual current head:

- `status`;
- `next_action`;
- `current_status`.

These checks are navigation/provenance guards, not poem-quality claims.

## Current non-claim

P0002-D021 is same-turn unjudged; not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA value claim.
