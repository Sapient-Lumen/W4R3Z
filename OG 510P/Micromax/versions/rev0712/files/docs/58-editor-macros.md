Rev712 note: command recordability now has a tiny inspectable classifier, so future readers can tell at a glance whether a command is excluded from macro recording by exact name, by family prefix, by family suffix, or not at all; `docs/653-macro-recordability-kind-helper.md` records why that small archive-maintenance cleanup matters.

Latest tiny landing (rev712): this is a small maintainability/trust follow-up to rev708-rev711's recordability cleanup. Micromax already had the visible behavior we wanted: exact-name observer outliers stayed out of recorded macros, `show*` and `help*` family commands stayed out, `*pick` family commands stayed out, and ordinary commands still recorded exactly once. But the helper layer still only answered the yes/no question, which meant future readers had to mentally reconstruct *why* a given command was excluded. Rev712 keeps the surface intentionally stable while making that reason inspectable: `Editor._macro_command_recordability_kind(...)` now reports `exact`, `prefix`, `suffix`, `recordable`, or `empty`, the boolean helper reuses it, focused tests pin representative examples from each bucket, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/653-macro-recordability-kind-helper.md` record the intent. The goal is simple: once Micromax has trustworthy recording rules, the archive should make the reason behind each rule easy to inspect too.

# TODO (rev712)

- [x] add a tiny command-recordability classifier helper
- [x] keep the boolean helper and existing behavior wired through that classifier
- [x] pin representative exact/prefix/suffix/recordable/empty examples in tests
- [x] package rev712

Rev711 note: `prefixmode` now joins the read-only discovery side of macro recording, so entering a one-shot prefix-mode preview no longer quietly becomes a macro step just because it succeeds by showing reachable bindings; `docs/652-prefixmode-read-only-recording.md` records why that small trust/flow cleanup matters.

Latest tiny landing (rev711): this is a small trust/flow follow-up to rev710's `whichkey` cleanup. Micromax already had the key discovery surface partly on the right side of the recording line: `whichkey` stayed out of recorded macros, and most other observer/query families had already been moved to non-recordable helper rules. But one adjacent binding-discovery command still lingered as a successful outlier: `prefixmode MODE` enters a one-shot prefix mode and immediately surfaces reachable bindings, which is useful for discovery but not a replay-worthy macro step. Rev711 keeps the fix deliberately small and local: `prefixmode` now joins the exact-name non-recordable command set, focused tests pin both helper behavior and a live successful `prefixmode tools` path during recording, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/652-prefixmode-read-only-recording.md` record the intent. The goal is simple: binding discovery should help you choose automation, not become the automation.

# TODO (rev711)

- [x] treat `prefixmode` as a read-only discovery command in macro recording
- [x] pin a live successful `prefixmode` recording path next to `whichkey`
- [x] package rev711

Rev710 note: `whichkey` now joins the read-only side of macro recording, so live binding-discovery output stops quietly becoming a macro step even when it succeeds with a real active binding inventory; `docs/651-whichkey-read-only-recording.md` records why that small trust/flow cleanup matters.

Latest tiny landing (rev710): this is a small trust/flow follow-up to rev703-rev709's observer cleanup. Micromax already had most read-only discovery surfaces behaving better: `show*` inspectors, docs-help queries/navigation, state-reporting commands, and picker openers all stayed out of recorded macros, while ordinary successful commands still recorded exactly once. But one successful discovery command still lingered as an outlier: `whichkey` can render the currently available binding inventory, and before rev710 it still became a recorded command step just because it was not in the non-recordable set. Rev710 keeps the fix deliberately small and local: `whichkey` now joins the exact-name non-recordable command set, focused tests pin both the helper behavior and a live successful `whichkey` path during recording, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/651-whichkey-read-only-recording.md` record the intent. The goal is simple: binding discovery should help you inspect automation, not become the automation.

# TODO (rev710)

