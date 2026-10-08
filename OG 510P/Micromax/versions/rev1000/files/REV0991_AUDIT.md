# Rev0991 audit — line-vector genuine multi-range planning

The deep implementation, measurement, research, and residual-risk record is
`docs/948-line-vector-multirange-planning-audit.md`.

## Heart of the mission

A small multicursor action should stay small without surrendering original-
coordinate semantics, atomic overlap refusal, exact sidecars, or Undo. Rev0991
removes the final immediate-edit path that converted the canonical line vector
into complete source and result strings solely to plan and publish one action.

## Severe corrected waste

In the permanent 1,099,999-character / 11,000-line / 128-edit witness, complete
document-string generations fall from two to zero. Median traced current Python
allocation falls from 2,840,512 B to 226,168 B (92.038%) and peak allocation
falls from 4,162,760 B to 631,536 B (84.829%). The product reuses 10,872 source
line objects, and result, sidecars, sparse history, Undo, and Redo remain exact.

## Shipped change

Genuine multi-range edits now plan against one canonical line-vector snapshot,
share duplicate/overlap/mapping geometry with the flat oracle, join only touched
output lines, retain only changed old/new slices, and commit one detached vector
once. Equal replacements and suppressed aggregate actions no longer allocate
old slices that would be discarded. Composed component edits that cancel to the
exact source generation remain sidecar-only and never create a false text
mutation during application, Undo, or Redo.

## Audit/refactor

Sparse replay and immediate application share the same line-vector builder;
flat and line planners share geometry, mapping, and witness helpers. The
measurement witness was corrected to compare retained objects by identity rather
than raw allocator addresses and now stores one compact sidecar digest. A
30,000-plan differential audit exposed the net-zero composition bug; both the
flat oracle and line-vector product now classify change from the final document
generation rather than from individually changing rows.

## Evidence

The revision adds a 2,000-case Unicode/multiline differential lane, a 5,000-line
product no-flat-text action/Undo/Redo journey, overlap-before-build refusal,
exact duplicate coalescing, changed-range-only witness capture, equal multiline
no-copy behavior, suppressed-history no-copy behavior, and the permanent
`.artifacts/rev0991-line-vector-multirange-planning.json` witness. A development
probe matched 30,000 additional plans.

## Validation scope

Two disjoint focused batches passed 290 core history/planning/transaction tests
and 104 query-replace/macro/geometry/typing tests. Another 21 living-contract
tests and 61 archive/handoff/evidence tests passed. Doctor passed 19 + 9 + 3
bounded tests, portability passed 172/172 cases, and lint, formatting, context,
structural audit, and generated effect/resource checks passed. The current
release manifest records one clean 12-test batch but remains intentionally
partial, so no complete-full-suite claim is made.

## Remaining risk

Query-replace still owns one complete planning source; touched `ed.with-undo` and
immediate macro rows retain complete old/new generations; a huge changed logical
line still rebuilds one full string; `replace_lines()` copies the pointer vector;
exact-dirty may hash complete text; length-changing unrelated edits fail sparse
replay closed; sustained-use, signed release, and explicit platform evidence
remain incomplete.
