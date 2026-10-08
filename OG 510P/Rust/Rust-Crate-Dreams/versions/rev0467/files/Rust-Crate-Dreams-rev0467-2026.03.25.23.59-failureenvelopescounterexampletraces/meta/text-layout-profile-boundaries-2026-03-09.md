# Text layout profile boundaries — 2026-03-09

This note exists to stop the archive from flattening **case**, **profile**, **backend capability**, **decision origin**, and **font resolution** into one blurry text-layout blob.

The stack boundary note added earlier separated text *layers*.
This note separates the **receiver-facing artifacts** that a worthy crate should hand other people.

## Main judgment

A handoff-ready text-layout crate should make five different truths reviewable:

1. **what the caller asked for**,
2. **which policy/data profile the run claimed to honor**,
3. **which backend surfaces were even available**,
4. **which important decisions came from pinned policy versus backend discretion**, and
5. **which fonts actually resolved at runtime**.

If those get flattened together, maintainers cannot tell whether a diff came from Unicode-data drift, CSS-like policy drift, missing knobs in a backend, or a changed font universe.

## 1. Layout case
Primary artifact: `layout-case.json`.

This is the semantic request:

- input text,
- locale/script/direction hints,
- width constraints,
- requested families,
- style runs,
- and the comparison goal.

A case should **not** silently smuggle in a full policy profile.

## 2. Layout profile
Primary artifact: `layout-profile.json`.

This is the pinned policy/data contract:

- Unicode version / annex revisions,
- wrap-policy lane,
- line-break mode,
- word-break mode,
- overflow-wrap mode,
- emoji-presentation policy,
- fallback policy mode,
- and similar “expected semantics” knobs.

This is where a WPT-derived CSS-text lane should live.
It is also where a toolkit- or editor-tailored lane should become explicit instead of pretending to be a raw Unicode default.

## 3. Backend capability receipt
Primary artifact: `backend-capability.receipt.json`.

This records which backend lane ran, which shaping/segmentation/fallback substrate it used, and which exactness lane it honestly belongs to.

This artifact answers:

- what the runner was,
- what it claimed to support,
- and what should already be treated as advisory-only.

## 4. Decision-origin receipt
Primary artifact: `decision-origin.receipt.json`.

This is the missing explanation layer.
For the important surfaces, it should say whether the decision came from:

- the case,
- the pinned profile,
- Unicode/default data,
- backend default behavior,
- the font universe,
- platform APIs,
- manual override,
- or an unimplemented/missing lane.

Without this artifact, a future reader cannot tell whether a break-selection or emoji-presentation diff is a regression or simply a lane mismatch.

## 5. Font-resolution receipt
Primary artifact: `font-resolution.receipt.json`.

A `fontset.lock` says what was *allowed* or *intended*.
A font-resolution receipt says what *actually happened*.

That distinction matters because many text bugs are really:

- unavailable families,
- different bold/italic fallback selection,
- different emoji fonts,
- or different platform discovery results.

Do not make receivers infer runtime font truth from the request alone.

## Practical rule for future passes

Before editing **P-0197** or adding another nearby proposal, ask:

1. is this artifact about the **request**,
2. the **profile**,
3. the **backend capability surface**,
4. the **origin of decisions**,
5. or the **actual resolved fonts**?

If the answer is “all of them at once”, the archive is probably collapsing too much again.

## Why this matters now

Rust’s text substrate is active and improving.
Parley, COSMIC Text, ICU4X, and HarfRust/rustybuzz now make it possible to run real comparison lanes, but their policy knobs and backend defaults are not identical.
That means the next missing value is increasingly the **honest review artifact** above them, not another engine-shaped abstraction.
