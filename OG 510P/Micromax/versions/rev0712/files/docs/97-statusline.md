Rev537 note: plain `showstatus` command-bar completion now previews the portable status summary too — the exact command row keeps its ordinary command doc while replacing the generic info hint with the same deterministic summary `showstatus` is about to emit, and `docs/479-showstatus-command-preview.md` records why that tiny trust/headless-first follow-up matters.

Latest tiny landing (rev537): this is a small trust/headless-first follow-up to rev531/rev532/rev533/rev534/rev535/rev536's command-bar/status cleanup. Micromax already had the important nearby pieces: `status_model()` already exposed a stable scriptable snapshot, plain `showstatus` / `ed.status-summary` already emitted a deterministic human-facing summary, and nearby no-arg command rows like `jumpback`, `jumpforward`, `jumps`, `showjumpgroups`, `showjump`, and `jumppick` now previewed the state they were about to use before Enter. But one tiny seam still lingered on the smallest status surface itself: typing plain `showstatus` in the command bar still showed only a generic exact-command row, so humans and future LLMs had to press Enter just to confirm the portable summary Micromax already knew. Rev537 keeps the fix deliberately small and compatible: new `_prompt_showstatus_command_row(...)` reuses `status_summary(include_prompt=False)`, the formatter now accepts that one small preview-oriented flag so command-bar rows can omit transient prompt/capture/interaction noise, exact command completion for plain `showstatus` now surfaces the same portable summary before Enter, focused tests pin the command-row contract, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/43-worklist.md` / `docs/55-editor-command-bar.md` / `docs/64-editor-prompt-completion.md` / `docs/66-editor-micromax-commands.md` / `docs/97-statusline.md` plus `docs/479-showstatus-command-preview.md` record the intent. The goal is simple: if Micromax already knows the deterministic summary behind `showstatus`, the command bar should show that same truth before Enter instead of hiding it behind one more no-arg command.

# Statusline strings (rev213)

Micromax-editor exposes a structured `status_model()` for scripts/tests, a tiny shared `statusline_model(width)` layout snapshot for future UIs/scripts/LLMs, and a small reference formatter `statusline_text(width)` used by the minimal TUI.

This is inspired by micro’s split status format idea (left/right format strings with directives
like `$(filename)`, `$(line)`, `$(col)`, and `$(opt:filetype)`), while keeping Micromax’s default
formatter extremely small for now.

## `status_model()` additions

The status model already had most structural fields. We added a few portable “statusline staples”:

