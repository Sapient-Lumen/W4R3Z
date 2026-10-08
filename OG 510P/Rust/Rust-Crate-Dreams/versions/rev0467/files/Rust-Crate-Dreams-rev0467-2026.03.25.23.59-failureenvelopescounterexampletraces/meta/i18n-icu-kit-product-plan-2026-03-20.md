# i18n-icu-kit product plan — 2026-03-20

This note sharpens **P-0039 i18n-icu-kit** into an implementation-ready `0.1` direction.

## Main judgment

A worthwhile `0.1` should **not** try to become:

- the one blessed Rust localization syntax,
- a full translation-management system,
- or a replacement for ICU4X / Fluent / MF2.

It should instead become a **typed localization contract layer** that helps a crate or app publish one reviewable answer to four boring but high-value questions:

1. **What arguments do your messages actually require?**
2. **What locale-data profile do you actually ship?**
3. **Which rich formatter families are actually supported?**
4. **How does locale negotiation / fallback actually resolve at runtime?**

The missing value is the contract layer above today’s macros, message files, provider wiring, and runtime defaults.

## Why this lane got stronger

Current Rust localization substrate makes the gap more actionable than it used to be:

- ICU4X now explicitly supports both **compiled data** and **explicit provider-backed** data paths.
- ICU4X’s docs encourage data customization through `icu4x-datagen`, runtime providers, and fallback adapters.
- `fluent` still describes itself as the low-level container and says higher-level APIs sit above it.
- `fluent-templates`, `i18n-embed`, `typed-i18n`, and `rust-i18n` each solve real slices, but none of them own one compact support contract spanning typed args, data profile, formatter breadth, and fallback witnesses.

That means the ecosystem no longer mainly lacks raw primitives.
It lacks a **shared product-shape** for publishing localization support truth.

## What the crate should provide other people

For app teams, library authors, reviewers, and downstream adopters, the crate should provide:

1. **One message-argument schema receipt** instead of scattered macros and ad hoc key docs.
2. **One locale-data profile receipt** instead of vague “ICU4X-backed” marketing.
3. **One formatter-coverage report** instead of guessing which token families are really safe to use.
4. **One fallback witness report** instead of reverse-engineering locale negotiation from code.
5. **One compact contract-check report** that keeps generated facts, imported substrate, and manual-review zones visibly separate.

## Four first-class review objects

### 1. `message-arg-schema.receipt`

This artifact should answer:

- what each public message id is,
- which arguments are accepted,
- which argument names are required,
- which argument kinds are intended,
- and whether the evidence was generated directly or declared manually.

Suggested `0.1` argument kinds:

- `string`
- `number`
- `date`
- `datetime`
- `time`
- `list`
- `enum`
- `custom`

### 2. `data-profile.receipt`

This artifact should answer:

- whether the runtime uses `compiled_default`, `baked_subset`, `blob_runtime`, `filesystem_runtime`, `host_bridge`, or `mixed`,
- which locales are guaranteed,
- which locales are opportunistic or runtime-loaded,
- whether the profile is mutable after build,
- and whether size/breadth tradeoffs are explicit.

### 3. `formatter-coverage.report`

This artifact should answer:

- whether support is plain substitution, message-level selection only, or ICU4X-backed formatting,
- whether number/date/time/list/relative-time/plural/select families are fully wired,
- and whether any token family is adapter-specific or manual-review-required.

### 4. `fallback-witness.report`

This artifact should answer:

- what locale(s) were requested,
- what negotiation / fallback strategy was in play,
- what path actually resolved,
- whether the fallback came from message-layer policy, ICU4X locale fallback, or custom app logic,
- and whether the witness was directly observed or merely inferred.

## Recommended `0.1` command surface

### `cargo i18n-contract capture`
Capture the declared/generated contract and emit:
- `message-arg-schema.receipt.json`
- `data-profile.receipt.json`
- `formatter-coverage.report.json`

### `cargo i18n-contract witness`
Run locale-resolution witnesses and emit:
- `fallback-witness.report.json`

### `cargo i18n-contract check`
Run conservative checks and emit:
- `i18n-contract-check.report.json`

### `cargo i18n-contract diff`
Compare two contract bundles and emit:
- `i18n-contract-diff.report.json`

### `cargo i18n-contract bundle`
Produce one compact `.i18ncontractbundle.zip`.

## Workspace split

- `i18n_contract_model`
- `i18n_contract_codegen`
- `i18n_contract_icu4x`
- `i18n_contract_fluent`
- `i18n_contract_simple`
- `cargo-i18n-contract`

## Discovery order

1. **Capture message schema**
   - generated bindings
   - compile-time-checked message ids/args
   - manually declared overrides
2. **Capture data profile**
   - compiled defaults
   - baked subsets
   - runtime blob/fs/host-backed providers
3. **Capture formatter coverage**
   - plain substitution vs ICU4X-backed families
   - selection/plural support
   - adapter-specific holes
4. **Witness fallback**
   - requested locale list
   - negotiation result
   - ICU4X fallback path where applicable
5. **Bundle and diff**
   - export one compact review bundle

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- ICU4X compiled-data constructors
- custom `DataProvider` paths
- `LocaleFallbackProvider` / locale fallback configuration
- Fluent high-level loaders and resource managers
- compile-time message/arg checking from related crates
- asset embedding / locale-requester helpers

### Do not flatten into one fake verdict
- “uses ICU4X”
- “uses Fluent”
- “has typed keys”
- “has fallback”
- “supports localization”

Those are ingredients, not the contract.

## Preferred proving grounds

- a tiny CLI using compiled default ICU4X data and only plain string substitution,
- a desktop app with a baked locale subset and ICU4X-backed number/date formatting,
- a web/WASM app using browser-requested locale and runtime-loaded data,
- a Fluent-based app whose message arguments are compile-time checked but whose formatter coverage is only partial.

## Non-goals

- not a CAT / translation-management platform,
- not a new message syntax standard,
- not a replacement for MF2 work,
- not a UI/widget localization toolkit,
- not a translator-quality scoring system.
