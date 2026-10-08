# Store repair planning — rev0019

`storerepair.py` is small policy glue for deciding what to do after store contracts and custody audits disagree.

Possible local actions:

```text
no_action
renew_soon
cast_to_reserves
ask_garden_sentinels
hold_for_backoff
quarantine_record
```

The planner quarantines contradictions, false custody, replay pressure, and contract gaps. It renews near-expiry leases even after a successful audit. It casts to reserves when accepted leases or custody proofs are too few. It asks gardens/sentinels when the missing piece is family diversity rather than raw count.

This is intentionally not a scheduler. It is an executable policy seam so bad repair instincts can fail in unit tests before any live transport exists.
