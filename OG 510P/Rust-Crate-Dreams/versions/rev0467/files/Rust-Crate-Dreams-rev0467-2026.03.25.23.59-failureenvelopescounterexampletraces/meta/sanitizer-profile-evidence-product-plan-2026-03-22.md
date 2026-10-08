# Sanitizer Profile & Evidence Kit — product plan (2026-03-22)

This note sharpens **P-0434 Sanitizer Profile & Evidence Kit** into an implementation-ready `0.1` shape.

## Main judgment

A worthwhile `0.1` should **not** try to become a universal security framework, another shell-script wrapper around `RUSTFLAGS`, or a promise that every sanitizer/target combination is turnkey.

It should be a **small crate family plus CLI** that helps maintainers publish one reviewable answer to:

- what was actually instrumented,
- what runtime-linkage route was used,
- whether symbolization was good enough for handoff,
- and which suppressions are active, justified, or still debt.

The missing value is the **boring workflow-and-evidence layer** above today’s unstable-book pages, custom CI YAML, mixed-language linker lore, and one-off symbolizer setup.

## What the crate should provide other people

For maintainers, CI owners, security engineers, debugging specialists, and safety-critical teams, the crate should provide:

1. **One instrumentation-scope receipt** instead of guessing from `RUSTFLAGS` and job names.
2. **One runtime-linkage answer** instead of reverse-engineering which sanitizer runtime actually supplied symbols.
3. **One symbolization-route receipt** instead of “the stack looked readable on my machine.”
4. **One suppression-policy receipt** instead of opaque ignore files that silently launder evidence.
5. **One compact sanitizer bundle** that another team can review without rerunning the world.

## Four first-class review objects

### 1. Instrumentation scope receipt

Named classes for `0.1` should focus on what the run actually touched:

- `workspace_targets_instrumented`
- `dependencies_partially_instrumented`
- `instrumented_std_required`
- `instrumented_std_recommended`
- `host_helpers_excluded`
- `manual_review_required`

This object should answer:

- whether the main target crates were instrumented,
- whether `std` was rebuilt and instrumented,
- whether dependencies were fully, partially, or not instrumented,
- whether build scripts and procedural macros were intentionally kept off the sanitizer lane,
- and whether the run should be treated as advisory-only because coverage was partial.

### 2. Runtime-linkage receipt

Named classes for `0.1` should focus on which runtime lane actually carried the run:

- `rust_default_compiler_runtime`
- `external_clangrt_required`
- `mixed_language_runtime_route`
- `linkage_conflict_possible`
- `manual_review_required`

This object should answer:

- whether Rust’s default compiler runtime was used,
- whether `external-clangrt` or another external route was needed,
- whether C/C++ or other instrumented code shared the sanitizer runtime,
- and whether linkage caveats still block strong interpretation.

### 3. Symbolization-route receipt

Named classes for `0.1` should focus on handoff quality:

- `local_symbolizer_in_path`
- `symbolized_stacktrace`
- `partial_symbolization`
- `raw_pc_only`
- `symbolization_manual_review_required`

This object should answer:

- whether `llvm-symbolizer` was present,
- whether reports were symbolized at capture time,
- whether symbolization depended on local-only paths or tools,
- and whether the exported report is usable for another engineer without reconstruction.

### 4. Suppression-policy receipt

Named classes for `0.1` should focus on explicit debt and review posture:

- `no_suppressions`
- `suppression_set_declared`
- `temporary_suppression_with_owner`
- `third_party_suppression_imported`
- `stale_or_unowned_suppression`
- `manual_review_required`

This object should answer:

- which suppressions were active,
- why each suppression exists,
- which owner or review date applies,
- whether the suppression hides a target/toolchain/platform limitation,
- and whether the run should remain advisory because suppression debt is too large.

## Recommended `0.1` command surface

### `cargo sanitize-evidence capture`
Capture maintainer-authored policy and observed run facts and emit:
- `sanitizer.receipt.json`
- `sanitizer.caveats.json`
- `instrumentation-scope.receipt.json`
- `runtime-linkage.receipt.json`
- `symbolization-route.receipt.json`
- `suppression-policy.receipt.json`

### `cargo sanitize-evidence check`
Run conservative consistency checks and emit:
- `sanitizer-check.report.json`

