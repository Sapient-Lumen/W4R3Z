# Wake from amnesia — rev0093

Current revision: `rev0093 nativeloadloop-callcanary-dispatchfence`.

Read first: `docs/968-rev0093-nativeloadloop-callcanary-dispatchfence.md`.

Current code:

```text
src/i2p_dht_lab/nativeloadloop.py
src/i2p_dht_lab/nativecallcanary.py
src/i2p_dht_lab/dispatchfence.py
src/i2p_dht_lab/nativeloadloopfold.py
src/i2p_dht_lab/nativefoldspine.py
```

Current tests:

```text
tests/test_rev0093_nativeloadloop_callcanary_dispatchfence.py
```

Remember: the rev0093 path still forbids native load, native dispatch, and native call execution. It records loopback/canary/fence evidence while Python executes.
