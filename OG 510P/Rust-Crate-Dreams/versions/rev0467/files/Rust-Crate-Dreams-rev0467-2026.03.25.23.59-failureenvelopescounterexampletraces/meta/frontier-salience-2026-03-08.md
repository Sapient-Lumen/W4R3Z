# Frontier salience scan — 2026-03-08

This file exists to resist archive sprawl.

The archive is now large enough that a good pass should usually do one of three things:

1. **promote one genuinely sharp new seam**,
2. **compress / rank existing territory**, or
3. **add hygiene that prevents LLM drift**.

This pass mostly did **(1)** and **(2)**.

## External signals worth honoring right now

- The 2025 State of Rust survey still points to **resource usage (slow compile times and storage usage)** as a major productivity problem, while **debugging** remains a prominent pain point.
- Rust’s 2026 goals keep pushing toolchain surfaces that make support and review more machine-readable: **public/private dependencies**, **SBOM support**, and **building-block workflows** such as `build-std` and Cargo plumbing.
- The archive’s recent foreign-ecosystem work now has a real pattern: Python, Apple, Node/npm, and NuGet already have meaningful substrate, so the sharper missing value is often a **release contract / support bundle / loader receipt**, not another raw binding layer.
- The JVM now fits that same pattern more clearly than before because modern Java documents native-library loading as a more explicit **restricted/native-access** surface instead of invisible folklore.
- RubyGems now fits that same pattern too: modern Rust→Ruby authoring substrate exists, but the sharper missing layer is still a **fat-gem / Bundler / publish-identity support contract** rather than another extension DSL.

## What currently looks most worthy

Rough order, with intentional bias toward crates that would help many teams make Rust more explainable, reviewable, or shippable.

1. **P-0468 Cargo Resolver Explanation Kit**
   - One of the strongest archive candidates because ordinary teams still cannot get one compact cause-chain artifact for version choice, feature activation, and duplicate builds.
2. **P-0469 Cargo Rebuild Explanation Kit**
   - Still top tier because “why did this rebuild?” remains one of the most repeated day-to-day Rust questions.
3. **P-0496 Cargo Vendor & Source Parity Kit**
   - High leverage because offline/vendor/source-replacement workflows are real substrate now, but maintainers still lack one honest source-origin and parity receipt.
4. **P-0492 Cargo Registry Auth Doctor Kit**
   - Strong because Cargo auth/provider flows are no longer simple enough for README-only troubleshooting.
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Important because Cargo now explicitly acknowledges a tool-only compile surface, but teams still lack a parity/fallback receipt.
6. **P-0500 JAR/JNI Native ShipKit**
   - Newly promoted because JVM-native shipping now looks like the next obvious sibling of Python wheels, Apple XCFrameworks, Node prebuilds, and NuGet RIDs.
7. **P-0498 Node-API Package & Prebuild Contract Kit**
   - Strong because Node-API plus napi-rs already solve the raw binding problem; the missing layer is the publish/runtime contract.
8. **P-0499 NuGet Native Interop ShipKit**
   - Strong for the same reason on the .NET side: real substrate exists, but honest runtime-asset support contracts are still missing.
9. **P-0487 Foreign SDK Consumer Doctor Kit**
   - Strong follow-on because release promises are only half the story; downstream diagnosis remains painful.
10. **P-0497 CPU Baseline & Runtime Dispatch Contract Kit**
    - Strong because hardware support promises are still under-specified in many real Rust releases.

## What “epic crate” keeps meaning in this archive

The archive has enough breadth now that a pattern is visible.

The most worthy crates are often **not** “another parser”, “another wrapper”, or even “another implementation of an external standard”.

They more often do one of the following:

- make Cargo / rustc behavior **explainable**,
- make release promises **honest and portable**,
- turn support/debug chaos into **compact evidence bundles**, or
- turn unstable or low-level substrate into a **boring workflow contract** ordinary teams can review.

That is the current frontier.

## Demotions / things future passes should resist

- another broad “Rust for ecosystem X” SDK when the sharper gap is a package or support contract,
- narrow protocol expansion that does not multiply other work or clarify a major release boundary,
- dashboards or historical warehouses where the sharper missing thing is a **single-run witness**,
- generalized “interop framework” proposals that hide the concrete loader / package-manager / classifier / RID / tag facts people actually need.

## Frontier queue after this pass

1. **Cross-ecosystem support-contract generalization** — now more plausible, especially with a shared vocabulary file, but only if it stays schema/vocabulary-first and does not erase ecosystem-specific truths.
2. **Invocation-reuse compatibility kit** — still promising if the incremental-systems work sharpens a distinct `check` / `build` / `clippy` reuse receipt.
3. **Build-std adoption / support receipts** — still promising only if they stay adoption-first and do not duplicate the existing sysroot workbench.
4. **More foreign package ecosystems** — only when another ecosystem has enough official substrate plus enough boring maintainer pain to deserve its own contract crate.

## Working rule for future revisions

Before adding a new proposal, ask:

- does it create a **review artifact** other people can actually rely on,
- does it reduce one of Rust’s recurring pains around **builds, debugging, shipping, or support**,
- and is it sharper than simply adding another entry to the archive’s already-wide protocol map?

If the answer is no, compress or demote instead.
