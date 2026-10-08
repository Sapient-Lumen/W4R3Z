# i18n-icu-kit lane boundaries (2026-03-20)

This note exists so the archive does not flatten several adjacent localization lanes into one fake “Rust i18n crate” story.

## Core judgment

**P-0039 i18n-icu-kit** should be the lane for:

- **typed message-argument schema truth**,
- **locale-data profile truth**,
- **formatter-coverage truth**,
- and **fallback-witness truth**.

It is the lane for the question:

> “What localization support contract is this Rust crate or app actually publishing to another team?”

## Keep separate from these adjacent lanes

### 1. P-0136 Localization Pipeline Kit

Localization Pipeline Kit is about:
- extraction,
- compilation,
- pseudolocalization,
- QA/doctor workflows,
- and shipping bundles.

`i18n-icu-kit` is **not**:
- the whole product-localization workflow,
- the cargo command suite for translators,
- or the bundle-shipping lane.

Pipeline work may import contract artifacts.
It does not own them.

### 2. P-0199 MessageFormat 2 Localization Kit

MF2 is about:
- parser / AST / runtime conformance,
- spec-aligned formatting semantics,
- and migration toward the Unicode MF2 standard.

`i18n-icu-kit` is **not**:
- the MF2 parser/runtime,
- the normative syntax lane,
- or the MF2 conformance harness.

This lane should work whether the message syntax is Fluent, MF2, or a simpler generated form.

### 3. Generic Fluent / rust-i18n / embedding helpers

Existing crates already provide:
- high-level Fluent loading,
- compile-time embedding,
- simple translation lookup,
- and some compile-time message checking.

`i18n-icu-kit` should **not** collapse into:
- another string-lookup macro,
- another syntax-specific loader only,
- or another asset-embedding convenience wrapper.

The missing value is the **reviewable support contract above those helpers**.

### 4. Text layout / shaping / editor stacks

Text layout work is about:
- segmentation,
- shaping,
- line break / bidi / font fallback,
- text-input geometry,
- and rendering correctness.

`i18n-icu-kit` is **not**:
- a shaping engine,
- a text layout conformance lab,
- or a text-input integration layer.

It may share ICU4X substrate with those lanes, but it owns message/data/fallback support truth instead.

## Review objects that should stay first-class

### `message-arg-schema.receipt`

Keeps compile-time-checked arguments, declared message parameters, and ad hoc runtime interpolation from collapsing into one fake “typed message” claim.

### `data-profile.receipt`

Keeps compiled default data, baked subsets, runtime-loaded blobs, filesystem providers, and host-backed sources from collapsing into one fake “ICU4X-backed” claim.

### `formatter-coverage.report`

Keeps plain substitution, select/plural support, and ICU4X-backed number/date/list/relative-time formatting from collapsing into one fake “rich formatting” claim.

### `fallback-witness.report`

Keeps language negotiation, ICU4X locale fallback, custom app overrides, and observed resolution paths from collapsing into one fake “has locale fallback” claim.

## Doctor warnings worth keeping separate

The first implementation should distinguish warnings such as:

- `typed_args_unknown_for_public_message`
- `data_profile_not_declared`
- `formatter_family_used_without_coverage_claim`
- `fallback_basis_implicit`
- `fallback_path_observed_only_in_manual_note`
- `manual_review_required`

## Non-goals for this boundary note

This note is **not** asking P-0039 to become:

- a translation-management platform,
- an MF2 standards implementation,
- a full extraction/compile/ship workflow,
- or a typography/layout correctness suite.

It is only insisting that **message schema**, **data profile**, **formatter coverage**, and **fallback witnesses** stay reviewable.
