# SAM garden shadow families

`samgarden.py` expands `samshadow.py` from a single outbound streaming-first transcript into the families a future garden node will likely need:

```text
outbound_connect
inbound_accept
reconnect_after_close
naming_failure
datagram_assumption_probe
```

This is still not live SAM. It is a no-network transcript lab.

The positive path keeps the same assumptions as previous revisions:

```text
HELLO VERSION
DEST GENERATE SIGNATURE_TYPE=7
SESSION CREATE STYLE=STREAM ... persistent destination
STREAM CONNECT / STREAM ACCEPT as needed
```

The negative path remains important. The bundle-first i2pd path should not silently depend on SAM 3.3 primary/subsession datagram behavior before that assumption is tested against real routers. So rev0016 keeps a datagram-primary probe as an expected negative transcript in the garden family.

The main product-shaped guess:

```text
A garden node needs inbound accept, reconnect, and naming-failure behavior before it needs datagram cleverness.
```
