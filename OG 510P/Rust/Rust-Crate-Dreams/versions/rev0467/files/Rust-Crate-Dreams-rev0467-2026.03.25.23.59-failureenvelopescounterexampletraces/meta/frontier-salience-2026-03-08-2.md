# Frontier salience scan — 2026-03-08 (second pass)

This file exists to resist archive sprawl.

The archive is now large enough that a good pass should usually do one of three things:

1. **promote one genuinely sharp new seam**,
2. **compress / rank existing territory**, or
3. **add hygiene that prevents LLM drift**.

This pass mostly did **(1)** and **(2)** again, but with a stricter planning question attached: *what does the crate provide other people besides an interesting idea?*

## External signals worth honoring right now

- The 2025 State of Rust survey still points to **slow compile times / resource usage** and **debugging** as recurring pain areas, so the top frontier should still overweight explainability and support artifacts.
- Cargo and crates.io continue to grow more policy-heavy and machine-readable, which strengthens crate ideas that turn existing plumbing into **reviewable workflow contracts**.
- The archive’s foreign-ecosystem work now has a repeatable pattern: once real authoring substrate exists, the sharper missing layer is often a **package contract / loader receipt / support bundle**, not another binding generator.
- Ruby now joins Python, Apple, Node/npm, NuGet, and the JVM on that list because RubyGems, `rb-sys`, `magnus`, and cross-build helpers are already real enough that “can Rust bind into Ruby?” is no longer the sharp question.

## What currently looks most worthy

Rough order, with intentional bias toward crates that would help many teams make Rust more explainable, reviewable, or shippable.

1. **P-0468 Cargo Resolver Explanation Kit**
   - Still one of the strongest archive candidates because ordinary teams still cannot get one compact cause-chain artifact for version choice, feature activation, and duplicate builds.
2. **P-0469 Cargo Rebuild Explanation Kit**
   - Still top tier because “why did this rebuild?” remains one of the most repeated day-to-day Rust questions.
3. **P-0496 Cargo Vendor & Source Parity Kit**
   - High leverage because offline/vendor/source-replacement workflows are real substrate now, but maintainers still lack one honest source-origin and parity receipt.
4. **P-0492 Cargo Registry Auth Doctor Kit**
   - Strong because Cargo auth/provider flows are no longer simple enough for README-only troubleshooting.
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Important because Cargo now explicitly acknowledges a tool-only compile surface, but teams still lack a parity/fallback receipt.
6. **P-0500 JAR/JNI Native ShipKit**
   - Still newly strong because JVM-native shipping now looks like a clean package/runtime contract problem rather than generic interop.
7. **P-0498 Node-API Package & Prebuild Contract Kit**
   - Strong because Node-API plus napi-rs already solve much of the raw binding problem; the missing layer is the publish/runtime contract.
8. **P-0499 NuGet Native Interop ShipKit**
   - Strong for the same reason on the .NET side: real substrate exists, but honest runtime-asset support contracts are still missing.
9. **P-0497 CPU Baseline & Runtime Dispatch Contract Kit**
   - Strong because hardware support promises are still under-specified in many real Rust releases.
10. **P-0501 RubyGems Native Extension ShipKit**
   - Newly promoted because RubyGems now looks like another ecosystem where real authoring/build substrate exists, but the support contract is still too implicit.

## What “epic crate” keeps meaning in this archive

The most worthy crates are often **not** another parser, another wrapper, or another ambitious framework.

They more often do one of the following:

- make Cargo / rustc behavior **explainable**,
- make release promises **honest and portable**,
- turn support/debug chaos into **compact evidence bundles**, or
- turn low-level substrate into a **boring workflow contract** ordinary teams can review.

The extra planning rule from this pass is that good proposals should also answer a blunt question:

> **What does this crate provide other people that they can inspect, rely on, or plug into their own workflow?**

If the answer is vague, the proposal is probably not sharp enough yet.

## Demotions / things future passes should resist

- another broad “Rust for ecosystem X” SDK when the sharper gap is a package or support contract,
- narrow protocol expansion that does not multiply other work or clarify a major release boundary,
- dashboards or historical warehouses where the sharper missing thing is a **single-run witness**,
- generalized “interop framework” proposals that hide the concrete platform / loader / classifier / package-manager facts people actually need.

## Frontier queue after this pass

1. **Cross-ecosystem support-contract generalization** — now more plausible, but only if it stays schema/vocabulary-first and does not erase ecosystem-specific truths.
2. **Invocation-reuse compatibility kit** — still promising if the incremental-systems work sharpens a distinct `check` / `build` / `clippy` reuse receipt.
3. **Build-std adoption / support receipts** — still promising only if they stay adoption-first and do not duplicate the existing sysroot workbench.
4. **More foreign package ecosystems** — only when another ecosystem has enough official substrate plus enough boring maintainer pain to deserve its own contract crate.

## Working rule for future revisions

Before adding a new proposal, ask:

- does it create a **review artifact** other people can actually rely on,
- does it reduce one of Rust’s recurring pains around **builds, debugging, shipping, or support**,
- is it sharper than simply adding another entry to the archive’s already-wide protocol map,
- and can it say concretely what it **provides to other people** besides a neat abstraction?

If the answer is no, compress or demote instead.
