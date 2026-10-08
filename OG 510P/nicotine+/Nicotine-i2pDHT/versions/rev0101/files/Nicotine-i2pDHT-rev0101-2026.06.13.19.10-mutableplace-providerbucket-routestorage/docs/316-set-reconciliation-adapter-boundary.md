# Set-reconciliation adapter boundary

`sketchboundary.py` draws a line around toy exact sketches.

Exact sketches remain useful for deterministic tests, but they must not masquerade as the production reconciliation path. The boundary now distinguishes:

- `exact_debug` — lab only;
- `minisketch` — future native adapter seam;
- `iblt` — future probabilistic adapter seam.

The tests pin:

- exact debug is accepted only in lab context with explicit allowance;
- exact debug outside lab is quarantined;
- native minisketch/IBLT requests continue until an adapter offer is present;
- capacity shortfall requests extension instead of raw dump when the adapter can extend;
- salt replay is quarantined;
- short reconciliation IDs are salted per session.

The goal is to let peer/range reconciliation grow toward Minisketch/PinSketch or IBLT-style approaches without prematurely binding the DHT to one library or leaking whole peerbooks as the fallback.
