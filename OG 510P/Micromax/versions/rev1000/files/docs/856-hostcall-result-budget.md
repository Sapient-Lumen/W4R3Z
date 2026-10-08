# Rev0898 — VM hostcall result budgets

Date: 2026-07-07

## Executive finding

The riskiest unfinished lane was not another registry or doctrine page.  It was
that Micromax had allowlisted hostcalls but no shared limit on how much VM-visible
data an allowed hostcall could return to the stack.  A trusted or plugin-origin
script could ask a pure helper such as `re.findall`, `s-split`, `s-format`, or a
future structured model hostcall to produce a very large result.  Instruction
fuel only counts VM steps; it does not bound host work, host-allocated result
objects, or the amount of data left on the VM stack after a hostcall returns.

Rev0898 adds the first general result-payload boundary at the VM hostcall
chokepoint.  This is intentionally small and executable: hostcall dispatch now
captures the stack before calling an allowlisted host function, identifies the
changed stack suffix after the call, estimates the VM-visible result payload, and
restores the pre-call argument stack if the result exceeds tunable byte or cell
budgets.

## What changed

- `src/micromax/host_limits.py` adds deterministic host-value budget estimation
  for VM-visible values.  Strings and bytes count by byte length; lists, tuples,
  sets, and maps count visible cells recursively; cycles and excessive nesting
  terminate as bounded opaque cells; arbitrary host objects count by type name
  instead of calling impure or expensive `repr()`.
- `src/micromax/vm.py` now gives every VM two embedding-tunable limits:
  `hostcall_result_max_bytes` and `hostcall_result_max_cells`.  Values `<= 0`
  disable the corresponding limit.
- `src/micromax/core.py` applies the check inside `hostcall` after the allowlisted
  host function returns.  On violation it restores the argument stack captured
  after the hostcall name was consumed and raises `MicromaxError("hostcall result
  budget exceeded: ...")`.
- `tests/test_hostcall_result_budget.py` proves byte-budget restoration,
  nested-cell-budget rejection, and that `re.findall` is caught by the shared VM
  budget rather than a regex-specific side path.
- `tools/mxaudit.py` now exposes and checks the `vm_hostcall_result_budget` seam.

This is a refactor with substance: hostcall result ownership moved from a set of
ad hoc helper assumptions into the common VM bridge, with tests and audit
coverage.

## Why this was prioritized

Micromax has spent many revisions closing stale plugin-generation survivor
lanes.  That work matters, but resource exhaustion is a different failure mode:
no stale generation is required.  The script can still be authorized, the hostcall
can still be allowed, and the result can still be too large for an in-process
host to tolerate.

This was also the lowest-bureaucracy cut of the missing effect-lifecycle matrix:
not a complete table, just one live effect boundary made executable.  A future
matrix can now describe hostcall result budgets by pointing to real behavior
instead of inventing a paper contract first.

## Online research implications

OWASP treats unrestricted resource consumption as a practical API risk and
recommends server-side validation for parameters that control response size, plus
request-size limits and defenses against input-driven allocation.  That maps
almost directly to Micromax hostcalls: an allowlisted hostcall is an API from VM
code to the host, and result size is as important as call permission.

OpenSSF's Python secure-coding guide is still a reminder that process isolation,
adequate resource pools, cleanup, and release of unused resources are ordinary
engineering controls, not optional sandbox luxuries.  Micromax's current
in-process model cannot claim hostile-code containment; resource ceilings are the
honest next guardrail.

WASI remains a relevant future direction because its documentation emphasizes no
ambient authority and explicit host grants.  But recent WebAssembly-container
resource-isolation research is a warning: even Wasm/WASI runtimes can expose host
resource-exhaustion surfaces through their APIs.  Moving Micromax out of process
or into Wasm later will not remove the need for hostcall budgets.

VS Code extension-ecosystem research continues to support the main mission:
large extension systems accumulate suspicious behavior and weak practical
controls if authority and resource use remain implicit.  Micromax should keep
spending revisions on concrete host boundaries, not just on better docs about
why boundaries matter.

Research sources reviewed in this pass:

- OWASP API4:2023 Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OWASP Denial of Service Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html
- OpenSSF Secure Coding One Stop Shop for Python: https://best.openssf.org/Secure-Coding-Guide-for-Python/
- WASI introduction/security framing: https://wasi.dev/
- WebAssembly resource-isolation attack-surface paper: https://arxiv.org/abs/2509.11242
- VS Code extension-ecosystem analysis: https://arxiv.org/abs/2411.07479
- Python `re` timeout discussion, useful as a reminder that regex wall-clock
  budget remains separate from result-size budget: https://discuss.python.org/t/add-an-opt-in-timeout-parameter-to-re-to-mitigate-catastrophic-backtracking/107766

## Limits and residual risk

The new budget is post-call and VM-visible.  It prevents an oversized result from
surviving on the stack and restores the caller's argument data for inspection,
but it does not:

- preempt CPU-bound host work before the function returns;
- undo irreversible side effects from side-effecting hostcalls;
- prevent temporary allocation while a pure hostcall is building its result;
- bound regex catastrophic backtracking or shell/file/process wall time;
- estimate true Python heap memory.

Those are explicit next steps, not hidden claims.  The most practical follow-up is
to add preflight budgets for the highest-risk pure helper families (`re.*`,
`ed.fs-read`, structured screen/docs/prompt model rows) and a separate timeout or
safe-engine story for regex matching.

## Evidence

- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → rev0898 context check passed and lists `docs/856-hostcall-result-budget.md` as a curated entrypoint.
- `PYTHONPATH=src python tools/mxaudit.py --check` → pass while reporting `hostcall-result-budget=True`.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_hostcall_result_budget.py tests/test_string_hostcalls.py tests/test_regex_hostcalls.py tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py` → passed when split by file after the single combined invocation reached the cloudtainer tool timeout near completion.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_docs_living_hygiene.py tests/test_mkrevzip.py` → 8 passed.
- `PYTHONPATH=src python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context, audit, lint, and portable steps passed in 25.03s.

This revision does not claim full release verification, regex CPU containment,
out-of-process sandboxing, comprehensive input preflight, or transactional undo
for side-effecting hostcalls whose result later exceeds the budget.
