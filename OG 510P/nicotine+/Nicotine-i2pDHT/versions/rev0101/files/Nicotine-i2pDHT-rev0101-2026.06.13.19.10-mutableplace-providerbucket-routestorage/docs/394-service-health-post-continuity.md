# Service health after continuity

`servicehealth.py` treats post-continuity service health as local evidence, not reputation.  It joins continuity acceptance, probes, receipts, load observations, refusals, active withdrawal, hard negatives, family diversity, freshness, and metadata budgets before a garden service may be considered locally healthy.

Risk cases pinned in tests:

- active withdrawal overrides otherwise good health;
- replayed observations are quarantined;
- raw-key exposure and metadata budgets are enforced;
- one-family probe monoculture is not healthy diversity;
- refusal-heavy loops are not healthy contribution;
- scope drift blocks acceptance.

The point is to keep "service is still up" separate from "some branch returned a valid signature."
