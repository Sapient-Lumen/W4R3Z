# rev0057 — deadletter-retryquorum-effectreconcile

rev0057 follows the rev0056 recovery mesh into the next risky state: an effect survived restart, cleanup and chaos-budget pressure exist, but the effect may still be prepared-only, ambiguous, retryable, or unsafe to reinterpret.

Strong sentence:

```text
An unresolved effect is not an error log; it is sticky protocol memory until dead-letter, retry quorum, and reconciliation agree at one exact boundary.
```

New active surfaces:

- `deadletter.py` — signed, previous-linked dead-letter entries for prepared-only, ambiguous, retry-exhausted, component-watch, and hard-negative observations.
- `retryquorum.py` — signed retry votes after recovery/dead-letter watch, with budget-lane, family/path diversity, replay/fork, and useful-refusal backoff pressure.
- `effectreconcile.py` — joined local decision surface for terminal commit/abort, retry, dead-letter hold, phase conflict, hard negatives, and boundary drift.
- `reconcilefold.py` — audit/refactor fold tying rev0057 to rev0056 `recoveryfold` predecessor history.

Nonclaim: this is still no-network design-lab code. It is not a production DHT, database, scheduler, resolver, or I2P/SAM transport.
