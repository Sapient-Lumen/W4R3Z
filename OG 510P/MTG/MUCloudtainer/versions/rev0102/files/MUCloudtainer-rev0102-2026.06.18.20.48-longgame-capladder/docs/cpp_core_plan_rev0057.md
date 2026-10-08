# C++ core plan — rev0057

No new C++ kernel is needed for rev0057.

The C++ role remains parity checking and targeted acceleration. The live rev0056 evidence already passed C++ shadow checks with zero skipped events and zero mismatches. The next bottleneck is not raw transition speed; it is evaluation design and artifact hygiene.

## Next C++ rule

Only add C++ when one of these is true:

```text
1. A decomposition experiment is too slow in Python after profiling.
2. A Python rule path has already stabilized and has replay traces.
3. The C++ seam can be checked against source-of-truth Python transitions.
```

## Do not do yet

Do not rewrite the whole simulator in C++ while claim semantics are still being decomposed. That would trade a known scientific bottleneck for a larger parity burden.
