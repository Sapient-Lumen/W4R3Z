# Rematch worlds need declared hazard-cap profiles

## Claim

Once a rematch archive has already declared its budget family and minimum shared-core width, it should also declare the hazard-cap profile it is using — but it should be explicit about whether that profile is actually changing the shortlist or merely riding along as a non-binding guardrail.

## Why

A hazard band is a real modeling choice: it encodes how much extra paired-seed budget the archive is willing to spend before calling a delta neighborhood too knife-edge to trust. But a declared choice can still be inactive in a particular proxy. If the archive acts as though the hazard cap selected the final shortlist when the shortlist would have been identical across a wide cap range, then the public contract misattributes where the substantive judgment actually happened.

## Current proxy lesson

In the current leave/rematch proxy, once the family is fixed to `10/20/50/100` and the width floor is fixed at `0.0010`, the strict sub-`0.01` shortlist is unchanged across tested hazard caps `100`, `500`, `1000`, and `10000`: the same two candidates survive, and the same declared priority profiles pick the same winners. Meanwhile the family `4/10/20/50/100` stays empty at the same width floor across the same hazard-cap range.

So the discriminating choices in this proxy are the family declaration and the width floor. The hazard cap still belongs in the methods contract, but it is not the thing resolving the shortlist.

## Archive consequence

When publishing a shortlist contract, report all three layers distinctly:

1. exact budget family,
2. minimum shared-core width (preferably as a stable band when available),
3. hazard-cap profile.

Then say which of those layers are active filters in the current data. That keeps the archive from giving ceremonial credit to a guardrail that did not actually affect the recommendation.

## Minimal implementation shape

For each declared family/width profile that matters, publish a tiny hazard-cap table:

- tested hazard caps,
- surviving candidate count at each cap,
- candidate identities at each cap,
- whether declared priority winners change across caps.

If the table is invariant, say so plainly. If it is not invariant, then the hazard-cap declaration has become a first-class scientific choice and should be treated like the family declaration rather than a footnote.
