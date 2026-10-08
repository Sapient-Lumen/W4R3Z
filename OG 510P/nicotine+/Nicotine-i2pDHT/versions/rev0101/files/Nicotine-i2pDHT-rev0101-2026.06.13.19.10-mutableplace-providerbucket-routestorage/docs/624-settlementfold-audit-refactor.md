# settlementfold audit/refactor

`settlementfold.py` pins the rev0059 active path:

```text
attestationpack
settlementlane
tombstonerepair
settlementstore
terminalreceipt
settlementfold
```

The audit also checks the public surface, head registry, docs, VERSION, and rev0057/rev0058 predecessor visibility. The refactor choice is to fold the alternate rev0058 settlement branchlet into visible history instead of deleting it or pretending it never happened.
