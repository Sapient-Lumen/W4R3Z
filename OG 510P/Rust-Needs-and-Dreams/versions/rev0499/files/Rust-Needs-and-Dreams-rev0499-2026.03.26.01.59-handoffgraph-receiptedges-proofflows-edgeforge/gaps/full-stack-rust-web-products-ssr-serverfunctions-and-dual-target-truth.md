# Gap: full-stack Rust web products need dual-target, SSR/hydration, server-function, and deploy-boundary truth

## The gap
The archive had:
- browser-first web guidance;
- HTTP/service guidance;
- and broader web-productization theory.

It still lacked a maintained answer for **Rust-owned full-stack web products**.

That gap causes predictable confusion:
- teams flatten browser-only and full-stack web into one “Rust web” question;
- SSR and hydration get treated like minor render-mode toggles instead of product-shaping choices;
- build tools hide the fact that there are really two builds;
- server functions get treated as if they erase API boundary design;
- and auth/session/deploy assumptions stay tacit until late.

## Why this matters
Current official docs now make the split hard to ignore:
- Leptos explicitly separates **CSR with Trunk** from **SSR/full-stack with `cargo-leptos`**;
- Leptos documents SSR modes, hydration bugs, extractors, redirects, progressive enhancement, and deployment;
- Dioxus documents the server/client split, target-specific builds, middleware, websockets, and auth guidance for full-stack apps;
- Axum keeps request/state/extractor truth explicit;
- Cargo keeps feature/workspace/config reality explicit.

So the missing contribution is not “another web framework comparison.”
It is a maintained defaults-corpus card that keeps the right truths separate.

## Truths this lane must preserve
- **dual-target build truth:** browser and server are different targets/builds, even when the tool wraps them;
- **SSR/hydration truth:** full-stack web is not just CSR plus a server switch;
- **server-function / public-API truth:** first-party RPC convenience is not the same thing as an external contract;
- **auth/session/cookie truth:** session/auth state is a real server boundary, not a framework footnote;
- **deployment/origin/base-path truth:** product hosting assumptions are part of the lane;
- **support/docs truth:** framework docs and Cargo/build docs are both part of the support envelope.

## What a good contribution would look like
A worthy contribution here would:
- publish one conservative default for one recurring project class;
- preserve Dioxus and Actix as real alternatives;
- keep the browser-only CSR lane explicitly separate;
- keep the future npm-published Wasm lane available as a separate split;
- and attach a renewal receipt that records why the lane still reads the way it does.

## Anti-patterns to avoid
- treating “Rust web” as one lane;
- letting `cargo-leptos` or `dx` hide the two-build reality;
- treating server functions as proof that API/auth/deploy design is solved;
- or pretending the framework choice automatically answers deployment, auth, and support questions.
