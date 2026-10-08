---
id: P-0390
title: WebDriver BiDi + CDP Replay & Diagnostics Kit — browser capability locks, fallback diffs, and flake-minimizing evidence bundles
status: idea
domains: [testing, browser-automation, web, diagnostics, interoperability, replay]
last_reviewed: 2026-03-06
evidence:
  - https://www.w3.org/TR/webdriver-bidi/
  - https://github.com/w3c/webdriver-bidi
  - https://crates.io/crates/webdriverbidi
  - https://crates.io/crates/chromiumoxide
---

# Problem

Rust already has browser automation substrate: classic WebDriver clients, Chrome DevTools Protocol clients, and now dedicated WebDriver BiDi crates. The standard browser-automation future is increasingly BiDi, but the operational pain still lives at the seam between:

- **what a browser/driver claims to support via WebDriver BiDi and what test code still falls back to CDP for**,
- **streamed BiDi events and classic request/response control flows**,
- **browser, driver, and protocol-version drift**,
- **flake reports that currently mix screenshots, ad hoc logs, and half-reproducible traces**,
- and **framework-level abstractions that hide which protocol surface actually failed**.

The missing Rust contribution is not another test framework. It is a **replay/diagnostics kit** for capability locks, BiDi↔CDP fallback diffs, minimized incident bundles, and browser-version evidence.

# What it provides

- `browsercap.lock` — pins browser, driver, WebDriver BiDi modules, required capabilities, and allowed CDP fallbacks.
- `session-ir` — neutral IR for commands, events, navigation milestones, console/log events, script evaluation, network activity, and optional DOM/screenshot evidence.
- `fallback-diff` — explains exactly which action required vendor-specific or CDP-only behavior.
- `flake-minimizer` — shrinks a large capture into the smallest replayable scenario that still reproduces the failure.
- `cargo browser-evidence` — emits `*.browsersession.zip` with locks, traces, diffs, and findings.

# What the crate should provide other people

1. **A boring artifact for browser automation flakes**.
2. **Explicit capability locks** for browser/driver/protocol assumptions.
3. **BiDi-vs-CDP explainability** instead of mysterious vendor breakage.
4. **Smaller, shareable replay bundles**.
5. **One place to compare classic WebDriver, BiDi, and CDP views of the same scenario.**

# Persona / who it’s for

- Rust end-to-end test infrastructure maintainers
- Browser automation library authors
- CI/platform teams chasing flaky UI tests
- Tooling teams embedding browser automation in products

# Users & user stories

- **Infra engineer**: “Tell me whether the flake is a driver/browser version mismatch, a missing BiDi module, or an unstable DOM assumption.”
- **Library maintainer**: “Show which code path required CDP fallback.”
- **CI engineer**: “Share a compact replay bundle for a flaky test without shipping the whole workspace.”
- **Product team**: “Pin the browser automation capability set we rely on in production CI.”

# Prior art (and why it’s insufficient)

- WebDriver BiDi is now a living W3C standard.
- Rust has classical WebDriver clients and CDP crates.
- New Rust crates specifically target WebDriver BiDi.

What Rust still lacks is a **single evidence-grade workbench** for protocol-capability locks, fallback explanation, and replayable browser-session bundles.

# Design goals

1. **Protocol-honest** — keep BiDi, classic WebDriver, and CDP distinctions explicit.
2. **Replay-first** — artifacts must help reproduce flakes, not merely log them.
3. **Version-aware** — browser and driver versions belong in the contract surface.
4. **Framework-neutral** — useful above different Rust test stacks.
5. **Bounded evidence** — captures must be compact and redactable.

# MVP surface

- Minimal types: `BrowserCapabilityLock`, `SessionBundle`, `FallbackFinding`, `ReplaySlice`, `EnvironmentStamp`
- Minimal functions:
  - `capture_session()`
  - `diff_capabilities()`
  - `minimize_replay()`
  - `write_bundle()`
- Feature flags:
  - `webdriver-classic`
  - `webdriver-bidi`
  - `cdp`
  - `screenshots`
  - `dom-snapshots`

# Compatibility story

- Builds above `webdriverbidi`, `fantoccini`, `chromiumoxide`, or similar crates.
- Accepts captures from one or many protocol layers.
- Treats CDP fallback as explicit and versioned.
- Keeps replay slices separate from test-framework abstractions.

# Conformance & fixtures

- Tiny fixtures for capability negotiation drift, missing BiDi modules, stale element / DOM mutation races, network-event ordering, and console-script failures.
- Goldens for “same test intent, different protocol path”.
- Public example traces from small cross-browser scenarios.
- Adapters for classic WebDriver and CDP event ingestion around one bundle schema.

# Path to boring stability

- Stabilize lockfile and bundle schema before broad framework integration.
- Start with navigation, script, console, and network evidence.
- Keep large screenshots/videos optional.
- Version browser/protocol capability maps aggressively.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 25/30**

# Minimum lovable MVP

A library and CLI that pin browser-automation capability assumptions, capture session evidence across BiDi/CDP/classic WebDriver, explain fallback paths, and emit compact `*.browsersession.zip` artifacts.

# De-risk plan

1. Start with browser/driver/version locks plus BiDi capture.
2. Add explicit CDP fallback diffing next.
3. Keep replay slices small and deterministic.
4. Treat screenshots/DOM snapshots as optional overlays.

# Non-goals

- Not a new browser automation framework.
- Not a visual-regression platform.
- Not a universal browser profiler.
- Not a replacement for Selenium, Playwright, or Puppeteer ecosystems.

# Architecture & API sketch

```rust
pub struct BrowserCapabilityLock {
    pub browser: String,
    pub browser_version: String,
    pub driver_version: String,
    pub bidi_modules: Vec<String>,
    pub allowed_cdp_fallbacks: Vec<String>,
}

pub fn capture_session(input: SessionCaptureInput) -> Result<SessionBundle>;
pub fn diff_capabilities(bundle: &SessionBundle, lock: &BrowserCapabilityLock) -> Vec<FallbackFinding>;
pub fn minimize_replay(bundle: &SessionBundle) -> ReplaySlice;
```

Bundle draft: `browsercap.lock`, `session/events.ndjson`, `environment.json`, `fallback-diff.json`, `replay-slice.json`, `notes.md`.

# Security / safety model

- Support URL/header/cookie redaction.
- Bound optional capture sizes for screenshots and DOM snapshots.
- Record browser, driver, and protocol versions in every bundle.
- Treat vendor-specific CDP domains as explicitly non-portable evidence.

# Maintenance & governance plan

- Keep the core about locks, replay, and fallback explanation.
- Version protocol adapters separately if needed.
- Publish a small flake corpus with minimized traces.
- Resist drift into “full test runner” scope.

# Milestones

## 0.1
- capability lock
- BiDi capture
- replay slice prototype

## 0.2
- CDP fallback diffing
- classic WebDriver adapters
- public flake corpus

## 1.0
- stable `*.browsersession.zip`
- documented compatibility policy for capability maps
- broader library/framework adapters

# Open questions

- Which event classes belong in MVP versus optional modules?
- What is the smallest replay slice that remains useful across browsers?
- How should vendor-specific CDP domains be represented in capability diffs?

# Sources

- WebDriver BiDi W3C TR: https://www.w3.org/TR/webdriver-bidi/
- WebDriver BiDi repository: https://github.com/w3c/webdriver-bidi
- Rust `webdriverbidi` crate: https://crates.io/crates/webdriverbidi
- Rust `chromiumoxide` crate: https://crates.io/crates/chromiumoxide