- [x] treat `whichkey` as a read-only discovery command in macro recording
- [x] pin a live successful `whichkey` recording path next to the helper contract
- [x] package rev710

Rev709 note: docs-help navigation now lives on the read-only side of macro recording too, so successful help-browser commands like `helpfollow` and `helpback` stop quietly becoming macro steps even when they succeed in a real docs buffer; `docs/650-help-family-read-only-recording.md` records why that small trust/flow cleanup matters.

Latest tiny landing (rev709): this is a small trust/flow follow-up to rev705/rev708's recordability-pattern cleanup. Micromax already had the obvious docs/query entry points behaving better: `help`, `apropos`, `helphistory`, the `show*` family, and `*pick` pickers all stayed out of recorded macros, and the helper now made the exact-name versus family-pattern rules easier to inspect. But the broader docs-help navigation family still lingered on the wrong side of that line: commands like `helpfollow` and `helpback` can succeed inside a real docs buffer, yet they were still recordable even though they are exploratory help navigation rather than replay-worthy editor automation. Rev709 keeps the fix deliberately small and coherent: the command-recordability prefix family now includes `help`, focused tests pin both helper behavior and a live docs-buffer recording path for `helpfollow` / `helpback`, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/650-help-family-read-only-recording.md` record the intent. The goal is simple: docs-help navigation should help you inspect automation, not become the automation.

# TODO (rev709)

- [x] treat the broader `help*` family as read-only in macro recording
- [x] pin a live docs-buffer path for successful `helpfollow` / `helpback` while recording
- [x] package rev709

Rev708 note: macro command-recordability policy now has explicit exact-name, prefix, and suffix constants, so future readers can see at a glance which commands are excluded because they are specific outliers versus whole observer families like `show*` or `*pick`; `docs/649-macro-recordability-pattern-constants.md` records why that small archive-maintenance cleanup matters.

Latest tiny landing (rev708): this is a small maintainability/trust follow-up to rev706/rev707's recordability cleanup. Micromax already had the visible behavior we wanted: exact outliers like `macro`, `jumps`, `pwd`, `helphistory`, `help`, and `apropos` stayed out of recorded macros, `show*` inspectors stayed out, `*pick` picker openers stayed out, and ordinary commands still recorded exactly once. But the helper was still flattening three different kinds of policy into one condition, which made the archive a little harder to skim when you wanted to know whether a command was excluded by exact name, by family prefix, or by family suffix. Rev708 keeps the surface intentionally stable while making the pattern language explicit: `MACRO_NONRECORDABLE_COMMANDS`, `MACRO_NONRECORDABLE_COMMAND_PREFIXES`, and `MACRO_NONRECORDABLE_COMMAND_SUFFIXES` now split those cases apart, the helper reuses them, existing focused tests stay green, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/649-macro-recordability-pattern-constants.md` record the intent. The goal is simple: once Micromax has trustworthy command-recordability rules, the archive should make the shape of those rules easy to read before anyone edits them.

# TODO (rev708)

- [x] split macro non-recordable command policy into exact-name, prefix, and suffix constants
- [x] keep the existing helper/behavior tests green against the new shape
- [x] package rev708

Rev707 note: exploratory `*pick` commands now stay out of recorded macros, so searchable pickers like `commandpick`, `helppick`, and `jumppick` stop quietly becoming macro steps even though they are UI exploration rather than replay-worthy automation; `docs/648-picker-commands-read-only-recording.md` records why that small trust/flow cleanup matters.

Latest tiny landing (rev707): this is a small trust/flow follow-up to rev703-rev706's observer cleanup. Micromax already had the obvious inspector/reporting commands on the right side of macro recording: the `show*` family stayed out, non-`show` observers like `jumps`, `pwd`, `helphistory`, `help`, and `apropos` stayed out, and successful ordinary commands still recorded exactly once. But one adjacent exploratory UI family still lingered on the wrong side of that line: picker commands ending in `pick` open searchable prompts or pickers, which is useful for discovery but not a stable automation step to replay later. Rev707 keeps the fix deliberately small and coherent: the command-recordability helper now treats `*pick` commands as non-recordable alongside the other read-only/query surfaces, focused tests pin representative helper and live recording behavior for `commandpick`, `helppick`, and `jumppick`, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/648-picker-commands-read-only-recording.md` record the intent. The goal is simple: searchable pickers should help you choose automation, not become the automation.

