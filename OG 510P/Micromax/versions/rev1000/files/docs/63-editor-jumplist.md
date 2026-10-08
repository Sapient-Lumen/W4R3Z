Rev0952 note: plugin recovery restore now preserves valid jumplist index 0; successful reload and failed-reload rollback no longer leave one restored row with a false current index of -1.

Rev536 note: plain `jumppick` command-bar completion now previews live jumplist inventory too — the exact command row keeps its ordinary command doc while replacing the blank hint with either `N jumps · current #N [lane depth] buffer @ line:col` or `0 jumps`, and `docs/478-jumppick-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev536): this is a small trust/flow follow-up to rev527/rev529/rev531/rev533/rev535's jumplist cleanup. Micromax already had the important nearby pieces: `jumppick N|#N` argument completion already reused exact row metadata before submit, typed slot misses and submit feedback already stayed in the visible `#N [lane depth]` dialect, plain `jumps` / `showjumpgroups` / `showjump` now previewed the live register, grouped counts, and current exact slot before Enter, and `status_model()` already exposed a stable jumplist snapshot headlessly. But one tiny entry-point seam still lingered at the command's own no-arg row: typing plain `jumppick` in the command bar still showed an empty generic hint even though Micromax already knew how many visible jump slots existed and which one was current. Rev536 keeps the fix deliberately small and compatible: new `_prompt_jumppick_command_row(...)` reuses `jump_navigation_model()` truth, exact command completion for plain `jumppick` now swaps the blank hint for either `N jumps · current #N ...` or `0 jumps`, focused tests pin both populated and empty inventories, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/478-jumppick-command-preview.md` record the intent. The goal is simple: if Micromax already knows the live jumplist inventory, the picker's own entry point should say so before Enter instead of going blank.

Rev535 note: plain `showjump` command-bar completion now previews the current visible jumplist slot too — the exact command row keeps its ordinary command doc while replacing the generic provenance hint with either `current #N [lane depth] buffer @ line:col · expects INDEX|#N` or `no jumps · expects INDEX|#N`, and `docs/477-showjump-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev535): this is a small trust/flow follow-up to rev524/rev531/rev533/rev534's jumplist cleanup. Micromax already had the important nearby pieces: `showjump INDEX|#N` argument completion already reused exact row metadata before submit, plain `jumps` now previewed the live flat register before Enter, plain `showjumpgroups` now previewed grouped `Current` / `Back` / `Forward` section/sample truth before Enter, and `status_model()` already exposed stable current jump state headlessly. But one tiny exact-inspection seam still lingered at the command's own entry point: typing plain `showjump` in the command bar still showed only a generic command doc row, so humans and future LLMs had to type a slot first or reopen a neighboring jumplist surface just to confirm whether any current visible jump existed. Rev535 keeps the fix deliberately small and compatible: new `_prompt_showjump_command_row(...)` reuses `jump_navigation_model()` current-row truth, exact command completion for plain `showjump` now swaps its generic info hint for either `current #N ... · expects INDEX|#N` or `no jumps · expects INDEX|#N`, focused tests pin both populated and empty inventories, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/477-showjump-command-preview.md` record the intent. The goal is simple: if Micromax already knows the current visible jump slot, the exact inspection command should say so before asking for one more token.

Rev534 note: command-bar completion for plain `showjumpgroups` now previews grouped jumplist state too — the exact command row keeps its ordinary command doc while replacing the generic provenance hint with grouped-summary truth, and after rev577 that no-arg preview now uses the same neutral `LABEL: N | e.g. ...` section/sample dialect as neighboring grouped inspectors instead of flattening back to counts-only bucket totals; `docs/476-showjumpgroups-command-preview.md` and `docs/519-showjumpgroups-sample-preview.md` record why that tiny trust/flow follow-up matters.

