# Rev0901 — structured model dimension budget

Date: 2026-07-07

## Executive finding

Rev0898 made returned hostcall payloads VM-visible and budgeted, but that was
only a post-call boundary.  Several editor model hostcalls still accepted
script-controlled `lines`, `cols`, or `width` arguments and then walked editor
state or allocated visible row payloads before the shared hostcall-result budget
could inspect the result.  That is the wrong order for a least-authority host:
observational helpers still need input budgets when their arguments control how
much host-owned state is traversed.

Rev0901 adds a concrete preflight boundary for the highest-risk structured model
lane instead of creating another registry.  Screen/docs/help/prompt model
hostcalls now reject oversized dimensions before their builders run and before
direct operands are consumed, so a script can no longer ask `ed.screen-rows`,
`ed.display-rows`, `ed.docs-cues`, `ed.prompt-display`, or related helpers to
construct arbitrarily large visible-row snapshots as the first line of defense.

## What changed

- `src/micromax_editor/hostcall_boundary.py` now owns conservative editor model
  input budgets:
  - `DEFAULT_EDITOR_MODEL_MAX_LINES = 1000`
  - `DEFAULT_EDITOR_MODEL_MAX_COLS = 1000`
  - `DEFAULT_EDITOR_MODEL_MAX_CELLS = 262_144`
  - `DEFAULT_EDITOR_MODEL_MAX_WIDTH = 4096`
- `install_editor_hostcalls()` installs VM-tunable defaults named
  `editor_hostcall_model_max_lines`, `editor_hostcall_model_max_cols`,
  `editor_hostcall_model_max_cells`, and `editor_hostcall_model_max_width`.
  Embeddings can raise, lower, or disable them by setting non-positive limits.
- Screen-shaped hostcalls now use `pop_model_dimensions_arg()` for `(lines cols)`:
  `ed.prompt-panel`, `ed.screen-layout`, `ed.gutter-model`, `ed.edit-window`,
  `ed.search-rows`, `ed.showchars-rows`, `ed.display-rows`, `ed.docs-cues`,
  `ed.viewport-cues`, `ed.viewport-rows`, `ed.screen-model`, `ed.screen-rows`,
  and `ed.prompt-display`.
- Width/line-only model hostcalls now use `pop_model_width_arg()` or
  `pop_model_lines_arg()`: `ed.statusline-text`, `ed.statusline-model`,
  `ed.interaction-model`, `ed.keymenu-model`, `ed.infobar-model`,
  `ed.bottom-rows`, and `ed.prompt-window`.
- The checks preserve existing harmless negative-size behavior by treating
  negative dimensions as zero for budget purposes.  Huge positive values fail
  with a named boundary error before traversal.
- `tools/mxaudit.py` now reports and checks `editor_model_dimension_budget`, so
  this seam stays executable evidence.

## Online research implications

OWASP API4:2023 frames unrestricted resource consumption as a first-class API
risk and explicitly calls out validating request/body parameters that control
how many records are returned.  That maps directly to Micromax's model hostcalls:
`lines`, `cols`, and `width` are local API parameters that control how many rows,
spans, and strings are produced.

VS Code's Workspace Trust extension guide says the feature is driven by risks
from unintended code execution when a workspace is opened.  The lesson for
Micromax is not to clone Workspace Trust; Micromax already has restricted
startup and capability features.  The lesson is that host-exposed automation
surfaces must assume workspace/script-controlled inputs and put limits before
work starts, even for read-only helpers.

Python's current regex-timeout discussion, reviewed in rev0900, reinforces the
same design rule from a different angle: post-hoc observation is not enough once
a host helper has already entered an expensive operation.  Bound inputs, then
route dangerous work through a cancellable lane, then apply output budgets.

Research sources reviewed in this pass:

- OWASP API Security Top 10 2023, API4:2023 Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OWASP Input Validation Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- Visual Studio Code Workspace Trust Extension Guide: https://code.visualstudio.com/api/extension-guides/workspace-trust
- Visual Studio Code Workspace Trust user documentation: https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- Python.org discussion, "Add an opt-in timeout parameter to re to mitigate catastrophic backtracking": https://discuss.python.org/t/add-an-opt-in-timeout-parameter-to-re-to-mitigate-catastrophic-backtracking/107766

## Audit/refactor note

This is a narrow refactor of the bridge's model-argument plumbing.  The old path
used generic integer readers for screen and prompt dimensions.  That preserved
bad type evidence, but it did not distinguish ordinary integer operands from
integer operands that control host-state traversal.  The new helpers keep the
same stack-preservation style while moving the resource policy into
`hostcall_boundary.py`, where future effect-hostcall preflight helpers already
belong.  The bridge now imports the dimension-budget defaults from that module
instead of duplicating literals, and the nearby integer pop helper lost a
redundant type preflight while keeping the same error semantics.

The patch deliberately avoids a broad hostcall registry or per-model metadata
matrix.  The tests prove the important behavior: oversized dimensions preserve
operands and skip the builder entirely.

## Limits and residual risk

This does not make all editor observation cheap.  A permitted `1000 x 200` call
can still produce a large result and will still rely on the shared hostcall
result budget after the builder returns.  The new `screen area` limit exists to
keep common terminal-sized requests usable while stopping obviously runaway
matrix-shaped requests before traversal.

The remaining high-risk lanes are not new registries; they are concrete resource
or lifecycle boundaries:

1. `ed.fs-read` needed a pre-read byte budget so scripts could not ask the host
   to load arbitrarily large files before the result budget runs; rev0902 closes
   that lane in `docs/860-fs-read-preflight-budget.md`.
2. Prompt/docs/query row families that take free-text queries need input length
   budgets for query strings, not just returned-row budgets.
3. A complete full-release run remains separate from the focused cloudtainer
   evidence in this revision.

## Evidence

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py` → 49 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxaudit.py` → 2 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_editor_screen_layout.py tests/test_tui_prompt_display_items.py tests/test_mxaudit.py` → 104 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 9 passed.
- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxaudit.py --check` → passed with `model-dim-budget=True`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → passed for rev0901.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context/audit/lint/portable passed.
