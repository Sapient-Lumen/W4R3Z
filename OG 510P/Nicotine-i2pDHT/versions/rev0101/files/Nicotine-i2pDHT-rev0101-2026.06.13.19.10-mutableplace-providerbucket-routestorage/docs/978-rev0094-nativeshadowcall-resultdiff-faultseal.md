# rev0094 — nativeshadowcall-resultdiff-faultseal

rev0094 goes one seam past `nativeloadloop`, `nativecallcanary`, and `dispatchfence`.

The new boundary is deliberately narrow: a native leaf may be observed in shadow form, but the Python oracle remains the only authority. A native result can become evidence, a mismatch can become fault pressure, and either path must preserve fallback/quarantine/crash memory.

Strongest sentence:

> A native shadow result is not native permission; it is evidence until result-diff and fault-seal memory agree while Python remains authoritative.

New active surfaces:

- `src/i2p_dht_lab/nativeshadowcall.py`
- `src/i2p_dht_lab/resultdiff.py`
- `src/i2p_dht_lab/faultseal.py`
- `src/i2p_dht_lab/nativeshadowfold.py`
- `tests/test_rev0094_nativeshadowcall_resultdiff_faultseal.py`

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production native loader/ABI/sandbox, no native parser/crypto, no production native dispatch authority, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
