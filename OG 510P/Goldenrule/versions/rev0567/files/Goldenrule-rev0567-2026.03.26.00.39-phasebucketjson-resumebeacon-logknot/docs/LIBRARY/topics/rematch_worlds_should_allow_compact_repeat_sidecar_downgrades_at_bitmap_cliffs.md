# Rematch worlds should allow compact repeat sidecar downgrades at bitmap cliffs

## Claim

Compact repeat sidecars should not be treated as monotone archive growth. At marginal repeat budgets, the best compact state can **downgrade** after a route-block bitmap cliff:

- bare paged catalogs can retake the lead for a short window,
- filters can then retake the lead,
- and route blocks can become optimal again only after enough new pages accumulate inside the next bitmap band.

## Why this matters

The archive is size-constrained. A sticky policy like “once route blocks pay off, keep them forever” is wrong near the compact frontier.

On the live deterministic `274`-fingerprint frontier with `16`-entry pages:

- baseline repeat thresholds are:
  - bare pages -> filters: `0.185996`,
  - filters -> route blocks: `0.650001`,
  - bare pages -> route blocks: `0.219221`.
- but at a marginal budget of `0.18` expected repeats, the exact best-state plan over the next `256` novel appends is:
  - bare pages for appends `0`–`8`,
  - filters for `9`–`14`,
  - bare pages for `15`–`23`,
  - filters for `24`–`30`,
  - bare pages for `31`–`37`,
  - filters for `38`–`46`,
  - bare pages for `47`–`53`,
  - filters for `54`–`62`,
  - route blocks for `63`–`110`,
  - bare pages again at the first bitmap cliff, append `111`,
  - filters for `112`–`158`,
  - route blocks for `159`–`238`,
  - filters again for `239`–`256`.

So the correct operational memory is not “sidecars accumulate.” It is:

- repeat budget,
- novel-append horizon,
- and whether the next route-block bitmap cliff will temporarily invalidate the current sidecar choice.

## Implementor consequence

The archive-local sidecar planner should permit all three operations:

- add filters,
- upgrade filters to route blocks,
- and downgrade route blocks back to filters or bare pages when a cliff makes them temporarily too expensive for the current repeat budget.

That keeps the archive compact without discarding the option to regain stronger sidecars later.

## Pointers

- `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_staging_snapshot_20260307.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_staging.py`
