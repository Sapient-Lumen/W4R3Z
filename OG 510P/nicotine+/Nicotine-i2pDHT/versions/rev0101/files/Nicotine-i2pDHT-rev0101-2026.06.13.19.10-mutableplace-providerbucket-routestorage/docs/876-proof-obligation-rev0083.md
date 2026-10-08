# Proof obligation rev0083

Before any future native hotpath can be used outside the lab, it owes:

```text
Python reference implementation
stable ABI manifest
source/object/compiler flag digests
parity vectors and mismatch preservation
source audit with no heap/I/O/network/process tokens
runtime stamp after build/restart
exact-call dispatch seal
fallback path selected and tested
```

A native-required profile remains suspect. Portable fallback is still part of the safety boundary.
