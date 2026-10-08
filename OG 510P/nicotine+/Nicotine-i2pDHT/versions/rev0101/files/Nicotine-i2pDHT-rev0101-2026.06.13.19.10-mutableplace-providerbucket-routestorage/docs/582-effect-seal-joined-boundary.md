# Effect seal joined boundary

`effectseal.py` is the no-network final seal before a future handler or public-edge side effect could become sticky authority.

It joins:

- handler replay;
- handler quench/cooldown;
- side-effect journal final phase;
- restart-chaos cuts;
- fuzz-ledger persistence;
- fuzz-shrink coverage.

A valid component report is not enough. The seal must bind the same action, phase, profile, service, scope, request, payload, idempotency key, component digests, sequence, previous seal, family, and path family.

Cooldown, watch pressure, hard-negative pressure, digest drift, replay, rollback, forks, and previous-link mismatch are explicit outcomes.
