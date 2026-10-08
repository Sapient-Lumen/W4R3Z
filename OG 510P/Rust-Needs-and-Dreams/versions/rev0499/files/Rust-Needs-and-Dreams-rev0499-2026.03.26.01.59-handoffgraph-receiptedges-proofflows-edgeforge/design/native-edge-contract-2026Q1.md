## Execution addendum (rev0423)
Read `design/native-edge-execution-blueprint-2026Q1.md` when the question is no longer “why should this frontier exist?” but “what exact artifact families, commands, pilot lanes, and anti-goals should it ship?”

Interpretation rule:
- this contract still defines the frontier boundary;
- the new blueprint defines the preferred v0 execution shape above imported boundary/provider/context/handoff evidence;
- and neither note should be mistaken for a universal FFI framework or one-tool interop empire.


# Design: Native Edge Contract (2026Q1)

## Goal
Promote the existing **Native Edge Stack** into an explicit contract for **Rust adoption inside large mixed-language and native-library-heavy systems**.

The missing contribution is not another binding generator, another `-sys` helper, another provider crate, or another build-system bridge.
It is the **review boundary above those lanes**: one way to say **which Rust↔native boundary was reviewed, which native providers and link plans actually won, what host/target/toolchain context mattered, what external-build handoff is expected, and what later release/support/audit consumers may honestly import**.

This contract should sit above and import:
- `design/ffi-boundary-kit.md`
- `design/native-dependency-kit.md`
- `design/build-interop-kit.md`
- `design/cross-toolchain-kit.md`
- `design/support-envelope-kit.md`
- `design/release-truth-stack.md`
- `design/polyglot-productization-stack.md`

## Why this is worth promoting now
Rust’s official and primary-project signals now line up around one conclusion: **cross-language interop is not a niche side quest, and the missing layer is above today’s ingredients**.

- The accepted 2025H1 goal **Evaluate approaches for seamless interop between C++ and Rust** says Rust should seriously consider what it takes to enable adoption in projects that must use **large, rich C++ APIs**.  
  https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- The 2025H2 **C++/Rust Interop Problem Space Mapping** goal says there are **billions of lines of C++** representing enormous value and that broad rewrites are neither feasible nor advisable in the near term.  
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- The July 2025 project-goals update says the language team established that Rust should evolve toward a **first-class C++ interop story**, while also emphasizing that interop needs differ across groups.  
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The January 2026 program-management update says **Cross-language interop** is now an explicit Rust application area, with companies that have large C++ codebases expected to care directly about that roadmap.  
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The January 2026 safety-critical writeup says teams will integrate Rust into existing C and C++ systems and carry that boundary for years, and explicitly recommends treating interop as part of the safety story.  
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust 2024 now requires `unsafe extern` blocks, which is a useful language-level signal that the signatures themselves are a review boundary and still require manual correctness review.  
  https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- Rust release notes now include FFI/ABI hardening like making it a hard error to use vector types with a non-Rust ABI without the required target feature, which reinforces that ABI details remain real surface area.  
  https://doc.rust-lang.org/beta/releases.html
- The tool ecosystem is real but plural rather than converged:
  - **CXX** deliberately carves out a safe common regime and requires paired generated code/static assertions.  
    https://cxx.rs/
  - **autocxx** explicitly targets **large existing C++ codebases** and layers automation over `bindgen` + CXX-style safety.  
    https://google.github.io/autocxx/
  - **bindgen** still depends on `libclang`, which means host/toolchain friction remains part of the lane.  
    https://rust-lang.github.io/rust-bindgen/requirements.html
  - **Corrosion** can import Rust targets into CMake, but direct bindgen integration is still left to build scripts or custom steps, and cbindgen integration is still marked experimental.  
    https://corrosion-rs.github.io/corrosion/usage.html  
    https://corrosion-rs.github.io/corrosion/ffi_bindings.html

Together these signals say the missing move is now **not** “pick the winning interop tool.”
It is to define the **portable review and handoff boundary above non-equivalent interop lanes**.

## What this contract should own
### 1) Native-edge subject truth
One concrete reviewed subject:
- crate/workspace/revision identity
- lane classification (C ABI export, system-library consumer, C++ bridge, external-build handoff, etc.)
- comparison base
- supported host/target tuples in scope

