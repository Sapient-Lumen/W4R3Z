# Rev0983 audit — compact splice undo and mission correction

The deep audit is `docs/940-compact-splice-undo-mission-audit.md`.

## Heart of the mission

Micromax is a trustworthy, inhabitable editor for understandable least-authority automation. The language, VM, capability model, headless contracts, and release evidence are means by which configuration, macros, and plugins can remain explicit and recoverable during ordinary work. The project fails if proving boundaries becomes more important than making the editor calm enough to use every day.

## Severe corrected defect

Large saved buffers could opt into visible `fastdirty` and avoid whole-document hashing on each mutation, but ordinary undo still captured complete before/after document strings. Ten one-character edits to a 4,000,000-character buffer retained a median 40,021,417 traced bytes in the rev0982 snapshot reference shape. Rev0983 stores an exact inverse splice on the unambiguous one-cursor path; the corresponding median was 4,037,597 bytes, with 30,834 bytes of incremental traced growth after the first edit rather than 36,018,087 bytes.

## Missing or underweighted

- a visible per-buffer history byte budget and retained-text accounting;
- complete large delete/paste, fallback, save/recovery, search/replace/render, and cancellation journeys;
- sustained-use, taste, and flow evidence with release prominence comparable to safety proofs;
- a materially smaller coordinator extracted through net deletion;
- exact release locking, signed provenance, and an explicit filesystem/terminal/Windows support matrix; and
- documentation compaction so revision archaeology does not remain a parallel product.

## What should not change yet

Do not introduce a rope, piece table, undo tree, broker, watcher, background index, Wasm host, or generic owner registry by anticipation. Preserve the line-vector buffer and broad snapshot fallbacks until repeated product journeys establish a concrete unacceptable cost and exact replacement semantics.
