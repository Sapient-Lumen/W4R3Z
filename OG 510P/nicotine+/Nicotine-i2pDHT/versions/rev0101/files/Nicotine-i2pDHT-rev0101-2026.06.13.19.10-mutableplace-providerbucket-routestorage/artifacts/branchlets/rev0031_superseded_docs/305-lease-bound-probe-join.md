# Lease-bound probe join

`leaseprobe.py` joins four surfaces before a leased contact is promoted into sticky entrance or route confidence:

- a signed, fresh `ContactLease`
- a lease-bound `LiveProbeReport`
- an `EgressWindowReport` generated from bounded outbound work
- an optional `KeyCrisisGateReport` for the leased public key

The module treats these outcomes differently:

- accepted probe
- accepted with watch pressure
- router unavailable / live probe missing
- purpose mismatch
- key crisis block
- egress budget quarantine
- probe-family replay or monoculture

A valid lease alone is not enough. A successful probe alone is not enough. An affordable egress window alone is not enough. rev0031 makes the join explicit.
