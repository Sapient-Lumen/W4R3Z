# Rev0990 audit — atomic line-vector sparse replay and long-line attribution

The deep implementation, measurement, online research, and residual-risk record
is `docs/947-line-vector-sparse-replay-long-line-audit.md`.

## Heart of the mission

A tiny accepted replacement or multicursor edit should remain tiny when the user
undoes it. Rev0990 keeps exact atomic history while removing complete-document
current/result strings from sparse product replay under fast-dirty policy.

## Severe corrected waste

The permanent 1,099,999-character, 11,000-line, 128-splice witness removes two
complete reads, two complete writes, and two complete replay-result strings over
Undo plus Redo. Traced peak Python allocation falls from 6,059,264 B to
569,036 B (90.609%) and 10,872 of 11,000 line string objects are reused. Both
paths round-trip exactly. The product path is locally slower (0.029138 s versus
0.012062 s), so this is an honest memory-shape correction rather than a latency
claim.

## Shipped change

Sparse witness replay now shares one direction/validation core, resolves offsets
against a compact line-start index, validates every target before mutation,
walks the source vector once, joins only touched output lines, reuses complete
untouched strings, and publishes one detached vector through one buffer mutation.
The old flat replay remains a pure oracle and exceptional query-replace checker.

## Long-line audit

A 1,100,000-character one-line journey covers insertion, Backspace, Delete, and
replacement with exact text/cursor/Undo/Redo oracles. Fast-dirty eliminates every
post-mutation exact signature pass and reduces local elapsed time about 61–68%
versus the explicit exact-dirty policy. Immutable line rebuilding remains real,
but this witness does not justify a piece tree, rope, or gap-buffer migration.

## Evidence

The new tests include 2,000 seeded multiline/Unicode differential plans, stale
later-slice atomic refusal, line-object identity reuse, and a product trap proving
Undo/Redo call neither `get_text` nor `set_text` and commit once each. The
permanent machine-readable witness is
`.artifacts/rev0990-line-vector-replay-long-line.json`.

## Validation scope

Two disjoint bounded subsystem batches passed: 110 core history, retention,
measurement, authority, and transaction tests; and 216 multicursor,
query-replace, macro, viewport-typing, and generation-journey tests. The doctor
preflight passed its 19 + 9 + 3 bounded tests, the portability corpus passed
172/172 cases, and lint, formatting, generated effect contracts, context, and
structural audit checks passed.

A monolithic runner collected 3,439 tests but exceeded the cloudtainer command
window before completion. Its process group was terminated, so this revision
makes no complete-full-suite claim.

## Remaining risk

Multi-range planning and query-replace planning still own complete strings;
exact-dirty can still hash complete text; one huge logical line still rebuilds
one immutable line; aggregate transaction rows remain broad; length-changing
unrelated edits before sparse offsets fail closed; signed/hermetic and explicit
cross-platform release evidence remain incomplete.
