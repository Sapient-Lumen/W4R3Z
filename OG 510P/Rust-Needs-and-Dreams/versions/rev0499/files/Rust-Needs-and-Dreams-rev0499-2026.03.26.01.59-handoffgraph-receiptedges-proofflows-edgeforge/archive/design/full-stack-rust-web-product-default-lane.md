# Design: Full-stack Rust web product default lane (dual-target build + SSR/hydration + server-function/API + auth/deploy truth)

## Goal
Add the first maintained **full-stack web-product defaults-corpus card** so the archive can answer a recurring practical question:
**what should a serious Rust web product normalize around right now when Rust should own both the browser and server halves?**

This lane should not replace:
- `design/web-productization-stack.md`;
- `design/browser-web-app-default-lane.md`;
- or `design/conservative-http-service-2026Q1.md`.

It should give the web-productization frontier a second maintained answer in one bounded project class.

## Why this note is needed now
The archive already had:
- a browser-first web card for **CSR + static-hosted assets**;
- a service card for **ordinary HTTP backends**;
- and good abstract web-productization theory.

What it still lacked was a maintained answer for the recurring middle:
**full-stack Rust web products where SSR, hydration, server functions, and dual-target builds are all first-class.**

The current public signals make that omission harder to justify:
- Rust’s March 20, 2026 challenges post still frames ecosystem navigation as a problem of **choice paralysis** and **tacit knowledge**;
- the 2025 State of Rust survey still says online docs are the preferred canonical reference while editor/LLM-mediated workflows rise;
- browser-facing Wasm remains a mainstream Rust lane, which means the browser half of full-stack products is not niche;
- Leptos’s current docs now expose a very clear **CSR with Trunk** versus **SSR/full-stack with `cargo-leptos`** split, and explicitly describe SSR/hydration modes, hydration bugs, progressive enhancement, extractors, redirects, and deployment;
- `cargo-leptos` exists specifically to coordinate the two-target build and dev loop;
- Dioxus’s current full-stack docs are serious enough that a useful default must keep them visible as a real alternative rather than pretending the lane has fully converged;
- and Axum continuity still matters because the current conservative HTTP/service card already showed that **Tokio + axum + tower-friendly composition** remains unusually coherent for ordinary server work.

Together, those signals say the next worthy move is not another broad web essay.
It is a bounded boring default card for **Rust-owned full-stack web products**.

## Chosen project class
The first full-stack card should cover:
- Rust-owned web products where the browser and server halves are both part of the same deliberate lane;
- SSR plus hydration as an intentional part of the product shape;
- teams willing to accept a **dual-target** Rust build;
- products that benefit from server functions and progressively-enhanced forms/actions;
- and teams that want the clearest boring web-first answer rather than an immediate cross-platform ambition.

It should **not** try to cover in one card:
- browser-first static-hosted apps with an already-separate backend;
- npm-published Wasm packages or JS-interop-first libraries;
- edge-worker/serverless-first web products;
- desktop/mobile/web one-codebase ambitions as the primary driver;
- or generic public API/service platforms where the UI is only one client among many.

## Default thesis
For this bounded project class, the conservative default should currently be:

**Leptos SSR + Axum + `cargo-leptos`**, with explicit dual-target build truth, explicit SSR/hydration truth, explicit server-function versus public-API truth, and explicit auth/session/deploy posture.

Why this is the right first card:
- Leptos’s current docs explicitly describe this as the **full-stack SSR** path, including `cargo-leptos`, SSR modes, hydration, server functions, extractors, redirects, forms, and deployment.
- `cargo-leptos` exists exactly because the app is really two builds coordinated together.
- Axum keeps continuity with the existing conservative HTTP/service card and fits Leptos’s extractor/server-function integration well.
- Leptos’s server-function + progressive-enhancement story makes the browser/server boundary usable without pretending that every endpoint or external contract should become a framework-private RPC.
- This lane stays honest about the real tradeoffs: slower iteration than CSR-only, hydration complexity, two-target build surfaces, and deployment/config truth that cannot be hand-waved away.

## Serious alternatives that must stay visible
### 1. Dioxus Fullstack
This wins when the team wants:
- a more unified app framework story;
- a stronger one-codebase ambition that may later span desktop or mobile;
- or tighter framework-provided websockets/streams/fullstack features inside one Dioxus-shaped toolchain.

It should stay a serious alternative rather than a footnote.

### 2. Leptos SSR + Actix Web
This wins when the team already has strong local Actix expertise or needs that application model.
The card should not erase Actix merely because Axum is the current conservative default.

### 3. Conservative browser web app
This wins when Rust should own the browser UI but **not** the server half by default.
Do not silently widen the browser-first CSR card into this full-stack lane, or vice versa.

### 4. Conventional split frontend + API
This wins when:
- the browser side needs much deeper JavaScript ecosystem interop;
- the backend must stay framework-neutral or client-agnostic;
- or a separate public API contract matters more than same-language full-stack convenience.

## What the card must keep separate
The maintained card should visibly preserve:
- **dual-target build truth**;
- **SSR/hydration truth**;
- **server-function / external-API truth**;
- **auth/session/cookie boundary truth**;
- **deployment/origin/base-path truth**;
- **support/docs truth**;
- and **lane judgment** versus project-specific escalation.

## Practical design consequences
A real full-stack default card should:
- normalize around a **workspace or clearly separated package layout** that makes server/client responsibilities visible;
- treat the browser and server as two builds even when the dev tool wraps them;
- keep shared types explicit and prefer fixed-width numeric types across wasm32/server boundaries;
- keep server functions as a first-party product boundary tool, not a license to hide every external API contract;
- keep auth/session work explicit and server-owned rather than pretending the framework solved it;
- and keep deployment assumptions visible, especially static asset serving, origin/base-path assumptions, and container/VPS/server-host reality.

## Non-goals
- picking one Rust web framework for every web project;
- flattening browser-only apps, full-stack apps, and npm-published Wasm packages into one story;
- pretending SSR/hydration removes tradeoffs around build complexity or deployment;
- or treating server functions as a universal replacement for explicit public APIs.

## Archive implications
- Add a first maintained full-stack web-product card under `defaults/`.
- Add a first renewal receipt under `evidence/`.
- Refresh corpus/frontier/meta files so the repo treats **full-stack Rust web product** as a maintained public lane distinct from both **browser-first web app** and **browser package / npm-published Wasm**.
- Keep a future **browser package / npm-published Wasm** card available as the likely next web split once the app lanes are both covered.

## References
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Leptos book / getting started / SSR:
  https://book.leptos.dev/
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/ssr/index.html
  https://book.leptos.dev/ssr/21_cargo_leptos.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/23_ssr_modes.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
- Leptos server / progressive enhancement:
  https://book.leptos.dev/server/25_server_functions.html
  https://book.leptos.dev/server/26_extractors.html
  https://book.leptos.dev/server/27_response.html
  https://book.leptos.dev/progressive_enhancement/action_form.html
- Leptos deployment:
  https://book.leptos.dev/deployment/ssr.html
  https://book.leptos.dev/deployment/binary_size.html
- Dioxus full-stack:
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/server_functions/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/middleware/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/websockets/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/authentication/
- Axum:
  https://docs.rs/axum/latest/axum/
  https://docs.rs/axum/latest/axum/extract/
  https://docs.rs/axum/latest/axum/struct.Router.html
  https://docs.rs/axum/latest/axum/extract/struct.State.html
- Cargo:
  https://doc.rust-lang.org/cargo/reference/features.html
  https://doc.rust-lang.org/cargo/reference/workspaces.html
  https://doc.rust-lang.org/cargo/reference/config.html
