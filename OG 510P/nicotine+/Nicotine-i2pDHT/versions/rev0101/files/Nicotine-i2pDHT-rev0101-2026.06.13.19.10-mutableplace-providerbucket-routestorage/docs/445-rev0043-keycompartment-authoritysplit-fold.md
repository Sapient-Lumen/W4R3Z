# rev0043 — keycompartment-authoritysplit-fold

This revision dives below the service/control-plane lifecycle and treats **key separation** as the next risky boundary. A future I2P DHT node will carry several public identities: router/Destination reachability, DHT node identity, operator authority, service signing, mutable publishing, witness signing, ticket minting, and diagnostics. The dangerous shortcut is to let one convenient key become all of them.

rev0043 adds a no-network pressure lane for that shortcut:

- `keycompartment.py` models signed public-key binding capsules for specific roles, scopes, profiles, previous links, sequences, and family hints.
- `authoritysplit.py` joins component reports across the exact same profile/scope/object/request boundary before authority-sensitive side effects are allowed.
- `compartmentfold.py` keeps this revision visible from public pointers, foldmap, foldregistry, the active surface ledger, and the rev0042 predecessor fold.

The current design sentence:

```text
A key that can route, operate, publish, witness, ticket, and diagnose everything is not convenience; it is a silent root compromise.
```

## What is implemented

`keycompartment.py` tests role reuse pressure around keys that try to be both operator and service signer, router Destination and service signer, witness and mutable publisher, and other suspicious pairs. It also tests bad signatures, replay, scope drift, crisis quarantine, rollback, previous-link mismatch, same-sequence forks, and family-diversity holds.

`authoritysplit.py` models the joined boundary after a compartment passes. Key compartment success is not enough if operator-key state, profile cooldown, router harness, service catalog, or hard-negative scans fail or drift to a different request. Reports have to agree on profile, scope, object, request, component status, actor key, and family diversity.

## Why this matters

The cube has been adding garden services, operator actions, bridge announcements, cooldowns, exits, and resumes. Those surfaces all depend on one quiet assumption: that the keys underneath them mean what they claim to mean. rev0043 makes that assumption executable and hostile.

## Nonclaims

This is still a toy lab surface. It does not manage private keys, encrypt key material, define a production keystore, prove key independence, implement real hardware-backed storage, or connect to live I2P/SAM.
