# rev0029 — checkpointlane / egressmeter / foldseal

Artifact: `Nicotine-i2pDHT-rev0029-2026.06.03.18.17-checkpointlane-egressmeter-foldseal`

rev0029 attacks joined local-boundary failures before the cube moves closer to live I2P/SAM transport.  The new work treats restart checkpoints, outbound metadata spend, and final handler dispatch as safety boundaries.

Strong sentence:

```text
A signed local summary, an accepted egress budget, and a bound handler intent are still separate observations until they are joined at the exact scope/object/request boundary.
```

New implementation surfaces:

- `checkpointlane.py`: signed checkpoint summaries over local memory with monotonic generation, previous-checkpoint link, journal-tip binding, hard-negative preservation, same-generation fork detection, rollback detection, and generation-gap watch pressure.
- `egressmeter.py`: outbound metadata/byte/stream/family budget pressure for provider probes, decoys, witness publication, route gossip, repair work, STORE requests, and SAM-shadow sends.
- `dispatchjoin.py`: joins `misbindguard.py` and `egressmeter.py` so a future handler cannot use a valid upstream object to spend egress in another scope/object.
- `foldseal.py`: current-revision audit/refactor that pins rev0029 surfaces while proving the rev0028 foldspine still passes.

This revision deliberately keeps live I2P/SAM transport out of scope.