Latest tiny landing (rev534): this is a small trust/flow follow-up to rev525/rev531/rev533's jumplist cleanup. Micromax already had the important nearby pieces: `showjumpgroups [QUERY]` already printed grouped `Current` / `Back` / `Forward` counts after Enter, `showjumpgroups QUERY` argument completion already reused exact section-summary rows, plain `jumps` now previewed the live flat register before Enter, and `status_model()` already exposed stable jumplist-navigation state headlessly. But one tiny grouped-inspection seam still lingered exactly at the no-arg `showjumpgroups` entry point: typing plain `showjumpgroups` in the command bar still showed only a generic command doc row, so humans and future LLMs had to press Enter just to confirm whether any grouped buckets were visible and how many jumps sat in each one. Rev534 keeps the fix deliberately small and compatible: new `_prompt_showjumpgroups_command_row(...)` reuses `jump_section_summary_rows('')`, exact command completion for plain `showjumpgroups` now swaps its generic info hint for `N section(s), M jump(s) · ...`, focused tests pin both populated and empty grouped inventories, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/476-showjumpgroups-command-preview.md` record the intent. The goal is simple: if Micromax already knows the grouped jumplist buckets, the command bar should show that truth before Enter too.

Rev533 note: command-bar completion for plain `jumps` now previews the live jumplist register too — the exact command row keeps its ordinary command doc while replacing the generic provenance hint with either `0 jumps` or `N jumps · #current ...`, and `docs/475-jumps-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev533): this is a small trust/flow follow-up to rev531/rev532's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` printed the flat visible register after Enter, `jumpback` / `jumpforward` command rows already previewed exact next targets, and `status_model()` / `showstatus` already exposed structured `jump_current_*`, `jump_back_*`, `jump_forward_*`, and `jump_navigation_*` state. But one tiny direct-inspection seam still lingered exactly at the no-arg `jumps` entry point: typing plain `jumps` in the command bar still showed only a generic command doc row, so humans and future LLMs had to press Enter just to confirm whether any visible jump slots existed and which `#N` row was current. Rev533 keeps the fix deliberately small and compatible: new `_prompt_jumps_command_row(...)` reuses the stable jump-navigation snapshot, exact command completion for `jumps` now swaps its generic hint for either `0 jumps` or `N jumps · ...`, focused tests pin both populated and empty inventories, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/475-jumps-command-preview.md` record the intent. The goal is simple: if Micromax already knows the current visible jumplist register, the command bar should show that truth before Enter instead of hiding it behind one more no-arg command.

Rev532 note: command-bar completion for plain `jumpback` / `jumpforward` now previews the exact next jumplist slot too — their command rows keep the ordinary command doc while swapping the generic provenance hint for either `next #N [lane depth] buffer @ line:col` or an explicit no-op cue like `no earlier jump`, and `docs/474-jump-navigation-command-preview.md` records why that tiny trust/flow follow-up matters.

Latest tiny landing (rev532): this is a small trust/flow follow-up to rev530/rev531's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumpback` / `jumpforward` now kept visible slot/lane truth on success, `status_model()` / `showstatus` already exposed structured `jump_current_*`, `jump_back_*`, `jump_forward_*`, and `jump_navigation_*` state, and adjacent exact command-bar paths like `showjump INDEX|#N` and `jumppick N|#N` already previewed the exact row they would use before submit. But one tiny flow seam still lingered exactly at the simplest command-bar entry point: typing plain `jumpback` or `jumpforward` still showed only a generic command doc row, so humans and future LLMs had to press Enter, reopen `showstatus`, or inspect `jumps` just to learn what that no-arg command would do right now. Rev532 keeps the fix deliberately small and compatible: new `_prompt_jump_navigation_command_row(...)` reuses the same side-effect-free jumplist peek helpers as the adjacent status/feedback paths, command completion rows for `jumpback` / `jumpforward` now replace their generic info hint with either `next #N [lane depth] buffer @ line:col` or an explicit no-op cue, focused tests pin both actionable and no-op command-bar previews, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/474-jump-navigation-command-preview.md` record the intent. The goal is simple: if Micromax already knows the exact next visible jumplist row, the command bar should show that truth before Enter instead of making callers infer it later.

