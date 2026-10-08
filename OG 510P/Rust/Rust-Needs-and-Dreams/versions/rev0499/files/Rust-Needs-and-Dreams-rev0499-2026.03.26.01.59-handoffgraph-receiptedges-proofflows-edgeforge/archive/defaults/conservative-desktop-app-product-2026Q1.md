# Default card: Conservative desktop app product (2026 Q1)

Latest renewal receipt: `evidence/conservative-desktop-app-product-2026Q1-renewal-2026-03-22.md`

## Scope
This card applies to:
- desktop-first Rust GUI products intended for real users, not only internal demos;
- teams that want a boring cross-platform desktop starting point;
- products where packaging, permissions, and support posture matter alongside UI code;
- teams willing to accept a webview-hosted shell when it buys portability and productization clarity.

Assumptions:
- stable Rust;
- desktop-first support scope (Windows / macOS / Linux), even if mobile is a future ambition;
- ordinary product teams that want the clearest boring default rather than the most specialized renderer;
- explicit permission/capability posture is desirable;
- accessibility posture should be named, not hand-waved.

This is **not** the default for:
- mobile-first or store-first products;
- embedded HMIs or resource-constrained native UIs;
- apps that need lower-level custom rendering or game-engine-style control as a first principle;
- highly native-looking products where a webview shell is the wrong fit;
- or internal highly interactive tools where immediate-mode UI may win on iteration speed.

## Why this default now
Rust’s latest challenges framing still says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey still says online documentation is the preferred canonical reference while editor/LLM-mediated learning rises.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Tauri 2 is now stable and explicitly positions itself as a framework for tiny, fast binaries on all major desktop and mobile platforms. Its docs also make the real constraints visible: Tauri is frontend-agnostic, acts conceptually as a static web host, recommends Vite for most JavaScript/TypeScript frontend cases, and provides explicit capability and plugin-permission systems.
https://v2.tauri.app/blog/tauri-20/
https://v2.tauri.app/start/
https://v2.tauri.app/start/frontend/
https://v2.tauri.app/security/capabilities/
https://v2.tauri.app/learn/security/using-plugin-permissions/

At the same time, the serious alternatives are now too credible to ignore:
- Dioxus is a cross-platform Rust app framework with one codebase, integrated tooling, system-webview desktop rendering, `dx doctor`, and explicit native-platform bundling limits.
  https://dioxuslabs.com/learn/0.7/
  https://dioxuslabs.com/learn/0.7/getting_started/
  https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- Slint is a native declarative GUI toolkit spanning embedded, desktop, and mobile, with explicit backend/renderer choices and desktop accessibility backed by AccessKit.
  https://slint.dev/
  https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/
  https://slint.dev/blog/slint-1.1-released
- AccessKit now provides a real shared accessibility substrate for multiple Rust UI projects.
  https://accesskit.dev/
- iced and egui remain real watch lanes, but iced still marks itself as experimental and egui’s immediate-mode posture makes it a better default for some tool-like apps than for this conservative product lane.
  https://docs.rs/iced/latest/iced/
  https://docs.rs/crate/egui/latest

For this exact project class, the archive’s current answer is:
**use Tauri 2 as the conservative default shell for cross-platform desktop products, keep capabilities and plugin permissions explicit, keep the frontend/static-host assumptions honest, and escalate to Slint or Dioxus when the product wants a meaningfully different UI/runtime contract.**

## Decision label
**default-with-caveats**

It is the clearest boring default for this narrow scope, but the client-app ecosystem is still plural enough that the default must remain explicit about what it is *not* covering.

## Default lane summary
### Default lane
- desktop shell/runtime: **Tauri 2**
- frontend posture: **static-hosted frontend assets; prefer the simplest framework/tooling that fits, often Vite-based SPA/MPA**
- Rust boundary posture: **small explicit Rust↔frontend bridge, not ambient backend reachability**
- permission posture: **explicit capabilities and plugin permissions**
- accessibility posture: **semantic HTML plus explicit a11y checks; do not treat screenshots as evidence**
- packaging/distribution posture: **desktop bundles/direct distribution first; updater/store stories remain project-specific unless explicitly owned**

### Serious alternatives
- **Slint** when native declarative UI, embedded/Desktop continuity, or non-webview rendering is central.
- **Dioxus** when the team wants a Rust-first app framework with integrated tooling and accepts the current system-webview desktop contract.

### Watch / not-default here
- **iced** when lower-level native rendering and Elm-style architecture are central, but keep its experimental status visible.
- **egui / eframe** when immediate-mode iteration speed and highly interactive tool UIs matter more than this lane’s conservative product posture.
- **mobile-first Tauri/Dioxus lanes** until the archive gives them a separate default card.

