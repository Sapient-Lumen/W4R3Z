# rev0037 — ticketlane-servicereceipt-registryfold

rev0037 moves one boundary past rev0036. A garden can now advertise service
capacity and pass a load sheath, but that still must not become an unmetered
side effect. The new surface adds short-lived service tickets and signed service
receipts before any future handler is allowed to treat work as completed,
refused, or partially served.

Strong sentence:

```text
A catalog says what a garden offers; a ticket says exactly what one caller may spend; a receipt says what happened without becoming reputation.
```

New active code:

```text
src/i2p_dht_lab/serviceticket.py
src/i2p_dht_lab/servicereceipt.py
src/i2p_dht_lab/ticketfold.py
tests/test_rev0037_service_ticket_receipt_fold.py
```

Risk-first focus:

- exact-scope service tickets bound to catalog report, load report, caller,
  demand, scope, object, and request;
- receipt shape pressure so completion, useful refusal, and partial result do
  not blur into one another;
- refusal-only loop detection before garden usefulness can be laundered;
- foldregistry/foldmap/surfaceledger updates so rev0037 is visible from the
  cube spine instead of added as loose code.

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production
garden service protocol, no private retrieval guarantee, no global reputation,
no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.

## Folded serviceguard branchlet

This revision also folds in `serviceannounce.py` and `ingressgate.py` as a
second active lane. A service announcement is a redacted entrance hint, not a
permission. Ingressgate joins announcement acceptance, catalog acceptance,
load-sheath pressure, replay memory, family pressure, and metadata budget before
future handler work can reach the ticket lane. `serviceguardfold.py` pins this
branchlet through foldmap, foldregistry, surfaceledger, docs, public pointers,
and tests.
