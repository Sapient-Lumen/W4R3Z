# Rev0984 audit — retained-history ownership and transaction compaction

The deep audit is `docs/941-retained-history-budget-transaction-snapshot-compaction.md`.

## Heart of the mission

Micromax is a calm, trustworthy editor for understandable least-authority end-user automation. Its VM, capability boundaries, worker owners, headless models, and evidence are valuable when they make daily editing explicit, recoverable, and pleasant; they are not the product by themselves.

## Severe corrected defects

History had no byte ownership after rev0983's compact splice correction. Large deletes and broad fallbacks could accumulate without a visible limit. Rev0984 adds exact logical retained-text charges, a local 32 MiB `undobytes` soft budget, complete-oldest-row truncation, preserved newest recovery, visible trim/overage feedback, and `undostatus`.

Aggregate transactions also retained full before/after state for every open buffer even when only one changed. In the permanent three-buffer, 4,000,000-character witness, the rev0983 retained shape held six full-text rows and 24,000,001 bytes. Changed-buffer retention holds two rows and 8,000,001 bytes; median traced current allocation falls 66.636%. Successful after-snapshots reuse unchanged text by version.

A hot-path audit found that snapshot capture used an eager `getattr` default, so every snapshot joined and hashed every open document even when the saved signature existed. The fallback is now explicit and receives the already captured/reused text.

A second hot-path audit caught a flaw in the initial budget implementation before packaging: every edit rescanned all history and oldest-row trimming shifted a list prefix. Undo now maintains cached per-stack/per-owner totals and deque-backed stacks. A 20,000-row deterministic probe records zero historical charge reads for status plus a no-op budget check and one read for one retired row. Consecutive mutation-compatible budget feedback now replaces its controlled tail: trim totals accumulate and repeated soft-overage rows describe only the newest retained action. This prevents either ordinary expiry or a deliberately tiny limit from creating a second unbounded per-edit message history, while lower authority cannot erase protected rows.

## Missing or still risky

- Initial rollback capture remains broad, so peak traced allocation falls only 28.354% in the default witness.
- One oversized newest row is preserved and may exceed `undobytes`; there is no hard outer limit.
- Multi-cursor, query-replace, line-plan, and changed-buffer aggregate rows can still retain complete snapshots.
- Logical text accounting excludes callback/object overhead, native memory, RSS, allocator arenas, and metadata-only history.
- The global linear stack means satisfying one buffer's local limit can retire an older row for another buffer as part of the only chronology-safe prefix.
- Tiny typing rows are not coalesced, and sustained-use/product evidence still trails boundary evidence.
- Signed/hermetic release and explicit Windows/filesystem/terminal support evidence remain incomplete.

## What should change next

Complete one large retained-history product journey before adding architecture. If multi-cursor snapshot retention dominates, compact that existing simultaneous-edit plan with atomic old-slice validation. Measure sustained typing before specifying coalescing or a secondary row limit. Prototype first-write transaction capture only behind a narrow path and keep broad rollback as the differential oracle. Extract a history owner only when it deletes more `Editor` policy than it adds.

## What should not change yet

Do not add an undo tree, independent per-buffer transaction graph, rope, piece table, broker, watcher, background index, generic owner registry, or Wasm host by anticipation. The current correction is measurable, local, user-visible, and exact about its residuals.

## Release-context audit

The final archive lane exposed a bounded-handoff regression: twelve recent revision entries now required 66 document paths against the declared 64-path context ceiling. The generator now retains the newest eleven revisions, preserving all current and core evidence while aging the oldest catalog-backed entry out deliberately. This is a rollover correction, not another registry.

The first otherwise-valid archive then exposed a more serious evidence break: `.artifacts/rev0984-history-retention.json` was named by the context and revision ledger but omitted by a fixed four-name artifact allowlist. Packaging now recognizes a narrow canonical per-revision receipt convention instead of adding another name to that registry, validates strict object JSON, enforces a 1 MiB per-file ceiling, and binds the included bytes into normal archive provenance.
