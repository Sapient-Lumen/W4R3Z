---
id: P-0197
title: Text Layout & Shaping Conformance Kit — deterministic layout cases, corpus imports, and portable repro bundles for Rust text stacks
status: idea
domains: [gui, text, i18n, correctness, conformance, devtools]
last_reviewed: 2026-03-09
evidence:
  - https://github.com/linebender/parley
  - https://github.com/pop-os/cosmic-text
  - https://github.com/unicode-org/icu4x/blob/main/CHANGELOG.md
  - https://blog.unicode.org/2025/05/icu4x-20-released.html
  - https://www.unicode.org/reports/tr14/
  - https://www.unicode.org/reports/tr29/
  - https://www.unicode.org/reports/tr41/
  - https://github.com/harfbuzz/rustybuzz
  - https://github.com/harfbuzz/harfbuzz-testing-wikipedia
  - https://github.com/web-platform-tests/wpt/tree/master/css/css-text
  - https://github.com/bevyengine/bevy/issues/21765
  - https://www.unicode.org/versions/Unicode17.0.0/
  - https://github.com/linebender/parley/issues/492
  - https://github.com/linebender/parley/issues/555
  - https://github.com/pop-os/cosmic-text/issues/434
  - https://github.com/pop-os/cosmic-text/issues/416
needs:
  - Rust now has credible text substrate in Parley, COSMIC Text, HarfRust/rustybuzz, and ICU4X, but it still lacks a shared correctness-lab crate that can freeze layout cases, corpus imports, backend capabilities, and portable bug bundles.
  - Unicode annexes and test data cover break opportunities and segmentation defaults, but real text regressions in apps often come from the layer above them: fallback, bidi/layout interaction, width fitting, emergency breaks, and backend-tailoring policy.
  - Backend choice is still moving in the ecosystem, which makes a stable comparison/reporting artifact more valuable than prematurely blessing one text engine or renderer as the answer.
risks:
  - Pixel-perfect equality is the wrong target; the kit must compare semantic layout outputs and declared policy lanes, not promise identical rasterization everywhere.
  - Fonts, Unicode data, and fallback policies drift independently; the kit must pin and report each of them separately.
  - Corpus scope can explode unless the crate starts with a tiny pinned font pack, Unicode-derived imports, and a small curated Rust-text failure suite.
---

# P-0197 — Text Layout & Shaping Conformance Kit

**Codename:** `textlayoutkit`

**Bundle:** `*.textlayoutbundle.zip`

**Primary surface:** a layered crate workspace plus `cargo textlayout`.

## Problem

Rust’s text stack is no longer missing in the primitive sense.

There is now real substrate:

- `parley` provides rich text layout and explicitly sits on a stack that includes Fontique, HarfRust, Skrifa, and ICU4X.
- `cosmic-text` provides advanced shaping, layout, font fallback, and bidi handling in safe Rust.
- ICU4X 2.0 makes the i18n substrate more credible, but also makes version pinning and upgrade-diff discipline more important.
- `rustybuzz` is already close to HarfBuzz behavior on the published shaping tests, which means the gap is less about “can Rust shape text?” and more about “can Rust teams compare and explain text behavior?”
- GUI stacks are still choosing and re-choosing layout backends; even Bevy discussion shows active comparison between `parley` and `cosmic-text` rather than a universally settled answer.

But the ecosystem still lacks the thing maintainers most need when text goes wrong:

> one stable way to describe a layout case, pin the corpus/fonts/Unicode inputs **and the layout profile that claims to interpret them**, run it across backends, diff the semantic results, and attach a portable repro bundle upstream.

Unicode itself also draws a boundary that matters here.
UAX #14 defines line-break opportunities, UAX #29 defines default segmentation boundaries, and TR41 links the current data and test files.
Those are crucial anchors, but they do **not** define the whole product surface that application teams actually debug.
Real regressions often live above them:

- fallback family choice,
- emergency-break policy,
- bidi/layout interaction,
- cluster mapping,
- width measurement,
- emoji or variation-sequence handling,
- line-break or word-break policy imported from CSS/toolkit/editor lanes,
- and “same text, different backend/data/font inputs” drift.

So the missing crate is not “yet another text engine”.
It is the **correctness lab above moving text substrate**.

## Main judgment

A worthy crate contribution here would not mainly be another renderer, widget toolkit, or shaping engine.

It would be a kit that lets another team say:

- here is the exact layout case,
- here is the pinned corpus / Unicode / font / fallback profile,
- here is what each backend claimed it could do,
- here is the semantic layout output,
- and here is the diffable bundle showing what changed and why it may or may not be comparable.

