# Fallback seal and native quarantine

The fallback seal joins parity and ABI reports.

Selection outcomes:

```text
ABI accepted + parity accepted -> native leaf may be used, Python oracle retained
native missing                 -> Python fallback, watch
native mismatch/exception      -> quarantine native, Python fallback
native required + missing/bad  -> profile quarantine
```

The seal exists to prevent a common implementation bug: one subsystem notices a native mismatch, another subsystem notices a fallback exists, and the combined system accidentally continues as if native evidence were healthy.

rev0082 makes the fallback decision explicit, digest-bound, and testable.
