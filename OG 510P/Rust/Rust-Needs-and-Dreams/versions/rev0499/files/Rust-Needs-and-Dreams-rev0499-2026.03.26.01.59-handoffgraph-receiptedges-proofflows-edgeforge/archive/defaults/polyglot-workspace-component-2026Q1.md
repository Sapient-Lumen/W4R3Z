# Default card: Polyglot workspace / monorepo component (2026 Q1)

## Scope
This card applies to:
- adding one Rust component to an existing larger system;
- monorepos and polyglot workspaces where Rust is not yet the sole orchestration center;
- teams deciding whether to bind Rust directly into Python, C++, Node, or mobile stacks;
- and projects where the biggest risk is **premature commitment to one boundary framework** rather than lack of options.

Assumptions:
- existing workspace or repo policy already matters;
- build/discovery/config boundaries are important;
- the Rust component may need to cross a language boundary later;
- and long-term maintainability matters more than getting the first binding demo fastest.

This is **not** the default for:
- greenfield all-Rust workspaces;
- cases where the host boundary is already decisively fixed and non-negotiable;
- or product classes where extension/runtime packaging is the real dominant problem.

## Why this default now
Many real Rust adoptions happen inside an existing larger system, not as a fresh Rust-only repo.
Cargo itself is still actively discussing workspace and configuration discovery because parent manifests or config files can affect unrelated projects, which is strong evidence that workspace attachment and configuration boundaries are first-order concerns here.
Cargo now also supports `include` in `.cargo/config.toml`, which makes local overlays more tractable but also makes the configuration surface more layered rather than less.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://blog.rust-lang.org/releases/latest/
https://doc.rust-lang.org/cargo/reference/config.html
https://doc.rust-lang.org/cargo/reference/workspaces.html

For this exact scope, the archive’s current default is:
**start with an ordinary Cargo workspace member and a narrow Rust core crate, then add a thin boundary adapter crate only after the host language/runtime and package contract are explicit.**

That means the default is architectural restraint:
- keep the Rust core ordinary first;
- make workspace/package/config inheritance explicit;
- treat host-package/distribution requirements as a separate design slot;
- and choose the boundary tool only when the foreign host contract is actually known.

Why this wins here:
- Cargo workspaces already provide shared package metadata, shared dependencies, and shared lints, which is the right base layer for a Rust component inside a larger system.
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo configuration discovery still walks parent directories, and `include` now makes reusable local overlays easier, which means the workspace/config boundary needs to stay visible instead of hidden in folklore.
  https://doc.rust-lang.org/cargo/reference/config.html
- the main foreign-boundary tools are real but materially different:
  - **CXX** is a safe Rust↔C++ common-regime tool, not a universal foreign-binding story.
    https://cxx.rs/
  - **PyO3** is a rich Python integration path and explicitly separates extension-module packaging concerns such as `maturin`, `setuptools-rust`, and `abi3` from the core Rust code.
    https://pyo3.rs/
    https://pyo3.rs/main/building-and-distribution
    https://www.maturin.rs/
  - **UniFFI** generates foreign-language bindings, but its own docs explicitly say it does **not** build the foreign-language code for you.
    https://mozilla.github.io/uniffi-rs/
    https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html
  - **napi-rs** is specifically about compiled Node add-ons via Node-API and comes with an npm/distribution model rather than a generic FFI story.
    https://napi.rs/
    https://napi.rs/docs/introduction/getting-started

Because those lanes differ so much, the safe reusable default here is **core-first + boundary-later**, not immediate commitment to one binding framework.

## Default lane summary
### Default lane
- workspace posture: **ordinary Cargo workspace member with explicit shared metadata/dependency/lint posture**
- Rust architecture: **core crate first, boundary adapter second**
- config posture: **treat `.cargo/config.toml` and config includes as explicit overlays, not invisible magic**
- foreign-boundary posture: **defer framework choice until host/runtime/package contract is explicit**

