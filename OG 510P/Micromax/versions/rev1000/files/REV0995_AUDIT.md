# Rev0995 audit — one-payload save and complete huge-line journey

## Priority chosen

Rev0994 explicitly left the complete very-long-line loop unmeasured. Rev0995 ran
that loop through viewport, literal search, movement, edit, Undo/Redo, recovery,
and save before considering segmentation. The journey stayed exact and locally
responsive; the sharper risk was repeated full-document work in the trust-critical
save path.

## Severe and wasteful findings corrected

- An ordinary dirty Unix/UTF-8 save materialized the document three times through
  `get_text()`, encoded commit and recovery separately, snapshotted undo and
  complete buffer state even though no pre-write mutation could occur, and then
  rejoined/re-encoded the generation to establish a clean baseline.
- A no-op `rmtrailingws=true` save eagerly copied and joined the complete document.
- Recovery checkpointing hashed identical recovery/commit bytes twice.
- Cleanup rollback became active only after the first mutation and undo recording
  had completed, so an exception during cleanup mutation itself could leave the
  live buffer changed before any disk write.
- The first lazy-whitespace refactor still created a transient prefix slice before
  the normalized vector; the audit removed that duplicate pointer container.

## Landing

- Ordinary Unix/UTF-8 no-cleanup save now uses one immutable payload for recovery,
  commit, writing, and exact clean-baseline hashing.
- DOS, non-UTF-8, and normalization lanes keep distinct representations and exact
  pre-cleanup recovery semantics.
- Undo-manager and full buffer snapshots exist only around a real cleanup
  mutation; before/after states reuse text already materialized for encoding.
- Cleanup rollback authority begins immediately before `set_text()` and restores
  text, sidecars, dirty/fastdirty state, version, generation signatures, and undo
  state after any mutation/write failure.
- No-op trailing-whitespace cleanup scans lazily without a full copy/join. Changed
  cleanup builds one normalized vector without a transient prefix slice.
- Recovery byte coercion preserves immutable identity, and checkpoint commit
  fingerprints reuse the payload digest when both contents alias.

## Measurement and qualification

The permanent 8,000,000-character journey found and projected the exact needle,
round-tripped movement, edit, Undo, and Redo, then saved exact bytes through one
recovery payload. Save performed one `get_text()`, no full signature recomputation,
no undo snapshot, and no buffer-state snapshot.

The controlled local preparation witness reduced `get_text()` calls from three to
one, median elapsed time by 29.021%, and CPython traced peak allocation by 60.195%
(40,197,979 to 16,000,893 bytes). These are cloudtainer attribution results, not
portable benchmark, RSS, total-memory, or filesystem claims. The recovery format
still expands a 2,000,000-byte payload to a 2,667,418-byte base64 JSON record.

## Evidence

The new regression lane covers ordinary one-payload save, codec aliasing, exact
recovery/commit identity, normalization with undo, failure during the first
cleanup mutation, DOS/LF signature separation, randomized Unicode signature
differentials, and single payload hashing. The measurement schema pins the
complete huge-line journey and save-work counters.

Focused save/recovery and legacy evidence passed 27 tests. Revision-index,
context, document-hygiene, structural-audit, and effect-contract gates passed 21
tests; three current-tree archive smoke tests also passed. Compile and lint pass.
The timely lane passed context, audit, lint, 172 portability cases, and doctor.

A combined evidence invocation exceeded its five-minute envelope after 38 passing
cases and no observed failure; it is not counted as a completed suite. Publication
therefore also exercises the real archive builder, its exact verifier, and
`unzip -t` rather than converting a timeout into a claim. The online comparison,
residual-risk analysis, and speculative next pressure are in
`docs/952-single-payload-save-clean-baseline-audit.md`.
