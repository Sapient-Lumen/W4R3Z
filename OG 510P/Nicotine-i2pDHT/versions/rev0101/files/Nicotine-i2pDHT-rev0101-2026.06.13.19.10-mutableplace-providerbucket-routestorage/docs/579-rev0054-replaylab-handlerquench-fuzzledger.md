# rev0054 — replaylab-handlerquench-fuzzledger

rev0054 goes one seam deeper than handler capsules and side-effect journals.

A handler capsule can pass. A side-effect journal can commit. Adapter fuzz can cover the obvious drift surfaces. None of that means restart replay, repeated near-miss ingress, or persisted fuzz coverage is safe.

Strong sentence:

> Restart replay, repeated near-miss ingress, and persisted fuzz coverage are protocol boundaries, not test leftovers.

New active surfaces:

- `src/i2p_dht_lab/handlerreplay.py`
- `src/i2p_dht_lab/handlerquench.py`
- `src/i2p_dht_lab/fuzzledger.py`
- `src/i2p_dht_lab/replayfold.py`
- `tests/test_rev0054_replay_quench_fuzzledger.py`

The revision is still no-network and toy-signed. It adds pressure before sticky handler state, future side effects, and fuzz evidence can survive restarts or repetition.
