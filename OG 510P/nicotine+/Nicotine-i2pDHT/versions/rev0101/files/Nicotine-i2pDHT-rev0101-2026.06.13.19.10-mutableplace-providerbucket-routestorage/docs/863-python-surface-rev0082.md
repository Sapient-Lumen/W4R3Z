# Python surface — rev0082

Active Python surfaces added in rev0082:

```text
src/i2p_dht_lab/nativeparity.py
src/i2p_dht_lab/abiguard.py
src/i2p_dht_lab/fallbackseal.py
src/i2p_dht_lab/nativeparityfold.py
tests/test_rev0082_nativeparity_abiguard_fallbackseal.py
```

Native leaf surface retained from rev0081:

```text
native/gcc/xor_distance.c
```

The implementation posture is still Python-first: native leaf kernels can be selected only through parity, ABI, and fallback-seal evidence.
