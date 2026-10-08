# Design: Localization Surface Kit (`cargo locale`, `locale-pack/v0`)

## Goal
Define a portable contract for declaring, validating, diffing, and reviewing Rust localization support: supported locales, message catalogs, placeholder schemas, negotiation/fallback behavior, runtime data requirements, surface coverage, and evidence that translations still match what the program claims.

This should **not** replace Fluent, ICU4X, gettext, `rust-i18n`, `i18n-embed`, `cargo-i18n`, or framework-specific i18n helpers.
It should make them compose better and make localization support claims reviewable.

## References (signals)
- AreWeWebYet still says internationalization is a work in progress in Rust and that there is no standard mature implementation.
  https://www.arewewebyet.org/topics/i18n/
- `fluent` and Project Fluent provide an expressive localization system and FTL syntax designed for natural-language-friendly translations.
  https://docs.rs/fluent
  https://projectfluent.org/
  https://projectfluent.org/fluent/guide/
- `icu` is the ICU4X meta-crate and explicitly treats locale-aware internationalization as data-driven functionality.
  https://docs.rs/icu
- `icu_provider`, `icu_provider_fs`, and `icu_provider_adapters` make data transmission, filesystem loading, provider composition, filtering, and fallback explicit layers.
  https://docs.rs/icu_provider
  https://docs.rs/icu_provider_fs
  https://docs.rs/icu_provider_adapters
- `i18n-embed` exists to embed localization assets into Rust applications/libraries and works with `cargo-i18n`.
  https://docs.rs/i18n-embed
  https://docs.rs/cargo-i18n
- `gettext-rs` and the pure-Rust `gettext` crate show that gettext-style message catalogs remain a real Rust path.
  https://docs.rs/gettext-rs/latest/gettextrs/
  https://docs.rs/gettext
- `rust-i18n` shows a simpler compile-time mapping path is also alive in the ecosystem.
  https://docs.rs/rust-i18n
- `leptos_i18n` shows framework-level typed locale/key checks, compile-time loading, and reactive locale switching already exist in modern Rust UI work.
  https://docs.rs/leptos_i18n

## Core components

### 1) `locale-surface/v0`
A design-time declaration of the localization support an application/workspace/library claims to expose.

Required ideas:
- subject identity (crate / workspace / binary / library / app / service)
- locale inventory:
  - locale id / canonical form
  - support posture (`official`, `community`, `partial`, `experimental`, `deprecated`, `internal`)
  - default locale status
  - translation completeness posture when known
- localized surface classes:
  - `ui`
  - `cli`
  - `templates`
  - `docs`
  - `email`
  - `diagnostics`
  - `api-text`
  - `route/slug`
  - `other`
- resource attachments:
  - raw resource format (`ftl`, `po/mo`, `yaml`, `json`, `toml`, `custom`)
  - catalog attachment pointers
  - translator-comment availability
- support metadata:
  - text direction hints when relevant
  - region/script specificity posture
  - machine-translated / human-reviewed posture when relevant

Design rule: **`locale-surface` must separate the supported-locale claim from negotiation/fallback behavior and from observed validation runs.**
A folder of translation files alone is not the whole localization contract.

### 2) `message-catalog/v0`
A machine-readable inventory of message definitions and placeholder/contracts without flattening raw resource truth.

Should record:
- linked `locale-surface/v0`
- catalog identity and raw format
- message ids / contexts / groups
- placeholder declarations:
  - names
  - expected kinds (`string`, `number`, `date`, `select`, `plural`, opaque/custom)
  - optionality / required status when knowable
- translator comments / developer notes
- source references where keys originate
- attachment pointers to raw FTL/PO/YAML/TOML/JSON/custom resources
- extract/build provenance when relevant
- unsupported normalization notes when raw formats cannot be losslessly compared

This is the missing answer to “what are the translation-bearing message contracts, independent of one rendering engine?”

### 3) `locale-negotiation-plan/v0`
A machine-readable plan for how locale choice and data loading actually work.

Should record:
- linked `locale-surface/v0`
- locale-detection sources:
  - explicit user setting
  - CLI flag
  - environment
  - OS/browser headers
  - embedded default
- canonicalization and matching policy
- fallback chains and unsupported-locale behavior
- partial-locale policy (`reject`, `fallback`, `mix`, `best-effort`)
- runtime formatting/data assumptions:
  - ICU compiled-data usage
  - filesystem/blob/provider loading
  - provider composition/filtering/fallback assumptions
  - network or dynamic updates if present
- build/load strategy:
  - embedded resources
  - sidecar resources
  - runtime-downloaded resources
  - OS catalog usage
- skip/waiver reasons such as:
  - `manual-translation-gap`
  - `provider-not-captured`
  - `framework-binding-opaque`
  - `partial-locale-accepted`

This is the missing answer to “how does the app decide which locale to use, and what runtime data does that require?”

### 4) `locale-check-report/v0`
Report artifact capturing what localization support was actually checked.

