# Editor goals: taste, trust, and flow

This is the current editor product note.

The editor already **works**: files open, edits apply, saves happen, search/replace exists, macros exist, multiple cursors exist, docs/help navigation exists, and the curses TUI can render all of that.

What it does **not** fully do yet is make people want to stay in it all day.

That last step is not mainly about adding giant new subsystems. It is about getting three qualities to compound:

1. **Taste** — the editor looks intentional, calm, and pleasantly opinionated.
2. **Trust** — the editor behaves honestly, predictably, and safely enough that users stop second-guessing it.
3. **Flow** — the editor keeps the user moving, with less friction between intention and action.

Those three words are the current editing lens. When future contributors ask “what should we build next?” or “is this polish worth it?”, this doc is the answer.

## Why these three qualities

Micromax is trying to be a small editor with a real scripting language, not a pile of features with a tiny VM stapled on later. That means:

- the editor should feel **coherent**, not merely capable
- scripting should make behavior *more inspectable*, not more mysterious
- tiny improvements should accumulate into a daily-driver feel

Taste, trust, and flow give us a way to say “no” to random feature sprawl while still leaving room for many small wins.

- command-palette file-open paths should feel as explicit and trustworthy as ordinary `open ...`
- plugin refresh failure should stay as inspectable as plugin inventory/detail instead of collapsing to a generic exception string
- even empty plugin-error inventory should keep the same tiny count-aware shape as the non-empty case instead of dropping back to a vaguer special-case message
- plugin detail should keep dependency inventory structurally consistent too, with an explicit `requires: 0` instead of silently omitting the whole section when nothing is required

## The product standard

The target standard is not “have a checkbox for every editor feature”.

The target standard is:

- a first-time user can open a file and immediately feel oriented
- a returning user can make edits quickly without wondering whether the editor is fighting them
- a power user can inspect and script behavior without losing confidence in what the editor will do next
- the UI feels modest but deliberate: calm by default, expressive when it matters
- navigation and docs-browsing paths narrate real landings instead of making the user infer where a successful command actually left them
- dropping a mark should confirm the anchored target, not merely acknowledge that a command ran
- searchable inventory buckets should surface tiny count cues when that materially reduces row-counting or state reconstruction

## 1. Taste

Taste is how the editor communicates quality before the user has measured anything.

It is the combination of:

- visual hierarchy
- restraint
- consistency
- good defaults
- small cues that make the screen easier to read

Taste does **not** mean decorative chrome. It means the UI feels cared for.

### What “taste” should feel like

- The important thing on screen is visually obvious.
- Prompts, pickers, docs, status rows, and editing rows feel like parts of one system.
- Cues such as search hits, current line, matched braces, overflow markers, and markdown structure feel helpful rather than noisy.
- Color and emphasis are used on purpose.
- The editor has a recognizable personality even when running in a plain terminal.

### Current taste strengths

The repo already has many small ingredients:

- line numbers, ruler/relativeruler, cursorline, matchbrace, overflow markers, scrollbar, colorcolumn, `hlsearch`, `hltrailingws`, `hltaberrors`, softwrap, keymenu, infobar, and statusline shaping
- docs/help rendering that already distinguishes headings, links, code spans, blockquotes, tables, task lists, and other markdown-ish structures
- shared screen/status/prompt models so different UIs/scripts can inspect the same visible state

This is a good base. The repo is past the point of “can we show useful cues?” and into “which cues create the best overall feel?”.

### Taste goals

#### A. Give the editor a stronger visual hierarchy

The current TUI surfaces should tell a clearer story about:

- where the cursor is
- what pane or interaction is active
- what is primary vs secondary information
- what is selectable vs merely informative

Concrete near-term goals:

- settle on a default cue stack that feels good without local tweaking
- make prompt/picker/status/help visuals feel more obviously related
- make docs/help pages look intentional rather than “text with a few attributes”

#### B. Make colors and emphasis feel designed, not accumulated

Many cues already exist, but they risk reading like independent feature flags rather than one taste system.

Concrete near-term goals:

- define a tiny theme vocabulary for the reference TUI
- map existing cues into that vocabulary instead of choosing styles ad hoc
- choose which cues should be bold, dim, reversed, or underlined only when that distinction carries meaning

#### C. Improve preview surfaces

A great editor feels smart before the user commits.

Concrete near-term goals:

- better command/picker previews
- more obvious current-item context in lists and prompts
- search/replace previews that help the user decide before mutating text

### Taste anti-goals

- no theme engine explosion
- no decorative chrome that steals rows from text without clear value
- no giant styling system before the small default look feels right

## 2. Trust

Trust is the feeling that the editor tells the truth.

A trustworthy editor:

