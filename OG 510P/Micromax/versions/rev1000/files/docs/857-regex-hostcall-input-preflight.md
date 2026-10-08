# Rev0899 — Regex hostcall input preflight

Date: 2026-07-07

## Executive finding

The next risky lane after rev0898's shared hostcall result budget was the part
rev0898 explicitly did **not** cover: expensive work that happens before a
hostcall returns.  The highest-value narrow cut was the `re.*` hostcall family.
It accepts caller-controlled haystacks, patterns, flags, and replacements; it
uses Python's backtracking `re` engine; and several previous tests already made
regex helpers part of the public script/plugin surface.

Rev0899 adds a concrete preflight boundary instead of another registry pass:
regex hostcalls now validate public argument shape and byte budgets before
consuming arguments or entering the regex engine / replacement compiler.  This
turns the first unresolved resource-exhaustion follow-up from rev0898 into
runtime behavior.

## What changed

- `src/micromax/vm.py` now gives each VM three embedding-tunable regex hostcall
  input limits:
  - `hostcall_regex_max_haystack_bytes` (default `262_144`),
  - `hostcall_regex_max_pattern_bytes` (default `10_000`),
  - `hostcall_regex_max_replacement_bytes` (default `262_144`).
  Values `<= 0` disable the corresponding limit for hosts that provide their
  own containment.
- `src/micromax/host_regex.py` now validates the whole public argument shape for
  `re.search`, `re.findall`, `re.sub`, `re.subn`, and `re.escape` before
  deleting stack arguments.
- Oversized haystacks, patterns, replacements, and `re.escape` inputs fail with
  stable `re: ... too large: N bytes > LIMIT` errors.
- Invalid search starts, invalid flags, invalid patterns, zero-width
  substitution patterns, and invalid replacement templates now leave direct
  hostcall arguments visible for inspection instead of consuming evidence first.
- `tools/mxaudit.py` now has a `regex_hostcall_input_budget` integrity seam so a
  future cleanup cannot silently remove the preflight boundary.
- Focused tests in `tests/test_regex_hostcalls.py` cover input-budget failures,
  `re.escape` input preflight, and argument preservation for preflight errors.

## Why regex, not another matrix

The project's usual vice is turning risk into inventories before the runtime has
changed.  Here the evidence already pointed at a live chokepoint.  `re.findall`
was the rev0898 result-budget example, and the same family still had an
unbounded input side.  Fixing that has more value than cataloging every
hostcall, because it creates an executable pattern the next preflight lanes can
copy: validate visible caller arguments, name the exceeded budget, then consume.

This is also a small refactor: regex hostcalls no longer mix stack mutation with
validation.  The helper split (`_preflight_search_args`, `_preflight_sub_args`,
`_check_bytes`, `_require_str_arg`) gives later budget work a clear shape while
keeping behavior local to the risky family.

## Online research implications

OWASP's ReDoS description is the key warning: many regex implementations can
reach extreme, exponentially slow cases, allowing a crafted pattern/input pair
to hang a program for a long time.

- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

The June 2026 Python discussion about adding a timeout to `re` is especially
relevant to Micromax because it says the current reliable containment workaround
for stdlib `re` is to run matching in a subprocess with a kill timer, while
noting the operational overhead and that third-party engines/modules may expose
timeout controls.

- https://discuss.python.org/t/add-an-opt-in-timeout-parameter-to-re-to-mitigate-catastrophic-backtracking/107766

A 2024 systematization paper frames ReDoS as an asymmetric DoS class and argues
that engineering work increasingly needs migration paths to defended engines and
systematic defenses, not just ad hoc regex audits.

- https://arxiv.org/abs/2406.11618

VS Code's extension-runtime documentation is the parallel host lesson: extension
code may read/write files, make network requests, run processes, and modify
workspace settings with the host's permissions, so runtime permission boundaries
and marketplace/trust signals are only part of the story.  Micromax should keep
making host authority and host resource costs explicit at each boundary.

- https://code.visualstudio.com/docs/configure/extensions/extension-runtime-security

## Limits and residual risk

This revision does **not** make Python regex execution safe against every ReDoS
case.  A small input can still trigger catastrophic backtracking with a bad
pattern.  The honest next step remains a regex wall-clock story: a cancellable
worker, subprocess-backed matching, a defended engine, or a narrower regex
dialect for plugin-hosted helpers.

It also does not preflight every hostcall.  The next practical candidates are
`ed.fs-read` and the structured screen/docs/prompt row builders, because those
can allocate or traverse large host-owned data before the shared result budget
has a chance to reject a returned payload.

## Evidence

- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_regex_hostcalls.py tests/test_hostcall_result_budget.py tests/test_string_hostcalls.py tests/test_editor_hostcall_boundary.py tests/test_mxaudit.py` → 87 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mxcontext.py tests/test_revision_index.py tests/test_docs_living_hygiene.py` → 9 passed.
- `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 pytest -q tests/test_mkrevzip.py` → 5 passed.
- `PYTHONPATH=src python tools/mxlint.py` → `mxlint: ok`.
- `PYTHONPATH=src python tools/mxcontext.py --check` → rev0899 context check passed and lists `docs/857-regex-hostcall-input-preflight.md` as a curated entrypoint.
- `PYTHONPATH=src python tools/mxaudit.py --check` → pass while reporting `regex-input-budget=True`.
- `PYTHONPATH=src python tools/mxportable.py --quiet` → 156/156 portability cases passed.
- `PYTHONPATH=src python tools/mxtimely.py --skip-doctor --skip-tests --summary-json .artifacts/mxtimely-summary.json` → context, audit, lint, and portable steps passed in 23.64s.

A single larger combined pytest invocation across the same selected files reached
the cloudtainer tool timeout after visible progress; the selected checks above
were therefore split by file group rather than treated as one stale claim.
