# Side-effect journal boundary

The side-effect journal is local restart memory for future public-edge side effects. It is intentionally modeled before any live side effects exist.

Journal entries have phases:

```text
prepare -> commit
prepare -> abort
```

They bind action, profile, service, scope, request, payload, idempotency key, side-effect target, profile-edge digest, live-adapter digest, handler-capsule digest, optional SAM-canary digest, hard-negative count, sequence, previous digest, family/path family, and signature.

The journal rejects:

- replay;
- sequence rollback;
- same-sequence forks;
- previous-link mismatch;
- phase regression;
- idempotency-key conflicts;
- component digest drift;
- hard-negative pressure.

The core idea is that a component acceptance is not sticky state. Only a signed, exact-boundary journal step can advance local side-effect memory.
