# Epic proposal: Browser Wasm package default lane

## Problem
The archive can now answer two neighboring but different web questions:
- what should a **browser-first Rust web app** start with?
- what should a **full-stack Rust web product** start with?

It still could not answer the remaining central question:
**what should a reusable Rust-authored browser package start with when the primary product surface is an npm package consumed from JavaScript or TypeScript?**

That gap matters because the hard parts are not only “pick `wasm-bindgen`.”
They are:
- Rust crate identity versus npm package identity;
- generated JS glue and `.d.ts` surfaces;
- bundler-target versus direct-browser-target truth;
- browser-test posture;
- ownership and maintenance truth after the `rustwasm` org sunset;
- and publication/security posture when crates.io and npm identities both exist.

## Proposed contribution
Publish and maintain a bounded defaults-corpus lane for:

**conservative browser Wasm package (2026 Q1)**

with:
- one design note;
- one maintained default card;
- one renewal receipt;
- and the usual frontier/queue/meta updates.

## Intended default
The current conservative answer for this bounded lane is:

**`wasm-bindgen` + `wasm-pack build --target bundler` + explicit npm package identity + browser tests**

with **raw `wasm-bindgen` + explicit package scaffolding**, **browser-web app lanes**, **`napi-rs`**, and **Wasm component / WIT tooling** kept visible as serious alternatives for different scopes.

## Why this is worthy
This is worthy because it turns a recurring fuzzy adoption conversation into a **bounded, reviewable, freshness-aware answer**.

It does not try to bless “the Rust/WebAssembly stack.”
It does something more useful:
- preserve the three-way web split that the repo now exposes;
- publish one boring current answer for one recurring package class;
- keep the maintenance caveat around `wasm-pack` visible instead of burying it;
- keep serious alternatives visible;
- and make the review receipts portable and renewable.

## Artifacts
- `design/browser-wasm-package-default-lane.md`
- `defaults/conservative-browser-wasm-package-2026Q1.md`
- `evidence/conservative-browser-wasm-package-2026Q1-renewal-2026-03-22.md`

## Non-goals
- universal Rust/WebAssembly governance;
- replacing project-specific architecture briefs;
- hiding npm/package ownership and JS glue behind one tool name;
- or flattening browser packages, browser apps, full-stack web products, Node add-ons, and component-model artifacts into one lane.