### Serious alternatives
- **CXX** when the real problem is a Rust↔C++ common-regime boundary and that host is already fixed.
- **PyO3** when the component is clearly a Python extension or embedding story and Python packaging is part of the requirement.
- **UniFFI** when one Rust core must intentionally target multiple foreign-language bindings.
- **napi-rs** when the real host is Node and the compiled add-on + npm package model is known up front.

## Slot guidance
### Workspace slot
Use an ordinary Cargo workspace member unless there is a compelling reason not to.
Leverage `workspace.package`, `workspace.dependencies`, and `workspace.lints` to keep shared Rust policy visible.
For config, prefer explicit `.cargo/config.toml` layering and explicit `include` files over ambient machine-local lore.

### Core/boundary split
Prefer a Rust core crate that is not prematurely contaminated by one host-language framework.
Then add a thin boundary crate when the foreign interface is really settled.
This keeps tests, semver thinking, and local Rust ergonomics from being silently dictated by the first demo binding.

### Host-package / distribution slot
Decide separately whether the project is really shipping:
- a C++ library boundary,
- a Python extension/wheel,
- generated bindings plus downstream host builds,
- or a Node add-on with npm packaging.

That package/distribution slot is not the same decision as “which Rust crate should we try first.”

### Boundary-tool slot
Choose the boundary tool **after** answering:
- Is the host fixed?
- Is package/distribution shape part of the requirement?
- Is one foreign language enough, or are multiple needed?
- Is the boundary a safe common regime, generated bindings, addon ABI story, or extension-module packaging story?

## Serious alternatives and when they win
### CXX wins when
- the target host is clearly C++;
- safety over a shared Rust/C++ regime is the point;
- and a generated C-style FFI layer would be the wrong maintenance tradeoff.

### PyO3 wins when
- the host/runtime is Python;
- extension-module or embedding behavior is central;
- packaging/build distribution is part of the requirement;
- and `maturin` / `setuptools-rust` / `abi3` decisions are real project requirements rather than afterthoughts.

### UniFFI wins when
- one Rust core is intentionally targeting multiple foreign-language bindings;
- the object-model/generation approach is the right fit;
- and it is acceptable that binding generation and foreign build/distribution remain distinct concerns.

### napi-rs wins when
- the project is clearly a Node add-on lane;
- precompiled addon packaging and npm package topology are part of the core problem;
- and using the recommended `@napi-rs/cli` path plus platform packages is acceptable.

## Escalate to a project-specific brief when
- the host language/runtime is already fixed and unavoidable;
- packaging/distribution constraints dominate architecture;
- the component must ship to multiple foreign-language consumers immediately;
- workspace discovery/config inheritance is already a known local pain point;
- or the local institution already has strong overlays around packaging, CI, security review, or runtime selection.

## Canonical references
- Cargo workspaces:
  https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo configuration discovery and includes:
  https://doc.rust-lang.org/cargo/reference/config.html
- Cargo 1.94 discovery discussion:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust 1.94 release note for config includes:
  https://blog.rust-lang.org/releases/latest/
- CXX:
  https://cxx.rs/
  https://cxx.rs/tutorial.html
- PyO3 guide and build/distribution notes:
  https://pyo3.rs/
  https://pyo3.rs/main/building-and-distribution
- maturin user guide:
  https://www.maturin.rs/
- UniFFI guide:
  https://mozilla.github.io/uniffi-rs/
  https://mozilla.github.io/uniffi-rs/latest/tutorial/foreign_language_bindings.html
- napi-rs:
  https://napi.rs/
  https://napi.rs/docs/introduction/getting-started

## Renewal inputs
Recheck before renewal:
- Cargo workspace/config discovery posture and config-include ergonomics;
- whether one boundary family becomes clearly more dominant for this project class;
- host-package and extension/productization shifts in the broader archive;
- packaging/distribution tooling changes for Python, Node, and multi-language generator lanes;
- and whether exact-package-identity hygiene needs to be made more machine-checkable for boundary crates and package-manager outputs.

## Non-goals
- declaring one foreign-binding framework the universal default;
- treating boundary-framework choice as a starter-template decision;
- flattening workspace policy, host-package policy, and Rust-core design into one move;
- pretending this card replaces polyglot-productization or host-package review.
