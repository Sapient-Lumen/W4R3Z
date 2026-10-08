# servicecontinuityfold audit/refactor

`servicecontinuityfold.py` is the rev0038 audit/refactor lane. It checks that the folded service branchlets and new continuity join are visible from code, tests, docs, public pointers, the head registry, the fold map, the fold registry, and the active surface ledger.

It also preserves predecessor history by checking both rev0037 lanes:

```text
ticketfold        -> service tickets and service receipts
serviceguardfold  -> service announcements and ingress gating
```

The purpose is not to make the cube bureaucratic. The purpose is to keep branchlet growth from turning into hidden alternate protocol histories.
