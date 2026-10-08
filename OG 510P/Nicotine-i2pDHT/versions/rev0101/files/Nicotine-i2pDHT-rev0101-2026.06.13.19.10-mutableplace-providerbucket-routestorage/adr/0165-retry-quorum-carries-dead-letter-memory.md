# ADR 0165 — Retry quorum carries dead-letter memory

Status: accepted in rev0057.

Retry authorization must bind recovery mesh, dead-letter report, chaos budget, exact scope, and idempotency key. A retry cannot erase dead-letter memory.

Useful refusals produce backoff/watch, not fake progress.