### 2) Boundary truth (imported, not reinvented)
Import `ffi-pack`-style facts for:
- exported/imported symbols and types
- ownership/lifetime/layout contracts
- generator provenance (`bindgen`, `cbindgen`, `cxx`, `autocxx`, handwritten)
- boundary drift reports

Design rule: **boundary truth is not provider truth**.

### 3) Provider/link truth (imported, not reinvented)
Import `native-pack`-style facts for:
- provider choices (`pkg-config`, `system-deps`, vendored builds, external injection, etc.)
- include/lib/framework/tool decisions
- link plans
- reason-coded provider fallbacks and conflicts

Design rule: **provider truth is not the ABI/boundary story**.

### 4) Host / target / toolchain / external-build context
Attach the operating context that shaped the subject:
- host vs target split
- compiler/SDK/sysroot assumptions when relevant
- Cargo-only vs foreign-linker vs foreign-build ownership
- CMake/Bazel/Buck/Nix/distro handoff notes

Design rule: **Cargo success is not the same thing as external-build success**.

### 5) Bounded downstream handoff
Emit lossy, clearly-bounded consumer summaries for:
- release review
- support / incident intake
- audit / safety review
- ecosystem guidance / adoption navigation
- later polyglot productization work

Design rule: **consumer conclusions stay explicitly downstream**.

## What a worthy epic contribution looks like in theory and practice
A worthy contribution here should look like a thin, compositional layer such as:
- CLI: `cargo native-edge`
- aggregate artifact: `native-edge-pack/v0`

It should prove five things in order:
1. **boundary-first review** — one subject can carry exact boundary facts and generated-artifact provenance;
2. **provider/link honesty** — native providers, fallbacks, and link plans are explicit instead of trapped in `build.rs` and logs;
3. **context separation** — host/target/toolchain/external-build facts are visible without swallowing the lower layers;
4. **foreign-build handoff** — at least one non-Cargo consumer can ingest the result without archaeology;
5. **bounded consumer imports** — release/support/audit/guidance layers can import the subject without flattening it.

The epic should remain **thin**:
- no universal Rust ABI claim;
- no one-true C++ bridge;
- no one-true native package manager;
- no one-true external build system;
- no fake “interop readiness score”.

## Ranked rollout
1. **C ABI export lane**
   - smallest boundary surface, strongest proof that exact boundary and generated-artifact provenance can travel.
2. **System-library consumer lane**
   - strongest proof that provider locks and link plans deserve their own lane.
3. **C++ bridge lane**
   - strongest proof that richer C++ interop still needs the same joined review boundary.
4. **External-build handoff lane**
   - strongest proof that the contract matters outside Cargo.
5. **Support / audit / safety import lane**
   - only after the lower-level artifacts are stable enough to import honestly.

## Distinctions from nearby archive frontiers
- **Public API Contract** is about Rust library evolution and semver evidence, not foreign-boundary/provider/build-handoff joins.
- **Toolchain Productization Contract** is about provisioned toolchains, rebuilt std/sysroot families, and runtime-analysis lanes.
- **Compatibility Claims** is about support envelopes and declared-vs-observed support posture.
- **Polyglot Productization Stack** is about shipped foreign-consumer products (Python wheels, Node packages, mobile bindings, components, etc.) above native-edge facts.
- **Native Edge Contract** is the missing **adoption / review / external-build-handoff** boundary between those layers.

## Non-goals
- a stable general-purpose Rust ABI
- flattening C ABI export, C++ bridge, provider selection, and foreign-build handoff into one lane
- replacing `bindgen`, `cbindgen`, CXX, `autocxx`, `pkg-config`, `system-deps`, Corrosion, or distro/native package managers
- treating one successful local Cargo build as proof of broader interop support

## References
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html
- https://doc.rust-lang.org/beta/releases.html
- https://cxx.rs/
- https://google.github.io/autocxx/
- https://rust-lang.github.io/rust-bindgen/requirements.html
- https://corrosion-rs.github.io/corrosion/usage.html
- https://corrosion-rs.github.io/corrosion/ffi_bindings.html
