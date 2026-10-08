# Sanitizer Profile & Evidence Kit fixtures

This fixture family exists to keep **P-0434 Sanitizer Profile & Evidence Kit** concrete.

The core claim is that sanitizer workflows need a **reviewable evidence contract**, not just shell flags, passing CI jobs, or ad hoc suppression files.

## Core review objects

- `instrumentation-scope.receipt.json`
- `runtime-linkage.receipt.json`
- `symbolization-route.receipt.json`
- `suppression-policy.receipt.json`

## What these fixtures are trying to protect

They protect against flattening all of the following into one fake verdict:

- a requested sanitizer profile,
- partial versus full instrumentation,
- mixed Rust/C++ runtime-linkage routes,
- symbolized versus unsymbolized handoff quality,
- and suppression files with very different review debt.

## Scenario families

### `memorysanitizer_requires_fully_instrumented_std_and_deps/`
A sanitizer run can look “successful” while still carrying weak evidence if the standard library or dependencies were not instrumented.
The fixture keeps the stronger MSan requirement visible.

### `target_flag_keeps_build_scripts_and_proc_macros_off_sanitized_lane/`
A Cargo workflow can keep host build helpers off the sanitizer lane on purpose.
The fixture makes that scope split explicit instead of pretending everything in the build graph was instrumented.

### `mixed_rust_cpp_sanitized_build_needs_external_clangrt_route/`
A mixed-language run can succeed only because runtime linkage was deliberately routed outside Rust’s default compiler runtime.
The fixture keeps that route honest and reviewable.

### `llvm_symbolizer_missing_turns_report_into_partial_handoff/`
A report with raw PCs is still a report, but it is a worse handoff artifact.
The fixture keeps local symbolizer availability separate from the underlying sanitizer finding.

### `suppressions_must_stay_visible_and_reasoned/`
A suppression file can be careful operational debt or silent evidence laundering.
The fixture keeps ownership, reason, and review date visible.
