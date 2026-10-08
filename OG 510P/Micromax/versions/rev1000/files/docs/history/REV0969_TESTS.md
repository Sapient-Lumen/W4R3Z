# Revision 0969 validation

## Changed product evidence

The final changed product slice passed:

```text
77 passed in 3.85s
```

It combines `test_search_navigation_journey.py`, `test_editor_core.py`, and
`test_tui_hlsearch.py`. The 13 new journeys cover forward/backward and initial
wrap, sole-match no-op truth, newline progression, non-overlap agreement,
original-coordinate Unicode behavior, adjacent/zero-width regex policy,
cross-line projection, softwrap and horizontal-scroll anchor integrity,
mutation-stale and cross-buffer snapshot rejection, and one shared screen scan.

## Focused adjacent regression evidence

Successful adjacent slices were:

```text
18 passed, 92 deselected  active-search authority/plugin containment,
                           selection/highlight precedence, compact contract,
                           and independent consumer selectors
 9 passed, 41 deselected  screen-model/search/viewport-cue selectors
 3 passed, 37 deselected  search statusline selectors
```

These selectors overlap conceptually with the changed product slice and are not
summed into a fabricated repository total. A broader combined status/screen
invocation reached 40 passing tests before its cloudtainer command window
expired; it is not counted as a completed result.

## Structural and generated-contract evidence

```text
python -m compileall -q src tests tools   passed
scripts/lint.sh                           mxlint: ok
python tools/mxaudit.py --check           rev0969 structural audit: ok
python tools/mxeffects.py --check         23-row effect/resource contract: ok
python tools/mxcontext.py --check         rev0969 context: ok
scripts/typecheck.sh                      documented skip: mypy unavailable
```

Focused generator and hygiene suites passed:

```text
 5 passed   revision index + living-document hygiene
 6 passed   context generation and bounds
 4 passed   structural audit
 5 passed   effect/resource contracts
52 passed   archive builder/verifier (1 expected duplicate-member warning)
```

`tools/mxdoctor.py` completed its bounded risk lane with 19, 9, and 3 passing
batches. Its only environment notices were transient caches plus absent optional
`ruff` and `mypy`; caches are removed before packaging. `tools/mxportable.py
--json` passed all 156 cases: 99 kernel and 57 stdlib, with zero failures.

## Archive evidence

The final sealed handoff is:

```text
Micromax-rev0969-2026.07.18.01.05-search-wrap-shared-match-crossline-projection-rivertern.zip
```

`mkrevzip --verify-archive --verify-json` reports `ok: true`, revision 969,
`search-wrap-shared-match-crossline-projection-rivertern`, and 1,357 members.
`unzip -t` reports no compressed-data errors. This evidence was first obtained
from a provisional seal; the same named archive was then rebuilt after this
record entered the generated context and was verified again. No source edit
follows that final verification.

## Honest scope

No complete repository-suite result is claimed. Direct editor regex timeout
containment, full Unicode case-fold equivalence, grapheme/cell coordinates,
workspace search, and universal large-file performance are outside this
revision's evidence.
