# Design: Native Edge Pilot Program (FFI Boundary + Native Dependency)

## Goal
Turn the archive's **cross-language / native integration** band into an executable program instead of two adjacent good ideas.

The pilot program couples:
- [`design/native-edge-stack.md`](./native-edge-stack.md)
- [`design/native-edge-cpp-lane-map.md`](./native-edge-cpp-lane-map.md)
- [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md)
- [`design/native-dependency-kit.md`](./native-dependency-kit.md)
- [`proposals/epic-native-edge-stack.md`](../proposals/epic-native-edge-stack.md)
- [`proposals/epic-ffi-boundary-kit.md`](../proposals/epic-ffi-boundary-kit.md)
- [`proposals/epic-native-dependency-kit.md`](../proposals/epic-native-dependency-kit.md)

The central thesis is that Rust adoption across existing native estates usually fails at **boundary + dependency + build-handoff** seams, not because one more FFI generator is missing.

## Why this now deserves a pilot program
- The Rust project has now made C++/Rust interop an explicit design area twice: first with **Evaluate approaches for seamless interop between C++ and Rust**, then with **C++/Rust Interop Problem Space Mapping**. Both frame interop as necessary for adoption in large existing codebases rather than as a niche edge case.
  - https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- Cargo is actively trying to reduce reliance on bespoke `build.rs` behavior and make build flows more structured. The plumbing goal, build-script delegation work, artifact-dependency direction, and final-artifact discussion all point toward a missing structured handoff layer above today's point tools.
  - https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  - https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
  - https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
  - https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The sandboxed-build-script work explicitly says `-sys` crates and system-library probing are a first-class use case that any eventual sandbox story must support. That means native-provider truth cannot stay trapped in opaque scripts forever.
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- The Rust Foundation's 2026–2028 strategy explicitly emphasizes **responsible growth in adoption** and **meaningful engagement from organizations that rely on Rust**. The native edge is where that pressure lands in practice.
  - https://rustfoundation.org/strategic-plan/
- The 2025 State of Rust survey says organizations are continuing to hire Rust developers, indicating a more structural presence in companies and codebases. That makes mixed-language adoption infrastructure more leveraged than it would be in a pure-greenfield story.
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Strategic posture
This should be treated as a **companion evidence substrate**, not as a demand that Rust/Cargo solve all native integration centrally.

- `cargo ffi` owns the explicit review boundary.
- `cargo native` owns provider choice, host/target truth, and link-plan evidence.
- existing tools (`bindgen`, `cbindgen`, `cxx`, `autocxx`, `system-deps`, `pkg-config`, `vcpkg`, `cmake`, Cargo artifact dependencies, external build systems) remain first-class producers or consumers.

## Ranked pilot order
Treat [`design/native-edge-cpp-lane-map.md`](./native-edge-cpp-lane-map.md) as the semantic lane map for this program. The pilot program stays ordered by execution value, but the lane-map note keeps the archive from collapsing C ABI, CXX-style safe-common bridges, autocxx-style automation, provider truth, and foreign-build handoff into one interop story.


### Pilot 1 — C ABI export lane
**Shape**
- Rust library exposing a C ABI to an external consumer.
- Typical tools: `cbindgen`, symbol export controls, packaging metadata.

**Why first**
- Smallest surface area.
- Clear release artifact boundary.
- Useful to downstream C, C++, packaging, and regulated review flows.

**Must prove**
- `ffi-manifest/v0` can describe exported items, ownership contracts, and toolchain/generator provenance.
- `ffi-report/v0` can classify drift between releases.
- `ffi-pack/v0` is sufficient for a downstream consumer to integrate without reading `build.rs`.

### Pilot 2 — System-library consumer lane
**Shape**
- Rust crate consuming an existing native library via `pkg-config`, `system-deps`, `vcpkg`, or similar.

**Why second**
- This is the common `-sys` pain shape.
- It stresses provider choice, duplicate `links`, host/target distinctions, and fallback explanation.