# TODO (rev707)

- [x] treat `*pick` commands as read-only exploratory UI in macro recording
- [x] pin representative helper and live recording behavior for the picker family
- [x] package rev707

Rev706 note: macro recordability names now live in small named sets, so the growing non-recordable command/action policy stops hiding inside helper conditionals and becomes much easier for future humans or LLMs to inspect safely; `docs/647-macro-recordability-constants.md` records why that small archive-maintenance cleanup matters.

Latest tiny landing (rev706): this is a small maintainability/trust follow-up to rev702-rev705's recording-honesty cleanup. Micromax already had the visible behavior we wanted: read-only observers like `show*`, `jumps`, `pwd`, `helphistory`, `help`, and `apropos` stay out of recorded macros, macro-control actions stay out too, and successful ordinary commands/actions still record exactly once. But the tiny allow/deny names behind that behavior had grown enough that they were starting to hide inside helper conditionals again, which made the archive a little harder to scan at a glance. Rev706 keeps the surface intentionally stable while making the policy more inspectable: `MACRO_NONRECORDABLE_COMMANDS` and `MACRO_NONRECORDABLE_ACTIONS` now hold those names in one obvious place, the command/action helpers reuse them, focused tests keep the same visible contract pinned, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/647-macro-recordability-constants.md` record the intent. The goal is simple: once Micromax has trustworthy recording rules, the archive should make those rules easy to read before you change them.

# TODO (rev706)

- [x] promote macro non-recordable command/action names into explicit constants
- [x] keep the existing helper and behavior tests green against the new constants
- [x] package rev706

Rev705 note: `help` and `apropos` now join the read-only side of macro recording, so tiny documentation/query commands stop quietly becoming recorded macro steps while you are just asking the editor to explain itself; `docs/646-help-apropos-read-only-recording.md` records why that small trust cleanup matters.

Latest tiny landing (rev705): this is a small trust-first follow-up to rev704's state-reporting cleanup. Micromax already had several obvious observers on the right side of the recording line: the `show*` family stayed out of recorded macros, and non-`show` state reporters like `jumps`, `pwd`, and `helphistory` no longer polluted recordings just because they had different names. But two more tiny documentation/query commands still lingered on the wrong side of that policy: `help` and `apropos` are both there to explain or search the editor's surface, yet both still became recorded command steps during macro recording. Rev705 keeps the fix deliberately small and local: the command-recordability helper now treats `help` and `apropos` as read-only observers too, focused tests pin both helper and live recording behavior next to the earlier observer cases, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/646-help-apropos-read-only-recording.md` record the intent. The goal is simple: documentation/query commands should explain automation, not become part of it.

# TODO (rev705)

- [x] treat `help` and `apropos` as read-only documentation/query commands in macro recording
- [x] pin helper and live recording behavior next to the earlier observer cases
- [x] package rev705

Rev704 note: `pwd` and `helphistory` now join the read-only side of macro recording, so tiny state-reporting commands for the current directory and help-history register stop quietly becoming recorded macro steps; `docs/645-pwd-helphistory-read-only-recording.md` records why that small trust cleanup matters.

Latest tiny landing (rev704): this is a small trust-first follow-up to rev703's `jumps` cleanup. Micromax already had a better story for obvious inspectors: the `show*` family stayed out of recorded macros, `jumps` no longer polluted recordings just because it lacked a `show` prefix, and successful ordinary commands still recorded exactly once. But two more tiny non-`show` observers still sat on the wrong side of that line: `pwd` only reports the current directory, and `helphistory` only reports the docs help-history register, yet both still became recorded command steps during macro recording. Rev704 keeps the fix deliberately small and local: the command-recordability helper now treats `pwd` and `helphistory` as observational commands alongside `jumps`, focused tests pin both helper and live recording behavior, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/645-pwd-helphistory-read-only-recording.md` record the intent. The goal is simple: tiny state-reporting commands should observe editor state, not become part of the automation they are describing.

