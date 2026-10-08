# Rematch worlds should enforce minimum dwell lengths for compact repeat sidecars

## Claim
When the inheritor wants a simple online rule that suppresses short-lived sidecar churn, compact repeat-sidecar planning should enforce a minimum dwell length for each regime instead of replaying every exact frontier toggle.

## Why
The measured 0.18-repeat frontier over the next 256 novel appends shows that the exact optimum is sensitive to very short cliff events. A minimum dwell of 2 unique appends already kills the single-step fallback at append 111 and drops the schedule from 12 transitions to 11 with only 1.979429 bytes of regret. A minimum dwell of 8 unique appends removes the remaining 6-step and 7-step micro-bands, collapsing the schedule to 5 transitions while still keeping 0.980481 of the full dynamic savings.

That is the important practical compression. The archive does not need to memorize every tiny oscillation to stay near-optimal. The current frontier says the schedule can be reduced from 12 transitions to 5 by requiring each regime to persist for at least 8 novel appends, and that simplification costs only 217.295277 bytes over the whole 256-append horizon. If the inheritor wants even less churn, a minimum dwell of 19 unique appends collapses the plan to 3 transitions while still keeping 0.870482 of the dynamic savings.

## Implementor rule
- Use minimum dwell 8 as the default simplifier on the current frontier.
- Use minimum dwell 2 when the only goal is to suppress one-step cliff fallbacks.
- Use minimum dwell 19 when operational simplicity matters more than the last 10–15% of dynamic savings.
- Once minimum dwell reaches 57, stop switching and keep route blocks from the start.
- Treat minimum dwell as an online guard: do not rewrite into a new sidecar state unless the projected winning band is expected to last at least that many novel appends.

## Minimal takeaway
Eight-appends minimum dwell is the current sweet spot: it kills the cliff chatter while preserving almost all of the value.
