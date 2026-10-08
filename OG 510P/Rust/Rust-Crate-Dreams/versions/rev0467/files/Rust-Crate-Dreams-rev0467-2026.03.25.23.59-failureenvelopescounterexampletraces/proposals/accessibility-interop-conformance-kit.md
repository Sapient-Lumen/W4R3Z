---
id: P-0202
title: Accessibility Capture & Interop Lab — cross-platform tree capture, semantic diffs, and repro bundles
status: idea
domains: [ui, accessibility, conformance, tooling, cross-platform]
last_reviewed: 2026-03-09
evidence:
  - https://accesskit.dev/
  - https://docs.rs/crate/accesskit_winit/latest
  - https://www.freedesktop.org/wiki/Accessibility/AT-SPI2/
  - https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-providersoverview
  - https://developer.apple.com/documentation/appkit/nsaccessibility
  - https://blogs.gnome.org/a11y/2024/06/18/update-on-newton-the-wayland-native-accessibility-project/
  - https://www.w3.org/TR/WCAG22/
  - https://www.w3.org/TR/act-rules-format/
---

# P-0202 — Accessibility Capture & Interop Lab

**Codename:** `a11ylab`

**Primary surface:** a crate family plus `a11ylab` CLI.

**Canonical artifact:** `*.a11ybundle.zip`.

## Problem

Even when a Rust toolkit emits a good accessibility tree, teams still need to answer a harder cross-platform question:

> “What did Linux/Windows/macOS accessibility clients actually see, what events fired, how did it differ from expectations, and what is the smallest redacted repro bundle we can share?”

That is a different problem from authoring-side semantic doctoring.
It lives on the **observer / capture / interop** side of the stack.

Rust already has stronger substrate than it used to:

- AccessKit provides a shared abstraction,
- the `winit` adapter exposes native accessibility APIs where supported,
- platform APIs already exist on AT-SPI2, UIA, and NSAccessibility/AX,
- and recent Linux work such as Newton shows the backend/interoperability story is still moving.

That combination makes the missing crate more specific.
The missing crate is not “yet another Rust accessibility abstraction”.
It is a **capture-and-diff lab** that freezes what was exposed on each platform and how to compare it safely.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “What accessibility tree and event stream were actually observed on a target platform, how does it differ from another build/platform/expected snapshot, and which parts are portable versus platform-specific?”

That answer should travel as one redacted bundle, with explicit loss accounting.

## What the crate should provide other people

### 1. A normalized capture model with explicit platform extensions
The crate should define a small, portable tree/event model that captures:

- stable node identity,
- role/name/description/value/state/action semantics,
- focus/selection/live-region events,
- parent/child and labeling relations,
- and platform-specific extension lanes when information does not map cleanly.

The key planning move is **not** to pretend AT-SPI2, UIA, and AX are identical.
The crate should preserve a common core plus explicit per-platform loss/extension fields.

### 2. A semantic diff engine
Another missing deliverable is a diff that says more than “JSON changed”.
A useful diff should explain:

- role/name/state changes,
- node appearance/disappearance,
- relation drift,
- event-sequence drift,
- unstable identity across rerenders,
- and platform-only differences that are not safely portable.

This is the part ordinary issue reports almost never provide today.

### 3. A redaction-aware repro bundle
The receiver-facing artifact should be `*.a11ybundle.zip` carrying:

- bundle manifest,
- tree snapshot,
- optional event stream,
- optional screenshot references or coordinate hints,
- backend capability notes,
- redaction policy,
- and optional diff report.

The important point is to make accessibility regressions shareable without dumping user content or raw screen-reader logs by default.

### 4. Conformance scenarios across backends
The crate should ship a tiny but serious TCK/lab for recurring UI patterns:

- dialogs,
- menus,
- tables,
- text fields,
- live regions,
- tree views,
- and focus restoration after modal transitions.

The purpose is not only correctness.
It is to make platform/backend drift visible and discussable.

### 5. Expected-vs-observed comparison
This kit should also make it possible to compare:

- an expected semantics snapshot (for example from authoring-side tooling such as **P-0087**),
- against observed platform capture bundles.

That gives Rust teams a sharper way to say whether the bug lives in:

- emitted semantics,
- platform translation,
- backend capability gaps,
- or capture incompleteness.

### 6. Receiver-facing capability and caveat reporting
A good crate contribution here should tell other people not only what was captured, but also what **could not** be captured or compared.
For example:

- unsupported table exposure,
- text attribute gaps,
- missing event classes,
- unstable element identities,
- or backend/platform mismatches that force manual review.

That honesty matters because the Linux story is still evolving, and portability claims can easily outrun reality.

## Persona / who it’s for

