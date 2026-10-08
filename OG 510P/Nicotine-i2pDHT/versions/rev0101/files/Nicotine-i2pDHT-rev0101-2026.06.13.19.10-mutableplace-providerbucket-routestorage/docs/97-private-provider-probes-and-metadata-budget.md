# Private-ish provider probes and metadata budget

The provider plane now has a separate pressure module: `privateprovider.py`.

The goal is not to claim private retrieval. The goal is to stop pretending semantic confirmation is free.

## Objects

```text
ProviderCandidate
PrivateProbeBudget
PrivateProviderProbe
PrivateProviderProbePlan
PrivateProbeAssessment
```

## Rules encoded

- Real probes may expose the content key to selected providers.
- Witness-visible surfaces can be commitment-only.
- Decoys can create a less obvious probe shape.
- Family caps stop the fastest family from receiving the whole probe budget.
- A plan can be rejected for insufficient real-family diversity, raw-key overexposure, or no decoys.

## Current guess

The DHT should allow multiple provider confirmation modes:

```text
raw confirmation        high utility, high metadata
commitment witnessing   evidence without raw witness key exposure
decoy padded probing    extra traffic, less obvious shape
sampled probing         fewer confirmations, less leak surface
```

A future transport can make this better or worse, but the DHT design needs the knobs now.

## What tests cover

- Real probes are selected across families.
- Decoys are added and do not carry the raw content key.
- One-family monoculture is rejected even when many candidates exist.
- Commitments and decoy keys are deterministic and distinct.