# TODO (rev704)

- [x] treat `pwd` and `helphistory` as read-only non-`show` observers in macro recording
- [x] pin helper and live recording behavior next to `showstatus` and `jumps`
- [x] package rev704

Rev703 note: `jumps` now joins the read-only inspection side of macro recording, so the jumplist register viewer stops quietly adding itself to recorded macros even though it is just reporting state; `docs/644-jumps-read-only-while-recording.md` records why that small trust cleanup matters.

Latest tiny landing (rev703): this is a small trust-first follow-up to rev699/rev702's command-recordability cleanup. Micromax already had the main inspector family behaving better: `show*` commands stayed out of recorded macros, command recording rules were centralized behind a helper, and successful ordinary commands still recorded exactly once. But one tiny non-`show` inspection outlier still lingered right beside that policy: `jumps` is just the jumplist register viewer, yet it still counted as a recordable command step during macro recording. Rev703 keeps the fix deliberately small and local: `jumps` now joins the helper's read-only command exclusions, focused tests pin both the helper contract and the live recording path next to `showstatus`, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/644-jumps-read-only-while-recording.md` record the intent. The goal is simple: register viewers should observe automation state, not become part of it.

# TODO (rev703)

- [x] treat `jumps` as a read-only non-`show` inspector in macro recording
- [x] pin the helper and live recording path next to `showstatus`
- [x] package rev703

Rev702 note: macro recordability rules now live behind tiny helpers, so the recent command/action success-only fixes and `show*` inspector exclusions stop being scattered across raw conditionals; `docs/643-macro-recordability-helpers.md` records why that small anti-drift cleanup matters.

Latest tiny landing (rev702): this is a small maintainability/trust follow-up to rev698-rev701's recording-honesty work. Micromax already had the visible behavior we wanted: read-only `show*` inspectors stay out of recorded macros, failed command lines no longer become recorded command steps, blocked read-only actions no longer become recorded action steps, and successful ordinary commands/actions still record exactly once. But the tiny name-based policy behind those fixes had started to spread across the command and action paths as ad hoc conditions, which made the archive slightly easier to fork by accident the next time someone touched macro recording. Rev702 keeps the surface intentionally stable while making that policy explicit: `Editor._macro_should_record_command_name(...)` and `Editor._macro_should_record_action_name(...)` now own the command/action filters, focused helper coverage pins the intended command/action examples directly, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/643-macro-recordability-helpers.md` record the intent. The goal is simple: once Micromax has trustworthy recording rules, future edits should have one small place to read and preserve them.

# TODO (rev702)

- [x] centralize command/action macro-recordability rules behind tiny helpers
- [x] pin representative command/action allow/deny cases directly in tests
- [x] package rev702

Rev701 note: action macro recording now keeps only successful actions too, so blocked edits like `InsertText` on a read-only buffer stop polluting recorded macros while the first successful action still records exactly once; `docs/642-action-recording-success-only.md` records why that small trust cleanup matters.

Latest tiny landing (rev701): this is a small trust-first sibling to rev700's command-recording honesty fix. Micromax already had the command side behaving better: failed command lines and read-only `show*` inspectors no longer slipped into recorded macros, and successful ordinary command lines still recorded normally. But the action path still had the same deeper seam underneath it: `run_action(...)` appended its `MacroStep(kind='action', ...)` before success was known, so a blocked mutating action like `InsertText` on a read-only buffer could still become recorded automation even though nothing actually happened. Rev701 keeps the fix deliberately small and local: action recording now snapshots the potential step up front but only appends it after the action returns success, blocked read-only mutations stay out of the macro buffer, successful actions still record exactly once, focused macro tests pin both the failure and success paths, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/642-action-recording-success-only.md` record the intent. The goal is simple: recorded automation should reflect actions that actually ran, not actions that were refused.

