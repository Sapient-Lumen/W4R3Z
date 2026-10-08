# Commit barrier public edge

The commit barrier exists because staged public-edge evidence can be individually valid while collectively unsafe.

A commit candidate binds:

- public action: refresh, withdraw, or repair
- profile and service
- scope, request, subject, and payload digests
- dry-run report digest
- public outbox report digest
- audit-gap report digest
- egress report digest
- scope-journal report digest
- idempotency key
- public effect digest
- sequence and previous commit digest
- family and path-family hints
- signer key and signature

The current rule is intentionally strict:

> valid components are observations; the commit barrier is the joined local permission boundary.

A component watch flag blocks commit unless the caller explicitly allows watch debt. This keeps repair/watch/appeal/evidence gaps from silently turning into public writes.

Idempotency is handled as a pressure surface. Replaying the same idempotency key with the same public effect digest is locally idempotent. Replaying it with a different public effect digest is quarantined.
