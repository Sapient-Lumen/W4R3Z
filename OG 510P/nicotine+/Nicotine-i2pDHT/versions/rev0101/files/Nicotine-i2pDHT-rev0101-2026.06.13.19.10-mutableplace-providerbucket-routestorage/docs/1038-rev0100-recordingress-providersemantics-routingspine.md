# rev0100 — recordingress-providersemantics-routingspine

rev0100 is the first milestone after the native/GCC branch was closed as shadow-only and the cube returned to the generic Python-owned I2P DHT substrate.

The central risk is now simple: a returned substrate can accidentally treat valid-looking DHT records as useful before Python-owned parsing, validation, admission, provider-proof, routing-anchor, and memory-preservation gates agree.

## New surfaces

- `recordingress.py` gates inbound DHT record admission after substrate re-entry and the record-plane oracle.
- `providersemantics.py` keeps provider records as routing claims until challenge-bound semantic proof and metadata budget agree.
- `routinganchor.py` gates I2P contact/routing records on lease, attestation, Destination/node binding, and family/path diversity.
- `substratespine.py` starts a small substrate-DHT spine after the native branch close.
- `substratecenturyfold.py` audits this rev0100 path and the rev0099 predecessor.

## Strong rule

A parsed, signed, validator-accepted DHT record is still not useful until exact-boundary ingress, semantic proof, routing anchor, and preserved hard-negative memory agree.

## Nonclaims

No live I2P/SAM transport. No production DHT. No production record-ingress protocol. No production provider-proof protocol. No production routing-contact protocol. No global reputation. No mutable-head consensus. No private retrieval guarantee. No Sybil/anonymity guarantee. No Nicotine+ patch.
