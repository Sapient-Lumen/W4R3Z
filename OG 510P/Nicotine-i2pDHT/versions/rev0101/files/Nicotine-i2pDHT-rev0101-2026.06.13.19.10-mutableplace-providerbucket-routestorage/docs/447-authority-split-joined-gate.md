# Authority split joined gate

A key compartment can pass locally and still be unsafe to use. rev0043 models a second gate: multiple component reports must agree at the same profile/scope/object/request boundary.

Required component reports may include:

- key compartment result;
- operator-key state;
- profile cooldown state;
- router harness state;
- service catalog state;
- hard-negative scan.

The joined gate rejects:

- missing required components;
- bad signatures;
- expired/future reports;
- replayed reports;
- profile, scope, object, or request drift;
- failed/quarantined components;
- actor-key reuse across components;
- same-component sequence forks;
- low family diversity.

The important design point is not bureaucracy. It is to avoid turning one valid local report into permission for another side effect with a different scope or request.

```text
A valid key binding is not permission to spend bandwidth, publish a service, mint a ticket, or resume a bridge.
```