- starts cleanly
- reports errors honestly
- never hides meaningful mutations
- makes destructive actions legible
- keeps script/plugin behavior inspectable
- preserves orientation across both typed commands and picker-driven navigation
- makes edit-recovery loops (`undo`, `redo`, macro playback, replace) inspectable instead of tacit
- makes ordinary clipboard loops (`copy`, `cut`, `paste`) explicit enough that small text movement is not mysterious
- makes plain open/plugin state inventory (`buffers`, `recent`, `marks`, `plugin list`) legible enough that active/dirty/readonly/anchored/loaded/error state is not guesswork, and count-aware enough that broad plugin health is glanceable without manual tallying
- makes plugin refresh feedback (`plugin reload NAME`) confirm the resulting state/version/dependencies instead of only naming the attempted action
- keeps plugin detail aligned with that same dialect so `plugin info NAME` and filtered `plugin errors NAME` start by stating the current plugin state honestly, unknown names fail plainly, healthy plugins can say clearly when there are currently no recorded load errors, broken-plugin detail can show the current error lines directly instead of hinting that a second command is needed, dependency rows can distinguish present/broken/absent requirements without flattening them together, and the `requires: N` line can summarize loaded/error/available/missing dependency shape before you scan the rows
- keeps broad plugin-failure inspection aligned too so plain `plugin errors` groups failures by plugin, starts with a tiny plugin/error count summary, and exposes broken-plugin inventory without making users reconstruct raw error logs
- keeps searchable broken-plugin inspection aligned too so `pluginpick` sends `Errors` rows to filtered `plugin errors NAME` instead of generic `plugin info NAME`
- keeps searchable plugin row/preview language aligned too so `pluginpick` uses the same compact bracketed plugin-state summaries as plain plugin inventory/detail surfaces instead of older free-form status labels

Users forgive missing features faster than they forgive surprises.

### What “trust” should feel like

- Startup is boring.
- Save/open/replace/undo/clipboard/plain-inventory/plugin-refresh behavior is predictable.
- Error messages explain what happened and what the user can do next.
- Plugins and hooks feel observable, not spooky.
- Small automation state is inspectable instead of requiring guesswork.
- Safety boundaries are obvious instead of implied.

### Current trust strengths

The repo already leans the right way:

- capability-gated surfaces
- protected/read-only buffer paths
- grouped plugin registrations and unload cleanup
- inspectable status, prompt, screen, and binding models
- portability work that tries to pin semantics down instead of relying on vibes

That is excellent infrastructure for trust. But infrastructure alone is not the same as user trust.

### Trust goals

#### A. First-run reliability

The first-run path should not emit mysterious warnings or require the user to infer which failures matter.

Concrete near-term goals:

- make core plugin load failures either impossible by default or extremely well-explained
- distinguish fatal startup problems from recoverable plugin problems in user-facing language
- ensure the editor can always reach a simple “editing works” baseline even when optional pieces fail

#### B. Honest bulk editing

Search/replace is where trust is won or lost.

Concrete near-term goals:

- preview count before replace-all
- optionally preview impacted regions/diff-ish context before committing
- keep confirm-each flows obviously stateful and cancellable
- make the current match/replacement story visible enough that users stop double-checking by hand

#### C. Human plugin and error UX

The repo already has inspectable plugin machinery, but the operator experience should feel friendlier.

Concrete near-term goals:

- one obvious place to inspect plugin health
- tiny command-level inventory paths that tell the truth about saved automation and plugin state
- recovery commands that say which edit just got traversed instead of only changing text
- clipboard actions that say what they moved instead of replying with vague one-word acknowledgements
- friendlier error formatting with file/line/group/capability context
- first-class “disable the thing that is failing” workflows
- clearer startup/status messages when the editor is running in a degraded but usable mode

#### D. File-operation confidence

Open/save paths should feel uneventful.

Concrete near-term goals:

- keep save-time normalizations honest and visible
- make ordinary clipboard actions say what they copied/cut/pasted, and where paste actually landed
- make successful saves say which path was written, not merely that “save happened”
- make explicit opens say which file/cursor target they actually landed on
- make ordinary buffer-switch/close commands say which active buffer/cursor target they actually landed on
- make readonly/protected/encoding/fileformat state obvious enough that the user is not surprised by write failures or conversions
- improve any remaining ambiguity around what buffer path and on-disk path the editor thinks it is editing

### Trust anti-goals

- no silent magical recovery that hides real state changes
- no plugin power increase without corresponding introspection
- no convenience features that bypass capability or readonly boundaries

## 3. Flow

Flow is the editor’s ability to get out of the way.

A flow-friendly editor reduces tiny pauses:

- finding the thing
- jumping to the thing
- changing the thing
- checking the result
- resuming the previous thread

### What “flow” should feel like

