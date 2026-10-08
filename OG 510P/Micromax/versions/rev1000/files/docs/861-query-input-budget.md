# Rev0903 — free-text query input budget

Date: 2026-07-07

## Executive finding

Rev0898 through rev0902 closed several resource boundaries after host work had
already become visible: hostcall results, regex input, risky regex wall-clock,
structured model dimensions, and `ed.fs-read` byte loading.  The next riskiest
unfinished lane was smaller but widespread: query-shaped editor hostcalls still
accepted arbitrarily large free-text strings before scanning docs, help links,
prompt rows, buffers, marks, plugins, recent files, bindings, jumps, options,
and command/action palettes.

Rev0903 makes free-text query size a first-class VM-to-editor hostcall boundary.
Query-bearing observational hostcalls now preflight a VM-tunable UTF-8 byte
budget before broad scans or prompt state changes.  Oversized query calls fail
with the original operand still on the VM stack, and the row/prompt builder is
not called.

This is deliberately not a registry expansion.  It is one shared helper in the
existing hostcall boundary layer, then direct use at the scan edges.

## What changed

- `src/micromax_editor/hostcall_boundary.py` now owns
  `DEFAULT_EDITOR_QUERY_MAX_BYTES = 4096`, `require_editor_query_budget()`,
  `peek_query_arg()`, and `pop_query_arg()`.
- `install_editor_hostcalls()` initializes the VM attribute
  `editor_hostcall_query_max_bytes` next to the existing structured-model and
  filesystem-read budgets.  Non-positive values disable this specific cap for
  hosts that provide a stronger outer boundary.
- Query-shaped broad-scan hostcalls in `src/micromax_editor/micromax_bridge.py`
  now use the query preflight helper before consuming stack operands.  The first
  cut covers docs/help rows, recent rows, buffer/mark/plugin sections,
  command/action/topic/binding palette rows, hook and option summaries,
  jumplist sections, prompt-opening query prefill for topic/binding prompts,
  command-palette opening, and `ed.find`.
- `tests/test_editor_hostcall_boundary.py` adds regressions proving that an
  oversized docs-section query preserves the operand and skips the section-row
  builder, that `ed.command-palette` does not open a prompt after an oversized
  query, and that embeddings can intentionally disable the cap by setting a
  non-positive VM limit.
- `tools/mxaudit.py` now reports and hard-checks `editor_query_input_budget`.
  This pass also corrected a rev0902 audit bug: `fs_read_preflight_byte_budget`
  was shown in human/JSON output and asserted by `tests/test_mxaudit.py`, but it
  was missing from the `mxaudit --check` hard-error list.  It is now checked.

## Online research implications

OWASP API4:2023 treats unrestricted resource consumption as a practical API risk
when limits such as payload size, memory, CPU time, execution timeout, or
returned-record count are missing or set inappropriately.  The editor hostcalls
are local APIs from Micromax code into host-owned data, so query strings that can
drive scans should be bounded before the scan begins.

CWE-400 frames the same failure as failing to control allocation or maintenance
of limited resources.  Its examples and mitigations emphasize maximum length
checks before large reads or allocations.  For Micromax, the relevant resource is
not just final returned rows; it is also CPU/memory spent matching one caller-
supplied query against host-owned inventories before the shared post-call result
budget runs.

The older OWASP API4:2019 wording is still useful for this narrow point: request
resource cost depends on user input and endpoint logic, and an API is vulnerable
when limits such as payload size, execution timeout, or number of records are
missing or inappropriate.  Rev0903 applies that directly to query-shaped local
hostcalls.

Research sources reviewed in this pass:

- OWASP API Security Top 10 2023, API4:2023 Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OWASP API Security Top 10 2019, API4:2019 Lack of Resources & Rate Limiting: https://owasp.org/API-Security/editions/2019/en/0xa4-lack-of-resources-and-rate-limiting/
- CWE-400, Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-770, Allocation of Resources Without Limits or Throttling: https://cwe.mitre.org/data/definitions/770.html

## Audit/refactor note

The riskiest part of this lane was not one specific picker.  It was repeated
ad hoc string popping at many broad scan edges, which meant each hostcall had to
remember resource preflight independently.  Rev0903 keeps the refactor small:
query size ownership is centralized in `hostcall_boundary.py`, and the bridge
chooses `pop_query_arg()` / `peek_query_arg()` only for free-text scan or prompt
query inputs.  Exact names, paths, command lines, templates, and source-load
paths remain on their existing validators because they are different authority
families.

The audit fix is intentionally included in the same revision because it keeps
the new boundary honest: `mxaudit --check` now fails if either the new query
budget seam or the previous fs-read preflight seam disappears.

## Limits and residual risk

This is still in-process resource control, not an OS sandbox:

- a host can disable the query cap by setting a non-positive VM limit;
- allowed-size queries can still scan large host inventories, so future work may
  need scan-count or candidate-count budgets around the builders themselves;
- `ed.command` and other command-line execution paths are not query hostcalls and
  are intentionally not capped by this helper;
- exact name/path/template/source strings remain separate authority surfaces;
- the cap does not create wall-clock cancellation for a slow builder;
- full release doctor/test sweep remains a separate release-engineering follow-up.

## Evidence

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py` → 54 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 63 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_prompt_completion_hostcalls.py tests/test_prompt_rows.py tests/test_editor_help_docs_boundary.py tests/test_editor_help_picker_browse_budget.py tests/test_editor_helplink_section_rows_hostcall.py tests/test_editor_helpnav_section_rows_hostcall.py tests/test_editor_command_authority.py tests/test_editor_pickers_buffers_marks.py` → 293 passed.
- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxaudit.py --check` → passed with `query-budget=True` and `fs-read-budget=True`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → passed for rev0903.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context/audit/lint/portable passed.
