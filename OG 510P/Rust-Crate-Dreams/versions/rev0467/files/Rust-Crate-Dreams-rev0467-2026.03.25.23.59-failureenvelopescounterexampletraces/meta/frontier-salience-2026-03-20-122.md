# Frontier salience snapshot — 2026-03-20 (122)

This pass did **not** open another Cargo lane, another translation pipeline, or another message-syntax battle.
It deepened **P-0039 i18n-icu-kit** by making a more boring but more reusable boundary explicit:

- **a Rust project can truthfully say it uses ICU4X, Fluent, typed message helpers, and fallback locales while still leaving downstream users unable to tell what data profile is shipped, which formatter families are really supported, and what fallback path actually resolves at runtime.**

## Main judgment

The sharper missing layer is no longer merely “typed keys + ICU formatting glue”.
The sharper missing layer is a **message-schema / data-profile / formatter-coverage / fallback-witness contract**.

Current Rust localization substrate makes that specific:

1. ICU4X’s current README says clients can start with compiled data or use explicit `DataProvider`s, including runtime-updateable blob providers and locale fallback adapters.
2. ICU4X’s data-management tutorials explicitly position locale data selection and runtime loading as normal integration choices, not obscure hacks.
3. ICU4X’s current APIs expose configurable locale fallback behavior, including different priority strategies when dropping subtags.
4. The `fluent` crate still describes `FluentBundle` as a low-level container and says higher-level APIs should build on it.
5. `fluent-templates` and the `fluent-rs` workspace show there is real demand for higher-level lifecycle helpers, but those helpers do not publish one shared support contract.
6. `typed-i18n`, `rust-i18n`, `i18n-embed`, and `i18n-embed-fl` prove there is strong demand for type safety, embedding, fallback, and compile-time checks — but those strengths are still fragmented across different contract surfaces.

That means the next worthy move is not another syntax-specific macro.
It is one conservative crate family that can publish:

- **message-argument schema truth**,
- **locale-data profile truth**,
- **formatter-coverage truth**,
- and **fallback-witness truth**.

## Why this beat nearby work

The archive already had adjacent lanes for:

- end-to-end localization pipelines,
- MF2 conformance,
- text layout correctness,
- and generic translation helpers.

What it still lacked was one compact way to say:

- “we compile-check message args, but only support plain string substitution,”
- “we support ICU4X date/number formatting, but only for a baked locale subset,”
- and “we do have fallback, but it is app-specific language negotiation plus ICU4X locale fallback, not one magical default.”

That is a real receiver-facing product boundary, not another syntax preference.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0039 i18n-icu-kit** — materially stronger after this pass because Rust now has real localization substrate but still lacks a shared support contract above it.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream testing truth remains under-served.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
6. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
7. **P-0199 MessageFormat 2 Localization Kit** — still unusually promising, but should remain conformance/spec-first rather than pretending to solve the whole contract lane.
8. **P-0136 Localization Pipeline Kit** — still useful, but stronger when it imports an explicit runtime contract rather than owning one implicitly.

## What changed in the archive

Added:
- `entries/2026-03-20-302.md`
- `meta/frontier-salience-2026-03-20-122.md`
- `meta/i18n-icu-kit-product-plan-2026-03-20.md`
- `meta/i18n-icu-kit-lane-boundaries-2026-03-20.md`
- `fixtures/i18n-icu-kit/README.md`
- `fixtures/i18n-icu-kit/message-arg-schema.receipt.schema.json`
- `fixtures/i18n-icu-kit/data-profile.receipt.schema.json`
- `fixtures/i18n-icu-kit/formatter-coverage.report.schema.json`
- `fixtures/i18n-icu-kit/fallback-witness.report.schema.json`
- scenario families for typed-argument coverage, compiled-vs-runtime data posture, and fallback-priority differences

Updated:
- `README.md`
- `INDEX.md`
- `proposals/i18n-icu-kit.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy localization-support contribution for Rust should now provide more than one pleasant API over Fluent or ICU4X.
It should provide:

- one explicit **message-argument schema receipt**,
- one explicit **locale-data profile receipt**,
- one explicit **formatter-coverage report**,
- and one explicit **fallback-witness report**.

## Freshness anchors

- ICU4X README / data management — https://docs.rs/icu/latest/source/README.md
- ICU4X data management tutorial — https://icu4x.unicode.org/2_1/tutorials/data-management/
- ICU4X runtime data loading tutorial — https://icu4x.unicode.org/2_0/tutorials/data-provider-runtime/
- ICU4X locale fallback docs — https://docs.rs/icu_locale/latest/icu_locale/fallback/struct.LocaleFallbackConfig.html
- `LocaleFallbackProvider` docs — https://docs.rs/icu_provider_adapters/latest/icu_provider_adapters/fallback/struct.LocaleFallbackProvider.html
- `fluent` docs — https://docs.rs/fluent/latest/fluent/
- `fluent-templates` docs — https://docs.rs/fluent-templates/latest/fluent_templates/
- Fluent high-level Rust APIs discussion — https://discourse.mozilla.org/t/high-level-fluent-rust-apis/123688
- `typed-i18n` docs — https://docs.rs/typed-i18n/latest/typed_i18n/
- `rust-i18n` docs — https://docs.rs/rust-i18n/latest/rust_i18n/
- `i18n-embed` docs — https://docs.rs/i18n-embed/latest/i18n_embed/
- `i18n-embed-fl` docs — https://docs.rs/i18n-embed-fl/latest/i18n_embed_fl/
