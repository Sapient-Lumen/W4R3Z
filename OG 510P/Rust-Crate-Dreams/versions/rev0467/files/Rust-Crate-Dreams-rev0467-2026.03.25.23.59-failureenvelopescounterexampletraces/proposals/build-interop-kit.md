---
id: P-0050
title: build-interop-kit — standardized build-script exports for native interop artifacts
status: idea
domains: [cargo, build-scripts, ffi, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://users.rust-lang.org/t/get-header-file-generated-with-cbindgen-from-a-dependency/117117
  - https://github.com/rust-lang/cargo/issues/7846
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://kornel.ski/rust-sys-crate
---

# Problem
Rust build scripts (`build.rs`) are frequently used to generate **headers**, **linker artifacts**, or other “native interop” outputs (cbindgen headers, generated bindings, compiled C libs). Downstream crates and external build systems often need to *find* these outputs, but Cargo’s current mechanism is mostly ad-hoc:
- `DEP_<links>_<key>` environment variables exist but are confusing and easy to misconfigure (and require `links`).  
- There is no standard way to represent “exported build artifacts” beyond linking metadata.

# Users & user stories
- FFI crate author: “My crate generates a header; I want dependents to discover it reliably.”
- Consumer with C/C++ build system: “Given a Cargo dependency, tell me the include path & library paths.”
- Workspace tooling: “I want a single query to list all exported native artifacts and how to use them.”

# Prior art (and why it’s insufficient)
- Cargo’s build-script docs explain linking directives, but do not provide a strong convention for exporting arbitrary artifacts.
- Community guidance for `*-sys` crates exists, but the artifact discovery story is scattered.
- Requests for generated headers & build-script dependency outputs keep recurring.

# Design goals
- A **standard export format** for build outputs that are intended for consumption.
- Helper APIs that make it easy for build scripts to export (and for dependents to import) these artifacts.
- Optional CLI tooling to query exports in a workspace.

# Non-goals
- Replacing `cc`, `bindgen`, or `cbindgen`.
- Designing a new build system.

# Architecture & API sketch
- Core crate: `build-interop-kit`
  - `Exporter` used in build.rs:
    - `export.include_dir(path)`
    - `export.header(path)`
    - `export.library_dir(path)`
    - `export.library(name)`
    - `export.tool("protoc", path)` etc.
  - Writes a **sidecar manifest** in `OUT_DIR`, e.g. `build-exports.json` (versioned schema).
  - Optionally also emits `cargo:KEY=VALUE` (so existing consumers can read via `DEP_*`).
- Consumer crate:
  - `Importer::for_dep("foo")` that checks (1) `DEP_*` if present, then (2) sidecar schema if discovered.
- CLI:
  - `cargo build-interop show [--json]` lists exports for workspace members and deps.
  - `cargo build-interop explain dep` describes how to consume artifacts.

# Security / safety model
- Treat paths as untrusted: canonicalize, forbid `..` traversal in emitted manifests, and avoid leaking host secrets in env vars.
- Encourage “declare outputs, not arbitrary strings.”

# Maintenance & governance plan
- Versioned schema with strict backward-compatibility rules.
- A corpus of fixtures: sys-crate, cbindgen header, multi-lib CMake project, cross-compile example.

# Milestones
- 0.1: schema v0 + Exporter/Importer + one end-to-end example (cbindgen header).
- 0.2: `cargo build-interop show` + JSON output + docs.
- 0.3: integrations with popular sys-crate patterns; “best practices” guide.

# Open questions
- Best way to locate a dependency’s `OUT_DIR` artifacts post-build without new Cargo hooks.
- How to handle multiple targets/feature sets producing different outputs.

# Sources
See front matter links.
