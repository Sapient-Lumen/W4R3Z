# rev0089 — nativecoldstart-probecorpus-loadergc

This revision continues the native-control line after rev0088.  The risky seam is:

```text
native unload accepted
+ sandbox-stub accepted
+ crash-GC accepted
    ≠ native artifact may load on restart
    ≠ old probe corpus is fresh enough
    ≠ loader state may be forgotten
```

The new rule is:

```text
Native discovery after restart is not native permission.
```

New code:

```text
src/i2p_dht_lab/nativecoldstart.py
src/i2p_dht_lab/probecorpus.py
src/i2p_dht_lab/loadergc.py
src/i2p_dht_lab/nativecoldfold.py
tests/test_rev0089_nativecoldstart_probecorpus_loadergc.py
```

The strongest sentence in this revision:

```text
A native artifact found after restart is only a file-shaped claim until cold-start, probe corpus, and loader-GC agree while Python remains the route.
```

Current nonclaims remain firm: no live I2P/SAM transport, no production DHT, no production native loader/ABI/sandbox, no native parser/crypto, no production supply-chain security, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
