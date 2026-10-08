# Rematch parent anchors are boundary-biased

## Claim

A budget-admissible rematch band should not normally publish its inherited min-cost anchor directly. In the current proxy, that anchor is often just the **leftmost admissible gridpoint**, which makes it a fragile boundary artifact rather than a scientifically privileged SESOI.

## Why

Once a parent band has already been declared admissible, the right scalar anchor is no longer “the cheapest point we happened to notice first.” The right compact anchor is the point that best represents the **panel-label summary the report is actually claiming**.

A raw parent-band anchor creates two avoidable problems:

1. **Boundary bias**: the chosen delta can sit exactly on a topology boundary even though the same parent summary survives across a wider interior interval.
2. **False exactness**: a tiny change in rounding or a later re-render can make the published anchor look like it was theoretically special when it was really just a bookkeeping endpoint.

## Current proxy consequence

In the current 20 admissible parent bands, `6` inherited anchors sit exactly on a topology boundary. Replacing the parent anchor with the midpoint of the **topology-stable subband that actually contains it** improves boundary buffer in `19 / 20` bands, preserves the parent topology in `20 / 20`, preserves the parent label counts in `20 / 20`, and stays within the same declared cap in `20 / 20`.

So the local evidence says the archive should stop treating the inherited parent anchor as the default handoff object.

## Implementor rule

If a rematch benchmark emits one scalar delta anchor per admissible parent band, emit the **topology-preserving interior anchor** instead:

- locate the topology-stable subband that contains the inherited parent anchor,
- take its midpoint,
- publish the resulting buffer to the nearest topology boundary,
- and publish the buffer gain relative to the inherited parent anchor.

That keeps the archive compact while stripping out a large class of accidental boundary fragility.