# TODO (rev701)

- [x] append action macro steps only after successful execution
- [x] keep blocked read-only mutations out of recorded macros
- [x] pin one successful action next to the blocked-action path
- [x] package rev701

Rev700 note: command-line macro recording now keeps only successful non-inspector commands, so failed commands and read-only `show*` inspections stop polluting recorded macros while real successful commands like `goto 1:1` still record normally; `docs/641-command-recording-success-only.md` records why that small trust cleanup matters.

Latest tiny landing (rev700): this is a small trust-first follow-up to rev698/rev699's read-only inspector cleanup. Micromax already had two important local improvements: `showmacro` stopped mutating recordings, and then the broader `show*` inspector family stopped doing the same. But one deeper honesty seam still lingered underneath the command-line recording path itself: Micromax was appending command steps to the in-flight macro *before* dispatch finished, which meant obviously failed commands like `nope` or other false-returning command lines could still become recorded automation despite the code comment promising only successful commands were kept. Rev700 keeps the fix deliberately small and local: command-line recording now decides whether a command is recordable up front but only appends the `MacroStep(kind='command', ...)` after dispatch succeeds, failed commands stay out of the macro buffer, read-only `show*` commands still stay out too, successful ordinary commands like `goto 1:1` still record exactly once, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/641-command-recording-success-only.md` record the intent. The goal is simple: recorded automation should reflect what actually ran, not failed attempts or observational probes.

# TODO (rev700)

- [x] record command-line macro steps only after successful dispatch
- [x] keep failed commands and read-only `show*` commands out of recorded macros
- [x] pin one successful ordinary command-line step next to the failure path
- [x] package rev700

Rev699 note: read-only `show*` inspector commands now stay out of recorded macros, so live inspection like `showstatus`, `showbuffer`, `showoption`, or `showmacro` no longer quietly rewrites the automation you are recording; `docs/640-show-commands-read-only-while-recording.md` records why that small trust cleanup matters.

Latest tiny landing (rev699): this is a small trust-first follow-up to rev698's `showmacro` cleanup. Micromax already had the right local fix for the exact macro inspector: `showmacro` stopped appending itself to in-flight recordings, exact/root step counts stayed aligned, and saved macros no longer grew just because you inspected them mid-recording. But the broader editor still had the same latent seam across the rest of the read-only inspector family: other `show*` commands like `showstatus` could still sneak into the recording buffer even though they were plainly observational. Rev699 keeps the fix deliberately small and uniform: command recording now treats the whole `show*` family as read-only alongside `macro` management commands, one focused test pins both `showstatus` and `showmacro` during an active recording, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/640-show-commands-read-only-while-recording.md` record the intent. The goal is simple: inspection commands should observe editor state, not become part of the automation they are inspecting.

# TODO (rev699)

- [x] keep the broader `show*` inspector family out of recorded macros
- [x] pin a representative non-macro inspector (`showstatus`) next to `showmacro` during recording
- [x] package rev699

Rev698 note: `showmacro` is now treated as a read-only inspector during recording, so exact macro inspection no longer quietly adds itself to the macro being recorded and the prompt/runtime step counts stay aligned while you inspect a live recording; `docs/639-showmacro-read-only-while-recording.md` records why that small trust cleanup matters.

