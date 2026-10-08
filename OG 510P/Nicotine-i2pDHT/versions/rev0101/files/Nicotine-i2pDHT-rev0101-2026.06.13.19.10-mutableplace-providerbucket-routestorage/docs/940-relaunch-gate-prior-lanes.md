# Relaunch gate prior-lane revalidation

A native handoff candidate cannot dispatch. The relaunch gate requires prior native lanes to revalidate before a relaunch plan exists.

The gate carries digests for parity, ABI, fallback seal, runtime stamp, and selection evidence. Missing or insufficient prior-lane revalidation holds the system on Python fallback.

Accepted relaunch plans are still no-network:

```text
native load allowed: false
dispatch allowed: false
fallback active: true
```

This keeps the branch aligned with the core rule: native code is a narrow optimization surface, not a second authority.
