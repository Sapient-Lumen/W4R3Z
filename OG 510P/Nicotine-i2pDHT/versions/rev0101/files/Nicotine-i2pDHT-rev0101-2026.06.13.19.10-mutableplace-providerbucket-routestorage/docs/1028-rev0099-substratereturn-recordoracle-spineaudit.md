# rev0099 — substratereturn-recordoracle-spineaudit

rev0099 deliberately turns away from the native/GCC branch after rev0098 closed it as shadow-only.  The new work is a DHT-substrate re-entry seam: the cube can resume record-plane, mutable-head, provider-proof, routing, and garden/witness work only after native close-out evidence and a Python-owned record-plane oracle agree at the same exact boundary.

The strongest rule:

```text
Closing the native branch is not enough; the DHT substrate must explicitly re-enter with Python still owning record truth.
```

New active surfaces:

```text
src/i2p_dht_lab/recordplaneoracle.py
src/i2p_dht_lab/substratereentry.py
src/i2p_dht_lab/substratereturnfold.py
tests/test_rev0099_substratereturn_recordoracle_spineaudit.py
```

rev0099 keeps the native branch closed. It does not add native load, dispatch, parser authority, crypto authority, transport authority, persistence authority, mutable-record truth, or provider truth.
