# Wake from amnesia — rev0083

Remember this if context is lost:

```text
rev0081 answered the GCC question: Python-first, GCC only for tiny deterministic leaves.
rev0082 added parity, ABI/load, and fallback sealing.
rev0083 adds runtime drift and exact-call dispatch sealing.
```

The new rule is not “native is safe after compile.” The rule is “native is selected only when Python parity, ABI evidence, fallback seal, runtime stamp, and dispatch request all bind to the same exact boundary.”

Current codename: `nativeruntime-dispatchaudit-fallbackbudget`.
