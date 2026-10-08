# Native sandbox-stub boundary

The cube now has a native sandbox-stub lane, but it explicitly does **not** claim production isolation.

The point of the stub is to keep future native work bounded:

```text
no parser ownership
no crypto ownership
no secret-key ownership
no filesystem/network/process/thread/dynamic-load power
bounded input
bounded runtime
Python fallback retained
```

A native call after unload or quarantine is rejected. A fallback-only plan is acceptable. A native plan that lacks the explicit nonproduction-stub acknowledgement holds instead of pretending the sandbox exists.

The active code is `src/i2p_dht_lab/nativesandboxstub.py`.
