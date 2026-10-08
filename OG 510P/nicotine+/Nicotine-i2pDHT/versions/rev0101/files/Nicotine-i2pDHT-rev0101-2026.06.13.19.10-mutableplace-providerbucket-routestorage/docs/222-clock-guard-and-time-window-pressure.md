# Clock guard and time-window pressure

Clock guard is the rev0024 answer to a quiet but severe DHT bug class: valid signatures can be stale, premature, overlong, forked at the same sequence, or valid only because local clock skew masks the problem.

`clockguard.py` models `ClockWindow` observations for relay tickets, gossip statements, contact leases, witness receipts, namespace policies, and anti-entropy sketches. It checks:

- internal time-window consistency;
- max TTL;
- future and past skew allowances;
- local highest-sequence rollback;
- same-subject same-sequence fork pressure;
- family diversity when a batch of clock observations is used to proceed.

The module does not solve time. It makes time a typed local evidence surface before expensive work or mutable control-plane acceptance.

Design rule:

```text
A fresh signature is not the same thing as a fresh fact.
```