## Slot guidance
### App-shell slot
Prefer **Tauri 2** when a system-webview desktop shell is acceptable and the team wants the clearest boring product path.
Do not smuggle webview acceptance in implicitly; make it a first-class part of the lane judgment.

### Frontend/runtime slot
Prefer the simplest frontend that fits.
Tauri’s own docs describe it as a static host and recommend **Vite** for most JavaScript/TypeScript frontend projects.
Avoid starting with SSR/meta-framework complexity unless the product truly requires it.

### Permission/capability slot
Treat Tauri capabilities and plugin permissions as part of the product contract, not as scattered configuration.
If the project cannot live with explicit capability scoping, it may not be in this lane.

### Accessibility slot
Do not say “accessible” because the toolkit website mentions accessibility.
For Tauri, require semantic HTML and explicit a11y checks for the webview UI.
For native/declarative alternatives, import their specific accessibility substrate and evidence separately.

### Packaging/support slot
Keep desktop packaging explicit and narrow at first.
Ship only the platforms and package types the team is ready to support.
Do not pretend direct downloads, store distribution, and self-updating are one solved lifecycle story.

## Serious alternatives and when they win
### Slint wins when
- native rendering matters more than web stack reuse;
- the product may need embedded/Desktop continuity;
- or the team wants a declarative UI DSL and explicit backend/renderer control.

### Dioxus wins when
- the team wants a Rust-first application framework;
- integrated CLI/tooling and fullstack adjacency matter;
- and the current webview-backed desktop renderer is an acceptable contract.

### iced wins when
- lower-level renderer control or Elm-style architecture is central;
- the team can tolerate a more advanced-Rust / less boring-default posture;
- and experimental status is acceptable.

### egui wins when
- the product is really closer to a highly interactive tool or operator console;
- immediate-mode ergonomics matter more than this lane’s conservative product defaults;
- or the team values egui’s portability and iteration speed above native/declarative product posture.

## Escalate to a project-specific brief when
- mobile becomes a first-class supported target;
- native widget fidelity or custom rendering dominates;
- store distribution, updater, signing, or enterprise policy dominates the lifecycle;
- accessibility or localization requirements become strict enough to drive framework choice;
- or the team is torn between Tauri, Slint, and Dioxus because the product spans more than one of those lane assumptions.

## Canonical references
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tauri 2 stable release:
  https://v2.tauri.app/blog/tauri-20/
- Tauri overview / start:
  https://v2.tauri.app/start/
- Tauri frontend configuration:
  https://v2.tauri.app/start/frontend/
- Tauri capabilities:
  https://v2.tauri.app/security/capabilities/
- Tauri plugin permissions:
  https://v2.tauri.app/learn/security/using-plugin-permissions/
- Tauri prerequisites:
  https://v2.tauri.app/start/prerequisites/
- Dioxus overview:
  https://dioxuslabs.com/learn/0.7/
- Dioxus getting started:
  https://dioxuslabs.com/learn/0.7/getting_started/
- Dioxus desktop:
  https://dioxuslabs.com/learn/0.7/guides/platforms/desktop/
- Dioxus bundle:
  https://dioxuslabs.com/learn/0.7/tutorial/bundle/
- Dioxus deploy:
  https://dioxuslabs.com/learn/0.7/tutorial/deploy/
- Slint homepage:
  https://slint.dev/
- Slint backends/renderers:
  https://docs.slint.dev/latest/docs/slint/guide/backends-and-renderers/backends_and_renderers/
- Slint accessibility release note:
  https://slint.dev/blog/slint-1.1-released
- AccessKit overview:
  https://accesskit.dev/
- iced docs:
  https://docs.rs/iced/latest/iced/
- egui docs:
  https://docs.rs/crate/egui/latest
- cargo-mobile2 maintenance status:
  https://github.com/tauri-apps/cargo-mobile2

## Renewal inputs
Recheck before renewal:
- whether Tauri remains the clearest boring default for desktop-first products;
- whether Dioxus’s desktop/runtime/bundling story changes enough to move it upward;
- whether Slint’s native/declarative story should become the default for a narrower but central sub-scope;
- whether a separate **mobile-first client product** card now deserves to split off;
- whether accessibility evidence becomes strong enough that the card should demand more than posture statements.

Signal refs:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://v2.tauri.app/blog/tauri-20/
- https://dioxuslabs.com/learn/0.7/
- https://slint.dev/
- https://accesskit.dev/

## Non-goals
- choosing one Rust GUI framework for every project;
- pretending desktop and mobile already share one boring default;
- treating Tauri as a universal updater/store solution;
- hiding the seriousness of Slint or Dioxus;
- or replacing project-specific client-productization review.
