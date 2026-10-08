# P0002-D020 chosen-water reanchor and status-field gate audit — rev0051

Current head: `P0002-D020` — **The Water Chosen**.  
Previous head: `P0002-D019`.  
Verdict on previous head: `revise_not_promote`.

## Literary move

D019 made the correct move by removing D018's visible elevation numbers, but it over-smoothed the source into an abstract `above what` argument. D020 keeps the exact NOAA heights in packet/disclosure space and names the two datum waters in the poem body: `Mean Lower Low Water` and `Mean High Water`.

The bet is narrower now: the same disk does not move; the water chosen for zero changes what `above` means.

This is not a promotion. D020 can fail by becoming a cleaner explanation rather than a poem.

## Audit/refactor

The concrete drift fault was in `registries/poem_index.json`: a P0002 row could have fresh `current_head` and core paths while stale convenience fields such as `latest_draft_path` or `current_status` still pointed backward. In rev0050, `latest_draft_path` was stale and `current_status` still carried older meters-above wording.

`tools/check_release_surfaces.py` now blocks these classes of drift:

- `latest_draft_path` must match the current draft path;
- `current_status` must match the P0002 row's actual `status`;
- `next_action` must mention the current head.

These checks are navigation/provenance guards, not poem-quality claims.

## Current non-claim

P0002-D020 is same-turn unjudged; not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA value claim.
