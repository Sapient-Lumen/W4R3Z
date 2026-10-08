# Delivery repair / live egress branch fold

A hidden sibling rev0061 cube already explored a useful path:

```text
missing ACK -> delivery repair probe -> rollback probe -> live egress retry/withdraw gate
```

rev0062 keeps that work instead of discarding it. The branchlet is preserved under:

```text
artifacts/branchlets/rev0061_deliveryrepair_liveegress_rollbackprobe/
```

The active source now includes the branchlet's three core modules:

```text
src/i2p_dht_lab/deliveryrepair.py
src/i2p_dht_lab/rollbackprobe.py
src/i2p_dht_lab/liveegress.py
```

Design rule:

```text
No acknowledgement is not success, and it is not permission to blindly resend.
```

A missing ACK becomes sticky repair memory. Rollback probes must fail to find remote commit evidence before retry can be considered. Live egress is still a no-network readiness report, not a send.
