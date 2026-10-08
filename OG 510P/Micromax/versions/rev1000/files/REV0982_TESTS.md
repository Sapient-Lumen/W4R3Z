# Revision 0982 tests

This record reports Linux-cloudtainer evidence. Allocation figures use Python
3.13.5 `tracemalloc` and do not claim RSS, native, total-heap, Windows, or
cross-platform performance bounds.

## Focused product and boundary evidence

- The final focused process/search/replace/multicursor/softwrap set passed
  **143/143 in 14.17 s** before publication checks.
- Process coverage includes blocked constructor, one-pending gate, gate plus
  constructor absolute deadline, exact completion timestamp, interruption,
  ordinary and interrupted thread-start publication, completed-child handoff,
  partial capture-thread startup, late cleanup, later recovery, regex
  construction plus readiness, and argv/shell construction plus execution.
- Geometry coverage includes reference starts/bounds/inverse lookup, seeded
  randomized equivalence, width-1 million-character storage ceiling, LRU reuse,
  changed-line eviction, visible-only rendering, fixed-wrap arithmetic, and
  cursor/viewport integration.
- Search/replace coverage includes 100,000-row packed storage, bounded `repr`,
  literal and regex behavior, match/result ceilings, compact edits, rich
  compatibility projection, query-replace generation witnesses, and no-rematch
  application.
- Multicursor coverage includes compact line starts, trailing empty lines, reuse
  of an index-only caller sequence without complete reboxing, overlap failure,
  one-touch mutation, cursor rebasing, and undo behavior.
- A separate deterministic cross-revision probe matched rev0981 output exactly
  across **350** literal-search cases, **350** literal-replacement plans, and
  **1,000** fixed/word-wrap geometries, including Unicode and trailing-newline
  coordinates.

## Reproducible witnesses

`tools/reproduce_subprocess_start_stall.py` observed:

- raw injected synchronous construction still blocked after **0.05 s**;
- first bounded caller return in **0.050075 s**;
- second bounded caller return in **0.050052 s**;
- zero second-constructor calls while the first was unresolved;
- late cleanup completion and successful subsequent startup.

`tools/measure_hotpath_allocations.py` observed:

- 1,000,000 characters at width 10: **100,000** true-wordwrap rows with **12,504
  bytes** retained coordinate payload;
- 100,000 literal matches: exactly **1,600,008 bytes** retained coordinate
  payload and **1,636,283 bytes** traced peak;
- 50,000 complete literal replacements: **6,996,148 bytes** traced peak with only
  three rich sample rows retained by the public plan.

A paired rev0981/rev0982 product-path run measured:

| Case | rev0981 peak | rev0982 peak | rev0981 time | rev0982 time |
| --- | ---: | ---: | ---: | ---: |
| editor view, 1.55M-character wordwrap line | 818,568 B | 8,460 B | 0.203 s | 0.152 s |
| cold search, 100,000 matches / lines | 26,730,947 B | 5,053,227 B | 0.496 s | 0.203 s |
| replace plan, 20,000 matches | 4,745,580 B | 2,825,420 B | 0.469 s | 0.290 s |

## Publication evidence

The clean pre-publication run recorded:

- targeted Ruff checks for the changed process-ownership files and regressions,
  `mxlint`, and bytecode compilation: passed;
- `mxaudit --check` and generated effect-contract checks: passed for rev0982;
- portability corpus: **172/172**;
- revision, context, audit, effect, documentation-hygiene, and archive-generation
  unit checks: **88/88** (the archive tests emit one intentional duplicate-name
  warning while exercising rejection behavior).

The repository-wide Ruff baseline still contains pre-existing violations, so no
clean global Ruff result is claimed. No complete pytest suite, mypy-clean tree,
Windows run, RSS bound, or cross-platform timing bound is claimed. Final archive
verification and ZIP integrity are established by the publication command and
its embedded receipt rather than retroactively editing this source tree.
