# Wake from amnesia — rev0011

You are inside a speculative Python-first DHT cube for a DHT above I2P. It is not a production DHT and not an application integration.

The current revision is rev0011 `providerpoison-gardenrefusal-churnforge`.

## Memory hook

rev0010 attacked mutable-head truth:

```text
valid signed mutable head != accepted latest truth
```

rev0011 attacks the surrounding claim surfaces:

```text
valid signed provider record != useful provider
signed garden refusal != target unavailable
fastest lookup frontier != healthy path diversity
```

## What exists in code

```text
providerpoison.py      challenge/receipt provider analysis
provider_poison.py     provider memory, quarantine, backoff
gardenrefusal.py       admission and useful-refusal receipts
garden_churn.py        garden mutable-head lookup under stale/refusing/dropping behavior
churnforge.py          family-rotating frontier and transcript digests
```

## What to read first

```text
START_HERE.md
docs/88-rev0011-dualfront-risk-implementation.md
docs/89-provider-poisoning-and-semantic-confirmation.md
docs/90-garden-useful-refusal-and-overload.md
docs/91-churn-frontier-and-transcript-pressure.md
docs/92-python-surface-rev0011.md
```

## Next sharp edge

Connect provider probes to garden sentinel witnessing, private/sampled provider checks, and delegated reprovide capabilities. A garden should be able to help reprovide, but only through explicit scoped authority that can be revoked or ignored locally.
