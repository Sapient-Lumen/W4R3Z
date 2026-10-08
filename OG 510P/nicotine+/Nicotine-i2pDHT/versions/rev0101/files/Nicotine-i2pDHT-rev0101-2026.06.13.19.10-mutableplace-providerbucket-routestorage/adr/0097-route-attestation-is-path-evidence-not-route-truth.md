# ADR 0097 — route attestation is path evidence, not route truth

Contact leases and route gossip are not enough when one introducer path can hand out many valid-looking contacts. Route attestations are accepted only as fresh, signed, lease-bound path evidence. They do not create identity truth, reputation, or route authority.

Status: accepted in rev0024.
