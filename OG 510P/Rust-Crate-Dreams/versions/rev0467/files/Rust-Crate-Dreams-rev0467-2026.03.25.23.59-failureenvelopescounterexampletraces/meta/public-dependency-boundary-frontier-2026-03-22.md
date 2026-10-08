# Public dependency boundary frontier — 2026-03-22

## Main judgment

The worthy crate in this lane is not another lint wrapper.
It is a crate that helps other people review **manifest intent, effective publicness, exposure routes, workspace gaps, and migration posture** without pretending those are the same thing.

## Why now

Current upstream and substrate signals line up unusually well:

- Rust’s 2025H2 goal is explicitly about finding an MVP for stabilization.
- The 2026 flagship themes keep public/private dependencies on the front line.
- Cargo already has unstable manifest syntax, nightly `cargo add` support, metadata/tree hooks, and better manifest diagnostics.
- RFC 3516 gives concrete examples of accidental exposure through errors, reexports, and hidden shims.
- rustdoc-based tools can already see public items and exposed external types.

## The support-contract split this lane needs

A serious crate here should keep these truths separate:

1. **manifest intent** — what Cargo declarations say;
2. **effective boundary verdict** — what is actually public now;
3. **exposure route** — how it escaped;
4. **evidence provenance** — which parts are compiler/Cargo facts versus rustdoc-based inference;
5. **workspace gap** — where current Cargo scope or inheritance limits block a cleaner declaration;
6. **migration posture** — what the safest next move is.

## Why this is better than another analyzer

An analyzer can show that some external type appears in the public API.
It cannot by itself say whether that was already declared public, whether the crate is blocked by `workspace.dependencies`, whether the case is a hidden proc-macro shim, or whether the right next move is a wrapper type rather than `public = true`.

## Practical lane boundary

- rustc/Cargo own the lint and unstable manifest feature;
- rustdoc JSON / `public_api` / `cargo-check-external-types` own important substrate;
- **support-contract truth and migration honesty** belong here.
