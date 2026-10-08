---
id: P-0087
title: UI Accessibility Doctor Kit — AccessKit semantic contracts, cargo a11y doctor, and regression gating
status: idea
domains: [gui, accessibility, a11y, devtools, testing]
last_reviewed: 2026-03-19
evidence:
  - https://accesskit.dev/
  - https://docs.rs/crate/accesskit_winit/latest
  - https://docs.rs/egui/latest/egui/
  - https://docs.rs/kittest/latest/kittest/
  - https://www.w3.org/WAI/standards-guidelines/act/
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
  - https://www.w3.org/TR/wai-aria-1.2/
  - https://www.w3.org/TR/WCAG22/
  - https://www.w3.org/TR/act-rules-format/
---

# P-0087 — UI Accessibility Doctor Kit

**Codename:** `a11ydoctor`

**Primary surface:** a crate workspace plus `cargo a11y doctor` / `cargo a11y gate`.

**Canonical artifacts:** `semantic-contract.report.json`, `rule-authority.policy.json`, `a11ydoctor.report.json`, `baseline-drift.report.json`, and `a11ygate.result.json`.

## Problem

Rust GUI stacks have better accessibility substrate than they used to.
That is good news, but it also changes what the missing crate is.

AccessKit already gives Rust toolkits a shared accessibility abstraction, and the `winit` adapter exposes an accessibility tree through supported platform-native APIs.
`egui` already documents optional/native AccessKit support.
That means the sharpest remaining gap is **not** “invent accessibility from scratch for Rust”.

The missing crate is a **doctor + gating kit** that helps toolkit and app authors answer:

> “What semantic tree are we claiming, which rules does it violate, which regressions are blocking, and what evidence should CI hand to another developer?”

That is different from a cross-platform capture lab.
This proposal is about the **authoring / emitted-semantics side** of the problem.

## Main judgment

A worthy crate contribution here would give other people one honest answer to:

> “Did this toolkit or app emit a coherent accessibility tree, what high-impact problems remain, and should a release be blocked?”

That answer should be small, explainable, and friendly to CI.
It should not require every Rust GUI project to invent its own semantic checklist, rule severities, or baseline format.

## What the crate should provide other people

### 1. A stable semantic contract above widgets
The first missing deliverable is a compact semantic contract that toolkit authors can emit and apps can inspect.
It should freeze the questions that keep recurring in accessibility reviews:

- accessible name present or missing,
- role correctness,
- state/action consistency,
- focus order / tab reachability,
- disabled/hidden semantics,
- live-region and value semantics,
- and whether node identity stays stable across rerenders.

This should stay **AccessKit-shaped** instead of inventing a new parallel tree model.
The goal is to make authoring-side semantics reviewable before the OS/backend layer enters the picture.

### 2. A doctor ruleset with explicit severity classes
The crate should ship a boring default ruleset with categories such as:

- `blocking` — missing accessible names for actionable controls, focus traps, non-reachable dialogs, role/state contradictions,
- `warning` — suspicious role choices, unstable focus restoration, incomplete descriptions, unexpected live-region usage,
- `info` — portability caveats, advisory naming/labeling consistency, manual-review reminders.

The rule source should be clearly inspired by WCAG, WAI-ARIA, and ACT-style rule structure, while remaining honest that this crate is **not** a legal-compliance oracle.

### 3. Regression gating and baseline packs
Another missing deliverable is a reusable way to say:

- what changed in the semantic tree,
- which changes are allowed,
- which changes need manual review,
- and which changes fail CI.

That means the crate should provide:

- baseline packs for common widget patterns,
- a normalized diff of semantic-tree changes,
- policy files for per-project allowlists / waivers / severity upgrades,
- and one clean machine-readable gate result.

### 4. Toolkit integration patterns
The crate should help people wire accessibility into real Rust UI stacks.
It should provide reference patterns for:

- immediate-mode toolkits,
- retained-mode toolkits,
- custom canvas/game UIs that still need a semantic tree,
- and `winit`/AccessKit host integration.

The important point is to make the kit useful **without** requiring a full framework rewrite.

### 5. A developer-facing overlay and explanation UX
The MVP should expose an overlay or inspect view that tells another developer:

- what node is currently focused,
- what name/role/state the toolkit emitted,
- which doctor rules triggered,
- and how to reach the problem again.

Good accessibility tooling wins when it shortens the feedback loop.
The crate should act like `clippy` or `cargo deny` for semantic UI truth, not like a giant standards document.

### 6. Small receiver-facing artifacts
The crate should hand other people compact outputs such as:

- `toolkit-profile.json` — what backend/toolkit/ruleset was evaluated,
- `a11ydoctor.report.json` — findings with severity, evidence refs, and suggested next actions,
- `a11ygate.result.json` — pass/warn/fail/manual-review-required with diff summary.

That keeps authoring-side accessibility evidence portable between maintainers, CI, and issue reports.

## Persona / who it’s for

- toolkit maintainers adopting or improving AccessKit integration
- app teams that need accessible releases without building an in-house accessibility practice from zero
- CI/release engineers who want gating rules and portable findings
- QA and support engineers who need a small repro artifact instead of screenshots and guesswork

## Users & user stories