### `cargo sanitize-evidence diff`
Compare two sanitizer bundles and emit:
- `sanitizer-drift.diff.json`

### `cargo sanitize-evidence summary`
Render a compact human review note from the structured artifacts.

### `cargo sanitize-evidence bundle`
Produce one compact `.sanitizerbundle.zip` containing reports, logs, raw traces, and selected receipts.

## Recommended crate/workspace split

- `sanitize_evidence_model`
- `sanitize_evidence_capture`
- `sanitize_evidence_linkage`
- `sanitize_evidence_symbolize`
- `sanitize_evidence_check`
- `cargo-sanitize-evidence`

## `0.1` artifact set

Core artifacts should be:

- `sanitizer-profile.toml`
- `sanitizer.receipt.json`
- `sanitizer.caveats.json`
- `instrumentation-scope.receipt.json`
- `runtime-linkage.receipt.json`
- `symbolization-route.receipt.json`
- `suppression-policy.receipt.json`
- `sanitizer-check.report.json`
- `sanitizer-notes.summary.md`

## Discovery order

1. **Import requested sanitizer policy**
   - sanitizer kind
   - target triple
   - required/recommended `build-std`
   - environment variable posture
2. **Normalize instrumentation scope**
   - workspace target crates
   - dependencies
   - rebuilt `std`
   - host build helpers and proc macros
3. **Normalize runtime linkage**
   - default Rust runtime
   - external compiler runtime
   - mixed-language route
4. **Normalize symbolization**
   - `llvm-symbolizer` presence
   - symbolized vs raw reports
   - path / tool portability
5. **Normalize suppression policy**
   - active suppressions
   - reason, owner, review date
   - imported third-party suppressions
6. **Check consistency**
   - “clean run” vs partial instrumentation
   - mixed-language linkage without explicit route
   - unsymbolized reports treated as production-ready evidence
   - stale/unowned suppressions
7. **Bundle export**
   - receipts
   - raw logs
   - reports
   - notes

## Ranking discipline

A good `0.1` should not treat “the sanitizer job passed” as the verdict.
It should keep separate:

- `requested_policy_known`
- `instrumentation_scope_known`
- `runtime_linkage_known`
- `symbolization_route_known`
- `suppression_policy_known`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten

- sanitizer unstable-book guidance about `--target`, `build-std`, partial instrumentation, and symbolization
- Cargo `-Z build-std` requirements
- project-goal progress on sanitizer stabilization and instrumented standard libraries
- mixed-language runtime-routing facts like `external-clangrt`
- CI job configuration and repro commands

### Do not flatten into one fake verdict

- “`-Zsanitizer` flag was present”
- “job passed”
- “stack trace exists”
- “used `-Zbuild-std`”
- “the project has a suppression file”
- “C++ was also instrumented”

## Preferred proving grounds

- a MemorySanitizer run that needs fully instrumented `std` and dependencies
- a Cargo workflow where `--target` keeps build scripts and proc macros off the sanitizer lane
- a mixed Rust/C++ build that needs explicit external runtime linkage
- a report with raw addresses because `llvm-symbolizer` was absent
- a suppression set with owners and review dates versus one with stale inherited entries

## Non-goals

- not a replacement for rustc sanitizer support
- not a guarantee that all sanitizer/target pairs work
- not a full verification or certification framework
- not a debugger feature matrix
- not a replacement for the broader toolchain/target support lane

## MVP API sketch

```rust
pub fn capture_instrumentation_scope(input: &SanitizerRunInput) -> Result<InstrumentationScopeReceipt>;
pub fn capture_runtime_linkage(input: &SanitizerRunInput) -> Result<RuntimeLinkageReceipt>;
pub fn capture_symbolization_route(input: &SanitizerRunInput) -> Result<SymbolizationRouteReceipt>;
pub fn capture_suppression_policy(input: &SanitizerRunInput) -> Result<SuppressionPolicyReceipt>;
pub fn check_sanitizer_bundle(bundle: &SanitizerBundle) -> Result<SanitizerCheckReport>;
pub fn write_bundle(bundle: &SanitizerBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Preserve `manual_review_required` as an honest output.
- Keep requested profile, observed scope, and interpretation clearly separate.
- Prefer small, versioned receipts over giant unstructured logs.