That would make text bugs portable, reviewable, and much easier to upstream across Rust GUI, editor, terminal, and document stacks.

## What the crate should provide other people

### 1. A stable layout case model
The kit should define a portable `LayoutCase` that captures:

- input text,
- style runs,
- locale / script / direction hints,
- width and line-fit constraints,
- selected Unicode-data profile,
- requested font families and fallback mode,
- feature toggles such as ligatures or variation settings,
- and declared comparison goals.

The point is to preserve the **semantic request**, not merely a screenshot.

### 2. A pinned layout profile contract
The kit should separate the *request* from the *interpretation policy*.
A `layout-profile.json` should pin things like:

- Unicode version and annex revisions,
- wrap-policy lane (`unicode_default`, `css_text_like`, `toolkit_tailored`, `editor_tailored`),
- line-break / word-break / overflow-wrap modes,
- emoji-presentation mode,
- fallback-policy mode,
- and grapheme-safety expectations.

This is how the crate avoids fake certainty when a WPT-derived CSS-text lane, a toolkit-default lane, and a raw Unicode-default lane are not actually asking the same question.

### 3. A corpus-import receipt
The crate should make normative and curated corpus provenance reviewable.
A receiver should be able to tell whether a case came from:

- Unicode line-break or segmentation tests,
- bidi tests,
- emoji data or variation-sequence data,
- HarfBuzz-derived shaping corpus,
- WPT CSS text cases,
- or a Rust-specific regression suite.

That means the crate should emit a `corpus-import.receipt.json` describing source URLs, pinned versions, normalization steps, and any lossy trimming.

### 4. Backend capability receipts
Every runner lane should report its truth surface explicitly.
A `backend-capability.receipt.json` should state things like:

- backend and version,
- shaping engine,
- segmentation provider,
- fallback source,
- exactness lane,
- whether metrics are native or imported,
- which profile axes are really supported,
- which surfaces are already known to be backend-discretion territory,
- and whether raster artifacts are comparable or advisory-only.

This is how the kit avoids fake certainty when two backends do not actually expose the same knobs.

### 5. A normalized semantic layout IR
The core output should be a stable JSON/CBOR IR with things like:

- resolved paragraphs and runs,
- line boxes,
- break opportunities considered and selected,
- glyph runs and advances,
- cluster / byte / scalar mappings,
- fallback decisions,
- bidi reordering notes,
- measurement and overflow decisions,
- and exactness / tailoring annotations.

That IR is what makes diffs and review possible.

### 6. Decision-origin and font-resolution receipts
The kit should not force receivers to guess where important decisions came from.
It should produce:

- `decision-origin.receipt.json` describing whether line-break choice, word boundaries, grapheme boundaries, bidi resolution, emoji presentation, fallback selection, and width measurement came from the case, the pinned profile, Unicode data, backend defaults, platform APIs, or the font universe,
- and `font-resolution.receipt.json` describing which requested families actually resolved at runtime, from which provider, for which role (`primary`, `fallback`, `emoji`, `bold`, `italic`), and whether the resulting font universe is honestly comparable.

This is the difference between a “text changed” complaint and a reviewable explanation.

### 7. Diff and diagnosis reports
The kit should separate raw layout output from interpretation.
It should produce:

- `layout-diff.report.json` for semantic differences,
- `diagnosis.report.json` for likely failure families,
- and `conformance-result.report.json` later for corpus-backed status.

A diagnosis report should classify likely causes such as:

- segmentation drift,
- bidi resolution drift,
- shaping drift,
- fallback mismatch,
- measurement-mode mismatch,
- or non-comparable font universe.

### 8. Portable repro bundles
`*.textlayoutbundle.zip` should capture:

- the case spec,
- font-set lock or referenced test-font hashes,
- corpus provenance receipt,
- backend capability receipts,
- semantic layout outputs,
- semantic diff and diagnosis reports,
- and optional overlays or screenshots.

A maintainer should be able to open one bundle and tell whether the failure is honestly comparable across lanes.

### 9. Explicit exactness and tailoring lanes
The kit should not flatten all results into “pass” or “fail”.
It should support lanes like:

- `unicode_default`,
- `backend_tailored`,
- `font_universe_variant`,
- `manual_review_only`,
- and `render_overlay_only`.

That keeps the crate honest when Unicode defaults, browser-style fallback lists, and application-specific policy diverge.

### 10. A small boring CLI
The CLI should support:

- `cargo textlayout run`
- `cargo textlayout diff`
- `cargo textlayout corpus import`
- `cargo textlayout bundle`
- `cargo textlayout doctor`

The doctor output should prefer short explanations over giant glyph dumps.

## Persona / who it’s for

