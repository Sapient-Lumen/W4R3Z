# Rematch worlds should price sidecar churn on exact switch-penalty frontiers

## Claim
When compact repeat-sidecar rewrites are not free, the archive should choose sidecar staging from an exact switch-penalty frontier rather than collapsing churn to one average break-even regret number.

## Why
The measured compact repeat-state frontier over the next 256 novel appends at 0.18 expected repeats is not “dynamic vs fixed.” It has nine exact non-negative switch-cost regimes. The small oscillatory bands disappear first, but a few large front-loaded transitions keep paying for much longer.

That means an average per-switch regret threshold is too coarse for the inheritor. Around the previously measured 927.685921-byte average break-even, the exact best policy is still a 4-transition schedule that beats fixed route blocks by 7069.915895 bytes. The archive should freeze the tiny bands first, keep the large jumps while they still pay, and only fall all the way back to a fixed sidecar once real rewrite cost crosses the exact fixed-policy frontier.

## Implementor rule
- Below about 45.40069 bytes per sidecar rewrite, exact micro-bands still matter.
- From 45.40069 to 134.276182 bytes, keep a 5-transition low-churn schedule.
- From 134.276182 to 1090.254986 bytes, keep a 4-transition schedule: bare pages through append 55, route blocks through 110, filters through 158, route blocks through 238, then filters again.
- From 1090.254986 to 2005.364255 bytes, keep a 3-transition schedule.
- From 2005.364255 to 5679.676082 bytes, keep only one front-loaded jump from bare pages into route blocks.
- Only at 5679.676082 bytes per transition or above should the archive freeze immediately into fixed route blocks.

## Minimal takeaway
The archive should price sidecar churn as a frontier of surviving switches, not as one average switch value.
