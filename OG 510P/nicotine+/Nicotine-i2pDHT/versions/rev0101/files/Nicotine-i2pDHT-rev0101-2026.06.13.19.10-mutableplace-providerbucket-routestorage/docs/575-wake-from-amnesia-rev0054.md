# Wake from amnesia — rev0054

Start here:

1. Read `docs/579-rev0054-replaylab-handlerquench-fuzzledger.md`.
2. Run `tests/test_rev0054_replay_quench_fuzzledger.py`.
3. Inspect `src/i2p_dht_lab/handlerreplay.py`, `handlerquench.py`, and `fuzzledger.py`.
4. Run `src/i2p_dht_lab/replayfold.py` via `audit_replay_fold(...)` or the evidence lane.

The important shift is that restart replay, repeated near-miss traffic, and fuzz coverage are now treated as sticky-state boundaries.
