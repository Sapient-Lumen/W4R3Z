# Native dispatch seal

`nativedispatch.py` gates a single call to the optional XOR-distance leaf. It binds component, operation, request id, input bytes, bounded input length, runtime report digest, and prior request memory before dispatch.

The dispatch seal can:

```text
accept native dispatch when Python reference agrees
accept Python fallback dispatch
hold when native runtime was selected but callable is absent
quarantine request replay
quarantine operation mismatch
quarantine input-limit drift
quarantine native result mismatch
```

The important asymmetry remains: Python may run without native; native may not run without Python-reference agreement.