Rev531 note: `status_model()` / `showstatus` now expose a tiny structured jumplist-navigation snapshot too — callers can inspect the current visible `#N` row plus immediate `jumpback` / `jumpforward` targets through `jump_current_*`, `jump_back_*`, `jump_forward_*`, `jump_navigation_summary`, and `jump_navigation_action_summary` without scraping transient messages, and `docs/473-jump-navigation-status-model.md` records why that small trust/headless-first follow-up matters.

Latest tiny landing (rev531): this is a small trust/headless-first follow-up to rev341/rev455/rev524/rev525/rev526/rev527/rev528/rev529/rev530's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` exposed visible `#N` entry ids, `showjump INDEX|#N` / `ed.jump-detail-row` already kept exact lane/depth/buffer/position/preview truth inspectable, `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows` already summarized grouped `Current` / `Back` / `Forward` buckets, `jumppick [QUERY|N|#N]` already kept the same visible-slot dialect through preview, miss, and success paths, and rev530 kept plain `jumpback` / `jumpforward` success in that same visible-slot/lane dialect too. But one tiny headless-first seam still lingered underneath the same everyday history loop: future UIs, scripts, tests, and LLMs still had to reopen `jumps` or scrape the last transient message just to learn whether `jumpback` / `jumpforward` were actionable and which visible slot was current. Rev531 keeps the fix deliberately small and compatible: new `Editor.jump_navigation_model()` now exposes the current visible row plus the immediate back/forward neighbors through stable `jump_current_*`, `jump_back_*`, `jump_forward_*`, `jump_navigation_summary`, and `jump_navigation_action_summary` fields, `status_model()` / `ed.status` include that same data, plain `showstatus` / `ed.status-summary` now mirror it as `jump_nav=` / `jump_actions=`, focused tests pin both the structured status fields and the human summary output, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/63-editor-jumplist.md` / `docs/97-statusline.md` plus `docs/473-jump-navigation-status-model.md` record the intent. The goal is simple: if Micromax already exposes visible jumplist truth elsewhere, the stable status snapshot should answer the same actionability question without scraping messages too.

Rev530 note: plain `jumpback` / `jumpforward` now keep the same visible jumplist slot and lane truth on success too — feedback now says `jumpback #N [back 1] -> target` or `jumpforward #N [forward 1] -> target` using the pre-move exact row, and `docs/472-jump-navigation-slot-feedback.md` records why that tiny trust/headless-first follow-up matters.

Latest tiny landing (rev530): this is a small trust/headless-first follow-up to rev341/rev455/rev524/rev525/rev526/rev527/rev528/rev529's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` exposed visible `#N` entry ids, `showjump INDEX|#N` / `ed.jump-detail-row` already kept exact lane/depth/buffer/position/preview truth inspectable, rev526 made the live `jumppick` prompt itself speak visible `#N` slots, rev527 taught command-bar completion for `jumppick N|#N` to preview that same exact row before submit, rev528 kept exact slot misses honest, and rev529 kept successful `jumppick` submits in that same visible-slot dialect. But one tiny trust seam still lingered in the simplest everyday history loop: plain `jumpback` / `jumpforward` still flattened success back to a generic landed-target message, which hid which visible slot and lane had just run. Rev530 keeps the fix deliberately small and compatible: new `Editor._peek_jump_navigation_detail_row(...)` captures the pre-move exact row, `JumpBack` / `JumpForward` actions plus `jumpback` / `jumpforward` commands now report `jumpback #N [back 1] -> target` or `jumpforward #N [forward 1] -> target`, focused tests pin both action and command feedback, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/472-jump-navigation-slot-feedback.md` record the intent. The goal is simple: if Micromax already exposes visible jumplist slots elsewhere, one-step history navigation should preserve that same truth too.

Rev528 note: direct `jumppick N|#N` misses now stay in an exact jumplist dialect too — if the typed visible slot does not exist, Micromax now reports `jumppick: no such jump: TOKEN` instead of collapsing that direct request back into a generic fuzzy `0 jump(s)` summary, and `docs/470-jumppick-exact-miss.md` records why that tiny trust/headless-first follow-up matters.

