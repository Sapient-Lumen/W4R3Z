# Scopefence / obligationdebt / decaymesh branchlet

The extracted rev0031 work already contained a valuable branchlet:

- `scopefence.py` — exact scope/object/request/purpose fences before joined evidence authorizes work;
- `obligationdebt.py` — proof obligations left by accept-with-watch decisions;
- `decaymesh.py` — evidence aging that preserves hard negatives while dropping soft convenience memory;
- `auditmesh.py` — an audit fold preserving the rev0030 keycrisisfold predecessor.

rev0031 keeps this branchlet active instead of hiding it. The new `foldmap.py` path treats it as part of the current revision's audit/refactor story while `probeledger.py`, `crisisroute.py`, and `sketchboundary.py` continue the risk-first implementation lane.

Core rule:

```text
A valid fact in one scope cannot pay proof debt, spend metadata, repair state, or authorize work in another scope.
```
