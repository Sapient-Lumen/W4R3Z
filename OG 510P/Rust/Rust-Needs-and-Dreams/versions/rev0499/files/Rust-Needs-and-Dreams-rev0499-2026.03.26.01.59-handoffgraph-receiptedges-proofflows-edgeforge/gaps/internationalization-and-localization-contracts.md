# Gap: internationalization and localization contracts

## What is missing
Rust has real localization building blocks, but it still lacks a **shared localization contract**.

Today there is no standard way to describe, exchange, and diff:
- which locales an application or crate officially supports,
- which surfaces are localized (`ui`, `cli`, `docs`, `templates`, `emails`, `routes`, `errors`) and which are intentionally English-only,
- which message catalogs and placeholder schemas define that support,
- how locale negotiation and fallback work,
- which runtime formatting/data capabilities are required,
- which translations were actually checked for completeness and argument drift,
- and what evidence exists that compiled resources, loaded resources, examples, and rendered surfaces still agree.

That missing layer matters because Rust already has multiple serious i18n directions — Fluent, ICU4X, gettext-based flows, embed/build helpers, framework-specific helpers, and lighter compile-time key/value approaches — but the supported localization interface still usually lives in ad hoc file trees, build scripts, README notes, screenshots, and maintainer memory.

Sources:
- https://www.arewewebyet.org/topics/i18n/
- https://docs.rs/fluent
- https://projectfluent.org/fluent/guide/
- https://docs.rs/icu
- https://docs.rs/icu_provider
- https://docs.rs/icu_provider_fs
- https://docs.rs/icu_provider_adapters
- https://docs.rs/i18n-embed
- https://docs.rs/cargo-i18n
- https://docs.rs/gettext-rs/latest/gettextrs/
- https://docs.rs/rust-i18n
- https://docs.rs/leptos_i18n

## The current seam is awkward
The ecosystem clearly has ingredients:
- AreWeWebYet still describes internationalization in Rust as a work in progress without one standard mature implementation,
- `fluent` and Project Fluent provide an expressive message system for natural-language-friendly translations,
- ICU4X provides locale-aware formatting and data-driven internationalization primitives, with explicit data-provider layers and filesystem/blob-based loading options,
- `i18n-embed` and `cargo-i18n` cover extraction/build/embed workflows,
- `gettext-rs` covers GNU gettext-style runtime lookup with plural/context support,
- `rust-i18n` covers compile-time-friendly key/value localization,
- and `leptos_i18n` shows that framework-level typed locale/key checks and compile-time loading are already practical in modern Rust web apps.

But real projects still hand-assemble their localization story out of:
- locale lists,
- raw FTL/PO/YAML/TOML/JSON files,
- extraction/build scripts,
- comments for translators,
- placeholder conventions,
- locale negotiation code,
- runtime data-provider choices,
- screenshots and manual QA,
- framework-specific bindings,
- and ad hoc support statements like “fr is partial” or “CLI help is English only.”

The result is not that Rust lacks i18n crates.
The result is that there is no portable way to say:
- “these are the locales we officially support,”
- “these message catalogs and placeholders define that claim,”
- “this is how we negotiate and fall back,”
- “these formatted data capabilities are required,”
- “these localized surfaces were actually checked,”
- or “this locale regressed from full to partial support between releases.”

Sources:
- https://www.arewewebyet.org/topics/i18n/
- https://docs.rs/fluent
- https://projectfluent.org/fluent/guide/
- https://docs.rs/icu
- https://docs.rs/icu_provider
- https://docs.rs/icu_provider_fs
- https://docs.rs/icu_provider_adapters
- https://docs.rs/i18n-embed
- https://docs.rs/gettext-rs/latest/gettextrs/
- https://docs.rs/rust-i18n
- https://docs.rs/leptos_i18n

## Why this matters
This gap is bigger than “better translation tooling.”
It affects:
1. **product reach** — Rust apps increasingly target global users on desktop, web, CLI, and service surfaces;
2. **support honesty** — “supports de-DE” is a real public claim, but today that claim is rarely attachable or diffable;
3. **operational correctness** — locale negotiation, fallback, and ICU data loading are runtime behaviors, not just static files;
4. **quality review** — missing placeholders, stale translator comments, untranslated strings, and partial surface coverage should be machine-reviewable;
5. **framework interop** — UI frameworks, CLI tools, templating engines, and backend renderers should not each invent an incompatible metadata story;
6. **cross-kit composition** — A11yKit, Command Surface Kit, Runtime Settings Kit, Diagnostic Surface Kit, and DocProof Kit all need a coherent place for locale support truth.

Rust now has enough i18n components that the missing contribution looks less like “invent another localization library” and more like “standardize the supported localization surface and its evidence.”

Sources:
- https://www.arewewebyet.org/topics/i18n/
- https://docs.rs/icu
- https://docs.rs/icu_provider
- https://docs.rs/i18n-embed
- https://docs.rs/gettext-rs/latest/gettextrs/
- https://docs.rs/leptos_i18n

## What “good” looks like
A worthy contribution here is **not** another message format, another translation SaaS, or another framework-specific helper.

It is a shared localization boundary:
- one `locale-surface/v0` describing supported locales, support posture, localized surface classes, default/fallback posture, and message-resource attachments,
- one `message-catalog/v0` inventorying message ids, contexts, placeholders, translator comments, source references, and raw-resource attachments without flattening Fluent/gettext/simple maps into one fake canonical syntax,
- one `locale-negotiation-plan/v0` describing locale detection, normalization, fallback chains, ICU/data-provider assumptions, embed/load strategy, and unsupported-locale behavior,
- one `locale-check-report/v0` recording completeness checks, placeholder drift, fallback results, untranslated segments, rendered-surface checks, and raw attachments,
- one optional `locale-diff-report/v0` describing added/removed locales, changed support posture, message-key drift, placeholder compatibility changes, and fallback/formatting changes between releases,
- and one `locale-pack/v0` bundle for CI, release review, docs, translators, operators, and archaeology.

That would let Rust projects expose localization support as a reviewable interface instead of a folder of resource files plus hope.
