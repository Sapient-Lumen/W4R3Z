# Send seal / effect ledger folded branchlet

rev0051 also folds a public-send branchlet into the cube as an active test pressure surface.

`sendseal.py` joins the no-network public commit barrier idea with the delivered rev0050 outbox-drain, SAM-canary, and compact-join lanes. A send seal is a signed local authorization that binds profile, service, session, Destination, scope, request, payload, idempotency key, public effect digest, component report digests, sequence, previous digest, family, and path family. It is explicitly not a live SAM send and not a public DHT write.

`effectledger.py` records local restartable memory after a send seal. It models prepare, send-shadow, commit, and abort entries with previous links, idempotency conflict checks, phase-regression checks, component-digest binding, and diversity pressure. The point is to prevent a future publisher from treating a staged public side effect, a SAM canary, or a restart as proof that the effect was safely committed.

This branchlet is deliberately tested beside the router-canary / ingress-drain red-team lane. The shared rule is:

```text
A future public edge has outbound, inbound, and restart-memory mouths; none of them can authorize the others by accident.
```

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production public publisher, no production idempotency database, and no global consensus about public effects.
