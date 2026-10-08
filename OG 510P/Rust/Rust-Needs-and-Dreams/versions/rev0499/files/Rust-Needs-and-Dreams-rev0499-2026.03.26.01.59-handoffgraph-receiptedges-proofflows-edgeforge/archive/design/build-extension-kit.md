# Design: Build Extension Kit (`cargo buildext`, `build-ext-pack/v0`)

## Goal
Define a small, versioned substrate for **declarative build extensions, parameter passing, and safe final-artifact uplift** so Cargo and ecosystem tools can replace a meaningful share of ad hoc `build.rs` wrappers without pretending `build.rs` disappears entirely.

This should not replace Cargo itself, native build systems, or the remaining fully imperative build-script escape hatch. It should make the common case more auditable, sandboxable, and interoperable.

## References (signals)
- Cargo roadmap issue: reduce the need for users to write build scripts because they hurt build times, increase bug risk, and enlarge audit scope.
  https://github.com/rust-lang/cargo/issues/14948
- RFC 2196 / Cargo unstable docs: metabuild is the existing declarative lane.
  https://rust-lang.github.io/rfcs/2196-metabuild.html
  https://doc.rust-lang.org/beta/cargo/reference/unstable.html
- Metabuild tracking issue: remaining work includes multiple build scripts, parameter passing, delegation, and conflict semantics.
  https://github.com/rust-lang/cargo/issues/14903
- Cargo 1.93 cycle: custom final artifacts discussion around explicit directives, selected-package uplift, collision reporting, and Cargo-managed locking.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo build-script docs: `links`, `cargo::metadata`, and `OUT_DIR` are today’s structured seams.
  https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Sandboxed build-scripts goal: determinism and least privilege matter for both trust and caching.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- RFC 2136: long-term declarative native dependencies remains a known destination.
  https://rust-lang.github.io/rfcs/2136-build-systems.html

## Core components

### 1) `build-ext-manifest/v0`
A canonical description of declarative build-extension intent for one package.

Key ideas:
- package identity
- ordered `steps`
- per-step `params`
- declared inputs (`files`, `env`, `cfg`, optional tool probes)
- declared generated outputs under `OUT_DIR`
- optional declared required capabilities for fallback imperative paths

Design rule: the manifest is **tool-facing JSON**, even if the source of truth began in `Cargo.toml` metadata.

### 2) `build-ext-report/v0`
A resolved report for an actual build invocation.

It should capture:
- which steps actually ran
- resolved versions of build-extension crates/tools
- timings
- declared vs observed inputs
- outputs generated under `OUT_DIR`
- warnings about unstable or fallback imperative behavior

This is where caching, sandbox policy, and CI review meet.

### 3) `build-artifact-export/v0`
A structured request to uplift final artifacts that originated under `OUT_DIR`.

Each export should include:
- package identity
- stable export name
- source path relative to `OUT_DIR`
- destination path relative to `artifact-dir`
- mode (`file` / `dir`)
- optional platform/profile selectors

Design rule: v0 only permits **Cargo-mediated uplift**. Build steps do not get direct write access to `artifact-dir`.

### 4) `build-artifact-report/v0`
A per-build report for export outcomes.

It should record:
- selected packages eligible for uplift
- copies performed
- digests / sizes of exported outputs
- collisions and why they errored
- skipped exports and why

This turns “where did my generated completions / manifests / templates come from?” into a reviewable answer.

### 5) `build-ext-pack/v0`
A portable bundle carrying:
- `build-ext-manifest/v0`
- `build-ext-report/v0`
- optional raw source metadata from `Cargo.toml`
- `build-artifact-export/v0`
- `build-artifact-report/v0`
- attachments for generated files or representative samples

This is the shareable artifact for CI, bug reports, policy review, and interop tests.

## Reference UX
A reference plugin should look something like:
- `cargo buildext explain`
- `cargo buildext validate`
- `cargo buildext run`
- `cargo buildext export`
- `cargo buildext pack`

The reference implementation should start as an **adapter** over existing Cargo surfaces, not as a demand for Cargo to stabilize everything at once.

## How it helps others
- **Cargo users:** fewer bespoke `build.rs` wrappers for common cases.
- **Security / policy tooling:** a smaller imperative surface and better evidence when imperative behavior remains.
- **Caching work:** declared inputs and outputs create a saner substrate for incremental and shared-cache decisions.
- **Build-system interop:** external tools can model build-extension behavior without scraping target-dir internals.
- **Native / FFI crates:** common probes and generated bindings get a clearer contract boundary.

## Hard problems (explicitly scoped)
1. **Do not overpromise native dependency unification**
   - v0 should help, not claim to solve every `-sys` crate and custom toolchain case.
2. **Conflict semantics must be explicit**
   - env vars, linker directives, metadata keys, and final artifact destinations all need deterministic behavior.
3. **Multiple build steps need stable ordering**
   - “alphabetical wins” is not a durable ecosystem contract.
4. **Selected-package uplift matters**
   - dependency trees cannot get implicit permission to spray final artifacts into outputs.
5. **Fallback imperative paths must remain honest**
   - the kit should report when it had to escape back into opaque `build.rs` logic.

## Overlap boundaries
- **Compile-Time Capabilities Kit** remains the place for sandbox policy, permission prompts, and capability enforcement.
- **Build Interop Kit** remains the place for discovery / graph / plan / event export.
- **Cross Toolchain Kit** remains the place for provisioning sysroots and host/target C toolchains.
- **CompileDB Kit** can consume generated native-build facts, but it is not the source-of-truth contract for declarative build extensions.

## Evaluation plan
Pilot on:
1. a crate generating shell completions or man pages,
2. a crate using metadata-driven code generation,
3. a `-sys` / FFI-adjacent crate with straightforward probe + link behavior,
4. a workspace with multiple build steps and conflicting outputs.

Success bar:
- common build-script patterns can move to structured configuration without loss of functionality,
- final artifacts can be uplifted safely without target-dir spelunking,
- policy/caching tools can reason about what happened,
- and the design reduces bespoke glue instead of inventing a second build system.

## Role in the Compile-Time Surface pilot program
This kit is the **structured replacement lane** inside [`design/compile-time-surface-pilot-program.md`](./compile-time-surface-pilot-program.md).
A strong revision should reward moving common `build.rs` patterns into declarative manifests and reports, not only policing imperative scripts more strictly. That distinction is strategic: ideal Rust should not merely sandbox arbitrary compile-time execution better; it should need less of it.

It should also compose explicitly with the profile ladder in [`design/compile-time-profile-ladder.md`](./compile-time-profile-ladder.md): many successful Build Extension migrations should graduate subjects into the `declared-no-run` profile rather than merely narrowing the permissions of imperative scripts.