- GUI toolkit maintainers
- editor and terminal authors
- app teams shipping multilingual UIs
- CI owners who need deterministic text regression coverage
- maintainers triaging “this paragraph wraps differently on backend B” bugs

## Users & user stories

- **Toolkit maintainer:** “We want to swap or upgrade a text backend without losing our regression memory.”
- **Editor author:** “A user found a bidi + fallback bug; export one bundle we can inspect without screen-sharing their exact machine.”
- **App team:** “We upgraded ICU4X / Unicode data / fonts; tell us exactly which layout cases changed and whether the diff is expected.”
- **Downstream integrator:** “Show me whether differences come from shaping, segmentation, line breaking, fallback, or line-fit policy.”

## Prior art scan (and why it’s insufficient)

### `parley`
`parley` is strong evidence that Rust now has serious layout substrate.
But that is exactly why the missing crate has changed.
`parley` is a backend, not a shared corpus / diff / bundle contract.

### `cosmic-text`
`cosmic-text` provides shaping, layout, rendering, bidi support, and custom fallback in safe Rust.
That makes it valuable substrate and a useful comparison lane.
It still does not define a backend-neutral repro-bundle or corpus-import workflow.

### ICU4X 2.0 and Unicode data/test files
ICU4X and Unicode annexes provide important segmentation and line-break anchors, and TR41 points to current data and test files.
But the Unicode material does not hand Rust maintainers a portable bug bundle or a backend-comparison harness.

### `rustybuzz` / HarfBuzz corpus
`rustybuzz` is already close to HarfBuzz behavior on the published shaping corpus, and the HarfBuzz ecosystem publishes real shaping test material.
That is excellent shaping substrate.
It still does not solve layout-level provenance, fallback truth, or backend comparison.

### WPT CSS text tests
WPT gives another valuable import lane, especially when browser-style line-break or wrapping expectations matter.
But WPT is not a Rust-native artifact contract and does not provide the review bundle the archive is targeting.

## Design goals

1. **Semantic comparison, not screenshot worship**
2. **Pinned corpus / font / Unicode provenance**
3. **Backend-neutral artifact contracts**
4. **Portable repro bundles**
5. **Explicit exactness and tailoring lanes**
6. **Incremental adoption above existing text stacks**

## Proposed architecture

```text
textlayout-case/       # case model, Unicode/font/profile pinning
textlayout-corpus/     # Unicode/WPT/HarfBuzz imports + curated Rust regressions
textlayout-ir/         # stable semantic layout IR and diff vocabulary
textlayout-runner/     # runner traits and backend adapters
textlayout-bundle/     # bundle reader/writer + diagnosis reports
textlayout-cli/        # cargo textlayout commands
```

## Core artifacts

### `layout-case.json`
Declares the semantic request, width constraints, locale/script hints, requested font stack, and comparison goals.

### `layout-profile.json`
Pins the Unicode/data/policy interpretation lane separately from the case.
This is where CSS-like line-break strictness, toolkit-tailored behavior, emoji-presentation preference, and similar “semantic expectation” knobs belong.

### `fontset.lock.json`
Pins test fonts, hashes, fallback order, and whether the case is using shipped test fonts or bring-your-own-font mode.

### `corpus-import.receipt.json`
Records where the case came from, what version was imported, what normalization/trimming occurred, and whether any normative information was discarded.

### `backend-capability.receipt.json`
Records exactly which backend lane produced the output and which features are authoritative versus advisory.

### `decision-origin.receipt.json`
Records which important decisions came from the profile, Unicode data, backend defaults, platform APIs, or the font universe.

### `font-resolution.receipt.json`
Records which requested fonts actually resolved and whether the runtime font universe is comparable.

### `layout-output.json`
The normalized semantic layout IR.

### `layout-diff.report.json`
Summarizes semantic differences and their suspected family.

### `diagnosis.report.json`
Explains likely root causes and comparability caveats.

### `*.textlayoutbundle.zip`
Portable container for the whole repro packet.

## Fixture-first MVP

The repo should ship fixture schemas for:

- `layout-case.json`
- `layout-profile.json`
- `fontset.lock.json`
- `corpus-import.receipt.json`
- `backend-capability.receipt.json`
- `decision-origin.receipt.json`
- `font-resolution.receipt.json`
- `layout-output.json`
- `layout-diff.report.json`
- `diagnosis.report.json`
- and the `textlayoutbundle` manifest.

The fixture pack should also include at least two scenario families:

1. a **Unicode/default-data** case such as Thai or emoji break behavior with pinned data,
2. a **backend-policy** case such as Arabic+Latin+bidi+fallback interaction,
3. and at least one **policy-profile** case where the same text is intentionally run under distinct interpretation lanes (for example `unicode_default` vs `css_text_like`).

