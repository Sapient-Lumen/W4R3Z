# Record expiry and visible rehabilitation countdowns are institutional dials

Recent trust-and-exclusion theory adds a compact warning for any Concord world that keeps only a bounded recent record of behavior.

- `RS-GR-142` studies trust enforcement when transgression records are retained only for a finite window.
- The key warning is that temporary exclusion can unravel when others can identify agents who are **close to rehabilitation** and selectively trust them on the eve of record expiry.

## Why this matters for Concord

Once a world has sanctions, bounded memory, or expiring reputation records, two hidden choices start to matter a great deal:

1. **record-retention length**, and
2. **how legible the countdown to rehabilitation is**.

If everyone can cheaply tell that an agent's bad record is about to expire, then a benchmark may reward end-of-sentence opportunism rather than durable trustworthiness.
That is not the same institution as one where rehabilitation timing is noisy, hidden, or not individually targetable.

So record expiry is not just archive hygiene.
And rehabilitation timing is not just UI state.
Together they shape whether exclusion is credible, gameable, or self-undermining.

## Minimal implementor handoff

If Concord adds bounded-memory trust, exclusion, or expiring reputations, publish at least:

1. record-retention window length,
2. whether expiry is deterministic or stochastic,
3. whether agents can observe another agent's exact distance to rehabilitation,
4. whether re-entry is automatic at expiry or requires a fresh qualifying action,
5. one comparison between visible-countdown and hidden-countdown variants before generalizing from exclusion results.

Without that compact contract, future sessions can mistake rehabilitation-legibility effects for deeper reciprocity or punishment effects.
