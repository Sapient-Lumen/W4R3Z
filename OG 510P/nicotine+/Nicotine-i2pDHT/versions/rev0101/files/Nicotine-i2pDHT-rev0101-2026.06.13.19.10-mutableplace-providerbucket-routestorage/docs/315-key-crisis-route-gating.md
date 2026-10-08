# Key-crisis route gating

`crisisroute.py` joins key-crisis gates to signed contact leases and succession evidence before route use.

The design target is a future DHT where sticky I2P entrances survive normal churn but do not survive key compromise by accident. A route/contact lease signed by a compromised key is still cryptographically valid, but local policy must block it once live crisis memory says the key is compromised, frozen, forked, or succession-required.

The accepted successor path requires:

```text
live crisis gate says successor recovery is acceptable
route lease is fresh and signed by the successor key
co-signed succession evidence maps old key -> successor key
no live revocation or tombstone pressure blocks the route
```

Destination-loss is softer: it can be accepted with watch pressure, because a lost destination may require alternate routing without implying signer compromise.

This is local pressure, not a global ban system. It keeps old valid signatures from silently routing future work after a crisis.
