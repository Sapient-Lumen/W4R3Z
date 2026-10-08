# Epic proposal: Compile Guidance Kit

## Thesis
Rust now has enough pieces for crate-authored compile-time guidance that one of the highest-leverage missing contributions is no longer another isolated macro helper, lint pack, or build-time trick.
The higher-leverage missing piece is a **portable compile-guidance contract** that lets the ecosystem identify, specify, validate, and ship developer-facing diagnostics, lint catalogs, fix hints, compile-fail examples, and extension-hook truth.

In other words: Rust needs a boring, attachable `guidance-pack/v0` more than it needs one more bespoke compile-time UX stack.

## Why now
The signals line up:
- Rust’s vision work explicitly recommends doubling down on extensibility, including better diagnostics and guidance from crates and deeper compilation-workflow integration.
- Stable Rust now includes a diagnostic attribute namespace, which means crate-authored compiler guidance is no longer purely experimental.
- The 2026 flagships include safety-critical lints in Clippy, which raises the importance of lint surfaces and their review posture.
- StableMIR publication to crates.io is explicit evidence that the project wants a healthier external tooling ecosystem around the compiler.
- Cargo experimentation with build-script delegation and multiple build scripts shows active pressure to structure build-time extension points.
- `trybuild` and UI-style compile-fail testing exist because compile-time diagnostics are already a real product surface for library users.

That means the missing substrate is not raw mechanism.
It is the **reviewable path for declaring and checking supportive compile-time behavior**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/beta/releases.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://docs.rs/trybuild

## What should be built
A first credible version should ship:
1. `guidance-surface/v0`, `diagnostic-catalog/v0`, `lint-catalog/v0`, `pipeline-hook-profile/v0`, `guidance-example-catalog/v0`, `guidance-check-report/v0`, and `guidance-pack/v0`
2. adapters for at least one stable trait-diagnostic case, one proc-macro/UI-test case, one lint-catalog case, and one build/analyzer hook case
3. normalization rules for compile-time examples so reports survive path/version/toolchain noise
4. docs/reference generation for guidance ids, help links, fix posture, and hook assumptions
5. CI examples proving that guidance drift can be caught intentionally instead of by surprise

The winning version is not flashy.
It is explicit about ids, spans, examples, and hook posture.

## Initial pilots
Follow a ranked rollout rather than trying to standardize every guidance lane at once:
1. trait-diagnostic pilot using stable diagnostic attributes
2. proc-macro pilot with `trybuild`-style compile-fail examples and normalized expected guidance
3. lint-catalog pilot oriented toward safety/policy or migration checks rather than style-only trivia
4. hook-profile pilot describing a build/delegated-build/StableMIR-based tool honestly enough for review and caching discussions
5. integration pilot showing how CI or editor tooling can consume a `guidance-pack/v0`

## Milestones
1. **v0 artifacts + docs**
   - publish schemas and examples
   - preserve distinctions between diagnostics, lints, examples, and hook posture
2. **v0.2 adapters + checkers**
   - ship trait, proc-macro, lint, and hook pilots
   - normalize compile-fail / UI outputs into stable reports
3. **v0.3 governance depth**
   - connect lint catalogs to profile and standards mappings
   - connect hook profiles to capability / determinism evidence
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one exact extension mechanism

## Success metrics
- Teams can review compile-time guidance as explicit artifacts instead of screenshotting failures or reading macro internals.
- Lint packs and safety-oriented guidance become easier to compare, scope, and govern.
- Build/analyzer hooks become more legible to reviewers, CI, and caching/tooling layers.
- Guidance drift between releases becomes diffable.
- Rust’s “supportive tooling” advantage becomes easier for crates to extend rather than being concentrated only in rustc proper.

## Archive fit
This proposal fills a real gap between existing archive kits:
- Compile-Time Capabilities Kit handles authority and sandboxing,
- Build Extension Kit handles declarative build-step structure,
- MIR Analysis Kit handles stable compiler-analysis export,
- Macro Workflow Kit inventories macro-heavy ecosystems,
- Lint Baseline Kit handles rollout and debt governance,
- and Diagnostic Surface Kit handles runtime/application failures.

But none of those is the portable contract for the **developer-facing compile/build guidance layer** shared across trait diagnostics, lint catalogs, proc-macro UI surfaces, and extension-hook truth.
Compile Guidance Kit is the missing substrate that lets Rust scale supportive extensibility deliberately instead of by folklore, snapshots, and custom glue.

The next execution refinement is now captured in [`design/compile-guidance-pilot-program.md`](../design/compile-guidance-pilot-program.md), so the archive can talk about guidance-family rollout, stability posture, consumer classes, and scorecards explicitly instead of treating `guidance-pack/v0` as a one-shot universal manifest.
