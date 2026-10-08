# Renewal receipt: polyglot workspace / monorepo component (2026-03-22)

## Subject
- default card: `defaults/polyglot-workspace-component-2026Q1.md`
- review date: 2026-03-22
- archive revision: rev0384
- scope: adding one Rust component to a larger non-Rust or mixed-language system where workspace boundaries, host-package constraints, and boundary-framework choice can easily get conflated
- non-goal: declaring one cross-language framework the default for all C++, Python, Node, mobile, or generated-binding scenarios

## Renewal verdict
**add first receipt; keep**

The lane still reads correctly as:
- an **ordinary Cargo workspace member** when possible,
- a **Rust core crate first**,
- a **thin boundary adapter crate second**,
- explicit workspace/config layering,
- and framework selection only after the host/runtime/package contract is known.

The fresh research did not reveal one framework that safely collapses the lane.
Instead, it reinforced that the main options solve materially different problems:
- **CXX** for a shared Rust↔C++ regime,
- **PyO3** for Python integration plus packaging/build-distribution choices,
- **UniFFI** for generated multi-language bindings,
- **napi-rs** for Node-API add-ons with npm-native distribution topology.

## Canon import checked this round
Primary documentation surfaces re-read:
- Rust challenges:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo 1.94 development cycle:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust 1.94 release notes:
  https://blog.rust-lang.org/releases/latest/
- Cargo workspaces:
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo configuration:
  https://doc.rust-lang.org/cargo/reference/config.html
- CXX:
  https://cxx.rs/
  https://cxx.rs/tutorial.html
- PyO3:
  https://pyo3.rs/
  https://pyo3.rs/main/building-and-distribution
- maturin:
  https://www.maturin.rs/
- UniFFI:
  https://mozilla.github.io/uniffi-rs/
  https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html
  https://mozilla.github.io/uniffi-rs/latest/bindings.html
- napi-rs:
  https://napi.rs/
  https://napi.rs/docs/introduction/getting-started

Canon judgment:
- Rust’s current ecosystem still has the exact problem this lane was meant to handle: choice paralysis and tacit knowledge are real, but the choice is not “which magic binding crate wins”; it is “which boundary family actually matches the host/package contract?”.
- Cargo’s workspace inheritance and config discovery remain active enough concerns that the core workspace boundary still deserves first billing in this lane.
- The current default remains correct because it is the one answer that stays useful across C++, Python, generated multi-language, and Node add-on variants without lying about their sameness.

## Workspace / config import
Imported judgments:
- `workspace.dependencies` and `workspace.lints` are now mature enough that a normal workspace member is still the right boring substrate for this lane.
- Cargo still probes parent directories for config, and config `include` now makes shared overlays easier, so the lane should explicitly name config layering rather than treating it as invisible background.
- The lane should keep **workspace shape**, **config overlays**, and **host boundary tooling** separate, because teams often misdiagnose one as the other.

## Boundary-framework import
Imported judgments:
- **CXX** still presents itself as a safe Rust↔C++ interop regime rather than a universal FFI abstraction.
- **PyO3** still explicitly distinguishes Python extension modules from Rust binaries embedding Python, and its build/distribution docs make packaging tools (`maturin`, `setuptools-rust`) and `abi3` decisions first-class.
- **UniFFI** still makes the generator boundary explicit: it generates foreign-language bindings, but it does not build the foreign-language code for you.
- **napi-rs** still positions itself as a Node-API add-on lane with precompiled binary and cross-compilation tooling, not as generic FFI.

Boundary judgment:
- no one framework should be promoted to universal default;
- the card is right to default to **core-first + boundary-later** instead of early framework commitment.

