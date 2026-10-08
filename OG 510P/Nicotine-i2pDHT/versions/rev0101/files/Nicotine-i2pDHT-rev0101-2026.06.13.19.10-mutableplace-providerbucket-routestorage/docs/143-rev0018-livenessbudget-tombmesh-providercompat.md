# rev0018 — livenessbudget / tombmesh / providercompat

rev0018 stays in DHT design space and attacks three pressure points that become dangerous if they are left as prose:

1. **Liveness vs metadata**: adaptive alpha/beta can widen a lookup under timeout or capture pressure, but a wider lookup plus semantic provider probes can leak interest. `livenessbudget.py` makes that spend explicit.
2. **Tombstones vs resurrection**: signed tombstones are not global truth, but stale alive/provider/latest evidence can resurrect withdrawn or compromised state. `tombmesh.py` turns that disagreement into local block/ask/quarantine decisions.
3. **Provider surface drift**: the cube still carries legacy `providerpoison.py` plus canonical `provider_poison.py`. `provider_compat.py` classifies legacy names before wrapper/deletion work.

Core sentence:

```text
Liveness pressure, resurrection pressure, and compatibility pressure must be budgeted before they become protocol defaults.
```

Nonclaims remain strict: no live SAM/I2P transport, no production DHT, no private retrieval, no tombstone consensus, no global reputation, no production provider proof protocol, and no Sybil/anonymity guarantee.
