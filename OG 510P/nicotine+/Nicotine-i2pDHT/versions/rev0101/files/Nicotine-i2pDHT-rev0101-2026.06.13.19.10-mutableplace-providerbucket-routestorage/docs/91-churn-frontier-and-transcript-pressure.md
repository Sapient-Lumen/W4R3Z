# Churn frontier and transcript pressure

The churn front starts from a different risk than provider or garden logic: before a lookup even begins, did the client choose a healthy enough candidate frontier?

rev0011 adds `churnforge.py`, a small deterministic selector and transcript surface.

## Implemented pressure

```text
selectable states: up, slow, refusing
bad states: down, lying
family-rotating candidate selection before latency/closeness greed
bad-contact fraction detection
captured-fast-window detection
order-stable transcript digests sensitive to state changes
```

A frontier can be diverse overall while the fastest window is dominated by one family. That should keep lookup pressure open.

## Why before live SAM/I2P

Live I2P will add stream setup cost, route churn, asymmetric latency, and noisy failure modes. The DHT needs a transcript algebra first so later live failures can be compared to deterministic fixtures.