## Suggested first scenario set

### `thai_emoji_wrap_upgrade`
Tests whether a Thai sentence with emoji/ZWJ content changes line-fit behavior after Unicode-data or backend upgrades.

### `arabic_latin_bidi_fallback_regression`
Tests whether bidi reordering, fallback family choice, and width measurement interact to change the chosen line breaks or cluster mapping.

### `cjk_unknown_lang_linebreak_policy`
Tests whether the same CJK text diverges under a raw Unicode-default lane versus a CSS-text-like strict line-break profile, with decision-origin receipts making the policy difference reviewable instead of mysterious.

## MVP surface

### 0.1
- stable `LayoutCase` JSON schema
- tiny pinned test-font pack
- corpus-import receipt format
- adapters for `parley` and one lower-level shaping/segmentation lane
- semantic `LayoutOutput` IR
- `cargo textlayout run`, `diff`, and `bundle`

### 0.2
- `cosmic-text` adapter
- layout-profile and decision-origin receipts
- diagnosis classifications
- WPT import helpers
- screenshot/SVG overlays as advisory artifacts

### 0.3
- optional platform/native backend import lanes
- richer fallback-policy reporting
- upgrade-diff mode for Unicode/backend/font-set changes

## Adoption plan

1. Start with one tiny bundled font pack and a bring-your-own-font escape hatch.
2. Ship adapters for two real Rust backends before chasing platform imports.
3. Make bundle reading easy enough that maintainers can request `textlayoutbundle.zip` in bug templates.
4. Publish a small curated “Rust text gotchas” corpus once the core schemas settle.
5. Treat `layout-profile` identifiers as reviewable public API, because profile drift is one of the main things downstream users will diff.

## Path to boring stability

- Freeze the case model, layout-profile vocabulary, and decision-origin receipts before expanding backend count.
- Treat font provenance as first-class support truth, not as an incidental implementation detail.
- Keep exactness lanes explicit whenever fallback or tailoring differs.
- Prefer semantic diffs over visual diffs unless a human-facing artifact is truly needed.
- Keep corpus import provenance visible so future readers know what was normative versus curated.

## Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 3/5
- Differentiation: 5/5
- **Total: 24/30**

## Minimum lovable MVP

A crate workspace that lets a maintainer run one pinned corpus across two profile/backend lanes, diff semantic layout outputs, and export one `textlayoutbundle.zip` that honestly states whether the results are comparable and which decisions came from policy versus backend discretion.

## De-risk plan

1. Start with semantic layout data only; avoid renderer wars.
2. Use a tiny pinned font pack plus optional bring-your-own-font mode.
3. Separate Unicode-default behavior from backend-tailored behavior in reports.
4. Pilot against one GUI toolkit and one editor-style integration before adding more backend count.

## Explicit non-goals

- Not a full renderer.
- Not a universal font-management system.
- Not a promise of identical pixels across operating systems.
- Not a replacement for Unicode specs, WPT, HarfBuzz tests, or backend-native test suites.
- Not a stealth attempt to crown one backend as “the Rust text winner”.

## Open questions

- Which adapter pair gives the sharpest 0.1 comparison surface: `parley` + lower-level lane, or `parley` + `cosmic-text` directly?
- What is the smallest redistributable font set that still exercises the tricky cases responsibly?
- How much fallback metadata can be standardized without leaking OS-specific internals or pretending browser and app fallback are the same?
- Which profile axes should become part of stable comparability policy in 0.1, and which should stay advisory-only until multiple adapters prove them out?
- Which WPT imports are most valuable without dragging a browser-sized corpus into the MVP?

## Sources

- https://github.com/linebender/parley
- https://github.com/pop-os/cosmic-text
- https://github.com/unicode-org/icu4x/blob/main/CHANGELOG.md
- https://blog.unicode.org/2025/05/icu4x-20-released.html
- https://www.unicode.org/reports/tr14/
- https://www.unicode.org/reports/tr29/
- https://www.unicode.org/reports/tr41/
- https://www.unicode.org/versions/Unicode17.0.0/
- https://github.com/harfbuzz/rustybuzz
- https://github.com/harfbuzz/harfbuzz-testing-wikipedia
- https://github.com/web-platform-tests/wpt/tree/master/css/css-text
- https://github.com/bevyengine/bevy/issues/21765
- https://github.com/linebender/parley/issues/492
- https://github.com/linebender/parley/issues/555
- https://github.com/pop-os/cosmic-text/issues/434
- https://github.com/pop-os/cosmic-text/issues/416
