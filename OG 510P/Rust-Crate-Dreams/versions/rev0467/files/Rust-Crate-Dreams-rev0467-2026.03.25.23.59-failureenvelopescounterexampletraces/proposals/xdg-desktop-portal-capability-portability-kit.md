---
id: P-0408
title: XDG Desktop Portal Capability Portability Kit — request/session receipts, backend capability diffs, and sandbox-safe desktop evidence
status: idea
domains: [desktop, linux, sandboxing, dbus, interoperability, portability, ui]
last_reviewed: 2026-03-06
evidence:
  - https://flatpak.github.io/xdg-desktop-portal/docs/
  - https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
  - https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
  - https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html
  - https://docs.rs/ashpd/latest/ashpd/
  - https://docs.rs/zbus
---

# Problem

Rust desktop applications are increasingly expected to behave correctly inside Flatpak-like sandboxes, Wayland-first environments, and mixed-desktop setups. XDG Desktop Portal is now the standard host-mediation surface for file access, URI opening, printing, screencast, remote desktop, documents, global shortcuts, and more.

Rust already has real substrate here: `zbus` is mature D-Bus infrastructure and `ashpd` is an actively maintained Rust wrapper over portal interfaces. Yet the painful failures still happen at the seam between:

- **the portal API an app thinks it is calling and the backend actually available on the current desktop**, 
- **request/session lifecycle semantics and the simplistic synchronous stories app code tells itself**,
- **sandboxed app expectations and host grants that are temporary, backend-specific, or silently denied**,
- **desktop-specific backend behavior and application-level capability detection**,
- and **bug reports that still arrive as “works on GNOME, fails on KDE/Hyprland” with no durable artifact.**

The missing Rust contribution is not another portal binding. It is a **capability portability kit** for request/session receipts, backend diffs, and reproducible portal evidence bundles.

# What it provides

- `portal.lock` — pins required portal interfaces, versions, backend expectations, app sandbox assumptions, and known fallbacks.
- `request-receipt` — normalized artifact for request handles, response signals, timing, window identifiers, documents grants, and cancellation paths.
- `backend-capability-matrix` — explicit view of which portal methods/options/backends were actually present.
- `interop-findings` — explains backend mismatch, missing interface version, session lifecycle misuse, and grant/path confusion.
- `cargo portal-evidence` — emits `*.portalbundle.zip` with locks, redacted D-Bus receipts, and notes.

# What the crate should provide other people

1. **A boring artifact for “works on one desktop, fails on another.”**
2. **Portable capability diffs** across portal backends and interface versions.
3. **Request/session receipts** that capture the asynchronous lifecycle apps usually hand-wave away.
4. **Sandbox-aware diagnostics** for document grants and host-mediated permissions.
5. **A coordination layer above `ashpd` / `zbus`**, not a replacement.

# Persona / who it’s for

- Rust desktop app authors
- Linux packaging / sandboxing teams
- toolkit authors
- maintainers debugging Flatpak / Wayland / portal regressions

# Users & user stories

- **App developer**: “Show me whether my failure is missing backend support, wrong request lifecycle handling, or a grant issue.”
- **Toolkit maintainer**: “Compare what my abstraction assumed with what the current portal backend actually exposed.”
- **Packager**: “Capture a portal bundle from a sandboxed app and attach it to a bug report.”
- **QA engineer**: “Run the same portal flow on multiple desktops and diff the capability results.”

# Prior art (and why it’s insufficient)

- XDG Desktop Portal’s official documentation now clearly separates common conventions, app-facing APIs, and desktop integration/backends.
- The Request and Documents interfaces make explicit that these are long-lived, user-mediated flows, not ordinary synchronous method calls.
- Rust already has `ashpd` and `zbus` for direct interaction.

What Rust still lacks is a **single portable artifact** for backend capability detection, request/session lifecycle capture, and explainable interoperability findings.

# Design goals

