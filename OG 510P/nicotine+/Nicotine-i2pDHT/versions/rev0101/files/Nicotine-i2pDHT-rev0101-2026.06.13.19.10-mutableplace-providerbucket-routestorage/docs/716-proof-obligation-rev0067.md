# Proof obligations — rev0067

The toy tests now prove these local properties:

```text
settlement accepts only when duplicate closure and ACK evidence agree
settlement quarantines dropped contradiction memory
archive rejects missing contradiction entries
archive detects same-sequence forks
prune permits soft repair pruning after archive
prune blocks attempts to drop contradiction evidence
fold audit sees current rev0067 surfaces and rev0066 predecessor
```

Future proof debt:

```text
exercise crash-cut archive writes
join archive/prune with a real persistence lane
model malicious remote witnesses after closure
carry these boundaries into a future live transport harness
```