- toolkit maintainers debugging platform accessibility backends
- app teams chasing cross-platform accessibility regressions
- QA/release engineers who need reproducible repro bundles
- maintainers comparing expected semantics against observed platform exposure
- ecosystem builders maintaining conformance suites for common UI patterns

## Users & user stories

- **Toolkit maintainer:** “Our semantic tree looks right; show me what AT-SPI2/UIA/AX actually exposed.”
- **App team:** “A screen-reader regression only happens on one OS; produce one bundle and semantic diff instead of a vague bug report.”
- **QA engineer:** “Store redacted evidence of the event stream and tree shape for a modal-dialog regression.”
- **Interop maintainer:** “Tell me whether a mismatch is portable truth, platform-specific behavior, or missing capture support.”

## Prior art scan (and why it’s insufficient)

### Platform APIs exist, but not a Rust-first repro workflow
AT-SPI2, UIA, and NSAccessibility define the platform contracts.
That is necessary substrate.
It is not the missing Rust crate.
The missing crate is the **portable capture / diff / bundle / caveat layer above them**.

### AccessKit proves the shared abstraction, not the observer lab
AccessKit and its adapters are strong evidence that Rust can share authoring-side infrastructure.
But the ecosystem still lacks one common observer-facing bundle and semantic diff surface for cross-platform debugging.

### Linux backend architecture is still moving
The Newton work is especially useful as a reality check.
It shows that some backend assumptions, especially on Linux/Wayland, are not permanently settled.
That makes an explicit capability/caveat layer more important, not less.

## Design goals

1. **Observer-side focus** — capture what platforms expose; do not collapse this into authoring-side doctor/gating.
2. **Portable core + explicit extensions** — normalize common semantics while preserving platform-specific truth.
3. **Redaction-first** — structure should be shareable without default leakage of user content.
4. **Diffability** — semantic drift should be machine-readable and human-explainable.
5. **Conservative comparability** — manual-review-required and not-comparable are first-class results.
6. **Expected-vs-observed support** — enable alignment checks with authoring-side tools.

## Explicit non-goals

- replacing screen readers,
- claiming full legal compliance,
- becoming a GUI framework,
- pretending platform APIs are perfectly interchangeable.

## Proposed architecture

```text
a11ylab-core/           # normalized tree/event model, loss accounting
a11ylab-linux/          # AT-SPI2 capture backend
a11ylab-windows/        # UIA capture backend
a11ylab-macos/          # AX/NSAccessibility capture backend
a11ylab-diff/           # semantic diff engine, comparability classes
a11ylab-bundle/         # a11ybundle packing/redaction/import
a11ylab-tck/            # scenario suites and fixtures
a11ylab-cli/            # snapshot, diff, explain, redact
```

## Core artifacts

### `bundle-manifest.json`
A compact record of:

- capture backend and version,
- OS/app/toolkit identity,
- scenario identity,
- capability and redaction profiles,
- and included artifact paths.

### `tree.snapshot.json`
A normalized tree with:

- stable ids,
- core semantics,
- relation edges,
- extension lanes,
- and loss/caveat annotations.

### `event-stream.jsonl`
Optional event records with:

- focus/value/selection/live-region events,
- event ordering,
- timestamps or logical order,
- and platform-specific fields when needed.

### `semantic-diff.report.json`
A machine-readable explanation of:

- portable deltas,
- platform-specific deltas,
- unsupported comparisons,
- and likely next actions.

## MVP

- bundle manifest + tree snapshot + semantic diff
- one backend first (likely Linux AT-SPI2 or AccessKit/winit-hosted capture)
- scenario corpus for dialogs, menus, and text controls
- redaction defaults for names, values, typed text, and screenshots
- expected-vs-observed comparison path against authoring-side snapshots

## v1 path

- more complete event-stream coverage,
- Windows/macOS parity,
- capability matrices per backend,
- richer table/tree/live-region scenarios,
- import/export bridges to broader evidence bundles.

## Why now

This area is timely because Rust now has just enough shared accessibility substrate that cross-platform bugs are increasingly about **interop, backend capability, and reproducible diffs**, not simply “nobody tried accessibility yet”.
The sharper missing value is the boring capture-and-bundle layer above a moving but credible substrate.

## Related proposals

- **P-0087 UI Accessibility Doctor Kit** should own authoring-side semantics, rule evaluation, and release gating.
- **P-0092 GUI Testing & Snapshot Harness Kit** is broader render/event testing; this proposal is specifically accessibility capture, semantic diff, and repro bundles.
- **P-0027 Text Input Kit** and similar lower-layer proposals can feed richer text semantics into this lab but should not be collapsed into it.