Should record:
- referenced surface/catalog/negotiation ids
- checkers used (`fluent`, gettext validators, framework adapters, custom render tests, snapshot tools, ICU data checks)
- checked locales and checked surface classes
- message completeness results
- missing-key / orphan-key / stale-key results
- placeholder drift results
- fallback and unsupported-locale results
- raw formatting/data load results
- rendered-surface attachments when available (text snapshots, DOM snapshots, template outputs, CLI help outputs)
- drift reason codes such as:
  - `missing-translation`
  - `orphan-message`
  - `placeholder-drift`
  - `fallback-drift`
  - `locale-negotiation-drift`
  - `icu-data-gap`
  - `partial-locale-surface-gap`
  - `translator-comment-gap`
  - `rendered-surface-drift`

This is the missing answer to “what part of the localization promise did we really verify?”

### 5) `locale-diff-report/v0` (optional but important)
Focused artifact for localization evolution between versions.

Should record:
- source release / destination release ids
- added/removed/deprecated locales
- changed support posture (`official` → `partial`, etc.)
- added/removed message ids and contexts
- placeholder compatibility changes
- fallback-policy changes
- data-provider/runtime-loading changes
- affected docs/example/template pointers

This keeps localization compatibility changes from being buried inside generic release notes.

### 6) `locale-pack/v0`
Bundle format containing:
- `locale-surface/v0`
- one or more `message-catalog/v0`
- one `locale-negotiation-plan/v0`
- one or more `locale-check-report/v0`
- optional `locale-diff-report/v0`
- optional raw attachments (FTL/PO/YAML/TOML/JSON resources, screenshots, rendered snapshots, ICU data manifests, extraction outputs)

This is the unit that should travel through CI, release review, localization QA, docs, and later archaeology.

### 7) `cargo locale`
Reference UX:
- `cargo locale init`
- `cargo locale catalog`
- `cargo locale check`
- `cargo locale diff`
- `cargo locale pack`

`cargo locale` should begin as an explainer / adapter / packer.
It should not pretend to be the one true localization engine.

## Default policy
- **Separate supported-locale claims from negotiation/fallback and from run evidence.**
- **Preserve raw format truth** instead of flattening Fluent/gettext/simple key/value files into one fake canonical syntax.
- **Record support posture per locale and per surface** so “partial support” is explicit.
- **Treat runtime data/provider assumptions as first-class** instead of burying them in build scripts or framework glue.
- **Differentiate declared message catalogs from rendered-surface checks** so passing extraction does not imply good UI output.
- **Prefer attachable evidence over screenshots-only folklore.**

## What the kit should provide to others
- **A11yKit:** connect language tags, directionality, and localized UI surfaces to accessibility/tree review without forcing one widget toolkit.
- **Command Surface Kit:** give localized help/manpages/completions and CLI text a place to declare locale coverage separately from the parse surface.
- **Runtime Settings Kit:** provide a place to describe locale-selection settings and fallback preferences without absorbing the broader configuration contract.
- **Diagnostic Surface Kit:** connect public diagnostic texts/help links to locale coverage and fallback policy.
- **DocProof Kit:** distinguish translated docs/examples from untranslated or illustrative-only materials.
- **Support Envelope Kit / Footprint Kit:** make ICU/resource-loading assumptions and bundled-data size tradeoffs reviewable instead of hidden inside build artifacts.

## Overlap boundaries
- **Not Fluent / gettext / `rust-i18n`:** those are message systems and runtime libraries; this kit packages the supported localization interface and evidence across them.
- **Not ICU4X:** ICU4X provides formatting/data capabilities; this kit records which capabilities and data assumptions a project depends on.
- **Not a translation platform:** translator workflow SaaS, review UI, and human translation management are adjacent but not required for v0.
- **Not DocProof Kit:** translated documentation/examples are one surface class among many; DocProof still owns the broader learning-surface contract.
- **Not Command Surface Kit or Diagnostic Surface Kit:** those kits own command and failure semantics; this kit owns locale coverage and translation evidence for those surfaces.
- **Not a framework binding replacement:** Yew/Leptos/Dioxus/desktop adapters remain free to innovate above the shared artifacts.

## Hard problems to respect
- Placeholder compatibility is format-specific and not always inferable.
- Locale negotiation can depend on platform/browser/runtime context that is hard to reproduce offline.
- Render quality is richer than string completeness; v0 should not pretend screenshots become machine-perfect quality metrics.
- Some projects intentionally support partial localization; the artifact must model that honestly instead of forcing binary yes/no support.
- Raw catalog formats and extraction conventions differ enough that v0 should normalize metadata and attach raw truth, not erase it.

## Why this could be an epic contribution
Rust already has strong i18n pieces, but they do not yet speak one reviewable language.
A Localization Surface Kit would turn “we have some translation files” into a concrete, diffable support claim:
- here are the locales,
- here are the message catalogs and placeholders,
- here is the negotiation/fallback policy,
- here are the runtime data assumptions,
- and here is what we actually checked.

That would be useful to app developers, library maintainers, framework authors, translators, QA, release engineers, and downstream distributors.

## Suggested first implementations
- adapter support for Fluent + ICU4X-backed applications
- adapter support for gettext-style applications
- one simple key/value path (`rust-i18n`-style) so the format model does not become Fluent-only
- one modern web/UI pilot (for example, a `leptos_i18n`-style app) to prove reactive/framework bindings can emit packs too
- one CLI-oriented pilot to test localized help/diagnostic surfaces
