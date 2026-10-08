# Debuggability-support capability stack plan — 2026-03-23

This note deepens **P-0486 Debuggability Support Contract Kit** around the next missing implementation layer:
**a capability stack**.

The archive already had good material for:

- support posture,
- artifact completeness,
- backend coverage,
- capability witnesses,
- session-scope boundaries,
- source-lookup impact,
- and artifact handoff.

What it still lacked was one practical answer to:

> What exact capabilities should a real debug-support crate classify, and how should it keep those capabilities from collapsing into one fake “debuggable” label?

## Main judgment

A credible `0.1` for **P-0486** should classify debug support as a **stack of distinct capabilities**, not a single score.

At minimum, that stack should separate:

1. symbol/material presence,
2. source lookup confidence,
3. launch / attach / step / breakpoint support,
4. local variable / expression-evaluation support,
5. async/task-aware inspection support,
6. pretty-printer / visualizer support,
7. post-mortem symbolication support,
8. remote/container/embedded session-family support.

That model is wide enough to matter to many Rust users while still staying reviewable.

## Why this matters now

### 1. Debugging is broad, not binary
The latest official survey work says debugger support is still inconsistent across debuggers, operating systems, async code, expression evaluation, and visualizers.
That makes a one-word “debugging works” claim too blurry to trust.

### 2. Cargo/rustc already provide important substrate, but not the receiver-facing contract
Profile settings, split debuginfo modes, strip modes, debugger visualizers, and sidecar formats already exist.
The missing crate is the receiver-facing layer that says which user-facing capabilities that substrate actually buys.

### 3. Different Rust worlds need different session families
A local CLI launch, a container attach, a post-mortem core/minidump inspection, and an embedded remote-target session are not the same support story.
The crate needs to say which one was actually checked.

## Proposed capability stack

### Layer 1 — `artifact_materials`
Question:
- Are the relevant symbols, sidecars, and visualizer assets present and retained?

Core outputs:
- `debuggability.receipt.json`
- `symbol-layout.manifest.json`
- `visualizer.manifest.json`
- `artifact-handoff.manifest.json`

What it should provide other people:
- one durable answer about whether the shipped/debugged artifact still has the required materials.

### Layer 2 — `source_lookup`
Question:
- Does the debugger have a plausible path to the expected sources?

Core outputs:
- `source-lookup-impact.report.json`
- optional `source-materials.receipt.json`

What it should provide other people:
- one conservative answer about remap/trim-path and source-component effects,
- without pretending source lookup equals interactive debugging.

### Layer 3 — `interactive_control`
Question:
- Was launch/attach/step/breakpoint control demonstrated for this session family?

Core outputs:
- `session-family.report.json`
- `capability-witness.report.json`

What it should provide other people:
- one concrete record of whether the subject could be launched, attached, stepped, and stopped in the intended session shape.

### Layer 4 — `inspection_and_eval`
Question:
- Could variables, frames, and expressions actually be inspected with useful fidelity?

Core outputs:
- `inspection-eval.report.json`

What it should provide other people:
- one honest answer about “backtrace only” versus “interactive variable inspection” versus “expression evaluation worked”.

### Layer 5 — `async_visibility`
Question:
- Could async stacks, tasks, wake/scheduler state, or async-relevant frames be inspected meaningfully?

Core outputs:
- `async-debug-coverage.report.json`

What it should provide other people:
- one explicit answer about whether async debugging is merely nominal, partially visible, or meaningfully supported.

### Layer 6 — `visualizer_help`
Question:
- Were NatVis/GDB-script/pretty-printer surfaces actually relevant and exercised?

Core outputs:
- `visualizer-activation.report.json`
- `visualizer-family-coverage.report.json` or imported adjacent receipts

What it should provide other people:
- one record of whether custom presentation actually worked and for which debugger family.

### Layer 7 — `postmortem_support`
Question:
- Is the build usable for core/minidump analysis and symbolication after the fact?

Core outputs:
- `postmortem-support.report.json`

What it should provide other people:
- one answer about crash-analysis posture that does **not** overclaim interactive debugging.

### Layer 8 — `remote_or_packaged_support`
Question:
- Does the support story survive relocation into CI artifacts, customer bundles, remote targets, containers, or embedded probes?

Core outputs:
- `packaged-debug-bundle.manifest.json`
- `support-claim-ceiling.report.json`

What it should provide other people:
- one honest answer about whether local developer success survives handoff.

## Proposed first-class artifacts

### `capability-stack.policy.json`
Purpose: declare which capability classes exist and what minimum evidence each class needs.

Suggested fields:
- `capability_classes`
- `required_evidence`
- `weaker_fallbacks`
- `manual_review_triggers`

### `session-family.report.json`
Purpose: record the debug subject shape.

Suggested values:
- `local_launch`
- `local_attach`
- `container_attach`
- `remote_target`
- `embedded_probe`
- `core_dump`
- `minidump`
- `packaged_bundle`
- `manual_review_required`

### `inspection-eval.report.json`
Purpose: keep raw symbol presence separate from usable inspection/evaluation.

Suggested fields:
- `frame_visibility`
- `locals_visibility`
- `pretty_printing`
- `expression_evaluation`
- `limitations`
- `manual_review_required`

### `async-debug-coverage.report.json`
Purpose: record async-specific support without pretending that a synchronous debugging success generalizes.

Suggested fields:
- `runtime_family`
- `task_visibility`
- `async_backtrace_quality`
- `scheduler_state_visibility`
- `limitations`
- `manual_review_required`

### `postmortem-support.report.json`
Purpose: classify crash-analysis support separately from live interactive support.

### `packaged-debug-bundle.manifest.json`
Purpose: show what materials and notes are preserved for somebody else after the original build machine is gone.

## Suggested commands

- `cargo debug-support survey`
- `cargo debug-support check`
- `cargo debug-support witness --session local_launch`
- `cargo debug-support bundle`
- `cargo debug-support diff old/ new/`

## Distinctions the implementation must keep explicit

### Symbols present is not interactive debugging
A build can be useful for symbolication or backtraces while still being poor for live inspection.

### Interactive stepping is not async visibility
A debugger may step through code while still giving poor async task insight.

### Visualizers working is not expression evaluation working
These are separate supports and should stay separate.

### Local success is not packaged success
A local session can work while shipped or archived artifacts lose the necessary sidecars or source path context.

### Post-mortem support is not launch/attach support
A useful core/minidump workflow deserves its own class rather than a weaker “failed interactive” label.

### Backend family is not session family
LLDB/GDB/WinDbg/CDB choice is one dimension; local/remote/post-mortem/container/embedded subject shape is another.

## Good proving grounds

1. a local CLI build with good symbols but only backtrace-level support,
2. a release bundle that preserved post-mortem symbolication but not rich local inspection,
3. an async service where ordinary stepping works but task visibility is partial,
4. a debugger-visualizer case where pretty-printing works but expression evaluation is weak,
5. a remote/container/embedded case where session-family support differs sharply from local launch.

## Sources
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://doc.rust-lang.org/cargo/reference/profiles.html
- https://doc.rust-lang.org/rustc/codegen-options/index.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- https://docs.rs/about/builds
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
