# rev0083 — nativeruntime-dispatchaudit-fallbackbudget

rev0083 continues the optional-GCC line without turning it into a rewrite. rev0081 allowed tiny deterministic native leaf kernels. rev0082 required Python/native parity, ABI/load checks, and fallback sealing before a leaf can be selected. rev0083 adds the next boundary: a concrete runtime stamp and a concrete dispatch request still have to agree with that evidence after build, restart, or artifact drift.

The design rule is:

```text
Native code is not selected because it compiled or passed parity once; every runtime stamp and every call must remain bound to the same Python oracle, ABI evidence, fallback seal, object digest, source digest, and exact request boundary.
```

New active surfaces:

```text
src/i2p_dht_lab/nativeruntime.py
src/i2p_dht_lab/nativedispatch.py
src/i2p_dht_lab/nativeaudit.py
src/i2p_dht_lab/nativedispatchfold.py
tests/test_rev0083_nativeruntime_dispatchaudit_fallbackbudget.py
```

The DHT still stays Python-owned for protocol truth. The native line is allowed only for side-effect-free hotpath leaves whose behavior is checked against Python reference logic. rev0083 makes even those leaves restart-aware and request-bound.
