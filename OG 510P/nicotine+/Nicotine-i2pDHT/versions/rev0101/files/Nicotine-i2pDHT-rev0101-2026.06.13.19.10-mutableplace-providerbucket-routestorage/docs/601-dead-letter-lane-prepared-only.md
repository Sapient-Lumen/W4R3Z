# Dead-letter lane for prepared-only effects

A prepared-only effect after restart is not harmless. It is the state where a future implementation is most tempted to either retry too eagerly or forget too aggressively.

`deadletter.py` makes that state explicit:

```text
effect seal + recovery mesh + side-effect journal + chaos budget
  -> signed dead-letter entry
  -> previous-linked local memory
  -> exact profile/service/scope/request/payload/idempotency boundary
```

The lane checks signatures, freshness, replay, rollback, same-sequence forks, previous-link mismatch, boundary drift, component digest drift, phase drift, missing `dead_letter` chaos-budget lanes, family/path diversity, and hard-negative pressure.

The key design guess is that dead-letter entries are not trash. They are sticky evidence that lets cleanup, retry, and reconciliation stay honest across restarts.
