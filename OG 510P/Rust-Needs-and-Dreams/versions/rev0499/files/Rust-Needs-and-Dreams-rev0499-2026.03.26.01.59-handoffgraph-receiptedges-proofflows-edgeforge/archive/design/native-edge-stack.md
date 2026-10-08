## rev0415 addendum: read this stack as a Native Edge Contract
This stack should now be read as more than a composition memo.
The archive now treats it as the clearest next **cross-language / native-adoption / external-build-handoff** frontier, with the explicit contract note in `design/native-edge-contract-2026Q1.md`.

Interpretation rule:
- keep **FFI Boundary** responsible for boundary truth;
- keep **Native Dependency** responsible for provider/link truth;
- keep **Build Interop** and **Cross Toolchain** as context imports;
- keep **Polyglot Productization** as the broader shipped-product seam above this layer; and
- use **Native Edge Contract** when the real missing layer is the joined review subject plus bounded handoff, not another generator or provider bake-off.


# Design note: Native Edge Stack (FFI Boundary + Native Dependency + external-build handoff)

## Goal
Define the **division of labor and consumer flow** between Rust↔native boundary manifests, native-provider selection and link plans, host/target/toolchain context, external-build handoff, and downstream release/support/audit consumers so Rust can become easier to adopt inside **large mixed-language and native-library-heavy codebases** without anointing one binding generator, one provider crate, one C++ bridge, or one external build system as the answer.

