# Decay mesh evidence aging

Evidence is not a scalar score. Positive provider or liveness evidence should decay quickly. Hard negative evidence — tombstones, forks, stale mutable heads, revocations, provider-false observations — deserves longer retention.

`decaymesh.py` tests:

- hard negatives remain under hard-retention windows
- fresh soft positives require family diversity
- old soft positives drop
- same-family replay refreshes quarantine instead of preserving poisoned memory
- same-sequence conflicting mutable facts quarantine

The intent is local memory hygiene, not deletion consensus.