- The next command is easy to discover.
- Navigation remembers context.
- Repetitive editing becomes lighter rather than more tedious.
- The editor helps the user stay oriented across files, prompts, and temporary modes.

### Current flow strengths

There is already a lot here:

- command palette / prompt completion
- search, replace, query-replace
- jumplist
- recent files, including a plain MRU view that tells the truth about what is still open
- keymodes/prefix maps/whichkey-style discovery
- macros
- multiple cursors
- docs/help navigation and copy/follow flows

So again, the repo is not missing the *idea* of flow. It mostly needs tighter composition.

### Flow goals

#### A. Faster project/file movement

The editor should make it easier to move across a small project without breaking concentration.

Concrete near-term goals:

- strengthen fuzzy open / recent-file flows
- keep plain `recent` / `buffers` / `marks` / `plugin list` inventory surfaces aligned with richer picker/detail behavior so quick inspection stays honest
- make project-aware recents and path navigation feel more intentional
- keep picker grouping/preview work focused on scan speed, not feature count

#### B. Better structural navigation

The editor should reduce the time between “I know roughly where I want to go” and “I am there”.

Concrete near-term goals:

- more polished go-to-line behavior
- eventual symbol-aware navigation where a filetype can support it
- better “go back / go forward / return to what I was doing” feel around jumps, help pages, and search-driven movement
- keep jumplist back/forward traversal itself verbally orienting, not just stateful
- search movement that says where it landed, not just whether a match exists somewhere
- keep buffer-switch / close / keep-only flows verbally orienting, not just behaviorally correct

#### C. Better edit loops

The user should be able to stay in motion while editing.

Concrete near-term goals:

- keep multi-cursor and macro workflows easy to recover from
- improve visual-line-aware movement and other tactile cursor behavior
- add small affordances such as comment toggling when they clearly reduce repeated friction

#### D. Layouts that support real work

At some point the editor should support comparing or referencing more than one thing at once.

Concrete near-term goals:

- buffer-list/tab awareness in status or picker surfaces
- later, splits once the single-window interaction model feels solid

Splits are not the first priority, but they are a meaningful future flow multiplier.

### Flow anti-goals

- no giant project-management subsystem before basic move/search/open loops feel great
- no symbol/index machinery without a clear filetype or capability story
- no modal complexity that makes ordinary movement harder to explain

## How we should sequence the work

The order matters.

### Phase 1 — Trust first

Before the editor becomes flashy, it should become boring in the best way.

Priority work:

1. startup/plugin reliability
2. clearer degraded-mode and error messaging
3. small automation honesty (macro playback, macro inventory, script-visible command results, repeated-edit feedback)
4. replace-preview/count work
5. file/save/read-only clarity

Why first:

- taste compounds poorly if users do not trust startup
- flow features feel risky when bulk edits are still stressful
- once the behavior is trustworthy, polish reads as confidence rather than camouflage

### Phase 2 — Taste as a coherent default

Once the basics are trustworthy, the default look should become more intentional.

Priority work:

1. settle a tiny theme vocabulary
2. tune the default cue stack
3. improve prompt/picker/help hierarchy
4. polish previews and context rows

Why second:

- this is where the editor starts to feel memorable
- many existing options are already present; they now need curation more than expansion

### Phase 3 — Flow multipliers

After trust and default taste are in place, the editor should remove more friction from daily work.

Priority work:

1. file/project navigation polish
2. stronger jump/return/orientation loops
3. plain-state inventory that is legible without entering a picker
4. tactile edit-loop improvements
5. eventually splits and stronger multi-buffer workflows

Why third:

- flow features shine once users already trust the surface they are moving through
- this phase should be driven by repeated user pain, not by feature tourism

## How to evaluate a proposed change

A good proposed editor change should answer most of these questions clearly:

- Does it improve **taste**, **trust**, or **flow**?
- Which of those three is primary?
- Is the gain visible to the user, or only satisfying to the implementer?
- Does it make the default experience better, or merely add another option?
- Can the behavior remain inspectable through the shared models / hostcalls / docs?
- Does it preserve the repo’s habit of small, replayable, testable landings?

If a change does not clearly improve one of taste/trust/flow, it is probably not a priority.

## Immediate recommendations

If we want the most leverage over the next several revisions, the default order should be:

1. **Trust** — remove startup/plugin weirdness, improve error UX, make replace safer
2. **Taste** — curate defaults, create a stronger visual identity, improve previews
3. **Flow** — sharpen navigation, edit loops, and later layouts

That order can change if a glaring UX pain appears in real use, but it is the best current bias.

## Summary

Micromax does not mainly need more proof that it can become an editor.

It needs to become a tool that feels:

- carefully designed (**taste**)
- safe to rely on (**trust**)
- easy to stay in (**flow**)

That is the current job.
