# Redress GC and hard-negative memory

`redressgc.py` models cleanup pressure for local moderation/redress evidence.

The dangerous cleanup bug is:

```text
redress lift arrives
soft cleanup runs
hard-negative evidence disappears
future side effect treats the subject as clean
```

rev0048 refuses that shape.  Hard negatives such as quarantine-deny, provider-false, witness-fork, and generic hard-negative records are pinned ahead of soft convenience records.  Redress can narrow or add watch pressure, but a broad lift cannot erase live hard negatives in this local model.

The GC report separates:

- kept evidence;
- dropped expired/soft evidence;
- hard-negative count;
- live redress count;
- retained byte pressure;
- watch versus quarantine decisions.

This is still not a production database or policy engine.  It is a pressure surface for restart memory and future operator/control-plane decisions.
