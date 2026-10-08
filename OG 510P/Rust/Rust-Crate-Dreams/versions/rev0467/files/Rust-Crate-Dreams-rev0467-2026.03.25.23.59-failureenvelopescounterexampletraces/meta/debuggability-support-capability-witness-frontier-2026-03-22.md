# Debuggability-support frontier — session scope, capability witnesses, and claim ceilings (2026-03-22)

This note sharpens **P-0486 Debuggability Support Contract Kit** around the next seam that still matters after symbol sidecars, visualizer assets, backend coverage, and source materials are already explicit.

## The sharper question

The remaining support question is no longer only:

> “Does this build look debuggable?”

It is now:

> “Which debugger tasks were actually witnessed, in what session scope, and what honest claim ceiling survives from that evidence?”

That matters because current official Rust debugging material is very explicit that support varies by debugger family, OS, version, and advanced capability class. A build can have symbols, a visualizer, and one successful session while still lacking portable evidence for Rust expression evaluation, async debugging, remote targets, post-mortem work, or alternate backend families.

## What should now count as first-class review objects

### `session-scope.receipt.json`
A compact receipt for the scope of the checked subject:
- `live_local_process`
- `remote_target`
- `containerized_local_process`
- `post_mortem_core`
- `post_mortem_minidump`
- `attached_existing_process`
- `manual_review_required`

The receipt should record host OS, target OS/triple, debugger family/version, launch or attach route, and which parts were observed versus imported.

### `capability-witness.report.json`
A task-level matrix of what the debugger user could actually do.

Good first capability keys:
- `symbol_load`
- `breakpoint_hit`
- `step_over`
- `step_into`
- `backtrace`
- `locals_expand`
- `pretty_render`
- `source_lookup`
- `rust_expression_eval`
- `async_task_inspection`
- `post_mortem_stack_walk`

Each row should keep verdict, evidence kind, notes, and blockers explicit.

### `claim-ceiling.report.json`
A small report that says what the strongest **receiver-facing** claim is after considering session scope and witnessed tasks.

Examples:
- `basic_live_debugging_only`
- `post_mortem_symbolication_only`
- `visualizer_supported_but_expression_eval_unwitnessed`
- `linux_lldb_lane_only`
- `windows_pdb_lane_unchecked`
- `manual_review_required`

## Boundary reminder

Do not let this seam get flattened into:
- broad support posture alone,
- backend-family coverage alone,
- visualizer conformance,
- source-path hygiene,
- or debugger UX wishlists.

The missing value here is the **reviewable task-evidence layer** above those components.

## Sources

- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rustc-dev-guide.rust-lang.org/debugging-support-in-rustc.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://rustc-dev-guide.rust-lang.org/tests/directives.html
- https://rustc-dev-guide.rust-lang.org/debuginfo/lldb-internals.html
