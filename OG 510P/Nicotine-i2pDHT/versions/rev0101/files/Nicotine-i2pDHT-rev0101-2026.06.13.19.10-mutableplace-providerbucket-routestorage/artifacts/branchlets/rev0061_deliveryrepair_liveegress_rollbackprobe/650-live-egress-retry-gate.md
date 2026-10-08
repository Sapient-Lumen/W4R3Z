# Live egress retry gate

`liveegress.py` joins live-send gate, delivery repair, rollback probe, send fence, and delivery witness reports before a future retry or withdraw side effect could be staged.

The gate makes retry idempotency explicit.  A retry idempotency key must differ from the original live-send key, must bind to the original gate, and must include the retry attempt number.

Decisions include:

- `accept_retry_ready`,
- `accept_withdraw_ready`,
- `hold_dead_letter_memory`,
- `hold_rollback_unknown`,
- `hold_retry_budget_exhausted`,
- quarantine for delivered-already, remote-commit-seen, hard negatives, boundary drift, idempotency drift, payload budget, and diversity failure.

needle: live egress
