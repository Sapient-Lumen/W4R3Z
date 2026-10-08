# Probe corpus refresh

The probe corpus is refreshed after cold-start, not reused blindly across restart, crash-GC, or unload.  It is a Python-oracle lane:

```text
Python fallback vectors
boundary vectors
bucket coverage
bounded input size
fault-regression vectors when crash history exists
```

The corpus requests evidence for future native reconsideration.  It does not select native code and does not load native code.
