# Renewal receipt: conservative full-stack Rust web product (2026-03-22)

## Subject
- default card: `defaults/conservative-full-stack-rust-web-product-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0386
- scope: conservative full-stack Rust web product where Rust owns both browser and server halves
- non-goal: package-admission or security signoff for a production internet-facing system

## Renewal verdict
**keep with caveats**

The lane currently still reads best as:
- **Leptos** for the full-stack app framework,
- **SSR + hydration** as an intentional render/runtime posture,
- **Axum** as the conservative server framework,
- **`cargo-leptos`** as the dual-target build coordinator,
- and **server functions + progressive enhancement** as the first-party browser/server boundary story,

with **Dioxus Fullstack** and **Leptos + Actix** kept visible as serious alternatives.

The caveat is important:
this is a **coherent default for Rust-owned full-stack web products**, not a universal answer for browser-only apps, npm-published Wasm packages, edge runtimes, public API platforms, or all security/auth postures.

## Canon import checked this round
Primary documentation surfaces re-read:
- Leptos getting started / SSR / life cycle / SSR modes / hydration:
  https://book.leptos.dev/getting_started/index.html
  https://book.leptos.dev/ssr/index.html
  https://book.leptos.dev/ssr/21_cargo_leptos.html
  https://book.leptos.dev/ssr/22_life_cycle.html
  https://book.leptos.dev/ssr/23_ssr_modes.html
  https://book.leptos.dev/ssr/24_hydration_bugs.html
- Leptos server functions / extractors / responses / ActionForm:
  https://book.leptos.dev/server/25_server_functions.html
  https://book.leptos.dev/server/26_extractors.html
  https://book.leptos.dev/server/27_response.html
  https://book.leptos.dev/progressive_enhancement/action_form.html
- Leptos deployment / binary-size guidance:
  https://book.leptos.dev/deployment/ssr.html
  https://book.leptos.dev/deployment/binary_size.html
- Axum overview / extractors / Router / State:
  https://docs.rs/axum/latest/axum/
  https://docs.rs/axum/latest/axum/extract/
  https://docs.rs/axum/latest/axum/struct.Router.html
  https://docs.rs/axum/latest/axum/extract/struct.State.html
- Dioxus Fullstack / project setup / server functions / middleware / websockets / auth:
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/project_setup/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/server_functions/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/middleware/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/websockets/
  https://dioxuslabs.com/learn/0.7/essentials/fullstack/authentication/

Canon judgment:
- Leptos still provides the clearest web-first documentation arc from CSR to SSR/full-stack while keeping SSR modes, hydration, extractors, redirects, and progressive enhancement visible.
- `cargo-leptos` still exists specifically to coordinate the two-target build and dev loop, which is exactly the build-truth this lane must preserve.
- Axum still fits the conservative server choice because typed request/state extraction remains a strong match for Leptos’s server-side integration.
- Dioxus remains strong enough that the default must stay bounded and must not pretend Leptos is the only serious full-stack path.

## Registry / supply-chain import
Public ecosystem signals checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

What this receipt takes from those sources:
- crates.io’s current security/review surfaces and trusted-publishing controls are useful, but they do not decide framework choice on their own;
- full-stack product lanes still need exact package identity and explicit package-admission review;
- and recent advisory activity reinforces that lane-level defaults are not a substitute for real dependency and deployment review.

Exact identity notes for this lane:
- `leptos`, `cargo-leptos`, `axum`, and `dioxus` should be recorded by exact name.
- This receipt is **not** making claims about a vague bucket called “Rust web frameworks”.

Registry judgment:
- the lane remains publishable as a public default card;
- but real product teams still need package-admission, advisory, and threat review on top of it.

## API / compatibility import
Relevant current signals:
- Cargo features:
  https://doc.rust-lang.org/cargo/reference/features.html
- Cargo workspaces:
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo config:
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo 1.94 development cycle note:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

Judgment:
- this lane still needs visible **dual-target** and **feature partition** discipline;
- Cargo workspace/config discovery remains important enough that full-stack build truth cannot be treated as local folklore;
- nothing here overturns the default, but it reinforces why the card must keep build coordination, target split, and config posture explicit.

## Maintenance / support-envelope import
Envelope facts that still hold:
- full-stack Rust web products are not “one build”; they are coordinated browser + server builds;
- hydration complexity is real and documented, not a hypothetical footnote;
- server functions are powerful for first-party app flows, but should not erase public/external API boundaries;
- auth/session posture remains explicit project work rather than an automatic property of the framework choice;
- and Dioxus’s auth docs reinforce that even strong full-stack frameworks do not remove the need to design authentication deliberately.

Imported lane-specific warning:
- Leptos’s server-function docs still warn that pointer-sized integers like `usize` can break across the wasm32/client versus 64-bit/server boundary, which is exactly the kind of cross-target truth this lane must preserve.
  https://book.leptos.dev/server/25_server_functions.html

Maintenance judgment:
- the lane should stay public;
- but it should stay narrow and should not be widened into “the Rust web answer” or “the secure-web answer”.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- Rust challenges post:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey:
  https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/

Replay notes:
- future renewal should explicitly re-check whether Leptos or Dioxus now offers the clearest boring answer for this exact web-first full-stack scope;
- re-check whether browser-only, full-stack, and npm-published Wasm lanes are still well-separated;
- re-check whether auth/session and deploy guidance now need a narrower overlay or split.

## Lane judgment
Keep the lane, but keep the caveats loud.

Why:
- Rust’s official ecosystem framing still says navigation is blocked by tacit knowledge and choice paralysis;
- current docs now expose the browser-only versus full-stack split clearly enough that the archive should preserve it;
- and the best public contribution here is still a bounded default with receipts, not a universal blessing.

## Open watch items
- whether a distinct **browser package / npm-published Wasm** card now deserves to split away next;
- whether an **edge-runtime / worker-first** web card ever becomes central enough to justify a maintained lane;
- whether Dioxus fullstack eventually becomes the clearer boring answer for this exact scope;
- and whether auth/session/deploy overlays need to become explicit companion notes rather than remaining escalation triggers.
