# Rev0905 source-load and eval budget

Rev0905 closes the executable-load half of the resource-boundary work that
followed the hostcall result, regex, model, file-read, query, and scan-row
budgets.  The target is deliberately narrow: `ed.require` and script-context
core `include` / `require` / `reload` now have VM-tunable source-size and nested
evaluation-step limits.

## Why this mattered

The prior filesystem work bounded observation: `ed.fs-read` cannot read an
oversized text payload, and broad picker/list hostcalls stop scanning before
materializing unbounded candidate lists.  `ed.require` is riskier than those
surfaces because it turns a file into executable VM authority.  A small path
argument could previously read a very large Micromax source file before any
post-call result budget fired, and a small source file could still spend an
unbounded number of VM steps during load.

Online research reinforced this as the right next cut rather than another
registry pass:

- OWASP API4:2023 Unrestricted Resource Consumption —
  https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- MITRE CWE-400 Uncontrolled Resource Consumption —
  https://cwe.mitre.org/data/definitions/400.html
- MITRE CWE-834 Excessive Iteration —
  https://cwe.mitre.org/data/definitions/834.html
- VS Code Workspace Trust —
  https://code.visualstudio.com/docs/editing/workspaces/workspace-trust
- WASI filesystem capability/preopen guidance —
  https://github.com/WebAssembly/wasi-filesystem

The useful product lesson is the same across these sources: editor-hosted code
loading is not “just file I/O.”  It is an execution boundary and needs explicit
resource ceilings in addition to capability/root checks.

## What changed

- `hostcall_boundary.py` now owns `DEFAULT_SOURCE_LOAD_MAX_BYTES`,
  `DEFAULT_SOURCE_EVAL_STEP_BUDGET`, `effective_source_load_max_bytes()`, and
  `effective_source_eval_step_budget()`.
- `install_editor_hostcalls()` installs those defaults as
  `editor_source_load_max_bytes` and `editor_source_eval_step_budget` on the VM.
- `ed.require` peeks its path operand, checks capability/root policy, reads the
  source through `read_file_for_editor(..., max_bytes=...)`, and preserves the
  direct operand if the executable-load boundary rejects the file before eval.
- `ed.require` evaluates the loaded source with `VM.eval(..., step_budget=...)`.
- Script-context core `include`, `require`, and `reload` use the same file-size
  cap through `vm_load_policy.read_policy()`.
- Core loader words now honor `editor_source_eval_step_budget` when evaluating a
  loaded source, so nested plugin-private includes get the same step ceiling.
- `read_file_for_editor()` accepts `max_bytes` without changing ordinary editor
  buffer reads that do not pass the argument.
- `mxaudit --check` hard-checks the new source-load/eval-budget seam.

## Audit/refactor note

This pass intentionally avoids creating a source-loader registry.  The existing
policy split remains intact:

- `vm_load_policy.py` owns editor script-context load policy and plugin-private
  load-root exceptions.
- `file_recovery.py` owns editor text-file decoding and newline normalization.
- `hostcall_boundary.py` owns embedding-visible resource dials.
- `core.py` owns the shared loader words and now consults one VM attribute for
  nested eval budgets.

The refactor keeps ordinary buffer reads separate from executable source loads,
so embedders can allow larger observation than execution.

## Evidence

Focused evidence for rev0905:

```bash
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_require_caps.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_require_caps.py tests/test_plugin_containment_and_caps.py tests/test_editor_plugin_manual_load_grants.py tests/test_mxaudit.py
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxlint.py
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxaudit.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxcontext.py --check
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxportable.py --quiet
PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json
```

The focused suite covers:

- oversized `ed.require` source files preserving the path operand and avoiding
  evaluation;
- `ed.require` nested evaluation hitting the step budget before executing the
  final hostcall;
- script-context core `include` using the source-load byte cap;
- script-context core `require` using the nested eval step budget and rolling
  back `loaded_paths` after budget failure;
- plugin-private load/root behavior still passing under the new defaults;
- audit output and hard-check coverage for `source_load_eval_budget`.

## Remaining risk

The source-load step budget is an instruction-count guard, not wall-clock
cancellation.  Hostcalls invoked from loaded source still rely on their own
hostcall boundaries.  Source include depth and cumulative multi-file load bytes
are still separate follow-ups; this landing caps each loaded file and each nested
evaluation, not a whole dependency graph.
