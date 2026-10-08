# Rev0902 — fs-read preflight byte budget

Date: 2026-07-07

## Executive finding

Rev0898 gave Micromax a shared post-call result budget and rev0901 added input
budgets for structured editor model rows.  The next riskiest executable gap was
`ed.fs-read`: it already had a hardcoded size limit inside the contained byte
reader, but the limit was not exposed as a first-class hostcall preflight seam
and could not be tuned by the embedding VM.

Rev0902 makes the file-observation boundary explicit.  `ed.fs-read` now gets a
VM-tunable pre-read byte budget, checks the opened file's concrete fd target,
kind, and size before entering the byte-loading loop, then repeats the fd-bound
size/kind/containment check at the final read seam.  The duplicate check is
intentional: preflight keeps obviously oversized reads away from byte loading,
while the final check still handles late file growth, symlink swaps, and other
races.

## What changed

- `src/micromax_editor/hostcall_boundary.py` now owns
  `DEFAULT_FS_READ_MAX_BYTES = 1_000_000` and
  `effective_fs_read_max_bytes(vm)`.  The VM attribute
  `editor_hostcall_fs_read_max_bytes` is embedding-tunable; non-positive values
  disable this specific cap for hosts that supply a stronger boundary elsewhere.
- `install_editor_hostcalls()` initializes `editor_hostcall_fs_read_max_bytes`
  beside the structured-model input budgets and passes the effective limit into
  `fs_read_text()`.
- `src/micromax_editor/file_access.py` adds
  `preflight_file_read_size_contained()`, an fd-bound kind/size/containment check
  that reads no file bytes.
- `src/micromax_editor/fs_hostcalls.py` runs that preflight before
  `read_file_bytes_contained()`.  The final read helper still rechecks regular
  file status, byte limit, and containment after opening its own fd.
- `tests/test_editor_fs_read.py` proves that an oversized file fails through the
  VM-tunable budget before the byte loader is called, and that a file which grows
  after preflight is still rejected by the final read check.
- `tools/mxaudit.py` now reports and checks `fs_read_preflight_byte_budget` so the
  seam remains executable evidence rather than a prose promise.

This is a small refactor, but it moves a real boundary into the shared hostcall
budget layer instead of leaving it as an incidental literal inside one helper.

## Online research implications

OWASP API4:2023 treats unrestricted resource consumption as a practical API risk
when limits such as execution timeouts, payload sizes, memory, or returned-record
counts are missing or inappropriate.  `ed.fs-read` is a local API from Micromax
code into the editor host, so the same rule applies: validate resource-controlling
parameters before doing host work, then keep a result budget after the work too.

CWE-400 frames uncontrolled resource consumption as software failing to control
allocation or maintenance of limited resources.  The relevant resource here is
not only the final VM stack result; it is also host memory and time spent loading
file bytes on behalf of a script.

The existing descriptor-backed containment work remains the right shape.  Python
and POSIX file APIs make path checks race-prone; Micromax should continue to bind
filesystem operations to opened descriptors where available, check the concrete
fd target, and avoid trusting a single early path resolution.  Rev0902 preserves
that pattern by making preflight advisory and final read authoritative.

Research sources reviewed in this pass:

- OWASP API Security Top 10 2023, API4:2023 Unrestricted Resource Consumption: https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- CWE-400, Uncontrolled Resource Consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-770, Allocation of Resources Without Limits or Throttling: https://cwe.mitre.org/data/definitions/770.html
- Python `os` documentation for fd-level operations such as `os.open`, `os.read`, and `os.fstat`: https://docs.python.org/3/library/os.html
- Safe path-handling discussion reviewed for portability cautions around `os.open`, `O_NOFOLLOW`, and `dir_fd`: https://snyk.io/articles/safe-path-handling/

## Audit/refactor note

The audit asked for substance over registry bureaucracy.  This pass touched the
smallest path that removed real risk:

1. The bridge now treats filesystem observation as part of the same budget family
   as screen/docs/prompt model observation.
2. The file-access helper owns the reusable fd-bound preflight rather than
   embedding an ad hoc `Path.stat()` check in the bridge.
3. The existing final read helper remains the source of truth for the actual byte
   load, so the refactor does not weaken symlink-swap or file-growth protection.

The important test is not merely that large files fail; it is that the oversized
case never reaches `read_file_bytes_contained()` at all, and the growth-after-
preflight case still fails later.

## Limits and residual risk

This is still an in-process best-effort guard, not an OS sandbox:

- a host can intentionally disable the cap by setting a non-positive VM limit;
- preflight opens the path once and the final read opens it again, so a hostile
  local process can still race between the two, but the final read rechecks;
- the cap does not impose a wall-clock timeout on unusual filesystems or devices;
- `ed.require` uses its own source-load/evaluation authority and remains a
  separate risk surface from plain `ed.fs-read`;
- free-text docs/help/prompt query strings can still drive broad scans before row
  budgets run and remain the next resource boundary to close.

## Evidence

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_read.py` → 8 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxaudit.py` → 2 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_fs_read.py tests/test_mxaudit.py tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 19 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_mkrevzip.py` → 54 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py tests/test_mxaudit.py` → 11 passed after the docs/revision-index refresh.
- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → passed for rev0902.
- `PYTHONPATH=src python tools/mxaudit.py --check` → passed with `fs-read-budget=True`.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context/audit/lint/portable passed.
