# Ticketfold audit/refactor

`ticketfold.py` is the rev0037 current-path fold. It checks that the ticket and
receipt surfaces are visible from code, tests, docs, public pointers, head
registry, fold map, fold registry, and surface ledger.

This continues the refactor started in rev0036: use `foldregistry.py` and
`foldmap.py` to reduce hidden current-path drift while preserving historical
wake-from-amnesia fold modules.

Pinned rev0037 paths:

```text
src/i2p_dht_lab/serviceticket.py
src/i2p_dht_lab/servicereceipt.py
src/i2p_dht_lab/ticketfold.py
tests/test_rev0037_service_ticket_receipt_fold.py
docs/371-rev0037-ticketlane-servicereceipt-registryfold.md
docs/372-service-ticket-exact-scope-grants.md
docs/373-service-receipts-and-refusal-loops.md
docs/374-ticketfold-audit-refactor.md
```

Predecessor preserved: rev0036 `servicefold.py`.