## Host-package / distribution import
Imported judgments:
- PyO3’s own docs make Python wheel/build/distribution choices part of the lane, including `maturin` versus `setuptools-rust` and `abi3` tradeoffs.
- napi-rs’s recommended flow uses `@napi-rs/cli`, target-platform selection, optional native npm packages, and generated GitHub actions, which makes package topology part of the real story rather than an implementation footnote.
- UniFFI’s docs still leave foreign-language build/distribution as downstream work, which is an important reason not to flatten it into the PyO3 or napi-rs lane.

Package judgment:
- the archive should keep **boundary framework** and **host-package/distribution contract** explicitly separate inside polyglot guidance;
- otherwise “it worked in the demo” becomes the false default for a very different packaging lane.

## Registry / supply-chain import
Public ecosystem signals checked:
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RustSec advisories:
  https://rustsec.org/advisories/
- crates.io malicious-crate notification policy:
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/

What this receipt takes from those sources:
- Security-tab advisory surfacing now belongs in renewal hygiene for named boundary crates.
- Trusted Publishing enhancements, SLOC, source browsing, and `pubtime` make public review materially better than before.
- Recent malicious/lookalike removals (`envlogger`, `oncecell`, `serd`, `postgress`, and others) are a concrete warning against fuzzy naming in exactly the sort of cross-language/package-manager context where people already juggle multiple package systems.

Exact identity notes for this lane:
- `cxx` is not a generic “Rust/C++ binding” label.
- `pyo3` is not interchangeable with `maturin`; one is the Rust/Python binding crate family and the other is a packaging/build tool.
- `uniffi` / `uniffi_bindgen` should be named exactly.
- `napi-rs` and `@napi-rs/cli` should be named exactly rather than as a vague Node binding story.

## Maintenance / support-envelope import
Support-envelope facts that still hold:
- this lane is for **polyglot component introduction**, not for whole-product package management;
- mixed-language teams benefit most from keeping Rust-core logic ordinary and boundary-specific logic thin;
- the costliest mistakes in this lane still come from choosing a boundary framework before the host/package contract is known.

Maintenance judgment:
- the lane deserves to remain a maintained card because it covers one of the most common real Rust-adoption shapes;
- but it should stay bounded enough that later revisions can split out narrower public lanes such as **public SDK / generated-client library** or **durable internal component** if the evidence says they need separate defaults.

## Freshness / replay notes
Fresh inputs checked on 2026-03-22:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://blog.rust-lang.org/releases/latest/
- https://doc.rust-lang.org/cargo/reference/workspaces.html
- https://doc.rust-lang.org/cargo/reference/config.html
- https://cxx.rs/
- https://cxx.rs/tutorial.html
- https://pyo3.rs/
- https://pyo3.rs/main/building-and-distribution
- https://www.maturin.rs/
- https://mozilla.github.io/uniffi-rs/
- https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html
- https://mozilla.github.io/uniffi-rs/latest/bindings.html
- https://napi.rs/
- https://napi.rs/docs/introduction/getting-started
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://rustsec.org/advisories/

Replay notes:
- renew when Cargo materially changes workspace/config discovery or config-include ergonomics;
- renew when one boundary family becomes clearly more central for this exact scope instead of just for a narrower host-specific lane;
- renew when PyO3, UniFFI, or napi-rs materially change their packaging/generation posture;
- split the card if the archive is ready to maintain separate lanes for **public SDK / generated-client library**, **Python extension product**, or **Node native package**.

## Lane judgment
Keep the lane and add this receipt as the missing first proof.

Why:
- it closes the last first-receipt gap in the maintained defaults corpus;
- it confirms the current answer with fresher Cargo and boundary-tool evidence;
- and it keeps the archive honest about one of Rust’s most common adoption shapes without pretending that one framework solved them all.

## Open watch items
- whether a separate **public SDK / generated-client library** card eventually deserves to split from this component lane;
- whether Cargo’s config/include ergonomics reduce enough local pain to simplify the workspace posture;
- whether exact-identity hygiene for boundary crates and package-manager outputs should become machine-checked in the archive;
- whether the next stronger corpus move is a renewal of an older central card rather than a new public lane.
