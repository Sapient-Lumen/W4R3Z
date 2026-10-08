# Service breaker pressure

`servicebreaker.py` models a circuit breaker for garden services after continuity has already passed.

A service may trip open on:

```text
false service
hard negative
active withdrawal
operator pause
refusal-only loop
failure streak
```

A previously open breaker may half-open only when recovery observations are diverse across families. One-family recovery is treated as capture pressure, not service health.

The important distinction is that useful refusal remains useful capacity evidence, but repeated refusal-only windows are not healthy service. A garden should be able to refuse; it should not be able to launder persistent refusal into “I am serving.”
