# Rev0985 tests and evidence

This record reports Linux-cloudtainer evidence. Allocation figures use Python
`tracemalloc`; they are not RSS, allocator-arena, native-memory, latency, or
cross-platform bounds.

## Focused simultaneous-history boundary

The rev0985 file completes **13 tests**, covering:

- 1,000 fixed-seed Unicode/newline non-overlapping edit plans with exact forward
  and inverse replay;
- adjacent deletes with same-offset inverse insertions;
- preservation of unrelated text after every witnessed target;
- exact multi-cursor backspace row geometry and sidecars;
- stale later-target refusal before any undo or redo mutation, retained stack
  membership, and successful replay after repair;
- 1,100,000-character sparse paste retention;
- equal-text sidecar-only rows with zero retained text;
- suppressed aggregate local-helper bypass and the live-qreplace exception;
- shared sparse Cut and hostcall seams;
- a 350,000-character render/search-cancel/save/undo/redo/interrupted-save/
  restart-recovery journey; and
- the executable rev0984-reference comparison.

Final focused receipts:

| Scope | Result |
| --- | ---: |
| `tests/test_rev0985_sparse_simultaneous_history.py` | **13 passed in 6.89 s** |
| rev0985 + simultaneous-edit + qreplace-boundary + rev0984-budget union | **65 passed in 7.05 s** |
| broad edit/transaction union | **120 passed in 3.30 s** |
| editor core | **60 passed in 2.74 s** |
| editor query-replace | **21 passed in 0.55 s** |
| selected interrupted-save recovery pair | **2 passed in 30.79 s** |
| recovery-journal journey | **35 passed in 0.36 s** |
| screen consumer/contract/visible-selection union | **38 passed in 17.03 s** |

The broad edit/transaction union covers multi-cursor journeys, `ed.with-undo`,
macro transactions, hostcall transactions, and hostcall boundaries. The selected
interrupted-save pair is the recovery path exercised by the permanent product
journey; the complete interrupted-save file was started but exceeded the
external tool slice, so no complete-file pass is claimed. One larger combined
pytest invocation likewise exceeded that slice and is not used as evidence.

## Permanent simultaneous-history witness

```bash
PYTHONPATH=src python tools/measure_simultaneous_history.py \
  --chars 1100000 --cursors 8 --edits 10 --samples 3
```

| Metric | Rev0984 broad immediate reference | Rev0985 sparse product |
| --- | ---: | ---: |
| document characters | 1,100,000 | 1,100,000 |
| cursors × actions | 8 × 10 | 8 × 10 |
| accounted retained text | 22,005,600 B | 560 B |
| largest callback string | 1,100,560 chars | 7 chars |
| median traced current | 11,052,850 B | 1,180,601 B |
| median traced peak | 12,157,875 B | 3,384,155 B |
| exact undo / redo | yes / yes | yes / yes |

The reduction is **99.997%** in accounted retained text, **89.319%** in median
traced current allocation, and **72.165%** in median traced peak. The reference
uses the current planner with rev0984's broad before/after history shape; it is
not a product mode.

The same receipt records zero local snapshot-helper calls across ten suppressed
actions versus twenty calls in the rev0984 control flow. Rev0984's helper payload
was a version sentinel plus copied cursor/selection/id sidecars when no
query-replace session was active; it did not contain full document text.

The machine-readable receipt is
`.artifacts/rev0985-simultaneous-history.json`.

## Structural and publication evidence

| Lane | Result |
| --- | ---: |
| revision-index + living-doc + context + audit + effect-contract tests | **21 passed in 24.00 s** |
| critical `mkrevzip` tests | **6 passed in 3.85 s** |
| `tools/mxportable.py --quiet` | **172 / 172 passed** |
| `scripts/lint.sh` | **`mxlint: ok`** |
| `tools/mxaudit.py --check` | **passed** |
| generated effect help/contract check | **passed** |
| generated context check | **passed** |
| touched Python compilation | **passed** |
| static type checking | **not run: `mypy` unavailable offline** |

The default timely-test lane reached its 18-second bound while collecting and
hashing 3,224 tests, before pytest execution. A documented timeout-scale retry
reached the same collection bottleneck; a wider custom retry exceeded the
external tool slice. Context, audit, lint, and portability portions passed, but
**no timely-test pass is claimed**. The transient partial timely JSON files are
not publication evidence and are excluded from the archive.

No unexecuted complete-suite, Windows, signed-release, hard-memory, RSS,
allocator-arena, portable-latency, or empty-source-slice neighborhood
validation claim is made.
