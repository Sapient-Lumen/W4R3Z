# Python surface — rev0096

Current rev0096 Python modules:

- `src/i2p_dht_lab/nativecallarchive.py`
- `src/i2p_dht_lab/nativepromotiondeny.py`
- `src/i2p_dht_lab/nativeshadowgc.py`
- `src/i2p_dht_lab/nativearchivefold.py`

The current test is:

- `tests/test_rev0096_callarchive_promotedeny_shadowgc.py`

The implementation remains deliberately Python-owned. GCC-native stays a side-effect-free leaf candidate and never becomes protocol authority in this revision.