Latest tiny landing (rev528): this is a small trust/headless-first follow-up to rev417/rev455/rev524/rev525/rev526/rev527's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` exposed visible `#N` entry ids, `showjump INDEX|#N` already kept exact side-effect-free lookup and typed misses honest, `showjumpgroups [QUERY]` already summarized grouped `Current` / `Back` / `Forward` buckets, rev526 made the live `jumppick` prompt itself speak visible `#N` slots, and rev527 taught command-bar completion for `jumppick N|#N` to preview exact lane/depth/buffer/position/preview truth before submit. But one tiny trust seam still lingered exactly at failure time: after all that exact-slot work, submitting a missing direct `jumppick N|#N` target still collapsed back into the generic fuzzy-search message `jumppick QUERY: 0 jump(s)`. Rev528 keeps the fix deliberately small and compatible: direct slot-shaped `jumppick` misses now report `jumppick: no such jump: TOKEN`, ordinary fuzzy name/content queries still keep the existing counted zero-summary path, focused tests pin both exact-miss and fuzzy-zero behavior, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` plus `docs/470-jumppick-exact-miss.md` record the intent. The goal is simple: if Micromax already treats `jumppick #N` as an exact visible-slot request, the failure path should say so too.

Rev527 note: command-bar completion for `jumppick` now reuses the same exact jumplist row truth too — typing `jumppick N` or `jumppick #N` now offers direct visible-slot candidates with lane/depth/buffer/position/preview metadata before submit, and `docs/469-jumppick-command-completion.md` records why that tiny trust/flow/headless-first follow-up matters.

Latest tiny landing (rev527): this is a small trust/flow/headless-first follow-up to rev417/rev455/rev524/rev525/rev526's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` exposed visible `#N` entry ids, exact `showjump INDEX|#N` / `ed.jump-detail-row` already gave side-effect-free slot truth, `showjumpgroups [QUERY]` already summarized grouped `Current` / `Back` / `Forward` buckets, and rev526 made the live `jumppick` prompt itself speak the same visible `#N` slot dialect. But one tiny flow seam still lingered exactly where humans and future LLMs often commit that jump from the command bar: `jumppick N|#N` was valid, yet command-bar completion still offered no direct slot candidates or exact row preview while adjacent `showjump` completion already did. Rev527 keeps the fix deliberately small and compatible: one shared exact-jump prompt-row helper now powers both `showjump` and `jumppick`, `jumppick` command-bar completion now offers `N` or `#N` candidates depending on the typed prefix, focused tests pin both bare-slot and visible-slot completion rows, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` / `docs/43-worklist.md` plus `docs/469-jumppick-command-completion.md` record the intent. The goal is simple: if `jumppick #N` is already a valid move, the command bar should show what that visible slot means before you commit.

Rev526 note: jumplist picker rows now keep the same visible slot dialect too — `jumppick` suggestion rows insert `#N`, typed `jumppick #N` now filters/submits directly, and the picker submit path accepts the same visible hash-prefixed token instead of treating it as invalid; `docs/468-jumppick-hash-dialect.md` records why that tiny trust/flow/headless-first follow-up matters.

Latest tiny landing (rev526): this is a small trust/flow/headless-first follow-up to rev417/rev455/rev524/rev525's jumplist cleanup. Micromax already had the important nearby pieces: plain `jumps` exposed visible `#N` entry ids, exact `showjump INDEX|#N` / `ed.jump-detail-row` understood the same visible token side-effect-free, and `showjumpgroups [QUERY]` already used `#N` sample names when summarizing grouped `Current` / `Back` / `Forward` state. But one tiny dialect seam still lingered exactly where humans and future LLMs actually moved through history: the live `jumppick` prompt itself still centered bare `N` insert keys and treated a literal `#N` submit as invalid even though every adjacent jumplist surface already advertised `#N`. Rev526 keeps the fix deliberately small and compatible: `jump_prompt_rows()` now expose visible `#N` insert keys, jumplist query ranking now treats `N` and `#N` as the same visible slot, picker submit parsing accepts that same `#N` token, focused tests pin the prompt/query/submit contract, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/55-editor-command-bar.md` / `docs/63-editor-jumplist.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` / `docs/43-worklist.md` plus `docs/468-jumppick-hash-dialect.md` record the intent. The goal is simple: if Micromax already shows one jump entry as `#N`, the searchable jumplist picker should speak that same visible token too.

