# Protocol negotiation downgrade pressure

`negotiationlane.py` treats a peer handshake as an adversarial boundary.

A signed offer includes:

```text
node id
source/path family hints
supported protocol versions
supported feature set
required feature set
namespace-policy digest
max frame budget
sequence and time window
signature
```

A signed selection binds two offer digests, a request id, a chosen version, chosen features, and the namespace-policy digest. The local assessment checks:

- bad offer signatures;
- expired offers;
- replayed offers;
- same-actor same-sequence forks;
- namespace-policy digest mismatch;
- missing required features;
- forbidden features;
- too-small frame budget;
- signed downgrade selection;
- selection not bound to the two offers.

The design guess: downgrade prevention is not just a TLS-ish concern. In this DHT, downgrades can quietly disable mutable-head safety, range-repair safety, refusal accounting, or future privacy-budget controls before any visible transport failure occurs.