Latest tiny landing (rev698): this is a small trust-first follow-up to rev663-rev697's macro inspection cleanup. Micromax already had the important nearby pieces: `showmacro NAME` could inspect exact saved or live-owned slots, plain `showmacro` now reused the same truthful live root summary as plain `macro`, and the macro preview/runtime dialect around `last` had become much easier to trust. But one narrow seam still lingered at exactly the wrong moment: while recording, running `showmacro` itself quietly appended command steps to the in-flight macro, which made the exact inspector mutate the thing it was inspecting and produced subtle prompt/runtime step-count drift. Rev698 keeps the fix deliberately small and local: `showmacro` is now excluded from command recording just like `macro` management commands, exact `showmacro` during recording stays read-only at the current live step count, saved counts after `stop` no longer grow just because you inspected them, focused tests pin both the exact slot and root-summary paths, and `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/58-editor-macros.md` and `docs/639-showmacro-read-only-while-recording.md` record the intent. The goal is simple: inspection should not secretly rewrite the automation it is trying to explain.

# TODO (rev698)

- [x] keep `showmacro` read-only while macro recording is active
- [x] align exact/root `showmacro` recording-time step counts with the real live macro buffer
- [x] package rev698

Rev694 note: the main macro guide now teaches the same root-action and default-slot dialect the live editor actually speaks, so `docs/58-editor-macros.md` stops lagging behind rev692/rev693's `macro` / `showmacro` root cleanup and the newer `[default]` / `default slot empty` playback story; `docs/635-macro-guide-sync.md` records why that small archive-trust cleanup matters.

Latest tiny landing (rev694): this is a small trust/documentation follow-up to rev680/rev692/rev693's macro-surface cleanup. Micromax already had the important nearby pieces in code and in the narrower prompt/command docs: the umbrella `macro` root now surfaces live action detail during recording and playback, plain `showmacro` now reuses that same truthful root summary instead of pretending playback is idle, default-slot rows wear `[default]`, and empty exact `macro play last` / `run last` paths now say `default slot empty` instead of flattening back to a missing-name dialect. But the main macro guide itself still lagged behind those improvements in a few important summary bullets, which made the archive slightly harder for future humans or LLMs to trust as a single source of truth. Rev694 keeps the fix deliberately small and documentation-only: `docs/58-editor-macros.md` now teaches the current root-action, default-slot, and exact-playback dialect directly, `README.md` / `TODO.md` / `docs/01-llm-start-here.md` / `docs/02-repo-map.md` / `docs/43-worklist.md` plus `docs/635-macro-guide-sync.md` record the intent, and the main macro guide stops quietly teaching an older intermediate prompt language. The goal is simple: the primary macro guide should describe the macro surface people actually have now, not the one it had a dozen tiny trust fixes ago.

# TODO (rev694)

- [x] refresh the main macro guide so its command-bar and inspection notes match the current root-action/default-slot behavior
- [x] sync copied overview breadcrumbs to point at the guide refresh
- [x] package rev694

# Macros (micro-inspired)

Macros are a deceptively powerful "low-hanging" editor feature because they unlock
automation before you have a full plugin ecosystem.

Micro binds (default keys):

- `Ctrl-u` — toggle macro recording
- `Ctrl-j` — play the latest recorded macro

Reference: micro runtime help/defaultkeys.md.

## What micromax-editor implements (v23)

Actions:

- `ToggleMacro` — start/stop recording the **last** macro (micro-style)
- `PlayMacro` — play the **last** macro
- `CancelMacro` — cancel recording without saving

Command bar:

