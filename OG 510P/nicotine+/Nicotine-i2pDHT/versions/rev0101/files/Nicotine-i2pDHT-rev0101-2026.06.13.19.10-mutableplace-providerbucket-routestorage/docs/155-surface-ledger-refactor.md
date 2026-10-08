# Surface ledger refactor

The cube has useful history, including duplicate historical docs and modules. That history should not be casually deleted because it supports wake-from-amnesia review.

At the same time, every new active surface should be named with its module, test, and design doc. rev0018 adds `surfaceledger.py` for that purpose.

The active rev0018 ledger pins:

```text
contactlease.py   -> contact lease tests/doc
siblingcast.py    -> siblingcast tests/doc
sweepaudit.py     -> sweep audit tests/doc
surfaceledger.py  -> surface ledger tests/doc
```

This is not a full packaging manifest. It is a compact local audit object for new work so future revisions can tell the difference between historical surface, active surface, and accidental drift.
