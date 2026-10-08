# Wake from amnesia — rev0068

Start here:

1. `docs/718-rev0068-archivejournal-prunereplay-closureaudit.md`
2. `tests/test_rev0068_archivejournal_prunereplay_closureaudit.py`
3. `src/i2p_dht_lab/archivejournal.py`
4. `src/i2p_dht_lab/prunereplay.py`
5. `src/i2p_dht_lab/closureaudit.py`
6. `src/i2p_dht_lab/archivejournalfold.py`

Needles: `rev0068 archivejournal prunereplay closureaudit archivejournalfold`.

Core invariant: a pruned duplicate-repair trace remains sticky protocol memory until archive journal, prune replay, and closure audit agree at the same boundary.
