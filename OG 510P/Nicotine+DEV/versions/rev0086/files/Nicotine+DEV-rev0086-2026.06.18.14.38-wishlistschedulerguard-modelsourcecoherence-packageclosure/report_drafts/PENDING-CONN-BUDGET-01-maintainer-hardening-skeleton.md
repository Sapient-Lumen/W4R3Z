# PENDING-CONN-BUDGET-01 maintainer hardening skeleton

## Summary

Pending peer connection state can retain outbound peer messages without an explicit per-user or global budget while address resolution, indirect connection setup, or socket-cap deferral is unresolved.

## Current behavior witness

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus python -m pytest maintainer_artifacts/pending-conn-budget-01/test_pending_peer_connection_budget_reproducer.py
```

Expected current behavior:

```text
4 tests pass in each checked lane, demonstrating current behavior rather than fixed behavior.
```

## Suggested invariant

```text
Pending peer egress state should be bounded per user, per connection type, and globally. When the budget or TTL is exceeded, all affected queued messages should fail through an explicit error path rather than silently accumulating or being lost.
```

## Compatibility constraints

Do not break ordinary direct/indirect connection fallback. A small queue of peer messages while a connection is being established is legitimate and necessary for normal browse/info/download workflows.
