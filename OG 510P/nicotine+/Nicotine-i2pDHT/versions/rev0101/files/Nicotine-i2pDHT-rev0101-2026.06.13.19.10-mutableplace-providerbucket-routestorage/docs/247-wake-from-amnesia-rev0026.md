# Wake from amnesia — rev0026

Start here when resuming the cube:

1. Read `docs/240-rev0026-schedjoin-custodygc-transportshadow.md`.
2. Skim `src/i2p_dht_lab/schedjoin.py`, then its tests.
3. Skim `src/i2p_dht_lab/custodygc.py`, then its tests.
4. Skim `src/i2p_dht_lab/partitionwitness.py`, then its tests.
5. Skim `src/i2p_dht_lab/transportshadow.py`, then its tests.
6. Run `scripts/ci/run_python_cloudtainer_lane.sh`.

Most important invariant:

```text
A report from one local safety surface should not silently authorize the next surface.
```
