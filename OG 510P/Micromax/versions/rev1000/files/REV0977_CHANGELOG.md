# Rev0977 changelog — bounded browser launch and deadline repair

## Open URL

- Replaced the product-default in-process `webbrowser.open()` call with one
  isolated `python -I -S` child.
- Added a six-second launch deadline, 16 KiB combined diagnostic ceiling,
  process-group teardown, and stable boolean failure.
- Kept URL validation, `cap.open-url`, and explicit test/embedder opener
  overrides unchanged.
- Detached browser stdout/stderr from parent capture pipes during launch so a
  successful background browser cannot retain reader threads.
- Kept controller registration itself inside the same child and added a real
  blocking-`xdg-settings` timeout/teardown regression.
- Added child-result, parent-argv, non-finite-deadline, default-editor,
  background-descriptor, and real hostcall timeout/liveness tests.

## Process and worker refactor

- Extracted one shared started-process capture loop for argv and shell commands.
- Added finite timeout/output-limit normalization to subprocess helpers.
- Added one shared multiprocessing timeout normalizer and reused common
  terminate/join/kill cleanup in filesystem, save, and plugin workers.
- Applied finite normalization to direct filesystem/save/plugin worker APIs and
  hostcall-derived filesystem/save/shell settings.
- Rejected malformed/boolean/non-finite hostcall deadlines and non-finite
  external clipboard deadlines while preserving existing
  finite non-positive/`None` direct-mode contracts.

## Contracts and documentation

- Added `ed.open-url` to the generated high-risk effect/resource contract.
- Added structural audit flags for the browser process boundary and finite worker
  deadline seam.
- Added `docs/934-open-url-process-finite-deadlines.md` with official Python
  research, measured failure, implementation, evidence, and residual risks.
- Updated the mission, security contract, roadmap, decisions, repo map, research,
  worklist, README, TODO, revision index, and current context.
