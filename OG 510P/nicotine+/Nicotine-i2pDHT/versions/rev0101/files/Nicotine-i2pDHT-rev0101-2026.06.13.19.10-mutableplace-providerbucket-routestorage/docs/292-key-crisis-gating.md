# Key crisis gating

`keycrisis.py` models live crisis notices for keys used by peer leases, mutable heads, provider records, garden offers, and future application control planes.

Notice kinds:

- key compromised
- destination lost
- signer forked
- emergency freeze
- succession required

The gate does not create global bans. It creates local pressure before a risky keyed operation runs. A key-compromise notice blocks keyed operations unless matching successor evidence is present. A destination-lost notice is softer: it accepts with watch and should push route repair. Same-sequence crisis forks quarantine.

This lets a FLOSS network acknowledge maintainer/operator/user crisis response without making one party own cryptographic truth for the whole DHT.
