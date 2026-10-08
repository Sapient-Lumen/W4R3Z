# Garden budget receipts — rev0019

Garden nodes need a way to refuse and throttle without becoming silent black holes. `budgetreceipt.py` now supports two related receipt styles:

```text
sweep-audit-bound receipt -> monotonic garden statement about one region sweep audit
service-window receipt    -> signed accepted/refused/deferred counts for one garden service window
```

A budget receipt is not currency, payment, consensus, or global reputation. It is local operator evidence. A useful refusal with backoff can be scored as healthier than a dropped request because it lets callers slow down instead of multiplying retries.

Risk tested here:

```text
bad signature
wrong sweep-audit binding
action mismatch
same-sequence fork
missing backoff on throttled/refused work
impossible accepted/refused/deferred counts
```
