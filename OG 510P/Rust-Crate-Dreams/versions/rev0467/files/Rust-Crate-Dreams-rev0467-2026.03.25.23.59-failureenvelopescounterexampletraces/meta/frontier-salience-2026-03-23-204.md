# Frontier salience refresh — 2026-03-23 (204)

This note exists to keep the archive broad while avoiding proposal spam.

## Main judgment

After another current-source sweep, the archive still looks strongest when it prioritizes **receiver-facing support contracts** for ecosystem pain, not another wave of helpers, wrappers, or dashboards.

The top frontier should therefore remain:

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## What changed in the frontier this pass

This pass does **not** change the ordering.
It changes the strength of **P-0538**.

The concurrency lane now looks more implementation-ready because current docs support a sharper separation between:

- **queue withdrawal** on cancellation (`Notify`, `Semaphore`, `Mutex`, `RwLock`);
- **true cancel safety with no message/value consumption** (`watch::Receiver::changed`, `mpsc::Receiver::recv`);
- **execution-context legality** (`blocking_*` methods that panic inside async contexts);
- and **panic recovery posture** (`std` poisoning, advisory recovery, `parking_lot` no poisoning, nightly `nonpoison`).

That means the lane is no longer only “document fairness/reentrancy.”
It can now own a compact product for **wait-cancellation class** and **failure-recovery posture** above existing primitive docs.

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
   - still high-value because docs, rustdoc JSON, examples, and README presence do not by themselves create a reviewable machine handoff;
   - the missing value is a bundle for **material basis**, **claim traces**, **query-support scope**, and **refusal zones**.

5. **Concurrency semantics**
   - now stronger than before because the ecosystem has enough concrete semantics to classify;
   - the missing value is a support contract for **reentrancy**, **fairness/progress**, **wait cancellation**, **panic/recovery posture**, and **execution-context boundaries**.

### Tier B — strong but one notch narrower or more adjacent

- **P-0524 Crate Example Surface Pack Kit**
- **P-0489 Cargo Build-Dir Consumer Transition Kit**
- **P-0486 Debuggability Support Contract Kit**
- **P-0121 FFI Boundary Conformance Kit**
- **P-0125 Cargo SBOM Precursor Workbench Kit**

## Practical takeaway

The repo should continue preferring **deepening passes** on the top frontiers over increasing proposal count.

For concurrency specifically, the next worthwhile proving grounds are:

1. one queue-withdrawal surface (`Notify` or `Semaphore`);
2. one truly cancel-safe receive surface (`watch::changed` or `mpsc::recv`);
3. one poisoning/advisory-recovery surface from `std`;
4. one no-poisoning surface from `parking_lot` or nightly `std::sync::nonpoison`;
5. and one portable bundle that keeps all of those axes visibly separate.

Do not spend the next pass on another mutex wrapper, another async tutorial crate, or another deadlock detector unless it exports better receipts than **P-0538** now can.
