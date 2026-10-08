# Gap: Desktop app defaults still collapse shell choice, capability truth, accessibility posture, and packaging reality

## The gap
Rust now has multiple credible desktop-app paths, but the ecosystem still lacks one **reviewable default lane** that keeps these truths separate:
- webview-hosted shell versus native declarative shell versus immediate-mode / custom-renderer shell;
- frontend/runtime contract;
- capability and plugin-permission exposure;
- accessibility substrate and evidence;
- packaging/distribution constraints;
- and project-specific escalation triggers.

Without that lane, desktop-app guidance collapses into:
- showcase pages,
- framework enthusiasm,
- partial bundle docs,
- and assistant folklore.

## Why this matters now
- Tauri 2 is stable and explicit about capabilities, permissions, frontend/static-host constraints, and cross-platform scope.
- Dioxus now offers a serious Rust-first desktop path with integrated tooling, but it still uses the system webview on desktop and documents native-platform bundling limits.
- Slint is now a serious native GUI choice across embedded, desktop, and mobile and exposes backend/renderer choices explicitly.
- AccessKit makes accessibility substrate a first-class review input rather than one toolkit’s hidden implementation detail.
- The 2025 State of Rust survey still says online docs are canonical while LLM/editor-mediated learning rises, which means bounded default cards matter more, not less.

## What a worthy contribution should look like
A worthy contribution is not another GUI framework.
It is a thin **desktop-app default lane** with:
- one bounded scope;
- one maintained default card;
- serious alternatives kept visible;
- explicit capability/a11y/package truths;
- and a readable renewal receipt.

## Anti-goals
- universal client-app guidance;
- flattening desktop, mobile, embedded, and web into one lane;
- accessibility reduced to screenshot tests or “supports ARIA” claims;
- pretending platform packaging/store reality is solved by a single framework.
