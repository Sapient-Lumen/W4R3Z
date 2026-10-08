# rev0088 — nativeunload-sandboxstub-crashgc

rev0088 continues the GCC/native line while keeping native code narrow and reversible.

The risk-first seam is now:

```text
native load accepted
+ crash ledger observed faults or no faults
+ performance guard created operator hints
    ≠ safe to keep native loaded
    ≠ safe to pretend a sandbox exists
    ≠ safe to garbage-collect crash evidence
```

New active surfaces:

```text
src/i2p_dht_lab/nativeunload.py
src/i2p_dht_lab/nativesandboxstub.py
src/i2p_dht_lab/nativecrashgc.py
src/i2p_dht_lab/nativecontrolfold.py
tests/test_rev0088_nativeunload_sandboxstub_crashgc.py
```

The strongest sentence for this revision:

```text
Native lifetime, sandbox posture, and crash-ledger cleanup are separate protocol boundaries; none may erase Python fallback or native fault memory.
```

Nonclaim: the sandbox surface is a typed no-network stub, not production isolation. The cube still forbids native ownership of parsing, crypto, transport, persistence finality, policy, moderation, mutable-head truth, or DHT authority.
