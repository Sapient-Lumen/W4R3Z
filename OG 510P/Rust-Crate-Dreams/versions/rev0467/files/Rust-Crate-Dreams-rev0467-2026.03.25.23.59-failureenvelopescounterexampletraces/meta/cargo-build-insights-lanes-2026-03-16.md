# Cargo build-insights lane boundaries — 2026-03-16

This note keeps **P-0035 cargo-build-insights** from collapsing back into a generic “Cargo build performance” crate.

## The distinct lane

**P-0035 cargo-build-insights** should now be treated as the **historical imported-session warehouse** and **regression/trend adjudication** layer.

Its job is to answer questions like:

- when did the regression begin,
- which selected sessions still belong in one comparable series,
- which branch/toolchain/profile/scope changes require a lane split,
- and what stable bundle should another human or tool review?

## Adjacent lanes that must stay separate

1. **Upstream Cargo build-analysis substrate**
   - `-Zbuild-analysis`
   - JSONL logs in Cargo home
   - `cargo report sessions`
   - `cargo report timings`
   - `cargo report rebuilds`

   This is the recorder and native report surface.
   **P-0035 should import it, not replace it.**

2. **P-0469 Cargo Rebuild Explanation Kit**
   - one run or one pair of runs
   - per-unit rebuild causes
   - support/CI handoff bundle
   - timings pointer and exactness receipts for one incident

   This is the **per-run support layer**, not the historical warehouse.

3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - editor/tool-oriented invocation parity
   - command-shape / selection / override drift
   - compile-time-deps versus fuller build coverage truth

   This can feed evidence into P-0035, but it should not be flattened into warehouse history.

4. **P-0490 Cargo Lock Contention Witness Kit**
   - blocked roots
   - lock waits
   - shared target-dir / build-dir / package-cache contention
   - mitigation plans for waiting stories

   Waiting is not automatically the same thing as a historical regression.

5. **P-0468 Cargo Resolver Explanation Kit**
   - graph choice
   - feature pressure
   - duplicate-build / version-selection explanations

   P-0035 may attach resolver bundles, but it should not claim resolver-cause truth by itself.

6. **Artifact / session-linked output lanes**
   - P-0471 artifact handoff
   - sidecar contracts
   - publish receipts

   Those lanes may attach a session id.
   That does **not** make them historical build warehouses.

## What a worthy crate contribution looks like now

A worthy implementation should provide:

- a stable **warehouse schema** above unstable Cargo session surfaces,
- explicit **series comparability** and **lane-split** decisions,
- claim-by-claim **exactness receipts**,
- stable **import receipts** with unknown-field preservation,
- and portable bundles for PR review / CI / internal performance triage.

The worthy crate is **not**:

- a giant dashboard-first product,
- a Cargo replacement recorder,
- a fuzzy “build doctor” that mixes rebuild cause, resolver cause, and contention into one answer,
- or an HTML timing scraper pretending to be the durable machine contract.

## Questions future passes should answer before expanding this lane

1. Is the new artifact about **history across many runs**, or is it really per-run support?
2. Does the proposed judgment depend on **series comparability** or on one invocation's evidence?
3. Is the crate preserving **exactness and provenance**, or quietly flattening imported Cargo data into certainty?
4. Does the value survive without a dashboard?
5. Should the proposal import adjacent resolver / contention / parity artifacts rather than duplicate them?
