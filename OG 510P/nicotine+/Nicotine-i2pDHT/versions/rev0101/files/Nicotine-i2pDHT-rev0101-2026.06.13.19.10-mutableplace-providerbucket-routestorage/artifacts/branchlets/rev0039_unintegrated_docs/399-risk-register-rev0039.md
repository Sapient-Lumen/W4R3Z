# Risk register rev0039

Still open:

- leases are toy signed capsules, not a production capability format
- session windows are deterministic fixtures, not live network telemetry
- family IDs are lab hints, not a solved independence oracle
- budget units are abstract and need later calibration
- no private retrieval guarantee
- no global reputation or payment system
- no mutable-head consensus
- no live I2P/SAM transport

Newly tested:

- ongoing service cannot rely on one continuity pass forever
- lease renewal needs previous-link memory
- session advance needs repeated-window diversity
- refusal-only loops are held rather than counted as healthy service
- hard negative evidence cannot be buried by completed-unit claims
