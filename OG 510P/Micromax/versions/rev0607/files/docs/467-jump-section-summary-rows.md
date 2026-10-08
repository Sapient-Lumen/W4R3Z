# jump section summary rows

Rev525 tightens one small trust/flow/headless-first seam in the jumplist loop: grouped jump history now has the same tiny broad-summary sibling many nearby picker surfaces already expose.

By rev524, Micromax already had a coherent four-part jumplist story except for one missing middle stop:

- plain `jumps` exposed the flat current/back/forward register for humans
- `ed.jump-history-rows` exposed the same ordered rows to scripts and future UIs
- `jumppick [QUERY]` / `ed.jump-section-rows` exposed grouped browse state by `Current` / `Back` / `Forward`
- `showjump INDEX|#N` / `jump-detail` / `ed.jump-detail-row` exposed one exact entry side-effect-free

That left one small but recurring question without a first-stop answer: before reopening grouped picker state or walking every grouped row, what jump buckets are visible right now and what does one representative entry look like?

Rev525 keeps the answer deliberately small and compatible:

- `showjumpgroups [QUERY]` now prints tiny count-aware jumplist buckets for `Current` / `Back` / `Forward`
- `jump_section_summary_rows(QUERY)` / `ed.jump-section-summary-rows` expose the same `[[label count sample_name sample_detail] ...]` rows headlessly
- `jump-section-summaries` mirrors that hostcall inside Micromax scripts
- command-bar completion for `showjumpgroups` now reuses the same summary rows, so one visible bucket keeps count/sample metadata visible instead of collapsing back to a bare label

The sample row stays intentionally tiny and honest:

- `label` is one visible group name like `Current`, `Back`, or `Forward`
- `count` is the number of grouped picker rows in that bucket
- `sample_name` is one representative visible slot like `#2`
- `sample_detail` keeps the same small orientation truth Micromax already knows, such as `buffer @ line:col — preview`

That matters because grouped jump history is already first-class inside the archive. Once Micromax can already tell you the exact grouped buckets behind `jumppick`, humans and future LLMs should not have to reopen transient picker state or scrape every grouped row just to ask which buckets are visible.

So the jumplist story now stays coherent at four scales:

- flat register: `jumps` / `ed.jump-history-rows`
- grouped browse state: `jumppick [QUERY]` / `ed.jump-section-rows`
- grouped summaries: `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows`
- exact entry detail: `showjump INDEX|#N` / `ed.jump-detail-row`

The goal is simple: if Micromax already knows the grouped jumplist sections behind `jumppick`, the archive should expose one tiny first-stop summary of those buckets too.
