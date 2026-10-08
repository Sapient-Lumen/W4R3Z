# Frontier salience refresh — 2026-03-23 (205)

This note exists to keep the archive broad while avoiding proposal spam.

## Main judgment

After another current-source sweep, the archive still looks strongest when it prioritizes **receiver-facing support contracts** for ecosystem pain rather than another wave of wrappers, bots, or hosted portals.

The top frontier should therefore remain:

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## What changed in the frontier this pass

This pass does **not** change the ordering.
It changes the strength of **P-0536**.

The crate-knowledge lane now looks more implementation-ready because official docs make a sharper distinction between:

- **floating convenience locators** (`latest`, semver ranges, `*`) and pinned review surfaces;
- **default-target docs pages** and target-specific hosted pages;
- **hosted HTML pages**, **hosted rustdoc JSON**, and **download archives with caveats**;
- and **query classes that can really support citations** versus classes that still need manual review.

That means the lane is no longer only “package crate docs for machine consumers.”
It can now own a compact product for **citation locators** and **citation-capability ceilings** above current docs.rs/rustdoc substrate.

## Broad territory map

### Tier A — cross-cutting, still under-served, worthy of “epic” treatment

1. **Compile iteration / local feedback**
   - still strongest because compile-time pain remains universal;
   - the missing value is a support contract for **reload surface**, **restart ceiling**, and **latency-budget truth**.

2. **Ecosystem navigation / starter-set choice**
   - still high-value because crate selection remains tacit and sticky;
   - the missing value is a decision packet for **candidate basis**, **support visibility**, **starter-set scope**, and **revisit triggers**.

3. **Dependency lifecycle / transition planning**
   - still high-value because teams need seam-backed answers, not more popularity data;
   - the missing value is a transition-support layer for **criticality**, **override authority**, **freshness**, and **replacement readiness**.

4. **Crate knowledge / machine-facing docs handoff**
   - now stronger because a machine-facing pack without citation-grade locators still leaves downstream tools guessing about version pins, target pages, and anchor fidelity;
   - the missing value is a bundle for **material basis**, **claim traces**, **query-support scope**, **citation locator resolution**, and **citation-capability ceilings**.

5. **Concurrency semantics**
   - still strong because the ecosystem now has enough concrete semantics to classify;
   - the missing value is a support contract for **reentrancy**, **fairness/progress**, **wait cancellation**, **panic/recovery posture**, and **execution-context boundaries**.

### Tier B — strong but one notch narrower or more adjacent

- **P-0524 Crate Example Surface Pack Kit**
- **P-0489 Cargo Build-Dir Consumer Transition Kit**
- **P-0486 Debuggability Support Contract Kit**
- **P-0121 FFI Boundary Conformance Kit**
- **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical takeaway

The repo should continue preferring **deepening passes** on the top frontiers over increasing proposal count.

For crate-knowledge specifically, the next worthwhile proving grounds are:

1. one floating docs.rs shorthand URL resolved into a pinned locator;
2. one target-specific item/docs page where default-target assumptions would be wrong;
3. one compact support pack that is citation-ready for setup/API lookup but manual-review-only for performance/security/safety;
4. one doctor rule that rejects “supported” query classes without locator coverage;
5. and one portable bundle that keeps material basis, claim traces, and citation ceilings visibly separate.

Do not spend the next pass on a chat UI, retrieval ranking, or offline docs mirror unless it exports stronger receipts than **P-0536** now can.