This is **not** a new mega-interop framework.
It is a stack note explaining how the existing archive pieces should compose, and it should be read together with [`design/native-edge-pilot-program.md`](./native-edge-pilot-program.md) and [`proposals/epic-native-edge-stack.md`](../proposals/epic-native-edge-stack.md):
- [`design/ffi-boundary-kit.md`](./ffi-boundary-kit.md)
- [`design/native-dependency-kit.md`](./native-dependency-kit.md)
- [`design/build-interop-kit.md`](./build-interop-kit.md)
- [`design/cross-toolchain-kit.md`](./cross-toolchain-kit.md)
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/safety-evidence-kit.md`](./safety-evidence-kit.md)

## Why this note is needed now
Rust’s current signals no longer say only “FFI is important” or “native dependencies are annoying.” They say the real missing seam is now **above** those pieces:
- the accepted 2025H1 goal **Evaluate approaches for seamless interop between C++ and Rust** explicitly targets Rust adoption in projects that must use large, rich C++ APIs;
- the 2025H2 **C++/Rust Interop Problem Space Mapping** effort says there are billions of lines of C++ code representing enormous value, that full rewrites are neither feasible nor advisable in the near term, and that external libraries currently solve the space in different ways with significant end-user investment;
- the July 2025 project-goals update says the language team established that Rust should evolve toward a **first-class C++ interop story**, while also stressing that interop needs differ across groups;
- Cargo’s roadmap issue to **reduce the need for users to write build scripts** says build scripts increase build times, bug risk, and dependency-review scope, with `-sys` / FFI work explicitly remaining among the reasons they persist;
- the sandboxed build-script goal sharpens the same point from the build-governance side: native probing is one of the trickiest reasons build scripts remain hard to restrict;
- Cargo’s build-script docs say `links` is useful but still limited: one package per `links` value, build-script mediation, and metadata that reaches only immediate dependents;
- the current tool families are legitimate but non-equivalent rather than converged: `system-deps` makes system requirements declarative in `Cargo.toml`, `pkg-config` shells out during build scripts, CXX focuses on a safe common regime for Rust/C++, and `autocxx` targets large existing C++ codebases with automated bindings layered over CXX-style safety.

Together these signals justify treating native adoption as a **frontier-worthy stack seam** rather than leaving it split across two kits, provider docs, generated headers, build logs, and README folklore.

## Stack layers

### 1) FFI Boundary Kit: explicit boundary truth
FFI Boundary owns the **declared Rust↔native interface**:
- exposed / imported symbols and types,
- ownership and lifetime contracts,
- generated header / binding provenance,
- boundary drift reports,
- and downstream-consumable `ffi-pack/v0` artifacts.

This layer answers questions like:
- “What boundary is actually being promised?”
- “Which generated artifacts came from which inputs?”
- “What changed at the boundary between releases?”

Design rule: **boundary truth must stay separate from provider/link truth**.
A generated header is not the same thing as a native-provider decision.

### 2) Native Dependency Kit: provider, lock, and link truth
Native Dependency owns the **provider-resolution and link-plan boundary**:
- native intent,
- provider choice and fallback order,
- host/target separation,
- include/lib/framework/tool/link-plan facts,
- reason-coded provider reports,
- and `native-pack/v0` artifacts.

This layer answers questions like:
- “Which provider actually satisfied this native dependency?”
- “Was the result system-provided, vendored, artifact-based, or externally injected?”
- “What include paths, libraries, frameworks, and tool invocations shaped the result?”

Design rule: **provider truth must stay separate from ABI/boundary truth**.
Knowing that OpenSSL came from `pkg-config` is not the same thing as knowing which Rust/C boundary is exposed.

### 3) Native Edge Stack: subject identity and build-handoff truth
The Native Edge Stack itself owns the **joined review subject**:
- one concrete mixed-language/native-integration subject,
- imported `ffi-pack/v0` and `native-pack/v0` references,
- subject-scoped host/target/toolchain context,
- external-build / downstream-handoff notes,
- and aggregate diff / handoff / decision artifacts.

This layer answers questions like:
- “Which boundary facts and provider facts belong to the same reviewed subject?”
- “What should a CMake/Bazel/Buck/Nix/distro consumer ingest?”
- “What part of the story is Cargo-only, and what part is intended to travel beyond Cargo?”

Design rule: **the stack is a thin referenced join, not a redefinition of the lower layers**.

### 4) Build Interop + Cross Toolchain + Compile-Time Capabilities: imported context, not replacement truth
These adjacent kits should remain imports:
- **Build Interop Kit** owns broader build-graph/export/import surfaces;
- **Cross Toolchain Kit** owns compilers, SDKs, sysroots, and target provisioning;
- **Compile-Time Capabilities Kit** owns what discovery/build actions are allowed or restricted.

The Native Edge Stack may import them when a subject needs them, but it should not let them erase boundary/provider distinctions.

Design rule: **context imports explain the operating environment; they do not become the boundary or provider source of truth**.

### 5) Support / Release / Safety consumers: bounded conclusions
Downstream consumers should import the stack rather than reconstruct it:
- **Support Envelope** can attach runtime-floor and support claims;
- **Release Truth** can tie packs to released artifacts;
- **Safety Evidence** can cite boundary/provider facts without flattening them into one fake certification story.

Design rule: **consumer conclusions remain lossy and say so**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust/C++ bridge” or “the one true native package manager.”
It is a thin, reviewable stack with clear boundaries:

1. **boundary truth first**
   - prove exported/imported boundary manifests, generated artifacts, and drift reports on one real mixed-language subject;
2. **provider/link truth second**
   - prove provider locks, host/target separation, and reviewable link plans without collapsing them into boundary manifests;
3. **external-build handoff third**
   - prove at least one non-Cargo consumer can ingest the result without reverse-engineering build scripts;
4. **support/release/audit consumers fourth**
   - prove the native-edge facts can travel into release/support/audit review without becoming a fake global verdict.

An aggregate artifact may exist, but it should be a **thin referenced pack** such as `native-edge-pack/v0`, not a new truth engine that hides whether a fact came from FFI review, provider resolution, or external-build integration.

## Ranked first execution lanes
Treat [`design/native-edge-cpp-lane-map.md`](./native-edge-cpp-lane-map.md) as the lane taxonomy for this stack. It keeps C ABI export/import, typed safe-common C++ bridges, large-existing-codebase automation, provider/link truth, foreign-build handoff, and watch-worthy upstream motion distinct while still allowing one joined native-edge subject.

1. **C ABI export lane**
   - smallest boundary surface, strongest downstream value, best first proof that one reviewed subject can tie headers/bindings to exact sources and toolchains.
2. **System-library consumer lane**
   - best proof that provider locks and link plans matter independently of ABI export.
3. **C++ bridge lane**
   - best proof that richer interop still needs the same joined review boundary.
4. **External build handoff lane**
   - best proof that the stack matters outside Cargo.
5. **Support / audit lane**
   - only after the lower-level artifacts are stable enough to import honestly.

## Non-goals
- a universal Rust ABI proposal;
- a universal C++ bridge generator;
- a universal native package manager;
- replacing `bindgen`, `cbindgen`, `cxx`, `autocxx`, `pkg-config`, `system-deps`, `vcpkg`, `cmake`, or external build systems;
- flattening boundary truth, provider truth, toolchain context, and downstream conclusions into one fake “interop support” claim.

## Archive implications
- The archive should now treat **FFI Boundary Kit + Native Dependency Kit** as an explicit **Native Edge Stack** rather than only a top-band frontier note.
- Future revisions should prefer **joined review subjects, imported lower-layer packs, external-build handoff proofs, and bounded support/release/safety consumers** over another generator bake-off or provider-manager pitch.
- When Polyglot Productization, Build Interop, Safety Evidence, or Release Truth work cites native adoption, they should import **boundary truth** and **provider/link truth** separately and then cite the joined native-edge subject only where needed.

## References (signals)
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://github.com/rust-lang/rust-project-goals/blob/main/src/2025h2/interop-problem-map.md
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://github.com/rust-lang/cargo/issues/14948
- https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- https://doc.rust-lang.org/cargo/reference/build-scripts.html
- https://docs.rs/system-deps/
- https://docs.rs/pkg-config
- https://cxx.rs/
- https://google.github.io/autocxx/
