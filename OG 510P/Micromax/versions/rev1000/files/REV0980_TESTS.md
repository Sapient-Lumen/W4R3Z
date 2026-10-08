# Revision 0980 tests

This record separates focused Linux-cloudtainer evidence from complete-suite and
cross-platform claims. Spawn tests in this instrumented host are unusually slow
because fresh interpreters execute heavy startup hooks.

## Search and geometry evidence

- Search, highlight, containment, query-replace, viewport, softwrap, typing, and
  reference-geometry modules passed **109/109 in 4.95 s** in the final focused
  run.
- Core buffer/edit, line-plan, simultaneous-edit, multicursor, and undo modules
  passed **136/136 in 6.38 s** during the implementation pass.
- A deterministic randomized cross-check passed **10,000 line-geometry cases and
  1,000 complete visual-row indexes** across fixed and word wrapping.
- Fixed-wrap regressions forbid use of the boundary-vector helper while handling
  a 1,000,003-character geometry case and a 2,000,000-character visible render.
- True-wordwrap rendering is instrumented to prove one boundary-map computation
  per visible logical line.

## Worker lifecycle evidence

- Shared worker lifecycle tests passed **26/26 in 10.49 s** in the final run,
  including context preference, native-task fork gating, full-frame transport,
  timeout, crash, malformed/oversize result, start-failure, and cleanup paths.
- Project-picker worker and interaction tests passed **18/18 in 36.50 s** under
  spawn-first.
- The complete 50-test screen-layout module passed under the uncapped
  many-native-thread host with spawn-first in **205.43 s**; the previous
  forkserver-first run stalled cumulatively at varying documentation tests.
- `tools/reproduce_process_start_stall.py` observed `Process.start()` still
  blocked after **0.35 s** while its private forkserver was stopped, then
  recovering after `SIGCONT`; the final observed elapsed value was **0.36163 s**.

## Reference benchmarks

On one Linux cloudtainer run using a 100,000-line, 3,999,999-character fixed-wrap
buffer at width 40:

| Operation | rev0979 | rev0980 |
| --- | ---: | ---: |
| cold/ordinary total visual rows | 57.8 ms | 66.5 ms cold build |
| unchanged total visual rows | 57.1 ms | 0.00246 ms median |
| unchanged cursor projection | 30.2 ms | 0.00500 ms median |
| unchanged ensure-visible | 149 ms | 0.0252 ms median |
| one-line edit plus geometry refresh | 57.1 ms | 0.0266 ms |

The rev0980 index payload is 1.6 MB for 100,000 lines. A separate
20,000,000-character single fixed-wrap line rendered 24 rows at subline 200,000
in **0.000128 s** with a 16-byte one-line index payload.

On a 3,099,999-character buffer with 100,000 literal matches:

| Operation | rev0979 | rev0980 |
| --- | ---: | ---: |
| initial find | 116 ms | 107 ms |
| first unchanged screen | 146 ms | 20.7 ms |
| second unchanged screen | 71.0 ms | 1.15 ms |
| unchanged status | 60.7 ms | 0.117 ms |

These are local wall-clock observations, not UI-frame, terminal, cross-host, or
complexity proofs. Exact call-count and randomized equivalence tests are the
primary regression contracts.

## Structural and publication evidence

- `python -m compileall -q` passed for `src`, `tools`, and changed test modules.
- The portability oracle passed **172/172** cases: 115 kernel and 57 stdlib.
- `python tools/mxlint.py` reported `mxlint: ok`.
- `python tools/mxaudit.py --check` passed with the rev0980 structural and
  generated-contract checks current.
- `python tools/mxeffects.py --write-help-doc --check-help-doc --check` passed
  with **24** current effect/resource rows.
- `python tools/mxcontext.py --json` regenerated `MICROMAX-CONTEXT.json`, and
  `python tools/mxcontext.py --check` passed with **64** curated docs and **63**
  code entrypoints.
- Revision-index, living-doc, and context tests passed **12/12 in 1.96 s**;
  structural-audit tests passed **4/4 in 8.93 s**; effect-contract tests passed
  **5/5 in 13.53 s**.
- Archive generation/lineage/verifier tests passed **52/52 in 12.54 s**. The one
  expected warning is Python `zipfile` reporting the deliberately duplicated
  member in the duplicate-rejection test.

No complete pytest suite, Windows run, preemptible process start, background
search index, rope, total-memory cap, syscall filter, native-crash recovery, or
hostile-plugin sandbox is claimed.
