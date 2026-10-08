Rev501 note: exact `showrecent PATH` / `ed.recent-detail-row` inspection now keeps the same tiny disk/action truth as first-class palette `Recent Files` rows, so one MRU target can say `existing file` or `new file` plus `current buffer` / `switch buffer` / `empty buffer @ 1:0` before any reopen or buffer switch; `docs/443-showrecent-detail-truth.md` records why that small trust follow-up matters.

# Exact recent-file detail truth (rev501)

Micromax already had two nearby honest surfaces:

- exact `recent_detail_row(PATH)` / `showrecent PATH` rows kept MRU index plus active/open/dirty/readonly/cursor state visible
- first-class palette `Recent Files` rows already reused that exact MRU metadata and, after rev497/rev500, also appended capability-gated `existing file` / `new file` plus tiny action truth like `current buffer`, `switch buffer`, or `empty buffer @ 1:0`

But one adjacent inspectability seam still lagged behind that model: the exact row surface the palette was derived from still stopped at section/detail metadata. That made the narrow explicit answer less honest than the browse row beside it exactly where trust matters most: when a human or future LLM wants to inspect one MRU target before deciding whether Enter is a boring reopen, a live-buffer revisit, or a missing-path surprise.

Rev501 keeps the fix tiny:

- `recent_detail_row(PATH)` now appends two new trailing fields: `disk_truth` and `action_truth`
- `disk_truth` reuses the same capability-gated `existing file` / `new file` check already trusted by adjacent palette recent-file rows
- `action_truth` reuses the same live-buffer cue (`current buffer` / `switch buffer`) and the same missing-path fallback (`empty buffer @ 1:0`)
- plain `showrecent PATH` now formats those cues too, and exact `showrecent` completion rows reuse them instead of flattening back to section/detail only

The intent is simple: if Micromax already knows the boring file-open truth for one exact recent-file target, the exact side-effect-free inspection surface should say that truth directly instead of making callers correlate a separate palette row.
