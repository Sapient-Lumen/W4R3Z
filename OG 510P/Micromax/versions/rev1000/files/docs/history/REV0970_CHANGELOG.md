# Revision 0970 changelog

## Product

- Moved every caller-authored editor regex compile and scan out of the editor thread; literal search remains local.
- Reused one exact worker-routed search snapshot across navigation, status, and highlight for the same buffer generation and execution policy.
- Preserved the prior search register, provenance, cursor, and replay truth when a candidate is invalid, over budget, timed out, or suffers worker/protocol failure.
- Restored the historical TUI/highlight helper's non-throwing invalid-regex contract without hiding errors from command/navigation surfaces.
- Planned query-replace captures and concrete replacement text once against immutable witnessed source; later responses never rematch mutated text.
- Fixed ignore-case literal replacement offsets by matching the original Unicode source.

## Runtime and VM

- Added `micromax.regex_runtime` as the one-shot process/protocol owner and a stdlib-only `python -I -S` child.
- Gave startup readiness and request/match execution separate finite deadlines.
- Kept pattern compilation in the child, including stable classification of CPython parser `RecursionError` for deeply nested patterns.
- Routed every finite positive-timeout VM regex operation through containment; the risky-shape classifier is no longer a safety decision.
- Normalized non-finite timeout configuration to the safe default; only an explicit finite nonpositive timeout selects the local embedding escape hatch.
- Enforced match/result/template ceilings during child materialization and accepted only a complete valid response captured by the deadline.
- Centralized multiprocessing terminate/join/kill policy shared with editor filesystem workers.

## Audit and evidence

- Strengthened `mxaudit.regex_hostcall_timeout_worker` to require child-owned parser-recursion handling and editor/VM/deep-pattern regressions.
- Added deterministic tests for catastrophic timeout, deep compile recursion, delayed readiness, startup timeout, slow teardown, incremental budgets, failed-search preservation, Unicode coordinates, one-pass query-replace, and compatibility-helper fail-closed behavior.
- Added primary-source research and residual-risk analysis in `docs/926-regex-fastchild-search-replace-containment.md`.
