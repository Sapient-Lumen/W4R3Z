# Frontier salience refresh — 2026-03-23 (206)

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
It changes the strength of **P-0536** again.

The crate-knowledge lane now looks more implementation-ready because the official docs make a sharper distinction between:

- **opaque blob-local IDs** and stable receiver-facing item identity;
- **item witnesses** and **citation routes**;
- **same conceptual item across versions/targets** and **same rendered docs page**;
- **docs.rs default-target or floating routes** and **exact version/target review surfaces**;
- and **cross-crate merge substrate** versus a stable public identity contract.

That means the lane is no longer only “package crate docs for machine consumers” or even “resolve citation locators.”
It can now own a compact product for **item witnesses** and **identity-fidelity ceilings** above current docs.rs/rustdoc substrate.

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
   - now stronger because a pack can resolve URLs and still fail to preserve a reviewable notion of “the same item” across versions, targets, or build surfaces;
   - the missing value is a bundle for **material basis**, **claim traces**, **citation locators**, **item witnesses**, and **identity-fidelity ceilings**.

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

1. one exported claim that is tied to a reviewable item witness, not only a locator;
2. one version bump where the same item keeps a witness while the rendered route or selector changes;
3. one target-specific item where default-target routing would otherwise mis-state what was reviewed;
4. one doctor rule that rejects cross-blob identity reuse based only on a rustdoc JSON ID;
5. and one portable bundle that keeps witness identity, locator choice, and claim ceilings visibly separate.

Do not spend the next pass on a chat UI, retrieval ranking, or offline docs mirror unless it exports stronger receipts than **P-0536** now can.
