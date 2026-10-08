# Python surface rev0083

Active rev0083 Python surfaces:

```text
src/i2p_dht_lab/nativeruntime.py
src/i2p_dht_lab/nativedispatch.py
src/i2p_dht_lab/nativeaudit.py
src/i2p_dht_lab/nativedispatchfold.py
```

Native-adjacent active surface:

```text
native/gcc/xor_distance.c
```

Active test:

```text
tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py
```

The active Python rule is still: Python owns semantics, C owns only leaf acceleration after parity/ABI/fallback/runtime/dispatch gates agree.
