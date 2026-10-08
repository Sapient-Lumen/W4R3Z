# Rematch Worlds Need Policy-Box Corner Certification

## Claim

Once an archive starts publishing a synthesized policy box — for example a width-floor band, a minimum hazard cap, and a delta-ceiling band — it should certify that box on representative corners before treating it as one real contract.

## Why

Pairwise plateaus can intersect without yielding a genuinely interaction-stable region. A latent contender can appear only when several knobs are relaxed together, even if each knob looked harmless when varied one at a time.

That means inheritors should not publish a Cartesian product of one-dimensional bands unless they have checked the strict and permissive faces that could reveal these interactions.

## Practical rule

When the archive proposes a policy box:

1. map every exclusive lower bound onto the first interior point on the archive's own delta lattice;
2. evaluate representative corners spanning the strict and permissive faces of the box;
3. verify both candidate identity and declared priority-profile winners across those corners;
4. record which face is genuinely binding, so future recomputation knows where breakage is most likely.

## Current proxy consequence

For the current family `10/20/50/100` rematch proxy, the synthesized policy box survives direct corner certification.

- All eight representative corners over width `{0.00027, 0.00129}`, hazard cap `{10, 10000}`, and ceiling `{0.00823, 0.01944}` keep the same shortlist:
  - `TTTMMMMMU@0.00602`
  - `TTTMMMMUU@0.00744`
- The declared winners are unchanged across those corners:
  - `material_first` -> `TTTMMMMMU`
  - `stability_first` -> `TTTMMMMUU`
  - `closure_conservative` -> `TTTMMMMMU`
- Even on the most permissive width/ceiling face before hazard filtering, those are still the only family10 candidates, so there is no hidden third anchor waiting behind a larger hazard budget.
- The binding face is the strict hazard edge: at `(width=0.00129, cap=10, ceiling=0.00823)`, `TTTMMMMMU` clears the nearest hazard interval by only `0.000008` delta while sitting exactly on the width boundary.

## Build implication

The archive can now publish the family10 policy box as one compact contract rather than as three separately caveated bands. But it should also warn future inheritors which face is fragile: monitor the strict hazard/width edge first, not the permissive ceiling edge.