- **Toolkit maintainer:** “Tell me whether our emitted semantic tree is coherent before I start debugging platform backends.”
- **App team:** “A dialog release regressed keyboard reachability; fail CI and tell me exactly why.”
- **Release engineer:** “Treat blocking accessibility regressions like test failures, but preserve manual-review-required as an honest outcome.”
- **Contributor:** “Show me the node path, role, name, and focus sequence so I can fix the bug quickly.”

## Prior art scan (and why it’s insufficient)

### AccessKit is strong substrate, not the missing product
AccessKit already provides the shared cross-platform abstraction over accessibility APIs, and the `winit` adapter exposes a toolkit’s accessibility tree through supported native APIs.
That is exactly why the gap is now smaller and sharper.
What most Rust projects still lack is the **doctor/gating layer above emitted semantics**.

### Existing toolkit support proves timeliness, not closure
`egui` already documents optional/native AccessKit support.
That is evidence that accessibility is not hypothetical in Rust GUI land anymore.
But it does not give the wider ecosystem one common severity model, baseline pack, or CI gate result surface.

### Standards exist, but they are not a Rust workflow
WAI-ARIA, WCAG, and ACT-style rules matter because they shape semantics and severity.
But they are not a drop-in Rust crate workflow for emitted tree diffs, toolkit baselines, and issue-friendly artifacts.

## Design goals

1. **AccessKit-first** — reuse the shared Rust substrate instead of inventing a rival ontology.
2. **Authoring-side focus** — emitted semantics, doctor findings, and gating are the core; cross-platform backend capture is separate work.
3. **Explainability** — every failure should point to a node path, rule, severity, and suggested next step.
4. **CI-friendly** — baseline diffs and machine-readable gate results must be first-class.
5. **Manual-review honesty** — not every accessibility question is safely automatable.
6. **Framework-light** — useful for immediate-mode, retained-mode, and custom/canvas UIs.

## Explicit non-goals

- replacing screen readers or assistive technologies,
- claiming legal compliance by itself,
- owning cross-platform OS tree capture and interop replay,
- becoming a full GUI framework.

## Proposed architecture

```text
a11ydoctor-core/        # rule model, findings, severities, baseline diff
a11ydoctor-accesskit/   # AccessKit-shaped semantic extraction and helpers
a11ydoctor-winit/       # host integration helpers, event hooks
a11ydoctor-overlay/     # developer inspect/overlay surface
a11ydoctor-gate/        # CI gate policies and waivers
cargo-a11y/             # cargo a11y doctor / gate
```

## Core artifacts

### `toolkit-profile.json`
A compact record of:

- toolkit/app identity,
- backend profile,
- evaluated ruleset versions,
- baseline pack identity,
- and waiver/policy inputs.

### `a11ydoctor.report.json`
A machine-readable finding list with:

- severity,
- rule id,
- node path / stable node id,
- summary,
- evidence refs,
- and suggested next actions.

### `a11ygate.result.json`
A release/CI-oriented result with:

- `pass`, `warn`, `fail`, or `manual-review-required`,
- counts by severity,
- semantic diff summary,
- upgraded/downgraded severities,
- and the policy pack that produced the verdict.

### `semantic-contract.report.json`
A machine-readable statement of what the authoring-side tree is actually claiming:

- stable node ids or their absence,
- names and name sources,
- roles/states,
- value/selection semantics,
- and where manual review still begins.

### `rule-authority.policy.json`
A rule inventory that keeps checks honest by distinguishing:

- `accesskit_structural`,
- `standards_inspired`,
- `toolkit_specific`,
- and `manual_review_required`.

### `baseline-drift.report.json`
A semantic diff report that says whether names, roles, states, focus order, or node identity changed between snapshots and how severe that drift should be treated.

## MVP

- AccessKit-first extraction helpers for authoring-side trees
- ~12 high-impact rules (names, roles, focusability, focus order, dialog/menu basics, hidden/disabled contradictions)
- baseline diff + CI gate result
- one overlay/inspect view
- example integrations for one immediate-mode and one retained-mode style

## v1 path

- richer widget baseline packs,
- stronger text-control/lists/tables coverage,
- imported waivers with expiry,
- alignment hooks to compare expected authoring-side semantics against capture bundles from **P-0202**,
- templates for org-level accessibility gating policies.

## Why now

This is a good moment because Rust now has enough shared accessibility substrate that projects can benefit from a **boring doctor layer** instead of each toolkit independently rediscovering severity, baselines, and CI patterns.
The gap is no longer “can Rust expose semantics at all?”
It is “can Rust teams get a repeatable semantic-quality workflow?”

## Related proposals

- **P-0202 Cross-Platform Accessibility Interop & Conformance Kit** should handle platform capture / bundle / diff / replay truth.
- **P-0092 GUI Testing & Snapshot Harness Kit** is broader GUI capture/replay, while this proposal is specifically accessibility-semantic doctoring and gating.
- **P-0027 Text Input Kit** remains a lower-level text/selection/input substrate that can feed this kit.


## Current archive stance

Treat `meta/ui-accessibility-doctor-product-plan-2026-03-19.md` as the current working build sketch for **P-0087**.
The proposal should now be read as a small **AccessKit-first doctor/gating product** with three first-class review objects: semantic contract, rule authority, and baseline drift.
