# Rematch worlds need delta-ceiling plateau contracts, not one magical `0.01`

After the archive declares an exact budget family, a minimum shared-core width, and a hazard guardrail, one more hidden policy choice still remains: **where exactly is the low-delta ceiling drawn?**

The new derived report in `artifacts/reports/rematch_proxy_delta_ceiling_plateau_snapshot_20260306.{md,json}` shows that this choice should also be published as a **stable band**, not as one ceremonial scalar such as `0.01`.

In the current leave/rematch proxy, once the family is fixed to `10/20/50/100`, the width floor is fixed at `0.0010`, and the archive keeps only hazard-clear cores:

- every ceiling in `0.00822 < ceiling <= 0.01944` yields the **same** two-candidate shortlist:
  - `TTTMMMMMU` at `0.00602`
  - `TTTMMMMUU` at `0.00744`
- the inherited `0.01` ceiling sits comfortably inside that band, with `0.00944` of extra headroom before a third candidate can enter,
- only above `0.01944` does a wider but much higher-delta candidate `TTTTTTMUT@0.01845` appear, and then the `stability_first` priority profile flips to that higher-delta anchor.

So the present archive is accidentally overclaiming precision when it talks as though “sub-`0.01`” were the uniquely canonical low-delta contract. In this proxy, `0.01` is just one point inside a much broader shortlist-preserving plateau.

That changes how the inheritor should write the public contract:

1. declare the exact budget family,
2. declare the width-floor band,
3. declare the hazard-cap profile,
4. declare a **delta-ceiling band** that leaves the shortlist unchanged,
5. only then declare the priority profile that resolves the shortlist to one scalar anchor, if a scalar is still needed.

This ordering matters because it isolates the real remaining judgment. Below `0.01944`, the shortlist stays compact and low-delta; above it, the ceiling itself starts changing what “stability first” means. So the salient boundary is not `0.01` but the entry point of the next candidate regime.

For the alternative family `4/10/20/50/100`, there are still no width-qualified hazard-clear candidates on `[0, 0.02]`, so ceiling tuning cannot rescue that family once width has already been fixed at `0.0010`.