- `macro record|rec|start [name]` — start recording into a named slot (default: `last`); bare roots now preview `record default slot`, `overwrite default slot on save`, or the active recording guard before Enter
- `macro stop|end` — stop and save
- `macro cancel|abort` — stop and discard
- `macro play|run [name] [count]` — play named macro (default: `last`, count default: `1`) and report exactly what ran (`macro: played NAME xN (K step[s])`); bare roots now preview `default slot empty`, `play default slot`, or `wait for playback` before Enter
- `macro list|ls` — list saved macros with recorded step counts; stays count-aware as `macros: N macro(s), ...`, reports `macros: 0 macro(s)` until something real is saved, and marks saved `last` as `[default]`
- `macro status|st` — show the combined live macro runtime state plus the same saved-macro inventory as `macro status: STATE [NAME (N step[s])], M macro(s), ...`; idle status keeps `default=last (N step[s])` visible, and playback status omits redundant echoes of the current live macro when another saved clue like `last [default]` is available
- plain `macro` — the umbrella root now previews the live next-action truth too: idle centers `default=last (N step[s])`, recording says `stop to save, cancel to discard`, and playback says `wait for playback`
- `showmacro NAME` — show one exact macro slot without replaying it; saved slots report their recorded size, active recording-owned slots stay inspectable as live steps before `stop`, `last` stays explicit as the default replay slot even when it is still empty, plain `showmacro` reuses the same truthful live root summary as plain `macro`, and rev698/rev699 now keep both `showmacro` and the broader read-only `show*` inspector family out of recorded macros so inspection no longer adds itself to the automation it is describing
- Command-line recording should be honest too: rev700 now appends recordable command steps only after dispatch succeeds, so failed commands and read-only inspectors stay out of the saved macro while a real successful command-line step like `goto 1:1` still records exactly once.
- Action recording should be honest too: rev701 now appends action steps only after success, so a blocked read-only mutation like `InsertText` stays out of the saved macro while the first successful `InsertText` still records exactly once.
- Recordability rules should be explicit too: rev702 now centralizes the command/action allow/deny filters behind tiny helpers, so the `macro` / `show*` command exclusions and the `ToggleMacro` / `PlayMacro` / `CancelMacro` action exclusions stop living as open-coded conditionals in two separate execution paths.
- Read-only register viewers should be explicit too: rev703 now teaches the command helper that `jumps` belongs on the observational side of the line, so that tiny jumplist register view no longer records itself just because it lacks a `show` prefix.
- Tiny state-reporting commands should be explicit too: rev704 now puts `pwd` and `helphistory` on that same observational side of the line, so current-directory and help-history reports stop becoming recorded command steps just because they are not spelled as `show*`.
- Binding discovery should be explicit too: rev710 now puts `whichkey` on that same observational side of the line, so successful binding-inventory output no longer becomes a macro step just because it is not part of the `show*` family.
- Prefix-mode discovery should be explicit too: rev711 now puts `prefixmode` on that same observational side of the line, so entering a one-shot prefix preview and showing reachable bindings no longer becomes a replay step.
- Tiny docs/query commands should be explicit too: rev705 now puts `help` and `apropos` on that same observational side of the line, so asking the editor to explain itself stops becoming a recorded macro step.
- Docs-help navigation should be explicit too: rev709 now extends that same observational side to the broader `help*` family, so successful docs-buffer moves like `helpfollow` and `helpback` stop becoming replay steps just because they are not simple query commands.
- Exploratory picker commands should be explicit too: rev707 now treats the `*pick` family as non-recordable, so searchable picker openers like `commandpick`, `helppick`, and `jumppick` stay on the UI/discovery side of the line instead of becoming replay steps.
- Recordability patterns should be explicit too: rev708 now separates exact command exclusions from prefix/suffix family exclusions, so future edits can immediately see whether a command is excluded because it is a named outlier or because it belongs to an observer family like `show*` or `*pick`.
- Recordability reasons should be explicit too: rev712 now adds a tiny classifier helper that says whether a command is excluded by exact name, prefix family, suffix family, or not excluded at all, so future edits can inspect the reason before they change the rule.
- Recordability names should be explicit too: rev706 now lifts the non-recordable command/action names into small named sets, so future recording tweaks can see the whole allow/deny policy before they touch the helper logic.

Hostcalls (portable surface; lists/ints/strings only):