- `encoding`: effective per-buffer text encoding (default `"utf-8"`, but now driven by the real editor option)
- `display_name`: effective user-facing filename/path for statusline-style displays (`basename=false` prefers full path, `basename=true` prefers basename)
- `fileformat`: effective per-buffer line-ending format (`"unix"` for LF, `"dos"` for CRLF)
- `percentage`: 0..100 based on the primary cursor line and the total line count
- `cursor_summary`: `"N/M"` for primary cursor index + cursor count
- `selection_summary`: selection count string
- `search_query` / `search_match_index` / `search_match_count` / `search_summary`: tiny whole-buffer search-position state
- `buffer_index` / `buffer_count` / `buffer_summary`: tiny current-buffer position state across the open-buffer set
- `help_topic` / `help_title` / `help_position`: current docs/help topic state plus the current landed docs cursor target when the active buffer is a docs page
- `help_navigation_active` / `help_navigation_dormant`: tiny active-vs-dormant state so future UIs/scripts/LLMs can tell whether the current docs target is on-screen or merely resumable from the session
- `help_session_available` / `help_session_topic` / `help_session_title` / `help_session_position` plus `help_resume_available` / `help_resume_target` / `help_resume_title` / `help_resume_position` / `help_resume_warning` / `help_resume_command`: explicit session-local current-target witness so leaving a docs buffer does not collapse the current page into a generic `help -> ...` blur; rev406 adds plain `helpresume` / `ed.help-resume` as the matching explicit reopen path without pretending this state is persisted, rev407 makes the exact replay command visible too, rev408 keeps stale missing-doc session targets witnessable without advertising `helpresume` as actionable when the doc no longer resolves, and rev413 closes the matching active-state seam so `help_resume_available` is only true when the current docs target is actually dormant and resumable rather than merely present on-screen; rev414 keeps the active command/hostcall path aligned with that same contract by making active-page `helpresume` fail explicitly instead of replaying the current page, and rev415 closes the matching stale-target seam so the replay commands now fail in the same typed `helpresume:` / `helpback:` / `helpforward:` dialect already exposed by `help_*_warning`
- `help_back_available` / `help_back_count` / `help_back_target` / `help_back_position` / `help_back_warning` / `help_back_command` plus `help_forward_available` / `help_forward_count` / `help_forward_target` / `help_forward_position` / `help_forward_warning` / `help_forward_command`: tiny docs-history state so future UIs/scripts/LLMs can tell whether `helpback` or `helpforward` are actionable, where they would return, which missing-doc blocker prevents replay when stale history survives, and which exact command replays that move without scraping transient messages; rev404 also makes same-page `helpjump` / fragment follow moves show up here as real retraceable history instead of flattening everything to the page slug alone
- `help_prune_available` / `help_prune_count` / `help_prune_command`: explicit local disposition state for blocked docs history so callers can tell when stale missing session/back/forward entries are witnessable but need `helpprune` before replay can continue
- `jump_navigation_available` / `jump_entry_count` plus `jump_current_*` / `jump_back_*` / `jump_forward_*`: tiny per-buffer jumplist-navigation state so future UIs/scripts/LLMs can tell which visible `#N` slot is current, whether `jumpback` / `jumpforward` are actionable, where the immediate replay targets would land, and which exact commands replay those moves without reopening `jumps` or scraping transient messages
- `jump_navigation_scope` / `jump_navigation_persisted` / `jump_navigation_summary` / `jump_navigation_actions` / `jump_navigation_action_summary`: explicit jumplist honesty + replay-cue fields so the model says that this navigation state is buffer-local and non-persisted, keeps the current/back/forward trail reviewable in one small summary string, and names the exact currently-actionable commands (`jumpback`, `jumpforward`) instead of leaving that translation implicit; rev531 also mirrors those cues into plain `showstatus` / `ed.status-summary` as `jump_nav=` / `jump_actions=`
- `help_navigation_scope` / `help_navigation_persisted` / `help_navigation_summary` / `help_navigation_actions` / `help_navigation_action_summary` / `help_navigation_warning_summary`: explicit docs-history honesty + replay-cue fields so the model says that this navigation state is local to the current session, keeps the trail reviewable, names the exact currently-actionable commands (`helpresume`, `helpback`, `helpforward`, `helpprune`) instead of leaving that last translation implicit, and separately names blocked missing-doc replay paths when remembered targets survive but no longer resolve; rev405 adds the complementary plain-register surfaces `helphistory` / `ed.helphistory-rows` when callers want the full ordered trail instead of just the current + next actionable heads, rev406 makes dormant summaries name the off-screen current target directly (`topic (dormant) -> ...`) instead of collapsing to a generic `help -> ...` prefix, rev407 carries the same cue into plain `showstatus` / `ed.status-summary` as `help_nav=` / `help_actions=`, rev408 adds the matching `help_warn=` blocker cue plus `[missing]` trail annotations, and rev409 adds `helpprune` as the explicit local cleanup action when blocked history should stay witnessable but not stay stuck

These are meant to be **stable, scriptable primitives** so future UIs don’t need to re-derive them.

## `statusline_model(width)`

`statusline_model(width)` returns a tiny text-first layout map for the visible status row:

- `active` / `width`
- `left_raw` / `right_raw` — rendered template outputs before clipping
- `left` / `right` — visible segments after truncation policy
- `padding` / `padding_width` — the spacer inserted between left and right
- `truncated_left` / `truncated_right`
- `text` — the final single-line row

This keeps the editor-side contract inspectable without forcing future UIs to reverse-engineer the deterministic baseline formatter.

## `statusline_text(width)`

`statusline_text(width)` formats a micro-esque single line with a left filename section and a
right “token” section that includes:

- `ft:<filetype>`
- `enc:<encoding>`
- `unix` or `dos` (fileformat)
- active-search count when available (`[i/n]`)
- current buffer position when more than one buffer is open (`[i/n]`)
- cursor position and percentage
- cursor/selection counts
- mode and one-shot keymode hints
- macro recording/playback flags

If the line is too narrow, the formatter truncates the left side first; if even the right side
doesn’t fit, it shows the **end** of the right side (keeping mode/key hints visible).

## Future direction

As of **rev72**, Micromax-editor exposes micro-esque `statusformatl`/`statusformatr` templating.

## `statusformatl` / `statusformatr`

These are simple format strings where directives are embedded as `$()` expressions.

Examples:

- `$(filename)$(modified)$(readonly)`
- `ft:$(opt:filetype) $(position)$(cur)$(sel) $(percentage)% $(mode)$(keymode)$(macro)`
- `ft:$(opt:filetype) enc:$(opt:encoding) $(opt:fileformat)$(searchpos)$(bufpos) $(position)`

Escape a literal `$` as `$$`.

## Hostcall helpers

For scripts/plugins that want to reuse the same renderer:

- `ed.statusfmt` ( template -- s ) render a statusformat template against the current `status_model()`
- `ed.statusline-text` ( width -- s ) render the full statusline string for a given width

### Supported directives

We intentionally match micro’s core directive names (so you can port settings) and add a few
editor-specific conveniences.

Micro-compatible:
- `$(filename)` — effective display name honoring `basename`
- `$(modified)`
- `$(line)` / `$(col)` / `$(lines)` / `$(percentage)`
- `$(opt:NAME)` — option value (buffer-local overrides apply)
- `$(bind:ACTION_SPEC)` — representative key bound to an action spec
- `$(overwrite)` — present for compatibility (currently empty)

Micromax-editor extensions:
Tiny conditional:
- `$(if:COND|THEN|ELSE)`
  - `COND` is a directive-like expression (e.g. `modified` or `opt:filetype`)
  - `THEN` / `ELSE` are templates (they can contain `$()` directives)
  - escape a literal `|` as `\|`

- `$(readonly)` / `$(ro)`
- `$(cur)` / `$(cursors)` — ` cur:N/M`
- `$(sel)` / `$(sels)` — ` sel:K` (only when K>0)
- `$(searchpos)` / `$(search)` / `$(searchcount)` — ` [i/n]` when a search is active
- `$(bufpos)` / `$(bufferpos)` / `$(buffers)` — ` [i/n]` when more than one buffer is open
- `$(keymode)` / `$(km)` — ` [name]` (with `!` when one-shot)
- `$(macro)` — ` REC` / ` PLAY`

Fallback: if a directive name matches a key in `status_model()`, that value is substituted. That means search-aware templates can already use `$(search_summary)` / `$(search_match_count)` / `$(search_query)` without adding more directive syntax, and buffer-aware templates can use `$(buffer_summary)` / `$(buffer_count)` directly when they want raw values instead of the bracketed `$(bufpos)` cue.

## Reference formatter

`statusline_text(width)` now simply returns the final `text` from `statusline_model(width)`, so the reference formatter, hostcall surface, and future UI inspection all share one deterministic truncation/padding policy.


## References
- micro options (statusformat directives): https://github.com/zyedidia/micro/blob/master/runtime/help/options.md
- example statusformat strings mentioning filetype/encoding: https://github.com/zyedidia/micro/issues/1419