**Must prove**
- `native-intent/v0` can represent provider preferences without flattening them.
- `native-provider-lock/v0` explains which provider won and why.
- `native-link-plan/v0` is enough for CI and external build systems to reason about inputs.

### Pilot 3 — C++ bridge lane
**Shape**
- Rust ↔ C++ integration through `cxx`, `autocxx`, or equivalent tooling.

**Why third**
- It captures the richer interop case the project-goals work is explicitly trying to enable.
- It forces the archive to model generated bridges, ownership contracts, and build-system assumptions more honestly.

**Must prove**
- `ffi-pack/v0` can carry generator inputs and bridge artifacts without pretending Rust has a stable general ABI.
- boundary drift and native-provider drift stay separable.
- mixed-language examples remain explainable to humans who did not author the bridge.

### Pilot 4 — External build handoff lane
**Shape**
- Cargo project integrated into CMake/Bazel/Meson/Buck/Nix/distro packaging workflows.

**Why fourth**
- This is the lane where adoption friction becomes organizational rather than crate-local.
- It tests whether the kits produce artifacts that other systems can ingest instead of reverse-engineering Cargo internals.

**Must prove**
- `ffi-pack/v0` and `native-pack/v0` are ingestible without Cargo-specific hidden state.
- override/injection flows are explicit.
- final-artifact handoff is reviewable.

### Pilot 5 — Audited / safety-oriented lane
**Shape**
- Native edge evidence consumed together with Safety Evidence, Support Envelope, and Policy.

**Why fifth**
- High value, but only after the archive proves the lower-level artifacts are stable enough to compose.

**Must prove**
- ownership and boundary contracts can feed assurance review.
- native-provider choices and support-floor claims can be attached without becoming a fake certification badge.

## Shared artifact family
The pilots should converge on a portable family, not parallel one-off reports.

### Boundary layer
- `ffi-manifest/v0`
- `ffi-report/v0`
- `ffi-pack/v0`

### Native-provider layer
- `native-intent/v0`
- `native-provider-lock/v0`
- `native-link-plan/v0`
- `native-report/v0`
- `native-pack/v0`

### Shared attachments
- generated headers / bindings
- symbol snapshots
- provider raw outputs (`pkg-config`, CMake cache fragments, provider manifests)
- downstream integration notes
- optional policy / support / safety attachments from other kits

## Cross-kit boundaries
- **Build Interop Kit** should consume these packs for larger build graphs, not redefine them.
- **Cross Toolchain Kit** should provision toolchains / SDKs / sysroots, not own provider locks.
- **Compile-Time Capabilities Kit** should govern what discovery/build actions are allowed, not describe the native graph itself.
- **Support Envelope Kit** should consume native runtime/provider claims, not replace them.
- **Safety Evidence Kit** should attach boundary/native facts, not hide them inside a generic assurance blob.
- **Wasm Component Kit** remains separate; do not let “interop” flatten native and component-model lanes together.

## Pilot scorecard
A pilot only graduates if it shows all of the following:
1. **Downstream legibility** — a consumer can integrate or review the result without reading local folklore.
2. **Diffability** — release or CI drift is explicit and reason-coded.
3. **Build-system neutrality** — the artifact is useful outside one exact Cargo invocation.
4. **Provider honesty** — vendored/system/artifact/external-provider differences stay explicit.
5. **No fake standardization** — v0 describes what exists and how it was chosen; it does not claim the ecosystem has one blessed native lane.

## Anti-goals
- Not a general Rust ABI proposal.
- Not a replacement for `bindgen`, `cbindgen`, `cxx`, `autocxx`, `pkg-config`, `system-deps`, `vcpkg`, `cmake`, or external build systems.
- Not a universal package manager for native dependencies.
- Not a promise that `build.rs` disappears in one step.
- Not another dashboard that only the crate author can interpret.


## Read this with
- `gaps/native-edge-adoption-boundaries-provider-locks-and-build-handoffs.md`
- `design/native-edge-stack.md`
- `proposals/epic-native-edge-stack.md`
