# Roadmap (rough)

This is intentionally coarse. The decisions log is the source of truth.

For *current priorities*, see `TODO.md` and `docs/43-worklist.md`.

## Language / VM

- **Rev1–3**: Python-hosted VM, wordlists, errors, hostcalls, dev tooling, budgets.
- **Rev4–6**: deferred words + locals + dynamic send + reload/unrequire + host API versioning.
- **Rev7–10**: embed into editor substrate; keep growing ergonomics while staying small.

Near-term language low-hanging fruit:
- dict/map type (structured plugin state)
- a tiny “stdlib” file loaded by default (pure micromax)
- better `see` output for quotations + source spans
- optional dev-mode stack effect checking (doc-first; after metadata/inspection proves useful)

## Editor substrate (micro-esque)

Already in place:
- headless `Editor` core + `Buffer` + `UndoManager`
- micro-style **action chaining** (`, | &`) with quote/escape support
- command bar + sh-like parsing
- plugin loader with lifecycle words (`preinit/init/postinit/deinit`)
- options + search substrate (`ignorecase`, `incsearch`)

Rev9–10 added:
- selection + clipboard + indentation
- replace/replaceall commands
- prompt history navigation
- macros (record/play)
- multi-cursor primitives

Recent small wins:
- named marks + basic multi-buffer navigation (`mark`/`markjump`/`marks`, `buffer`/`buffers`) to keep headless navigation testable early
- prompt completion now has a deterministic fuzzy fallback for command-ish tokens (paths remain explicit/prefix-based)
- prompt completion also covers a few high-value argument surfaces: option values, keymode names, command/hook inspection topics, and `bind`/`bindmode` action specs
- prompt suggestion sessions now carry best-effort metadata rows (`insert/kind/menu/info`) for future UIs and micromax-side tooling
- VM words now expose doc-first stack-effect metadata through `xt-effect`, cleaned-up `xt-doc`, and row-based dictionary views (`words-rows`, `wid-word-rows`)
- editor help/inspection now treats visible Micromax words as first-class topics via `help NAME` fallback and `showword NAME`
- editor topic discovery now has a tiny search-first layer via `apropos QUERY` plus row-first hostcalls (`ed.topic-rows`, `ed.apropos-rows`); search is name-first but can also fall back to summary/doc text, supports small multi-term / out-of-order matching, and failed `help` calls now suggest likely topics
- the editor now also has a dedicated searchable `topic` prompt (`topicpick [QUERY]`, `TopicPrompt`, `ed.topic-prompt`) built on the same topic-row substrate; it live-refreshes as the query changes, exposes the active row through `ed.prompt-current-row`, and now also exposes grouped section views plus compact current-item previews for future UIs/statuslines
- the same prompt/session substrate now also powers searchable **current-binding** discovery via `bindingpick [QUERY]`, `BindingPrompt`, `ed.binding-prompt`, and `ed.binding-prompt-rows`; binding search now also supports small multi-term queries across key, action-spec, and human description text
- micromax completion hooks can now optionally return aligned suggestion rows, so plugin commands no longer have to settle for blank completion metadata

Next editor low-hanging fruit:
- multi-cursor editing ergonomics: per-cursor paste mapping, per-cursor selections UI model
- command completion improvements: richer docs/current-value annotations for more argument surfaces and plugin-side row metadata merging/inspection
- optional detail-rich preview rendering on top of the new section/current-item surfaces for both topic and binding discovery
- optional deeper doc/help indexing only if summary-aware `apropos` proves insufficient
- statusline/infobar customization on top of the shared headless status model
- file browser-ish open prompt (or minimal path completion)
- split panes + tabs (only after the action model feels right)

## Terminal UI (later)

We deliberately postpone UI implementation until the headless core stabilizes.
When we do: pick a minimal terminal library and map it onto the existing prompt/message/action model.


## Rev58 checkpoint

Extended `xt-src` to include `\\ effect`/`\\ doc`/definition span and compilation metadata lines, and taught the editor’s `showword` command to append that `xt-src` view so a single inspection message can include both documentation and a decompiled definition.

- successful palette selections are remembered in a small palette-local MRU
- empty palette queries now show those recents first
- equivalent palette matches use recency as a tiebreaker
- grouped palette sections are now exposed via `ed.command-palette-section-rows`

This keeps the editor on the “searchable live environment” path while making the palette noticeably more useful before any popup/TUI rendering exists.
