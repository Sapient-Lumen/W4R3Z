# Start profile matrix

`startmatrix.py` models the future startup modes separately:

```text
leaf            ordinary DHT participant
garden          giving supernode / service node
bridge          explicit public bridge/gateway posture
offline_design  no-router/no-network design harness
```

The matrix refuses convenient drift:

- I2P-only profiles cannot silently enable classic fallback.
- Garden profiles need at least one declared giving service.
- Bridge profiles need an explicit public-bridge bit.
- Offline design profiles must bind to an offline router harness.
- High-cardinality diagnostics need explicit power metadata budget.
- The profile must bind to the exact launch-intent digest that the launch quorum accepted.

This is local pressure, not governance or consensus.
