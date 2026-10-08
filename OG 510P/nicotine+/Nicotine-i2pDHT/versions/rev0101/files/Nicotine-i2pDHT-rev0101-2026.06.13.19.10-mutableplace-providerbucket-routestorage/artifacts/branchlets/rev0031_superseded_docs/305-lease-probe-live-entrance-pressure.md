# Lease-probe liveness and metadata pressure

A contact lease is an entrance claim. It binds a DHT key, I2P Destination string, node id, purpose list, family hint, and sequence. It does not prove that the contact is reachable *now* or safe to probe repeatedly.

rev0031 adds `leaseprobe.py` to keep the liveness seam explicit:

```text
ContactLease -> LeaseProbeChallenge -> LeaseProbeReceipt -> local pressure report
```

A challenge is short-lived, signed by the requester, scoped to one lease hash and one request digest, purpose-bound, and byte-budgeted. A receipt is signed by the lease key and binds the lease hash, challenge digest, responder node id, source family, path family, response bytes, and any raw-key exposure count.

The tests pin these early guesses:

- a lease with no challenge is watchable, not proved live;
- a receipt replayed from an earlier window is quarantined;
- purpose mismatch is a hard failure;
- raw-key exposure requires explicit challenge permission;
- receipt family/path diversity is required before accepting liveness;
- egress-meter rejection blocks lease probing before side effects.

The design remains deliberately local. A lease-probe receipt is one observation, not network truth.
