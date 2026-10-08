# Wake from amnesia — rev0023

Read in this order:

1. `START_HERE.md`
2. `docs/00-index.md`
3. `docs/204-rev0023-rangesketch-admissionwall-namespacefold.md`
4. `docs/205-range-sketch-anti-entropy.md`
5. `docs/206-admission-wall-before-expensive-work.md`
6. `docs/207-namespace-registry-validator-policy.md`
7. `docs/208-namespace-fold-audit-refactor.md`
8. `tests/test_rev0023_rangesketch_admission_namespace.py`

The current design posture:

```text
Range sketches request repair, not truth.
Namespace policies gate local validation, not global governance.
Admission receipts show useful refusal, not payment.
```

The next likely work: connect range sketches to anti-entropy summaries and store/custody repair; turn namespace policies into mutable epoch heads; model handler dispatch queues under I2P-like latency.
