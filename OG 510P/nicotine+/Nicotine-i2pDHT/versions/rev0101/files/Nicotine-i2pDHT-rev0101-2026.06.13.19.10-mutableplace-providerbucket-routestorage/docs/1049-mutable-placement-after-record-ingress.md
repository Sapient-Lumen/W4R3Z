# Mutable placement after record ingress

`mutableplacement.py` models a risky DHT substrate boundary: a mutable record can be parse-safe, signature-valid, and ingress-accepted while still being stale, forked, tombstoned, gapped, or rollback-shaped.

The module accepts only a local observation. It deliberately does not claim global latestness.

It checks:

- record ingress accepted and is `mutable`
- Python validator/witness reports accepted
- target digest and signature/value/epoch window agree
- CAS/rollback pressure is clean
- same-sequence forks and live tombstones are absent
- previous-head links are present or the placement is held for watch
- head, fork, tombstone, witness, and rollback memory are preserved
- native mutable-truth attempts are quarantined
