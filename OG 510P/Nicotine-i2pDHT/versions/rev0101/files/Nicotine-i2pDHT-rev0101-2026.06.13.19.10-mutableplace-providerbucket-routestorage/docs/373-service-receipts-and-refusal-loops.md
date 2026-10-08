# Service receipts and refusal loops

`servicereceipt.py` models garden receipts as signed observations, not currency
or reputation.

Receipt result shapes are deliberately separate:

```text
completed       -> positive completed units, zero refused units
useful_refusal  -> zero completed units, positive refused units
partial         -> positive completed units and positive refused units
```

The tests pressure the dangerous cases:

- receipt replay;
- sequence rollback and same-sequence forks;
- receipt/ticket/report/scope binding drift;
- completed receipts that hide refusal;
- useful-refusal receipts that hide completion;
- unit overclaim beyond the ticket;
- refusal-only loops across a recent local window.

The point is to preserve the garden-node principle: giving nodes can refuse
usefully, but refusal-only service should not launder itself into healthy
contribution evidence.
