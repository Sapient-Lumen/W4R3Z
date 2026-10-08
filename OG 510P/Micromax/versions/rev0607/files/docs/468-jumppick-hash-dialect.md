# jumppick hash dialect

Rev526 tightens one tiny remaining jumplist dialect seam: the live searchable picker now speaks the same visible `#N` slot token as the adjacent flat, grouped, and exact jumplist surfaces.

By rev525, Micromax already had most of the jumplist loop aligned:

- `jumps` printed the flat current/back/forward register with visible `#N` ids
- `showjump INDEX|#N` / `jump-detail` / `ed.jump-detail-row` accepted that same visible slot token for exact side-effect-free inspection
- `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows` already used `#N` sample names when summarizing grouped `Current` / `Back` / `Forward` state
- `jumppick [QUERY]` / `ed.jump-section-rows` exposed the live grouped picker state

But the actual picker still lagged behind the dialect the rest of the archive already showed:

- jump prompt rows still inserted bare `N`
- a literal typed `jumppick #N` query no longer matched as the obvious exact visible slot
- picker submit parsing still treated `#N` as invalid even though adjacent jump surfaces already accepted it

Rev526 keeps the fix deliberately small and compatible:

- `jump_prompt_rows()` now expose visible `#N` insert keys
- jumplist row ranking treats `N` and `#N` as the same visible slot for picker queries
- picker submit parsing now accepts the same `#N` token directly

That matters because the jumplist story is now coherent at every nearby scale:

- flat register: `jumps` / `ed.jump-history-rows`
- grouped browse state: `jumppick [QUERY]` / `ed.jump-section-rows`
- grouped summaries: `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows`
- exact entry detail: `showjump INDEX|#N` / `ed.jump-detail-row`

If the archive already shows a human one jump entry as `#N`, the live picker should not be the one remaining place that falls back to a different token or rejects the visible one.

The goal is simple: visible jumplist slot identity should stay in one dialect from inspection through selection.
