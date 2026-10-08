# Python surface rev0039

Primary modules:

```text
servicelease.py      lease capsule, renewal pressure, exact-boundary checks
sessionledger.py     repeated-window session advance pressure
sessionfold.py       current revision audit/refactor fold
```

Primary test file:

```text
tests/test_rev0039_servicelease_sessionledger_fold.py
```

The tests cover lease acceptance, renewal, bad signature, stale/future lease,
replay, budget overclaim, caller/object drift, rollback, same-sequence fork,
previous-link mismatch, renewal drift, session replay, same-window fork, binding
drift, withdrawal, quota overspend, refusal-only loops, low family diversity,
negative-after-success pressure, and current fold visibility.
