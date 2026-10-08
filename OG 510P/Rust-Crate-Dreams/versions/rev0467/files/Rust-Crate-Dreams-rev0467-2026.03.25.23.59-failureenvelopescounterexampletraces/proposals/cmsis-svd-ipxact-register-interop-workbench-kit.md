---
id: P-0403
title: CMSIS-SVD + IP-XACT Register Interop Workbench Kit — register-map locks, semantic diffs, and codegen receipts across firmware and IP flows
status: idea
domains: [embedded, hardware, eda, interoperability, codegen, validation]
last_reviewed: 2026-03-06
evidence:
  - https://arm-software.github.io/CMSIS_5/SVD/html/index.html
  - https://arm-software.github.io/CMSIS_5/SVD/html/svd_Format_pg.html
  - https://www.accellera.org/downloads/standards/ip-xact
  - https://docs.rs/svd-rs
  - https://docs.rs/svd2rust
  - https://crates.io/crates/yarig
---

# Problem

Rust embedded tooling has real momentum around CMSIS-SVD and generated PACs. Meanwhile, hardware and IP-integration flows continue to rely on IP-XACT for richer packaging, integration, and register/interface metadata. These are not the same ecosystem layer, but they overlap heavily around register maps, field definitions, address blocks, reset values, arrays, enumerations, and code-generation expectations.

The painful failures still happen at the seam between:

- **a vendor-edited SVD file and the PAC code generated from it**,
- **a richer IP-XACT register model and the narrower SVD view exported for firmware teams**,
- **register descriptions and the patches people silently apply before handing them to `svd2rust`**,
- **firmware-facing address/field semantics and RTL/integration-facing packaging metadata**,
- and **tooling stacks that can parse their own format but cannot emit an honest receipt about what information was lost, normalized, or invented.**

The missing Rust contribution is not another PAC generator. It is a **register interop workbench** for normalized register IR, semantic diffs, export/import loss accounting, and portable codegen receipts.

# What it provides

- `register-model.lock` — pins source format/version, schema revision, generator assumptions, patch overlays, and naming policy.
- `register-ir` — neutral model for devices, peripherals/blocks, registers, fields, arrays, reset values, and enum/value sets.
- `semantic-diff` — explains register-model changes in terms firmware and hardware engineers both care about.
- `loss-report` — explicit accounting of what an SVD↔IP-XACT conversion preserved, normalized, dropped, or synthesized.
- `cargo register-evidence` — emits `*.registerbundle.zip` with source docs, IR snapshots, codegen receipts, and findings.

# What the crate should provide other people

1. **A boring artifact for register-description drift**.
2. **A neutral IR** for comparing SVD, patched SVD, and IP-XACT views.
3. **Conversion loss accounting** instead of silent best-effort export.
4. **Codegen receipts** that tie generated PAC or register code back to exact source inputs.
5. **A shared language for firmware and IP teams** to debug metadata disagreements.

# Persona / who it’s for

- Embedded Rust maintainers shipping PACs and BSPs
- Silicon/IP teams exporting register metadata to firmware consumers
- Tool authors working on SVD/IP-XACT conversion or validation
- QA/release engineers reviewing generated register-access crates

# Users & user stories

- **PAC maintainer**: “Tell me exactly what changed in this updated SVD and whether it is semver-breaking for generated code.”
- **SoC integrator**: “Show me what information was lost when we exported IP-XACT down to SVD.”
- **Firmware engineer**: “Capture the patch overlay that made this vendor SVD usable by our generator.”
- **Review engineer**: “Open one bundle and see source metadata, IR diff, and generated-code receipt.”

# Prior art (and why it’s insufficient)

- CMSIS-SVD formalizes device/peripheral/register metadata and has validation/conversion guidance.
- `svd-rs` and `svd2rust` are meaningful Rust substrate.
- IP-XACT has an IEEE/Accellera standard surface and broader packaging/integration metadata.
- YARIG and related register tools prove the broader Rust interest in register generation.

What Rust still lacks is an **interop-grade coordination layer** for pinned source models, semantic diffs, loss reports, and evidence bundles that survive handoff.

# Design goals

1. **Loss-honest** — every conversion should say what was preserved and what was not.
2. **Generator-neutral** — receipts must work above `svd2rust` and future generators.
3. **Firmware/EDA bilingual** — findings should be useful on both sides of the interface.
4. **Patch-explicit** — source patches are part of the artifact, not a hidden local script.
5. **Schema-aware** — exact CMSIS-SVD and IP-XACT revisions matter.