- `ed.macro-names` ( -- names ) — saved macro names only; empty-step named slots stay omitted until something real is recorded or set there
- `ed.macro-inventory-rows` ( -- rows ) — tiny `[name steps]` rows for the same saved macro inventory; empty-step named slots stay omitted here too
- `ed.macro-status-rows` ( -- rows )
- `ed.macro-detail-row` ( name -- row|0 ) — exact `[query canonical state steps default shadow_steps]` detail for one saved, live-owned, or default `last` slot, including recording-owned `last` / target slots before save and empty idle `last` at `0 steps`
- `ed.macro-get` ( name -- steps ) returns `[]` for missing named slots (only `last` keeps the default-slot fallback)
- `ed.macro-set` ( steps name -- ) — set one saved macro from portable steps; passing `[]` prunes a named slot (while `last` stays the special default slot), but writes to `last` or the active recording target are rejected while recording is open because `stop` / `cancel` would clobber them anyway
- `ed.macro-record` ( name -- ok )
- `ed.macro-stop` ( -- ok )
- `ed.macro-cancel` ( -- ok )
- `ed.macro-play` ( name n -- ok )
- `ed.macro-recording?` ( -- flag )
- `ed.macro-playing?` ( -- flag )

## Macro representation (portable)

A macro is a list of **steps** encoded with simple tags:

- `["a", ACTION, [[key val] ...]]` — run an action with an `editor.input` snapshot
- `["c", CMDLINE]` — run a command-bar line

This is intentionally simple so macros can be inspected, persisted, and replayed
from micromax without needing a map/dict type.

## Design notes

- Recording happens at the **action/command** level (not raw keypresses).
- Playback should be explicit too: successful `macro play` now reports the macro name, repeat count, and recorded step count, while missing named macros fail as `macro play: no such macro: NAME`; the special empty default `last` slot now stays inspectable as `0 steps [default]` and exact empty `macro play last` / `run last` paths say `default slot empty` / `default slot is empty` instead of pretending `last` is just another missing name.
- Inventory should be explicit too: `macro list` now stays count-aware as `macros: N macro(s), ...`, says `macros: 0 macro(s)` before anything real is saved, later shows `name (N step[s])` entries instead of raw names, and rev420/rev661 expose that same filtered `name/steps` register directly through `macro_inventory_rows()` / `ed.macro-inventory-rows` / `ed.macro-names` so scripts and future UIs inherit the same empty-slot honesty policy instead of rediscovering it.
- Runtime state should be explicit too: rev436 adds `macro status` plus `macro_status_rows()` / `ed.macro-status-rows`, so scripts and future UIs can inspect one tiny combined `idle` / `recording` / `playing` snapshot together with the saved-macro inventory instead of stitching together boolean flags and a separate list walk; playback status now also skips redundant echoes of the current live macro in its saved tail when another saved clue exists.
- Exact slot inspection should be explicit too: rev663/rev664 make `showmacro NAME` plus `macro_detail_row()` / `ed.macro-detail-row` tell the truth for one exact saved, live-owned, or default `last` slot — including recording-owned `last` / target slots before save and an idle empty `last` at `0 steps` — and rev680 now lets exact empty `macro play last` / `run last` paths inherit that same default-slot truth instead of flattening back to `no such macro` — instead of forcing humans or future scripts/LLMs to reconstruct that answer from list/status/raw step surfaces.
- Command discovery should be explicit too: plain `macro` and `showmacro` now keep truthful root summaries before Enter, plain `macro play|run` / `macro record|rec|start` preview default-slot action or active guards, exact `showmacro` / play / run / record rows keep `[default]` and `default slot empty` visible where it matters, and `macro` completion now offers the real `rec` / `start` aliases instead of hiding them.
- Command typos should be explicit too: unknown `macro` subcommands now fail as `macro: no such subcommand: NAME` instead of a context-free parser message.
- Each action step stores a shallow snapshot of `editor.input` so insertion and
  other parameterized actions replay correctly.
- Recording is disabled while playing back to avoid runaway recursion.
- "last macro" semantics match micro, but named macros make it easy to keep a
  small library of tiny automations (similar spirit to Vim/Emacs macro naming).