# Editor jumplist (navigation history)

A **jumplist** is navigation history: a small list of cursor/selection states that
lets you jump backward/forward through "places you've been".

This is **not undo**:
- Undo is about **edits**.
- Jumps are about **locations**.

Micromax-editor keeps a **per-buffer** jumplist, capturing the full cursor set:
- cursor positions (multi-cursor)
- selection anchors (directed)
- cursor ids (for "remove latest cursor" semantics)
- primary cursor index

## Semantics

- `PushJump` appends the current cursor/selection state.
- If you've jumped backward and then push a new jump, the "forward" tail is
  discarded (browser/Vim-style).
- Consecutive identical entries are deduplicated.
- The list is bounded (currently 100 entries).

## Actions

- `PushJump` — save current cursor/selection state to the jumplist.
- `JumpBack` — restore the previous jumplist entry.
- `JumpForward` — restore the next jumplist entry.
- `jumpback` / `jumpforward` — tiny command-bar mirrors for the same traversal.
  - successful traversal now keeps the chosen visible slot and lane truth too: `jumpback #N [back 1] -> buffer @ line:col` / `jumpforward #N [forward 1] -> buffer @ line:col`
- `jumps` — show the current jumplist register as a small count-aware inventory line.

## Hostcalls

- `ed.push-jump` ( -- ok )
- `ed.jump-back` ( -- ok )
- `ed.jump-forward` ( -- ok )
- `ed.jump-info` ( -- [index size] )
- `ed.jump-history-rows` ( -- rows ) — ordered jumplist register rows as `[lane depth index buffer position preview]`
- `ed.jump-detail-row` ( n|"#n" -- row|0 ) — exact jumplist row as `[query index lane depth buffer position preview]` behind plain `showjump INDEX|#N`
- `ed.status` / `status_model()` now also expose tiny `jump_current_*`, `jump_back_*`, `jump_forward_*`, and `jump_navigation_*` fields so future UIs/scripts/LLMs can tell whether `jumpback` / `jumpforward` are actionable without scraping transient messages
- `ed.clear-jumps` ( -- )
- `ed.jump-section-rows` ( query -- sections ) — grouped rows for future pickers/UIs (`Current` / `Back` / `Forward`)
- `ed.jump-section-summary-rows` ( query -- rows ) — tiny count-aware jumplist-section rows as `[[label count sample_name sample_detail] ...]` behind plain `showjumpgroups [QUERY]`

## Default bindings (host baseline, mirrored by the core plugin)

We currently bind:
- `Alt-j` → `PushJump`
- `Alt-LeftArrow` → `JumpBack`
- `Alt-RightArrow` → `JumpForward`

(We avoid `Ctrl-i` because many terminals treat it as `Tab`.)


## Register (rev417)

The same jumplist trail is now inspectable without opening the picker:

- Command: `jumps`
  - prints a count-aware summary of the current buffer's jumplist register
  - rows appear in register order: `current`, then `back`, then `forward`
- Hostcall: `ed.jump-history-rows`
  - returns ordered rows as `[lane depth index buffer position preview]`

This stays intentionally small. The goal is not a second navigation browser; it is a tiny, honest register surface for humans, scripts, and future UIs.


## Picker (rev64)

A jumplist is most useful when you can *see* it.

