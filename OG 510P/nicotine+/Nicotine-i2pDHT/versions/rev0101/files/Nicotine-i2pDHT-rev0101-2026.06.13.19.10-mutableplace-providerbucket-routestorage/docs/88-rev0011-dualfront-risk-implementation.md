# rev0011 — dual-start risk implementation

rev0011 starts from deliberately different places instead of polishing live I2P transport:

1. **provider truth** — a signed provider record is a claim, not semantic availability;
2. **garden capacity** — a giving supernode needs bounded signed refusal, not silent failure;
3. **lookup frontier pressure** — fast low-latency paths can still be captured by one family.

The shared risk is premature acceptance. A DHT client can be tricked by valid signatures, polite refusals, or fast answers if it treats any of them as authority.

## Implemented surfaces

```text
src/i2p_dht_lab/providerpoison.py      challenge/receipt provider-poison analysis
src/i2p_dht_lab/provider_poison.py     local provider memory, backoff, quarantine
src/i2p_dht_lab/gardenrefusal.py       garden admission and useful-refusal receipts
src/i2p_dht_lab/garden_churn.py        mutable-head lookup under stale/refusing/dropping gardens
src/i2p_dht_lab/churnforge.py          family-rotating frontier and transcript digests
```

Tests:

```text
tests/test_rev0011_providerpoison_gardenrefusal.py
tests/test_rev0011_provider_garden_churn.py
tests/test_rev0011_churnforge.py
```

## Current rule

```text
Do not make live transport pretty before the disagreement algebra exists.
```

The code is still a deterministic toy pressure surface. That is the point: these cases should be cheap to replay before SAM streams, I2P latency, router churn, and real operator behavior make the signal noisy.

## Nonclaim

These tests do not prove provider honesty, garden honesty, path independence, Sybil resistance, anonymity, or production safety. They only make the hardest guesses concrete enough to falsify next.
