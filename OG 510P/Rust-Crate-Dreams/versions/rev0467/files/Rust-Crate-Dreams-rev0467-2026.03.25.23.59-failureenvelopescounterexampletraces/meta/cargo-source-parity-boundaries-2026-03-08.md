# Cargo source parity boundaries — 2026-03-08

This note sharpens **P-0496 Cargo Vendor & Source Parity Kit** around one missing layer the archive still needed: **source identity and coverage truth**.

## Why this frontier got sharper

Cargo’s current source-management substrate is now strong enough that a new crate should not pretend the missing value is “vendoring exists”. The important facts are:

- Cargo source replacement assumes the replacement source contains **exactly the same source code** and no extra crates.
- Cargo says source replacement is **not** the right tool for patching or private-registry semantics.
- `cargo vendor` already has useful workflow flags such as `--sync`, `--respect-source-config`, and `--versioned-dirs`.
- Cargo’s offline docs explicitly warn that offline mode can yield **different dependency resolution** than online mode.
- Cargo path overrides are intentionally strict and cannot change the dependency graph.

Those facts create a clearer product boundary.

## The sharper missing artifact

The missing crate is not a downloader or mirror. It is a **review bundle** that can tell another person:

1. which logical source IDs appeared in the build graph,
2. which replacement chains were declared or observed,
3. which physical roots those chains resolved onto,
4. which packages still depend on path/git/external source classes,
5. and where the result is exact versus manual-review-required.

## Exactness boundaries this crate must preserve

A good P-0496 bundle should distinguish:

- **exact Cargo fact** — source ID, replacement chain entry, observed source class, vendored directory path, local-registry path
- **conservative classification** — “registry-equivalent enough”, “coverage incomplete”, “offline resolution may differ”
- **manual-review-required** — any case where Cargo’s current source-management surface is known to have edge cases or open gaps

Do not flatten those into one certainty tone.

## Why coverage truth matters as much as parity

Vendoring and source replacement do not automatically mean “everything needed for an offline or hermetic build is inside the bundle.”

The archive now needs P-0496 to make three blockers explicit:

1. **logical-source alias splits** — different source IDs may still matter even when they point at one physical vendored directory,
2. **git history requirements** — some replaced git workspace cases still want real git-style structure/history,
3. **path dependency spillover** — current vendoring workflows still do not automatically capture path dependencies as part of the vendored set.

## 0.1 bundle spine

A worthy 0.1 should prefer:

- `source-contract.toml`
- `source-origin.receipt.json`
- `source-parity.lock`
- `source-coverage.report.json`
- `vendor-parity.report.json`
- optional `source-replacement.diff.json`

That is enough to support real review without pretending to prove more than Cargo’s surfaces justify.

## Scenario lanes the archive should keep separate

1. **clean registry-to-vendored parity**
2. **two logical registries collapsed onto one vendored directory**
3. **git workspace replacement still requiring git-style structure/history**
4. **path dependency outside the vendored boundary**
5. **checksum/content drift or missing vendored member**

## What future passes should resist

- another generic “offline Cargo toolkit” proposal,
- a mirror/registry implementation hiding inside P-0496,
- flattening source identity, physical root, and coverage truth into one blob,
- or implying that a successful vendored build is the same thing as an honest air-gap or hermetic claim.

## Sources

- Cargo source replacement: https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo vendor`: https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- `cargo fetch`: https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo dependency overrides: https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Cargo issue #14821: https://github.com/rust-lang/cargo/issues/14821
- Cargo issue #16141: https://github.com/rust-lang/cargo/issues/16141
- Cargo issue #10134: https://github.com/rust-lang/cargo/issues/10134
