# U-123 artifact coherence refactor — rev0073

## What was wrong

The rev0072 active U-123 directory mixed four large, mostly self-contained harnesses from different design generations. Its landing README described an older identity-only policy while the selected patch rejected a conflicting token before replacement. A reader could apply the selected patch, run every file, see expected design conflicts, and misclassify the patch as broken.

The first rev0073 draft corrected the roles but compressed Python with semicolon-packed statements to produce an attractive line-count reduction. That was a bad metric optimization: fewer physical lines are not a refactor when readability falls.

## Refactor performed

Rev0073 now:

```text
- preserves the complete rev0072 active packet byte-for-byte under docs/archive/;
- centralizes repeated setup and cleanup in u123_harness.py;
- gives each active entrypoint one explicit role and expected result per source state;
- adds a 32-request bounded resource regression;
- isolates the unproven same-object state as a non-selected experiment;
- formats active Python for reviewability rather than minimum physical line count;
- gates against semicolon-packed statement lines;
- runs extracted source states in independent temporary roots.
```

## Current roles

```text
witness:
  reproduces active-owner replacement and stale-slot deletion

selected fixed invariants:
  reject a different transfer colliding on the same user+token
  preserve another object's active slot during stale cleanup
  bound a 32-request collision burst to one live session

composite:
  imports the three selected fixed invariants

strict experiment:
  rejects a synthesized same-object reentry not shown reachable at runtime
```

## Measured result

The archived baseline contains four Python files, 1,032 physical lines, and 37,914 bytes. The readable active set contains seven Python files—including two newly separated test roles—611 physical lines and 20,975 bytes.

```text
byte reduction: 16,939 bytes (44.7%)
line reduction: 421 lines (40.8%)
active lines over 100 characters: 0
active semicolon-packed statement lines: 0
active maximum line length: 88
```

The useful claim is shared-fixture and byte reduction while adding clearer coverage. The line count is secondary and is no longer achieved by statement packing.

## Validation-harness correction

An initial combined run put all three extracted source states under one temporary parent. During that run, sibling source paths disappeared before later lanes executed, producing `ModuleNotFoundError` and `pytest` “file not found” results. The exact external cleanup interaction was not conclusively traced, so rev0073 removes the assumption entirely:

```text
- each state receives an independent temporary root;
- baseline and selected upstream units run before focused harnesses;
- the two upstream unit lanes run in parallel but with separate HOME/XDG/TMP/CWD trees;
- every focused result is classified against an explicit expected pass/fail state;
- a state runner must execute at least one test before a result is accepted.
```

This was a cube validation defect, not evidence about Nicotine+ behavior. The final gate passes all classified expectations.

## General lesson

A finding directory is not a homogeneous suite. Each artifact needs a role, policy generation, expected state, and selected/experimental status. Refactor metrics must also resist gaming: compressed syntax is not evidence of reduced complexity.