- Command: `jumppick [QUERY|N|#N]`
  - opens a searchable prompt over the current buffer's jumplist
  - selecting an entry restores that cursor/selection snapshot
  - command-bar completion for `jumppick N|#N` now also reuses the same exact slot truth as `showjump`, so direct slot picks can show lane/depth/buffer/position/preview metadata before submit
  - successful submits now keep that same visible-slot truth in the final message too: `jumppick #N [lane depth] -> buffer @ line:col`

Notes:
- Entries are now grouped by relation to the active jump: `Current`, then `Back`, then `Forward`.
- The insert key now stays in the same visible dialect as adjacent `jumps` / `showjump` surfaces: a **1-based `#N` jumplist slot**. Typed picker queries can still use `N` or `#N`, and fuzzy search still matches the line preview and position metadata.
- The same grouping is available headlessly through `ed.jump-section-rows`, so future UIs/LLMs do not need to reverse-engineer picker sections from row text.
- `showjumpgroups [QUERY]` / `ed.jump-section-summary-rows` now expose the lighter count-aware sibling of that same grouped state too, so callers can inspect which `Current` / `Back` / `Forward` buckets are visible without reopening the picker or walking every grouped row.


## Runtime authority (rev793)

The jumplist is now treated as recovery state with provenance, not a raw scratch list.  `EditorBuffer.jump_list_authority` records who created each jump row.  In script context, Micromax now refuses to clear trusted/user rows, truncate a trusted forward tail by pushing a new jump, evict trusted rows from the bounded history, or traverse trusted rows with `jumpback` / `jumpforward` / direct index jumps.

Scripts can still create and navigate their own jumplist rows, and same-origin script rows can be cleared by that origin.  Missing legacy sidecar rows default to trusted authority so older editor/user navigation history does not become script-owned by accident.

## Auto-push for jump commands (rev22)

Some commands are "jump-worthy" (they move the primary cursor far enough that users often want to go back).
When the `jumplist.auto` option is enabled (default), the command-bar commands:

- `goto`
- `jump`

will record **both** the "from" and "to" locations so that `JumpBack` can immediately return.

Rev333 is a tiny UX follow-up: successful `goto` / `jump` / `helpjump` command-path navigation now also reports the real landed target (`name @ line:col`), so the jumplist can stay correct *and* the user does not have to infer where the move ended. Rev334 closes the picker-shaped gap by making `jumppick` report that same landed target too, and rev529 keeps the selected visible slot/lane in that final picker feedback instead of collapsing back to generic `jump: ...`.

## Feedback (rev341)

Rev341 makes actual jumplist traversal speak the same explicit-orientation dialect as recent `open`, `buffer`, `help`, `mark`, and committed `find` work. Successful back/forward traversal now reports the landed target:

- `jumpback #N [back 1] -> name @ line:col`
- `jumpforward #N [forward 1] -> name @ line:col`

No-op traversal is explicit too:

- `jumpback: no earlier jump`
- `jumpforward: no later jump`

That applies to both the `JumpBack` / `JumpForward` actions and the tiny `jumpback` / `jumpforward` command-bar commands. The aim is small but important: when users ask to go back, the editor should confirm where “back” actually is.

## Exact inspection

Rev455 closes the small exact sibling of the jumplist loop too. If a human, script, or future UI already knows the 1-based entry index from `jumps` or `jumppick`, `showjump INDEX|#N` and `jump_detail_row(INDEX|#N)` / `ed.jump-detail-row` now answer the next question without mutating history:

- `[query index lane depth buffer position preview]`
- example: `showjump 1 [back 1] a @ 1:0 — one`
- same visible-token path: `showjump #1 [back 1] a @ 1:0 — one`

Rev525 adds the matching broad-summary sibling too: `showjumpgroups [QUERY]` / `jump_section_summary_rows(QUERY)` / `ed.jump-section-summary-rows` report tiny `[[label count sample_name sample_detail] ...]` rows such as `Current: 1 (e.g. #2 — a @ 2:1 — two)` without reopening `jumppick`.

That keeps jumplist history coherent at five adjacent scales: flat register, grouped browse state, broad grouped summaries, one exact side-effect-free row, and the tiny stable `jump_*` status snapshot for immediate actionability.
