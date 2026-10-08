---
id: P-0039
title: i18n-icu-kit — typed localization contract kit for message args, locale-data profiles, formatter coverage, and fallback witnesses
status: idea
domains: [i18n, localization, libraries, gui, web, cli]
last_reviewed: 2026-03-20
evidence:
  - https://docs.rs/icu/latest/source/README.md
  - https://icu4x.unicode.org/2_1/tutorials/data-management/
  - https://icu4x.unicode.org/2_0/tutorials/data-provider-runtime/
  - https://docs.rs/fluent/latest/fluent/
  - https://docs.rs/fluent-templates/latest/fluent_templates/
  - https://discourse.mozilla.org/t/high-level-fluent-rust-apis/123688
  - https://docs.rs/typed-i18n/latest/typed_i18n/
  - https://docs.rs/rust-i18n/latest/rust_i18n/
  - https://docs.rs/i18n-embed/latest/i18n_embed/
  - https://docs.rs/i18n-embed-fl/latest/i18n_embed_fl/
---

# Problem

Rust now has meaningful localization substrate, but the pieces still stop too low or too narrowly:

- **ICU4X** gives modular locale-aware formatting plus multiple data-management modes.
- **Fluent** gives expressive messages, but the core crate explicitly stays low-level and expects higher-level APIs above it.
- crates like **fluent-templates**, **i18n-embed**, **rust-i18n**, **typed-i18n**, and **i18n-embed-fl** solve real slices, but they do not publish one compact, reviewable answer to the receiver-facing questions that app teams actually need.

Those questions are not just “does translation lookup work?” They are:

- what argument schema is promised for each message,
- what locale data profile is actually shipped,
- which rich formatter families are really supported,
- and how locale negotiation / fallback behaves when the requested locale is only partially covered.

Right now those truths are usually scattered across macros, README prose, Cargo features, app wiring, and implicit ICU4X defaults.

# What it provides

This crate should provide a **typed localization contract layer** above existing Rust i18n substrate.

It should give other people four reviewable artifacts:

1. **`message-arg-schema.receipt`**
   - key / message id
   - argument names
   - argument kinds (`string`, `number`, `date`, `datetime`, `list`, `enum`, etc.)
   - required / optional status
   - evidence origin (`generated`, `declared`, `manual_review_required`)

2. **`data-profile.receipt`**
   - whether locale data is `compiled_default`, `baked_subset`, `blob_runtime`, `filesystem_runtime`, `host_bridge`, or `mixed`
   - which locale set is guaranteed
   - whether updates happen only at build time or also at runtime
   - whether the profile is footprint-first, breadth-first, or manual-review-required

3. **`formatter-coverage.report`**
   - which token families are actually supported
   - whether support is plain substitution, Fluent-only selection, ICU4X-backed formatting, or custom project logic
   - whether number/date/list/relative-time/plural/select coverage is complete, partial, adapter-specific, or absent

4. **`fallback-witness.report`**
   - requested locale(s)
   - negotiation/fallback strategy
   - resolved locale path
   - whether fallback came from message-layer policy, ICU4X locale fallback, or ad hoc app behavior
   - whether the witness is direct, imported, or manual-review-required

The point is not to replace Fluent, MF2, or ICU4X.
The point is to make a Rust localization stack’s **receiver-facing support truth** reviewable.

# Users & user stories

- **GUI / app teams**: “We want typed localized messages, but also one honest answer to what locales and rich formatters we really support.”
- **Library authors**: “We need a small runtime contract that composes with Fluent, MF2, or simple catalogs without forcing one message syntax forever.”
- **Platform teams**: “We want to know whether a crate uses ICU4X compiled data, a tiny baked subset, or runtime-loaded data before adopting it.”
- **QA / release teams**: “We need a machine-readable witness for locale fallback and formatter coverage, not just screenshots and guesswork.”

# Prior art (and why it’s insufficient)

- **ICU4X** is intentionally modular and supports compiled data, baked subsets, and explicit runtime `DataProvider`s; that flexibility is powerful, but it leaves product-level support posture underspecified.
- **Fluent** and `fluent-bundle` are intentionally low-level; the docs say they are building blocks for higher-level APIs.
- **fluent-templates** provides a high-level loader and simple negotiation, which is useful, but it does not try to publish data-profile or formatter-coverage contracts.
- **i18n-embed** and **cargo-i18n** help with embedding assets and product workflows, but they still leave rich formatting coverage and fallback-path truth mostly implicit.
- **typed-i18n** proves there is demand for type-safe message arguments, but it is intentionally lightweight and does not own ICU4X data/formatter/fallback truth.
- **rust-i18n** gives a simple macro-driven experience with fallback chains and parameter substitution, but it is optimized for ease of use rather than an explicit reviewable contract for formatter/data posture.
- **i18n-embed-fl** checks Fluent message ids/arguments at compile time, which is great, but it still leaves locale-data profile and fallback-path truth outside the contract.

# Design goals

1. **Stay above substrate, below product pipeline**
   - do not replace ICU4X, Fluent, MF2, or translation-management tooling.
2. **Typed arguments should be first-class**
   - compile-time or generated evidence for argument names and kinds.
