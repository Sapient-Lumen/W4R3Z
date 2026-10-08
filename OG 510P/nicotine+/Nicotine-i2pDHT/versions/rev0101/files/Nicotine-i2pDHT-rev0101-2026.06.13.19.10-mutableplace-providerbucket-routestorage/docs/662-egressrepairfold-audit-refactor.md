# egressrepairfold audit/refactor

`egressrepairfold.py` is the rev0062 audit spine.

It checks:

- the folded branchlet modules are active;
- the new ACK/repair join, retry fence, and repair prune guard exist;
- the rev0062 tests and docs are visible;
- the rev0061 `ackfold` predecessor still passes;
- fold map, fold registry, and surface ledger know the current path;
- the hidden rev0061 delivery-repair branchlet is preserved under `artifacts/branchlets/`.

Audit stance:

```text
Branchlets should either be folded, superseded, or archived visibly. Hidden protocol ancestry is design debt.
```