# MVP surface

- Minimal types: `RegisterModelLock`, `RegisterIr`, `RegisterFinding`, `LossReport`, `CodegenReceipt`
- Minimal functions:
  - `load_svd()`
  - `load_ipxact()`
  - `diff_register_ir()`
  - `export_svd()`
  - `write_bundle()`
- Feature flags:
  - `svd`
  - `ipxact`
  - `codegen-receipts`
  - `patch-overlays`

# Compatibility story

- Starts as an offline workbench for source files and generated outputs.
- Works with vendor SVDs, patched SVDs, or richer IP-XACT exports.
- Keeps full IP packaging/interface metadata out of the first IR when it is not register-relevant.
- Lets future generators attach receipts without owning the core schema.

# Conformance & fixtures

- Goldens for register arrays, enumerated values, reset-value drift, field width changes, and address-block moves.
- Fixtures for common vendor-SVD cleanup patches.
- Tiny corpora showing IP-XACT constructs that cannot round-trip cleanly into SVD.
- Public examples linking one source model to generated Rust outputs.

# Path to boring stability

- Stabilize the lockfile, neutral IR, and diff/loss schemas before deeper generator integrations.
- Start with SVD as the thin but widely used firmware surface.
- Add IP-XACT import/export and loss reports next.
- Keep bus/interface/package metadata as later overlays unless directly needed for register semantics.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that load SVD and IP-XACT register descriptions, normalize them into one IR, compute semantic diffs and loss reports, and emit compact `*.registerbundle.zip` artifacts with optional codegen receipts.

# De-risk plan

1. Start with SVD loading/diffing and patch overlays.
2. Add limited IP-XACT register import focused on address maps and fields.
3. Keep generator adapters optional and thin.
4. Publish examples where conversion loss is explicit and reviewable.

# Non-goals

- Not a full EDA integration platform.
- Not a replacement for `svd2rust`.
- Not a general HDL generator.
- Not a complete IP-XACT implementation of every package/interface surface in v0.x.

# Architecture & API sketch

```rust
pub struct RegisterModelLock {
    pub source_kind: String,
    pub schema_version: String,
    pub patch_overlays: Vec<String>,
    pub generator_profile: Option<String>,
}

pub fn load_svd(path: &std::path::Path) -> Result<RegisterIr>;
pub fn load_ipxact(path: &std::path::Path) -> Result<RegisterIr>;
pub fn diff_register_ir(old: &RegisterIr, new: &RegisterIr) -> Vec<RegisterFinding>;
```

Bundle draft: `register-model.lock`, `source.svd`, `source.xml`, `register-ir.json`, `loss-report.json`, `codegen-receipt.json`, `notes.md`.

# Security / safety model

- Treat source XML as untrusted input.
- Bound resource use for large vendor metadata files.
- Preserve source hashes and patch overlays for auditability.
- Distinguish exact source values from inferred/defaulted values in all receipts.

# Maintenance & governance plan

- Keep the core about IR, diffs, loss reports, and receipts.
- Version CMSIS-SVD and IP-XACT adapters explicitly.
- Publish a small corpus of sanitized example source files.
- Resist drift into owning the whole PAC/EDA toolchain.

# Milestones

## 0.1
- `register-model.lock`
- SVD IR + semantic diff
- patch overlay support

## 0.2
- IP-XACT register import/export
- loss reports
- codegen receipts

## 1.0
- stable `*.registerbundle.zip`
- documented compatibility policy for SVD/IP-XACT revisions
- broader generator integrations

# Open questions

- What is the smallest useful neutral IR that still makes cross-format loss visible?
- How much IP-XACT packaging/interface metadata should be modeled in the core versus overlays?
- Which kinds of source patches deserve first-class structured representation?

# Sources

- CMSIS-SVD overview: https://arm-software.github.io/CMSIS_5/SVD/html/index.html
- CMSIS-SVD format docs: https://arm-software.github.io/CMSIS_5/SVD/html/svd_Format_pg.html
- Accellera IP-XACT downloads and user guide: https://www.accellera.org/downloads/standards/ip-xact
- `svd-rs`: https://docs.rs/svd-rs
- `svd2rust`: https://docs.rs/svd2rust
- `yarig`: https://crates.io/crates/yarig
