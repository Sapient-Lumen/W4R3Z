# Debuggability-support capability-witness plan — 2026-03-22

This note deepens **P-0486 Debuggability Support Contract Kit** around one product question:

> how should a support-oriented crate tell another engineer which debugger capabilities were actually demonstrated for a specific build, without overclaiming from one debugger lane or one artifact-rich session?

## Product stance

The crate should stay **reviewer-facing, conservative, and task-oriented**.
It should not try to orchestrate a debugger end to end.
Its job is to preserve evidence that another human can review later.

## New first-class artifacts

### `session-scope.receipt.json`

Records the checked subject and route:
- subject kind (`live_local_process`, `remote_target`, `post_mortem_core`, `post_mortem_minidump`, ...)
- host / target OS and target triple
- debugger family / frontend / backend version
- launch route (`launch`, `attach`, `open_dump`, `remote_stub`, `manual_review_required`)
- artifact basis (`native_binary`, `copied_binary`, `packaged_bundle`, `dump_only`)
- confidence (`observed`, `imported`, `mixed`, `manual_review_required`)

This keeps “debugging happened somewhere” separate from “this was a live local interactive lane”.

### `capability-witness.report.json`

Records concrete debugger tasks with per-task evidence.

For each task record:
- `capability_key`
- `verdict` (`observed_working`, `observed_partial`, `blocked_by_debugger_policy`, `blocked_by_missing_artifact`, `unwitnessed`, `manual_review_required`)
- `evidence_kind` (`interactive_session`, `scripted_session`, `imported_log`, `artifact_inference_only`, `manual_review_required`)
- `scope_dependency` (`session_scope`, `backend_family`, `target_os`, `artifact_layout`, ...)
- optional blocker or limitation note

This keeps “locals displayed once” separate from “Rust expressions evaluated” or “async tasks were inspectable”.

### `claim-ceiling.report.json`

Summarizes the strongest honest outward-facing claim after the task matrix is considered.

Useful fields:
- `portable_claim_ceiling`
- `checked_lane_summary`
- `unchecked_lane_summary`
- `overclaim_risks`
- `receiver_message`

This keeps “one LLDB/Linux session worked” separate from “debugging is fine on macOS or Windows/PDB too”.

## CLI / workflow refinement

### `capture`
Should allow importing or recording a session scope plus one or more capability witnesses.

### `doctor`
Should warn on situations such as:
- `post_mortem_scope_is_not_live_debug_claim`
- `pretty_render_without_expression_eval_claim`
- `single_linux_lane_does_not_settle_other_os_claims`
- `gdb_visualizer_asset_present_but_autoload_unwitnessed`
- `async_claim_without_async_task_evidence`

### `pack`
Should ensure portable bundles can include task evidence and claim ceilings without flattening them into the broad support-posture summary.

## Receiver-facing value

### For support engineers
They can tell whether a bug report came from live interactive debugging, a core dump, or a mixed imported lane.

### For release engineers
They can avoid overstating what a release build supports when only one narrow debugger lane was checked.

### For downstream integrators
They can decide whether a checked lane is relevant to their OS, debugger, and workflow.

## Good first scenario families

1. **Core dump / minidump symbolication is not evidence of live stepping or expression evaluation.**
2. **Locals, backtrace, and pretty rendering worked, but Rust expression evaluation remained unwitnessed.**
3. **One LLDB/Linux witness does not settle macOS or Windows/PDB claims.**
4. **A portable debug-support bundle must keep posture, session scope, task witnesses, and claim ceilings separate.**

## Sources

- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rustc-dev-guide.rust-lang.org/debugging-support-in-rustc.html
- https://doc.rust-lang.org/reference/attributes/debugger.html
- https://rustc-dev-guide.rust-lang.org/tests/directives.html
- https://rustc-dev-guide.rust-lang.org/debuginfo/lldb-internals.html
