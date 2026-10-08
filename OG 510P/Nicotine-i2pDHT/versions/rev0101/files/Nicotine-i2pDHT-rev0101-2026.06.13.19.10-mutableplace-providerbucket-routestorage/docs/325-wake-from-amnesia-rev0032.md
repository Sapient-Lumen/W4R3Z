# Wake from amnesia rev0032

Remember the shape:

```text
valid component report != valid joined side effect
```

The cube already had scope fences, proof obligations, probe ledgers, store repair planning, egress metering, shadow frames, and SAM-wire scripts. rev0032 does not invent a new protocol layer; it joins those layers at their dangerous side-effect boundaries.

The next likely risk lane is to collapse more fold modules behind `foldmap.py` while making persistence/replay of scopeledger and storedebt observations survive restart without dropping tombstones, revocations, or open obligations.
