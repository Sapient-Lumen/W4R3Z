# Publication ledger boundary

`bridgeledger.py` is about a local future side effect.  `publicationledger.py` is about the sticky public record that side effect would produce.

A publication ledger entry is signed and binds:

```text
publication action
profile / service
scope / request
bridge ledger digest
witness appeal mesh digest
optional validator-root digest
public record digest
side-effect digest
sequence / previous publication digest
time window
family / path family
```

The ledger rejects missing entries, bridge-ledger quarantine, missing appeal mesh when watch pressure exists, appeal mesh quarantine, appeal watch unless explicitly allowed, bad signatures, replay, rollback, same-sequence forks, previous-link mismatch, scope/request drift, action drift, and component digest drift.

This is still no-network code.  It is the boundary that must be true before a future DHT public bridge record is refreshed, withdrawn, repaired, or quenched.
