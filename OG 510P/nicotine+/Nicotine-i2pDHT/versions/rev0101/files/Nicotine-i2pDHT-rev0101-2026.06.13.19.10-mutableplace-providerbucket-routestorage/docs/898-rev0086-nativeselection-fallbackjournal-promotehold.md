# rev0086 — nativeselection-fallbackjournal-promotehold

This revision keeps pushing on the GCC/native branch without letting it become a rewrite.

rev0085 could prove native build provenance, differential corpus parity, and quarantine memory. rev0086 adds the next boundary: **selection itself**. A native artifact is not selected because its reports look good in isolation. It is selected only when provenance, corpus, quarantine, budget, artifact digest, source digest, Python fallback digest, sequence memory, and family/path diversity all bind to one exact operation boundary.

The core rule:

```text
Native selection is a local side effect.
Fallback selection is restart memory.
Promotion back to native must preserve why fallback happened.
```

New surfaces:

```text
src/i2p_dht_lab/nativeselection.py
src/i2p_dht_lab/fallbackjournal.py
src/i2p_dht_lab/nativepromotion.py
src/i2p_dht_lab/nativeselectionfold.py
tests/test_rev0086_nativeselection_fallbackjournal_promotehold.py
```

The strongest sentence in this revision:

```text
A native artifact is not selected because it is healthy; it is selected only when the exact boundary can still route to Python and remember why fallback ever happened.
```

Nonclaim: this is still no live I2P/SAM transport, no production DHT, no production native ABI, no native parser/crypto, and no production supply-chain security system.
