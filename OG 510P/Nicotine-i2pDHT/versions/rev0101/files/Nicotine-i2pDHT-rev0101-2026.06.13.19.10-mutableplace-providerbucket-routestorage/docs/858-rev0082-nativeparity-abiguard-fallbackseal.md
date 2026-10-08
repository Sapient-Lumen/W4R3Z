# rev0082 — nativeparity-abiguard-fallbackseal

This revision continues the GCC/native question from rev0081 without letting the answer drift into a rewrite.

The new design rule is:

> Native code is a speed witness, not a truth source.

rev0082 adds three executable surfaces:

- `nativeparity.py` compares optional native XOR-distance leaf results against the Python reference over deterministic, diverse vectors.
- `abiguard.py` checks native artifact load boundaries: ABI version, symbol set, source digest, compiler-flag digest, object digest, input bound, and Python fallback availability.
- `fallbackseal.py` joins parity and ABI reports so missing or quarantined native code routes to Python instead of silently failing open.

The tiny GCC XOR comparator remains the only native leaf candidate in the cube.  Protocol state, mutable-head judgment, policy, parsing of untrusted network bytes, transport/session control, and persistence/finality stay Python-owned.

The strongest rev0082 sentence:

```text
Native code is not selected because it compiled; it is selected only after ABI, parity, and fallback seal all agree while Python remains the oracle.
```

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production native ABI, no production fuzzer, no production native parser/crypto, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
