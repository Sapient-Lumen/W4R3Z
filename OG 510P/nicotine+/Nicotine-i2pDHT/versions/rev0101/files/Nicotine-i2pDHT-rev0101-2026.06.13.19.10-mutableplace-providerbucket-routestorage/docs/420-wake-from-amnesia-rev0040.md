# Wake-from-amnesia — rev0040

Resume here:

1. Read `docs/414-rev0040-operatorbreaker-serviceexit-fold.md`.
2. Inspect `operatorintent.py`, `servicebreaker.py`, and `serviceexit.py`.
3. Run `tests/test_rev0040_operator_breaker_exit_fold.py`.
4. Check `operationsfold.py` if navigation or metadata feels stale.

Mental model:

```text
operator intent -> breaker pressure -> drain / continuity / profile memory -> exit or resume
```

A garden node can be generous only if it has a safe way to pause, demote, freeze, and resume without deleting the negative evidence that keeps future decisions sane.
