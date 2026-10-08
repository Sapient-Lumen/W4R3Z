# rev0012 — probewitness / privateprovider / chaossweep

rev0012 keeps the cube in DHT-design space and starts from deliberately different places:

1. **Provider probe privacy and semantic truth.** A signed provider record is not availability truth, but probing a provider can leak interest. We need pressure objects for both problems at once.
2. **Garden/sentinel witnessing.** Gardens can preserve evidence, but receipts are not quorum. A witness mesh must resist family monoculture and self-contradiction.
3. **Captured fast windows and wire fixtures.** Lookup fronts can appear healthy while the fastest answers are captured. Canonical signing/transcript shape should be tested before live SAM/I2P transport.

## New hard guesses under test

```text
real provider probes must be budgeted
commitment-only witness surfaces are useful even if providers see more
one garden family is not diversity
contradictory witnesses should quarantine themselves
family caps can reduce fast-window capture
wire canonicalization needs tests before network code
```

## Why this is risky first

Provider records are the place where a DHT becomes useful and dangerous. They are useful because they point to data, heads, manifests, and services. They are dangerous because they invite false availability, interest leakage, and poisoning by fast but dishonest responders.

Witness receipts are similarly double-edged. They help leaves and gardens remember that something looked false, stale, forked, or empty. But a fleet of colluding witnesses can manufacture noise. rev0012 encodes the stance that witness receipts are local evidence, not protocol truth.

## Nonclaims

No live I2P/SAM transport. No production provider-probe protocol. No private retrieval. No production witness quorum. No proven Sybil resistance. No anonymity or metadata-safety guarantee.
