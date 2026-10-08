# Archive policy

## Compactness rules

- Prefer short markdown notes to large imported artifacts.
- Cite external work; do not warehouse PDFs in the long-term archive.
- Summarize source relevance in one or two sentences.
- Deduplicate aggressively.
- Keep revision history and other meta-surfaces ledger-style; `CHANGELOG.md` should normally have one detailed current entry plus a compact prior-revision table, not repeated multi-section boilerplate.
- Machine-readable surfaces must have distinct jobs; do not mirror the same payload across `RELEASES.json`, `REVISION-RECEIPT.json`, and `context-pack.json`.
- Keep `context-pack.json` route-first, deduped, and capped; it should point back into the archive rather than restating most of the archive.
- Keep entrypoint files table-first or checklist-first; when a matrix starts restating routing prose, collapse it back into links.
- Keep `ARCHIVE_INDEX.md` family-first and route-first; use `MANIFEST.json` for the exhaustive inventory instead of repeating long file-by-file dumps.
- Keep `docs/00-meta/llm-runbook.md` cluster-first and family-first; use route families and representative starts instead of long filename sprays.
- Keep `docs/10-framework/proposal-scorecard.md` scorecard-first; do not let it regrow a giant thesis paragraph or a redundant source-cues tail.
- Keep `docs/10-framework/open-questions.md` frontier-prompt-first; drop repeated "after the narrow waist / given the archive's compact..." scaffolding and point each open question straight to its first calibration memo.
- Keep `docs/10-framework/decision-procedure.md` checklist-first; use one short companion-routes block, not a long "keep X nearby" preamble.
- Keep `docs/10-framework/ideal-taxation-by-class-context-and-species.md` answer-first; compress repeated rule-intro scaffolding and use short `Route:` callouts instead of long routing sentences.
- Keep the founding-answer note top-light: after the title, give one compact direct answer and move quickly to the one-screen schedule instead of restating it in a second bullet layer.
- Keep `docs/10-framework/ai-exceptional-levy-trigger-routing.md` trigger-first and route-cluster-first.
- Keep `docs/00-meta/calibration-frontier-map.md` cluster-first and table-first; do not let it regrow into nine mini-memos with repeated "Use when / Main questions / Start files / Default outputs" boilerplate.
- Keep `docs/20-calibration/timing-cashflow-liquidity-deferral-and-prefunding-ladder.md` ladder-first; use `Companion routes`, a compact `Option scan`, and the five timing lanes rather than reopening long calibration scaffolding.
- Keep `docs/20-calibration/proceeds-visibility-local-share-and-earmarking-ladder.md` ladder-first; use `Companion routes`, a compact `Option scan`, and the five destination lanes rather than reopening long calibration scaffolding.
- Keep `docs/20-calibration/collection-anchor-choice-and-remittance-chain-ladder.md` ladder-first; use `Companion routes`, a compact `Option scan`, and the five anchor lanes rather than reopening long calibration scaffolding.

## Writing rules

- Distinguish **archive judgment** from **source-backed constraint**.
- Prefer one-line theses, ordered pattern packs, and short tests.
- Avoid ornamental quotations.
- When a distinction is load-bearing, name it early.

## Source rules

- Use authoritative or durable sources where possible.
- Keep a compact registry split across `SOURCES.md` and `SOURCES.json`: `SOURCES.md` is the human citation index (ID, title, URL only), while extended source notes live in `SOURCES.json`.
- Do not keep the same source under multiple IDs; merge duplicate URLs or titles and repoint citations.
- Do not let `SOURCES.md` regrow per-source explanatory blurbs once the same note already lives in `SOURCES.json`.
- In `archive/*.md`, prefer thin source-cues lines over redundant footnote tails.
- Machine-readable templates should be revision-neutral unless the revision itself is part of the modeled object.
- When a source supports multiple notes, point back to the same source ID rather than reproducing long background.
- Keep markdown citation clusters and source-footnote blocks deduped; repeated source IDs should be treated as an archive-lint failure, not harmless noise.
- Remove orphan `[S..]:` footnote definitions when inline citations disappear.
- Every markdown file that uses `[S..]` citations must carry matching local `[S..]:` definitions pointing back to `SOURCES.md`; the shared registry does not replace local link definitions.
- High-traffic reused markdown anchors should be explicit (`<a id="...">`) rather than relying only on heading-slug generation.
- Keep `MANIFEST.json` compact, and keep the builder in parity with that shape.
- Keep machine-readable JSON compact and revision-aligned; stale revision headers in active packets are archive-lint failures.

## Red lines

- no stored PDFs as archive canon
- no giant literature dumps
- no pretending a tax base is a moral subject
- no calling a machine a taxpayer merely because it is computationally salient