1. **Lifecycle-honest** — request handles, response signals, and sessions are first-class.
2. **Backend-explicit** — differences between portal backends belong in data, not folklore.
3. **Sandbox-aware** — document grants and host-mediated access must be observable.
4. **Toolkit-neutral** — sit above app/toolkit bindings rather than fighting them.
5. **Low-drama adoption** — useful even as a test/diagnostics sidecar in existing apps.

# MVP surface

- Minimal types: `PortalLock`, `RequestReceipt`, `CapabilityMatrix`, `PortalFinding`, `PortalBundle`
- Minimal functions:
  - `probe_capabilities()`
  - `capture_request()`
  - `evaluate_backend_diff()`
  - `write_bundle()`
- Feature flags:
  - `file-chooser`
  - `documents`
  - `remote-desktop`
  - `screencast`
  - `global-shortcuts`

# Compatibility story

- Works above `ashpd`, `zbus`, or toolkit-specific bindings.
- Supports offline analysis of captured request/session receipts.
- Separates standardized portal interfaces from backend-specific behavior.
- Keeps UI/toolkit integration outside the core model.

# Conformance & fixtures

- Goldens for missing portal interface, version mismatch, cancelled requests, and document grant confusion.
- Tiny corpora for file chooser, document portal, screencast, and remote desktop flows.
- Fixtures that compare the same app flow across multiple backends.
- Public redacted D-Bus receipts small enough for CI artifacts.

# Path to boring stability

- Stabilize the lockfile and receipt schema first.
- Start with capability probing and request capture before deep toolkits integrations.
- Keep backend quirks versioned and explicit.
- Resist drift into becoming a full desktop toolkit.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 5/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A Rust library and CLI that probe portal capabilities, capture request/session receipts, classify backend portability failures, and emit compact `*.portalbundle.zip` artifacts.

# De-risk plan

1. Start with file chooser + documents flows.
2. Add screencast/remote-desktop only after the receipt model is stable.
3. Keep backend identifiers and version checks explicit in every bundle.
4. Pilot via integration tests in one existing Rust desktop app.

# Non-goals

- Not a new desktop UI toolkit.
- Not a replacement for portal backends.
- Not a sandbox runtime.
- Not a generic D-Bus sniffer for all applications.

# Architecture & API sketch

```rust
pub struct PortalLock {
    pub required_interfaces: Vec<String>,
    pub min_versions: Vec<(String, u32)>,
    pub sandbox_assumptions: Vec<String>,
    pub backend_overlays: Vec<String>,
}

pub fn probe_capabilities(conn: &zbus::Connection) -> Result<CapabilityMatrix>;
pub fn capture_request(event: PortalEvent) -> Result<RequestReceipt>;
pub fn evaluate_backend_diff(lock: &PortalLock, seen: &CapabilityMatrix) -> Vec<PortalFinding>;
```

Bundle draft: `portal.lock`, `capabilities.json`, `requests.jsonl`, `findings.json`, `notes.md`.

# Security / safety model

- Redact user paths, app IDs, and document IDs where appropriate.
- Distinguish host-mediated grants from application assumptions.
- Preserve request/session ordering for replayability.
- Keep captured D-Bus evidence bounded and human-reviewable.

# Maintenance & governance plan

- Keep the core about capabilities, receipts, and findings.
- Version portal interfaces and backend overlays separately.
- Publish a tiny conformance corpus for common flows.
- Resist becoming a giant desktop compatibility database.

# Milestones

## 0.1
- `portal.lock`
- capability probe
- request receipt schema

## 0.2
- backend diff engine
- document portal receipts
- public fixture corpus

## 1.0
- stable `*.portalbundle.zip`
- documented compatibility policy for backend overlays
- CI-friendly portability checks

# Open questions

- What is the smallest backend capability schema that still explains real app failures?
- Which backend quirks deserve first-class overlays versus ordinary findings?
- How far should live request tracing go before privacy or complexity outweighs value?

# Sources

- XDG Desktop Portal docs: https://flatpak.github.io/xdg-desktop-portal/docs/
- Portal API reference: https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
- Request interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
- Documents interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html
- `ashpd`: https://docs.rs/ashpd/latest/ashpd/
- `zbus`: https://docs.rs/zbus

