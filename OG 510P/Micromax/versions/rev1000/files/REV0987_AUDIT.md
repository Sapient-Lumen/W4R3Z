# Rev0987 audit — macro first-write rollback and nested history integrity

The deep implementation, measurement, research, and residual-risk record is
`docs/944-macro-first-write-replay-transaction.md`.

## Heart of the mission

A tiny macro should feel like one trustworthy editor action. It must not copy
unrelated open documents, puncture an enclosing undo group, or leave ambiguous
history after failure. Transaction policy exists to protect that ordinary loop,
not to become a parallel bureaucracy.

## Severe corrected waste

Immediate macro replay previously joined complete text for every open buffer
before its first step. In the permanent eight-buffer × 1,000,000-character
witness:

- one-character success falls from 9 joins to 2 and median traced peak from
  9,036,532 B to 2,040,877 B (77.415%);
- edit-then-failure falls from 8 joins to 1 and peak from 20,891,005 B to
  2,638,654 B (87.369%); and
- navigation-only replay falls from 8 joins to 0 and peak from 8,027,256 B to
  34,573 B (99.569%).

The successful history row retains the same 2,000,001 logical text bytes and all
cases preserve exact return, forward/rollback, undo, and redo behavior.

## Shipped change

`play_macro()` now reuses the rev0986 first-write transaction owner. It captures a
text-free state shell, joins old text only immediately before a buffer's first
write, captures one text-free after shell, short-circuits navigation-only replay,
and materializes complete strings only for changed identities. The eager prior
control flow remains an executable oracle in tests and measurement tools.

Finalization failure restores editor state, history, input, and macro runtime
flags. Untouched buffers can be made join-forbidden in tests without affecting
successful or failed local replay.

## Correctness audit and refactor

The audit found a pre-existing nested suppression bug. Failed safe action-only
replay restored its saved undo snapshot while still inside the macro's
`suppress_recording()` guard. Inside `ed.with-undo`, the guard's later decrement
could consume the outer suppression level and allow a following edit to record a
stray row.

Rollback now occurs only after step-level suppression has unwound. Regressions
pin one- and two-level counts and the real hostcall journey: failed macro edit is
restored, a following edit remains suppressed, exactly one outer row commits, and
undo/redo are exact.

## Online design evidence

Scintilla keeps navigation outside document history, groups nested undo actions,
and makes selection-history memory cost explicit. VS Code separates transactional
edit application from explicit undo-stop policy. Qt gives nested edit blocks the
outermost user-visible scope. ProseMirror can exclude internal transactions from
history. Upstream micro stores text and undo handling with each buffer. Micromax
uses those only as directional evidence: global automation can span buffers, but
unrelated buffer text should not become transaction payload.

## Executed validation

- Rev0987 differential, failure-injection, nesting, authority, and measurement
  module: **71 passed**.
- Shared rev0986 first-write owner: **92 passed**.
- Macro authority, named macros, replay transactions, deferred authority,
  hostcall transactions, and `ed.with-undo`: **107 passed**.
- Relevant script-origin macro capability journeys: **4 passed**.
- Revision/context/living-doc/index contracts: **27 passed**.
- Effect-contract and structural-audit tests: **9 passed**.
- Portability oracle: **172/172 cases passed**.
- Compile and repository lint: passed; `mxaudit`, generated effect contracts,
  context lineage, and portable checks: passed.
- The permanent witness schema and exact join/retention/replay assertions: passed.

That is 274 focused behavioral test cases plus 36 handoff/effect/audit cases;
there is no full-suite claim. Mypy was not installed in the cloudtainer, so the
optional typecheck lane was skipped rather than reported as passed. Exact archive
provenance and verification live in the generated archive manifest.

## Missing or still risky

- Touched aggregate buffers still retain complete old/new generations.
- The non-text shell still copies broad sidecars and registers.
- Accepted query-replace remains a broad delayed session.
- Complete-result planners and very long lines remain allocation risks.
- Raw pre-observation aliases, private mutation, concurrent writers, process
  crash, external effects, and hostile Python/native code are outside rollback.
- Typing remains uncoalesced; logical `undobytes` is not total heap or RSS.
- Sustained-use/taste evidence, signed release provenance, and explicit platform
  support remain incomplete.

## Highest-value next work

Measure sustained typing retention and Undo boundaries in a real editing journey,
then implement only the coalescing policy that evidence supports. Measure long
accepted query-replace separately. Prefer net product behavior over another
owner registry or doctrine layer.
