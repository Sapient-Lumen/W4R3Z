# Epic proposal: Localization Surface Kit

## Thesis
Rust does not primarily need one more localization crate.
It needs a **reviewable localization surface**.

The ecosystem already has:
- expressive message systems (`fluent`, Project Fluent),
- locale-aware formatting/data primitives (ICU4X),
- embed/extract/build helpers (`i18n-embed`, `cargo-i18n`),
- gettext-style catalog support,
- simpler compile-time key/value approaches (`rust-i18n`),
- and framework-specific typed locale/key tooling (`leptos_i18n`).

At the same time, AreWeWebYet still describes i18n in Rust as lacking a standard mature implementation.
That combination is a strong sign that the missing contribution is not “pick the winning library,” but “standardize the portable contract above the current diversity.”

Sources:
- https://www.arewewebyet.org/topics/i18n/
- https://docs.rs/fluent
- https://projectfluent.org/fluent/guide/
- https://docs.rs/icu
- https://docs.rs/i18n-embed
- https://docs.rs/gettext-rs/latest/gettextrs/
- https://docs.rs/rust-i18n
- https://docs.rs/leptos_i18n

## Proposal
Create **Localization Surface Kit**, centered on:
- `locale-surface/v0`
- `message-catalog/v0`
- `locale-negotiation-plan/v0`
- `locale-check-report/v0`
- optional `locale-diff-report/v0`
- `locale-pack/v0`

And a reference `cargo locale` adapter/packer that can ingest metadata from existing ecosystems rather than replacing them.

## What it should make possible
1. review “supported locales” as a real product/support claim
2. diff localization posture between releases
3. keep message ids/placeholders/fallback rules from drifting silently
4. attach localization evidence to CI, docs, QA, and release workflows
5. let frameworks and libraries share one artifact language without forcing one message format
6. make localization interact cleanly with A11y, docs, command surfaces, diagnostics, settings, and footprint/support-envelope reviews

## Why this deserves archive space
This proposal opens a domain the concise archive barely touches today: **globalized product surfaces**.
It is distinct from A11yKit, DocProof Kit, Runtime Settings Kit, and Command Surface Kit, but composes with all of them.
It also has a healthy “epic” shape: it can begin as adapters and artifacts, it serves multiple deployment domains, and it helps Rust projects communicate maturity/support more honestly.

## Initial pilots
- one GUI or web application with multiple locales and reactive switching
- one CLI tool with localized help/diagnostics
- one gettext-based project
- one Fluent + ICU4X project with nontrivial placeholders/plurals

## Milestones
1. **v0 artifacts + docs**
   - define schemas and example packs
   - preserve raw resource attachments and placeholder metadata honestly
2. **v0.2 adapters**
   - support Fluent, gettext, one simple key/value flow, and ICU4X data-provider metadata
3. **v0.3 cross-kit integration**
   - integrate with A11yKit, Command Surface, Diagnostic Surface, Runtime Settings, Support Envelope, and DocProof workflows
4. **v1 ecosystem pilots**
   - at least three materially different adopters emit useful packs without sharing one exact localization stack

## Success metrics
- Projects can declare locale support and surface coverage without burying it in prose.
- Placeholder and fallback regressions become reviewable in CI.
- Translators and maintainers can reason about raw catalogs and rendered surfaces without guessing which files matter.
- Framework-specific localization helpers gain a common export/report seam.
- Rust applications become better at making localization a first-class support claim instead of an afterthought.
