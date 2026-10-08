# Revision 0967 validation

## Product, contract, and regression slice

The combined selection/syntax projection, TUI precedence, compact screen
producer, 80x24 visual journey, existing viewport overlays, and query-replace
generation/undo regression slice passed:

```text
66 passed
```

This includes horizontal and softwrap projection, selected logical newlines,
empty lines, malformed syntax rows, filetype normalization, the 4096-character
syntax cap, primary retention under the 4096-source selection cap, off-screen
visible-range accounting, one normalization pass, one screen status snapshot,
strict compact cue production, the fixed overlap hierarchy, and the updated
query-replace golden journey.

The independent receiving and process-facing boundaries passed separately:

```text
22 passed  screen consumer + budget + plain/diagnostic CLI dump + installed resources
```

## Renderer and composition evidence

All 50 cases in `tests/test_editor_screen_layout.py` passed across six bounded
isolated invocations (10, 10, 6, 4, 10, and 10 cases):

```text
50 passed
```

They cover the historical screen-model surface as well as model-level
syntax/selection cues, fake-curses painting of primary and secondary selection
plus the selected newline cell, exact softwrap source/display alignment, one
composed screen, and prompt cursor placement after horizontal scroll without a
renderer-side status reread. A single long-lived invocation exceeded the
cloudtainer command bound after a passing prefix, so only the completed isolated
batches are claimed.

## Static and release-structure checks

The release and living-document boundaries passed:

```text
6 passed   tests/test_mxcontext.py
4 passed   tests/test_mxaudit.py
5 passed   tests/test_effect_contracts.py
52 passed  tests/test_mkrevzip.py
5 passed   revision-index + living-doc hygiene
mxlint: ok
compileall: ok
effect/resource contract: current, 23 rows
context snapshot: rev0967, 64 docs, revision sources agree
```

`make typecheck` reaches the repository-owned lane, but this offline
cloudtainer has no `mypy` installation, so that script reports its explicit skip
rather than a typecheck pass. The final archive is also checked with the
deterministic archive verifier and `unzip -t`; neither result is promoted into a
complete repository-suite claim.

## Honest scope

No complete repository-suite result is claimed. Validation concentrates on the
changed screen/model/renderer boundaries, the independent contract consumer,
installed resources, current structural checks, and deterministic packaging.
