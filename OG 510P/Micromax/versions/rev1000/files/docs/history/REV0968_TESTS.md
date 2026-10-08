# Revision 0968 validation

## Changed product and transaction evidence

The final focused transaction slice passed together:

```text
129 passed
```

It includes `test_simultaneous_edits.py`, `test_multicursor_edit_journey.py`,
`test_macro_replay_transaction.py`, `test_editor_with_undo_transaction.py`, both
hostcall transaction/argument-boundary files, and `test_editor_core.py`. The
slice covers repeated select-next progression, newest-selection skip,
active-buffer-local continuation, truthful exhaustion, visible selection cues,
exactly-once text/newline/tab replacement, cursor/anchor rebasing, duplicate
coalescing, overlap atomicity, VM argument preservation, direct one-cursor
splicing, cursor-only undo, one macro transaction, multi-buffer playback,
navigation-only redo preservation, exact Undo/Redo behavior, callback retention,
and playback authority.

The committed pure-planner suite retains a seeded 500-plan reference comparison.
Development-time deterministic checks additionally compared 20,000
non-overlapping edit sets with a reverse-application oracle and 20,000 position
mappings with a right-affinity oracle.

## Focused adjacent regression evidence

The final successful slices were:

```text
 72 passed  typing, autoindent/tab, viewport, tier-0, fastdirty, readonly,
            clipboard import/export/OSC52, default bindings, undo authority
 67 passed  query replace, qreplace interleaving/generation/witness,
            replace planning, regex hostcalls
 99 passed  named macros plus macro/action/command/interaction/deferred authority
 51 passed  selection projection, highlight precedence, compact contract/consumer,
            visual journey, and changed screen-layout cases
```

These slices overlap with the changed transaction slice and are not summed into
a fabricated repository total.

## Structural, portability, and publication evidence

The final source generation passed:

```text
python -m compileall -q src tests tools
scripts/lint.sh                         mxlint: ok
python tools/mxaudit.py --check         rev0968 structural audit: ok
python tools/mxeffects.py --check       23-row effect/resource contract: ok
python tools/mxcontext.py --check       curated 64-document context: ok
python tools/mxdoctor.py                bounded doctor preflight: 31 tests passed
python tools/mxportable.py --json       156 portability cases passed, 0 failed
```

Focused evidence-tool tests passed in split bounded invocations:

```text
 1 passed  revision index
 4 passed  living-document hygiene
 6 passed  context generator
 4 passed  structural audit
 5 passed  effect/resource contract
52 passed  revision archive builder/verifier
21 passed  doctor
```

`mypy` is not installed in this offline cloudtainer, so `scripts/typecheck.sh`
reported its documented skip instead of a typecheck pass.

## Comparative repeat probe

A one-step insert macro replayed 256 times in a 262,144-character fast-dirty
buffer produced:

```text
recovered rev0967: 262400 chars, 256 undo rows, 1.61 s, 361496 KiB max RSS
final rev0968:     262400 chars,   1 undo row, 1.69 s, 301536 KiB max RSS
```

This single local run proves the exercised history collapse and lower retained
memory witness. It is not a general latency or large-file benchmark.

## Archive evidence

The same-stamp final archive is:

```text
Micromax-rev0968-2026.07.17.23.57-multicursor-simultaneous-edit-macro-undo-redshank.zip
```

An initial same-stamp seal passed both the provenance verifier and `unzip -t`.
After generated caches/artifacts were removed and this evidence was embedded, the
archive was rebuilt at the same filename. The final verifier reports `ok: true`,
revision 968 from every embedded breadcrumb, the canonical tag, and 1,352 source
files; the final ZIP integrity walk reports no compressed-data errors.

## Honest scope

No complete repository-suite result is claimed. Combined structural test
invocations can exceed the cloudtainer command window even when their split
files pass, and the historical full screen-layout file remains slow. This
revision claims the changed product journeys, focused adjacent regressions,
current structural/portability checks, and the independently verified archive.
