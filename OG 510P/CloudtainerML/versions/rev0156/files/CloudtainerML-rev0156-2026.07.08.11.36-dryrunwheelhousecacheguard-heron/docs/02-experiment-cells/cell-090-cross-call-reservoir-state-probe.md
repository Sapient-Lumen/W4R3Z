# CELL-090 — Cross-Call Reservoir State Probe

Priority: **P2**
Status: **candidate**

## Cheap first run

Fixed random reservoir carried across chunked forward calls.

## Sources

SRC-0152

## Baselines

- stateless chunking
- KV carry
- EMA state
- reservoir state

## Metrics

- cross-boundary recall
- state drift
- readout capacity
- safety canary

## Stop condition

If useful state requires large learned readout, demote.