3. **Locale-data posture should be explicit**
   - compiled defaults, baked subsets, runtime blobs, and host-backed sources should not masquerade as the same support claim.
4. **Rich formatter support should be explicit**
   - plain string substitution is not the same promise as ICU4X-backed number/date/list formatting.
5. **Fallback / negotiation should be witnessed**
   - make the chosen locale path reviewable instead of folkloric.
6. **Keep message syntax pluggable**
   - support adapters for Fluent, MF2, simple keyed templates, or generated bindings.

# Non-goals

- Replacing ICU4X.
- Defining a new locale-data ecosystem.
- Forcing a single message syntax.
- Becoming a full translation-management platform.
- Pretending a contract receipt alone proves translation quality.

# Architecture & API sketch

## Workspace split

- `i18n_contract_model`
- `i18n_contract_codegen`
- `i18n_contract_fluent`
- `i18n_contract_simple`
- `i18n_contract_icu4x`
- `cargo-i18n-contract`

## Rust-facing core model

```rust
pub enum ArgKind {
    String,
    Number,
    Date,
    DateTime,
    Time,
    List,
    Enum,
    Custom(String),
}

pub struct MessageArgSchema {
    pub key: String,
    pub args: Vec<MessageArg>,
}

pub struct DataProfileReceipt {
    pub mode: DataMode,
    pub guaranteed_locales: Vec<String>,
    pub update_posture: UpdatePosture,
}

pub struct FormatterCoverageReport {
    pub number: Coverage,
    pub date: Coverage,
    pub time: Coverage,
    pub list: Coverage,
    pub plural: Coverage,
    pub select: Coverage,
    pub relative_time: Coverage,
}

pub struct FallbackWitnessReport {
    pub requested: Vec<String>,
    pub resolved_path: Vec<String>,
    pub fallback_basis: FallbackBasis,
    pub witness_origin: WitnessOrigin,
}
```

## Suggested command surface

- `cargo i18n-contract capture`
  - emit schemas/receipts/reports from a chosen catalog/runtime setup
- `cargo i18n-contract check`
  - fail on mismatched arguments, missing formatter coverage promises, or undocumented fallback basis
- `cargo i18n-contract witness`
  - record real locale-resolution outcomes for selected test cases
- `cargo i18n-contract diff`
  - compare two contract bundles across releases
- `cargo i18n-contract bundle`
  - export one compact `.i18ncontractbundle.zip`

## Recommended artifact set

- `message-arg-schema.receipt.json`
- `data-profile.receipt.json`
- `formatter-coverage.report.json`
- `fallback-witness.report.json`
- `i18n-contract.toml`
- `i18n-contract.summary.md`

# Security / safety model

- Treat runtime-loaded catalogs and locale data as untrusted inputs.
- Keep formatting safe: no arbitrary expression evaluation in the contract layer.
- Make host-locale import explicit; do not silently equate browser/system locale detection with user-approved locale policy.
- Prefer generated bindings and explicit schemas over ad hoc key strings when possible.

# Maintenance & governance plan

- Keep the core **schema-first** and **adapter-friendly**.
- Keep syntax adapters separate from the model crate.
- Keep ICU4X data posture explicit so upgrades in compiled data or datagen do not silently widen support claims.
- Ship tiny scenario fixtures that freeze fallback-path, coverage, and data-profile differences.

# Milestones

- **0.1**: core schemas + simple adapter + ICU4X data-profile capture + fallback witness runner.
- **0.2**: Fluent adapter + generated message-arg schema + formatter coverage checks.
- **0.3**: diff/bundle UX + targeted MF2 adapter hooks.
- **1.0**: stable artifact vocabulary + compatibility policy + reference fixtures.

# Open questions

- What should the minimal common `ArgKind` vocabulary be across Fluent, MF2, and simple template systems?
- Should fallback witnesses record both language negotiation and ICU4X subtag fallback in one report or in nested sections?
- How much formatter coverage should be inferred automatically versus declared by the app/team?
- Should the crate offer a compact built-in `LocaleProfile` enum for common app shapes (`tiny_cli`, `desktop_bundle`, `runtime_blob`, etc.)?

# Sources

- ICU4X README / data management — https://docs.rs/icu/latest/source/README.md
- ICU4X data management tutorial — https://icu4x.unicode.org/2_1/tutorials/data-management/
- ICU4X runtime data loading tutorial — https://icu4x.unicode.org/2_0/tutorials/data-provider-runtime/
- `fluent` docs — https://docs.rs/fluent/latest/fluent/
- `fluent-templates` docs — https://docs.rs/fluent-templates/latest/fluent_templates/
- Fluent high-level Rust API discussion — https://discourse.mozilla.org/t/high-level-fluent-rust-apis/123688
- `fluent-rs` workspace README — https://github.com/projectfluent/fluent-rs
- `typed-i18n` docs — https://docs.rs/typed-i18n/latest/typed_i18n/
- `rust-i18n` docs — https://docs.rs/rust-i18n/latest/rust_i18n/
- `i18n-embed` docs — https://docs.rs/i18n-embed/latest/i18n_embed/
- `i18n-embed-fl` docs — https://docs.rs/i18n-embed-fl/latest/i18n_embed_fl/
