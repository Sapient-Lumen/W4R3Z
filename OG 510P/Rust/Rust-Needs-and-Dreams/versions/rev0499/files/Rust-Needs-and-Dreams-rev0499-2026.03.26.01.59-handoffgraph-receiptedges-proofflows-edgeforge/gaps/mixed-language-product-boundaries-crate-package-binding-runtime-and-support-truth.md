# Gap: mixed-language Rust still lacks one product boundary above bindings, packages, components, and support

## Summary
Rust's mixed-language story is no longer a side quest.
The ecosystem now has several serious lanes:
- Rust is explicitly treating long-lived interop with existing C and C++ systems as real near-term work;
- the safety-critical writeup says teams will carry those language boundaries for years and need interfaces that stay correct, auditable, and in sync;
- PyO3 now directly recommends `maturin`, whose distribution story makes manylinux/musllinux portability, platform tags, and wheel compliance part of the product surface;
- Node-API gives Rust a stable ABI lane for addons, but only at the Node-API boundary;
- UniFFI is a real generated mobile-binding lane with explicit thread-safety and lifetime restrictions;
- CXX gives Rust/C++ teams both Cargo-native and foreign-build-system paths, but requires generated-code/version discipline;
- and the Wasm Component Model plus Rust’s 2026 Wasm Components flagship make multi-language component packaging and distribution part of the active frontier.

What Rust still lacks is the **portable product boundary above those lanes**.

Today, teams can answer fragments such as:
- “this crate can build a wheel,”
- “this addon uses Node-API,”
- “this Rust core can generate Swift/Kotlin bindings,”
- “this bridge works with Cargo or Bazel,”
- or “this component exposes WIT and can be published via registries.”

What they still struggle to answer cleanly is:
- what exact foreign package, module, bundle, addon, or component identity a user installs or imports,
- which generated bindings came from which source interface and generator versions,
- which runtime / interpreter / ABI / threading / lifetime constraints actually belong to the supported product,
- which shipped artifacts correspond to that promise,
- what install or distribution lane was actually exercised,
- and what release, support, policy, or atlas consumers may honestly conclude without rereading packaging folklore.

That missing layer is not another binding generator, not another universal IDL, not another package uploader, and not a “best interop framework” chooser.
It is a **polyglot productization boundary above native boundaries, host packages, component packages, release/install truth, and support truth**.

## Why now
Current ecosystem signals make this much more concrete than it used to be:
- the 2025H2 C++/Rust interop problem-space goal says the near term is not rewriting a significant fraction of active C++, but cooperating across language communities on real mixed-language issues;
- the Rust safety-critical writeup says many teams will integrate Rust into existing C and C++ systems and carry that boundary for years, and explicitly asks for guidance/tooling to keep interfaces correct, auditable, and in sync;
- Rust’s 2026 goal slate explicitly includes **Wasm Components**, pushing multi-language component workflows from experiment toward first-class toolchain work;
- PyO3’s current guide recommends `maturin` as the “batteries included” route to publishing to PyPI, which already turns Python package metadata and packaging workflow into first-class product truth;
- maturin’s distribution guide says portable Linux wheels must satisfy manylinux/musllinux rules, can be constrained to PyPI-compatible targets, and may include separate debug-info files in wheels;
- Node-API’s official docs say it is ABI-stable across Node.js versions, but that guarantee belongs to the Node-API boundary itself;
- UniFFI’s guide targets Kotlin and Swift explicitly, and its design principles say exposed objects must be `Sync` and `Send` and that borrowed data is not returned across the foreign boundary;
- CXX’s docs say foreign-build-system users must generate code, compile C++, and link mixed objects explicitly, and that the Rust-side and C++-side generated bindings must use the same CXX release;
- the Component Model docs say components can work together regardless of source language via portable binaries and WIT with a standardized ABI, while also making clear that publishing/distribution live in registries and tools like `wkg` rather than in the core model itself.

Sources:
- https://github.com/rust-lang/rust-project-goals/blob/main/src/2025h2/interop-problem-map.md
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://pyo3.rs/main/getting-started
- https://www.maturin.rs/distribution.html
- https://nodejs.org/api/n-api.html
- https://mozilla.github.io/uniffi-rs/latest/Getting_started.html
- https://mozilla.github.io/uniffi-rs/latest/internals/design_principles.html
- https://cxx.rs/build/cargo.html
- https://cxx.rs/build/other.html
- https://cxx.rs/build/bazel.html
- https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
- https://component-model.bytecodealliance.org/composing-and-distributing/distributing.html

## The current seam is awkward
Today, mixed-language product truth gets improvised from incompatible ingredients:
- Cargo package metadata,
- Python `pyproject.toml` or wheel tags,
- `package.json` and prebuild metadata,
- generated Swift/Kotlin/Python bindings,
- headers/staticlibs/shared libs,
- WIT files, component manifests, and registry names,
- CI upload steps,
- and README prose or issue archaeology about what is actually supported.

That usually leads to six failures:
1. crate identity and foreign package identity get flattened into one fake “package name” story;
2. generated-binding provenance disappears once artifacts are uploaded;
3. runtime and threading/lifetime constraints get buried in framework docs instead of product receipts;
4. component packages and native ABI packages get compared as though they were the same lane;
5. shipped-artifact truth and support/install truth drift apart;
6. every downstream consumer reinvents the same release/support/adoption summary from scratch.

## Why this matters
This gap matters to:
1. **crate maintainers** — because shipping to Python, Node, Swift/Kotlin, C++, or component consumers creates a product surface larger than the crate itself;
2. **release engineers** — because package/upload/install truth needs to stay attached to what was actually shipped;
3. **support and docs consumers** — because runtime floors, threading assumptions, module names, and platform caveats belong in a reviewable support boundary;
4. **atlas / adoption / guidance work** — because “Rust supports Python/Node/mobile/C++/Wasm” is too vague to guide real decisions;
5. **policy / trust / provenance work** — because foreign ecosystems need package-level artifact identity rather than only Cargo-native package truth.

## What good looks like
A worthy contribution here is a thin composition layer above **Host Package Kit**, **FFI Boundary Kit**, **Wasm Component Kit**, **Release Truth**, and **Support Envelope**.

It should provide at least:
- `polyglot-product-brief/v0` — why this subject exists and which foreign-consumer lane(s) it serves;
- `polyglot-product-subject/v0` — the exact Cargo package, foreign package/component/addon/bundle identities, and comparison base;
- `polyglot-product-pack/v0` — imported host-package / FFI / component / release / support evidence with explicit caveats;
- `polyglot-product-diff/v0` — what changed between two mixed-language product points;
- `polyglot-product-handoff/v0` — bounded summaries for release, support, policy, atlas, and assistant consumers.

The winning version should keep these distinctions visible:
- **crate identity** versus **foreign package identity** versus **installed artifact identity**,
- **generated-binding provenance** versus **runtime/support claims**,
- **native ABI boundary truth** versus **WIT/component boundary truth**,
- **release/install receipts** versus **support conclusions**,
- and **lane-specific caveats** versus **cross-lane comparison summaries**.

The bar is not a better upload wrapper.
The bar is a durable, explainable, importable **polyglot product boundary** for Rust mixed-language products.
