# Next revision pointer after rev0083

Suggested next revision: `rev0084 parserhold-sanitizerplan-nativebudget`.

Likely focus:

```text
Keep parseguard Python-owned.
Add explicit sanitizer/fuzz-plan evidence before any new native leaf class.
Add native hotpath budget so optimization work cannot starve semantic tests.
Consider range-sketch or set-reconciliation leaf boundaries only as adapters.
```
