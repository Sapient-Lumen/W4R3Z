# Rev0900 — regex timeout worker for risky patterns

Date: 2026-07-07

## Executive finding

Rev0899 closed the easiest regex resource hole: huge haystacks, patterns, and
replacement templates no longer enter Python's regex engine before Micromax has
named an input-budget failure and preserved caller evidence.  That was not enough
for the riskiest remaining regex failure.  A small pattern/input pair such as a
nested repeated group can still trigger catastrophic backtracking and wedge the
single in-process editor host.

Rev0900 adds a concrete wall-clock containment lane without turning the project
back into registry work.  Common risky regex shapes are routed to a subprocess
worker with an embedding-tunable timeout.  Successful worker results are reduced
to ordinary VM-visible maps/lists/strings before crossing back to the hostcall;
timeouts terminate the worker and preserve the caller's direct hostcall
arguments.

## What changed

- `VM.hostcall_regex_timeout_seconds` defaults to `0.25`.  Values `<= 0` disable
  the worker route for embeddings that supply their own defended engine or
  process boundary.
- `src/micromax/host_regex.py` now has a small ReDoS prefilter for repeated
  groups containing repeats or alternation, plus backreferences.  This is a
  routing heuristic, not a formal proof of safety.
- `re.search`, `re.findall`, `re.sub`, and `re.subn` use the worker only for
  patterns the prefilter marks risky.  Simple regexes continue to use the local
  compiled pattern, so common editor find/replace paths avoid subprocess cost.
- Risky `re.sub` / `re.subn` zero-width checks moved into the worker lane.  That
  avoids doing the potentially explosive scan in the main editor process before
  the timeout boundary is active.
- Regex execution errors and timeouts happen before the hostcall consumes public
  arguments.  A direct `hostcall` failure leaves haystack/pattern/start/flags or
  haystack/pattern/replacement/flags visible for diagnostics.
- `tools/mxaudit.py` reports and checks `regex_hostcall_timeout_worker` so the
  seam remains executable evidence rather than handoff prose.

## Online research implications

Python's own June 2026 timeout discussion names the core problem directly:
pathological user-controlled patterns or inputs can pin a worker, and the thread
model is not a reliable escape hatch when the engine is running in C while
holding the GIL.  The same thread also notes that a subprocess with a kill timer
is the reliable containment workaround today, while a built-in `re` timeout is
still only a proposal.

RE2 remains the longer-term design reference: it is positioned as a safe,
thread-friendly alternative to backtracking engines used by PCRE, Perl, and
Python, and Go/Rust regex packages follow similar no-backtracking principles.
That supports Micromax's current staged approach: make Python reference behavior
bounded enough to survive now, then decide later whether the public plugin regex
dialect should move to a defended engine or narrower syntax.

Research sources reviewed in this pass:

- Python.org discussion, "Add an opt-in timeout parameter to re to mitigate catastrophic backtracking": https://discuss.python.org/t/add-an-opt-in-timeout-parameter-to-re-to-mitigate-catastrophic-backtracking/107766
- Python 3.14 `re` documentation: https://docs.python.org/3/library/re.html
- Google RE2 repository and safety framing: https://github.com/google/re2
- SoK: A Literature and Engineering Review of Regular Expression Denial of Service: https://arxiv.org/abs/2406.11618

## Limits and residual risk

This revision still does not prove that every regex is safe.  The prefilter is a
small, explainable detector for common dangerous shapes.  It can miss other
pathological Python regexes, especially complex lookaround/backtracking cases,
and it can route some benign patterns through the worker.  That is acceptable for
this landing because false positives cost a subprocess, while a recognized false
negative can still wedge the in-process host.

The worker boundary is a mitigation, not an OS sandbox for hostile native code.
It bounds regex wall-clock execution for routed patterns, but it does not solve
all temporary allocation, IPC result-size, engine correctness, or broad plugin
resource abuse.  The shared hostcall result budget still checks returned
VM-visible payloads after the worker result is appended.

The next highest-value follow-up is to preflight structured row builders that can
traverse host-owned state before post-call result budgets fire, and to keep
compacting docs/evidence overhead as code boundaries land.

## Evidence

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_regex_hostcalls.py tests/test_hostcall_result_budget.py tests/test_string_hostcalls.py` → 42 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py` → 48 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 9 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mkrevzip.py` → 5 passed.
- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → refreshed context and passed.
- `PYTHONPATH=src python tools/mxaudit.py --check` → passed with `regex-timeout-worker=True`.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context/audit/lint/portable summary passed.
- A broad combined selected-pytest command hit the cloudtainer execution timeout near completion; the same coverage was split into the focused commands above so the final evidence remains reproducible.
