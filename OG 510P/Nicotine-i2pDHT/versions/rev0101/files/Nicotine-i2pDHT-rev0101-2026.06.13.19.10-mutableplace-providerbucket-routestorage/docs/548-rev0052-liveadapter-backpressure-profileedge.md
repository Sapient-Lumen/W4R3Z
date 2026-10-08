# rev0052 — liveadapter-backpressure-profileedge

This revision stays no-network and risk-first. rev0051 split the public edge into outbound router/session canaries and inbound ingress drains. rev0052 adds the seam that should sit after those reports but before any future live SAM send or public-bridge handler side effect.

Strong sentence:

> A public edge is not live because outbound and inbound rehearsals passed separately; it is live only when adapter intent, shared pressure, profile budget, and hard-negative memory bind to the same exact boundary.

New surfaces:

- `src/i2p_dht_lab/liveadapter.py`
- `src/i2p_dht_lab/backpressuremesh.py`
- `src/i2p_dht_lab/profileedge.py`
- `src/i2p_dht_lab/edgefold.py`
- `tests/test_rev0052_liveadapter_backpressure_profileedge.py`

The main design change is a three-step local side-effect ladder:

```text
router canary + ingress drain
  -> shared backpressure mesh
  -> no-network live adapter plan
  -> profile-edge capsule
  -> future live side effect, still not implemented here
```

Current nonclaims remain: no live I2P/SAM transport, no production DHT, no production public bridge adapter, no production backpressure scheduler, no production profile-edge database, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
