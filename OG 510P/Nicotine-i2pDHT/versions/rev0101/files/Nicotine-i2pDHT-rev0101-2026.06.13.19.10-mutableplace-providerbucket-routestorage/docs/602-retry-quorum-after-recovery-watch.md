# Retry quorum after recovery watch

Retries are local side effects wearing a friendly name. rev0057 makes retry authorization a small quorum-like evidence surface rather than a boolean from one component.

`retryquorum.py` adds signed retry votes:

```text
retry_ready
retry_after
still_dead_letter
refuse_usefully
hard_negative
```

A retry quorum binds recovery mesh, dead-letter report, chaos budget, action, profile, service, scope, request, payload, and idempotency key. It rejects missing retry-budget lanes, stale/replayed votes, forks, boundary drift, component digest drift, hard negatives, one-family monoculture, and one-path monoculture.

Useful refusal remains meaningful, but refusal-only evidence results in backoff/watch rather than pretend progress.
