# Text layout correctness stack boundaries — 2026-03-09

This note exists to stop the archive from collapsing several nearby ideas into one vague “Rust text crate”.

Rust now has enough text substrate that the sharper question is usually **which layer is missing**, not whether text matters.

## Main judgment

There are at least six different layers here:

1. **Unicode data and default algorithms**
2. **shaping engines**
3. **layout engines and width-fitting policy**
4. **font discovery and fallback policy**
5. **render/raster overlays**
6. **correctness labs and repro bundles**

Future revisions should keep those layers explicit.

## 1. Unicode data and default algorithms
Examples: **UAX #14**, **UAX #29**, bidi data/tests, ICU4X segmenters/data.

This layer is about:

- break opportunities,
- grapheme/word/sentence segmentation,
- bidi data and related test files,
- emoji / variation-sequence data,
- and pinned Unicode versions.

A proposal in this layer should talk about:

- data revision pinning,
- algorithmic conformance,
- test-file imports,
- and tailoring boundaries.

It is **not** automatically a full text layout or GUI correctness story.

## 2. Shaping engines
Examples: **HarfBuzz**, **HarfRust/rustybuzz**.

This layer is about:

- script-aware shaping,
- glyph selection and positioning,
- OpenType feature handling,
- and shaping-test corpus conformance.

It is adjacent to layout, but it is not the same thing as line fitting, fallback choice, or paragraph measurement.

## 3. Layout engines and width-fitting policy
Examples: **Parley**, **COSMIC Text**, lower-level layout pipelines.

This layer is about:

- line boxes,
- width constraints,
- break selection,
- cluster mapping,
- inline object handling,
- and paragraph metrics.

A proposal in this layer should talk about layout outputs and policy surfaces, not just shaping.

## 4. Font discovery and fallback policy
Examples: browser-style fallback lists, toolkit-specific font resolution, test-font packs.

This layer is about:

- which families are tried,
- which fonts actually resolved,
- fallback order,
- locale/script-sensitive font policy,
- and whether the font universe is even comparable across runs.

Many “text regressions” are really fallback or font-availability regressions.
The archive should not flatten those into generic shaping failure.

## 5. Render/raster overlays
Examples: screenshots, SVG overlays, glyph atlas output, pixel diffs.

This layer is useful for human debugging, but it should remain **advisory** in the archive’s main text-layout proposal.
Pixel-perfect equality is too strong and too backend-dependent to be the core contract.

## 6. Correctness labs and repro bundles
Primary archive home: **P-0197 Text Layout & Shaping Conformance Kit**.

This layer is about:

- stable case models,
- corpus-import receipts,
- backend capability receipts,
- normalized semantic layout outputs,
- semantic diffs and diagnosis reports,
- and portable repro bundles.

This is the layer that turns moving backend choice into reviewable support truth.

## Practical rule for future passes

Before adding or editing a proposal in this family, ask:

1. is the crate mainly about **Unicode/default algorithm conformance**,
2. about **shaping**,
3. about **layout and width-fitting policy**,
4. about **font/fallback resolution**,
5. about **render/raster visualization**,
6. or about a **cross-backend correctness lab**?

If the answer is “all of them at once”, the proposal is probably too blurry.

## Why this matters now

Current Rust substrate is no longer empty.
We now have enough real engines and data libraries that the likely missing crate is increasingly:

- a stable case format,
- corpus provenance,
- backend receipts,
- semantic diffs,
- and a portable support bundle,

rather than one more undifferentiated text engine.
