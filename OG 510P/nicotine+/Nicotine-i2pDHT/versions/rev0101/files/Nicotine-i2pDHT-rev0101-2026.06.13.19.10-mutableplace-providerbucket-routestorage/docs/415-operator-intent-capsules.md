# Operator intent capsules

`operatorintent.py` treats manual control as protocol data.

An operator intent binds:

```text
action
profile id
service name
scope digest
request digest
sequence
previous intent digest
reason digest
operator key
validity window
bridge-public bit
signature
```

The toy verifier rejects bad signatures, replay, sequence rollback, same-sequence fork, previous-link mismatch, profile drift, service/scope/request drift, disallowed actions, resume-disabled policy, and bridge-disable actions that are not explicitly bound to public bridge exposure.

The dream: a future garden operator can say “pause this service,” “demote this node to leaf,” or “disable public bridge mode,” but the cube will not let that become an unscoped override that bypasses drain, breaker, continuity, or profile-memory checks.
