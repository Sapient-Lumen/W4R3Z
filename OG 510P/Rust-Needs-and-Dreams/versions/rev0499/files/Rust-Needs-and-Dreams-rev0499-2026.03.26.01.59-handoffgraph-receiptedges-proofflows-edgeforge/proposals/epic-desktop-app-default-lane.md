# Epic proposal: Desktop app default lane

## Thesis
Rust does not most urgently need one more GUI framework comparison chart.
It needs a **reviewable boring-default lane for real desktop products**.

The problem is not that the ecosystem has no options.
The problem is that it has several credible ones with different truths:
- **Tauri** for webview-hosted desktop/mobile shells with explicit capabilities and plugin permissions;
- **Slint** for native declarative UI spanning embedded, desktop, and mobile;
- **Dioxus** for a Rust-first cross-platform app framework with integrated CLI/tooling and webview-backed desktop rendering today;
- **iced** for a lower-level Rust GUI story focused on simplicity and type-safety but still marked experimental;
- **egui** for immediate-mode, highly portable, highly interactive UIs.

A worthy contribution here is not a winner-take-all decree.
It is a thin lane that says what the **conservative default** is for one narrow recurring scope and when to escalate.

## Worthy contribution
The worthy contribution is a thin **desktop product lane** above the existing client-productization work:
- app shell/runtime truth,
- permission/capability truth,
- packaging/distribution truth,
- accessibility posture,
- and readable renewal receipts.

For the current narrow scope of **cross-platform desktop products**, the likely maintained answer is:
- **Tauri 2** as the conservative default shell,
- **Slint** as the main native/declarative serious alternative,
- **Dioxus** as the main Rust-first serious alternative,
- **iced** and **egui** as real watch lanes for lower-level or immediate-mode needs.

## Candidate artifact family
A thin artifact family could look like:
- `desktop-default-brief/v0`
- `desktop-support-brief/v0`
- `desktop-a11y-brief/v0`
- `desktop-package-brief/v0`
- `desktop-default-diff/v0`
- `desktop-product-pack/v0`

These should mostly reference lower-layer artifacts instead of replacing them.

## Reference CLI shape
- `cargo desktop-lane export`
  - emit the current lane brief for one project
- `cargo desktop-lane support`
  - attach platform/runtime/package posture
- `cargo desktop-lane a11y`
  - attach semantic/a11y posture notes
- `cargo desktop-lane diff --against <version|tag>`
  - emit a lane diff
- `cargo desktop-lane pack`
  - produce a linked pack of the above

This should remain a **composition and review layer**, not a framework or deployment service.

## Why this is ecosystem-shaping
A maintained desktop-default lane would help:
- teams choosing their first Rust desktop stack;
- teams deciding whether webview-hosted is actually acceptable;
- maintainers documenting capability and permission posture honestly;
- release/support consumers who need bundle/platform truth rather than demos;
- assistant- and atlas-style recommendation systems that currently fall back to vibes.

## Strong first proving grounds
1. **Tauri desktop product lane**
   - prove app shell, capability, plugin-permission, and simple bundle truths.
2. **Slint native desktop lane**
   - prove the default card preserves a serious non-webview alternative.
3. **Dioxus Rust-first lane**
   - prove the default card distinguishes framework ergonomics from runtime realities.
4. **A11y import lane**
   - prove AccessKit or semantic HTML posture can travel separately from shell choice.
5. **Packaging/support lane**
   - prove bundle/platform truth can be carried without inventing a universal store tool.

## What this should not become
- not a GUI league table;
- not a universal mobile/client lane;
- not a store pipeline;
- not a fake “desktop readiness score”;
- not a reason to stop doing project-specific briefs for serious products.

## Success bar
This becomes worthy when a maintainer or adopter can answer:
- what the boring default desktop lane is,
- why it is the default,
- what the serious alternatives are,
- and what facts force escalation,

without reconstructing the whole answer from showcase pages, issue threads, and scattered docs.

## Read this with
- `design/client-productization-stack.md`
- `design/client-productization-pilot-program.md`
- `design/desktop-app-default-lane.md`
- `defaults/conservative-desktop-app-product-2026Q1.md`
- `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`
