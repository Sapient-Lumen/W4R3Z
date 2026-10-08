# Optimizing recorded macros

VHK ships a baseline X11 recorder (`vhk record-x11`) that emits a *lexical*
sequence of low-level steps. This is useful for bootstrapping, but like other
recorders it tends to generate:

- lots of mouse move events
- key down/up pairs for every keypress
- small delay fragments between almost every event

Many macro tools add a post-processing/cleanup step for this. For example,
Pulover's Macro Creator users have asked for "removing extra pauses and mouse
movements" to reduce recordings to their necessary actions:

- https://github.com/Pulover/PuloversMacroCreator/issues/12

Similarly, xmacro-based record/playback workflows often require inserting (or
auto-inserting) delays to preserve timing:

- https://github.com/franciscod/xmacro
- https://askubuntu.com/questions/1162460/how-do-i-make-xmacro-in-ubuntu-playback-at-the-same-speed

## `vhk optimize`

You can also have `vhk record-x11` run the optimizer automatically:

```bash
vhk record-x11 --duration-ms 5000 --optimize > macros/recorded.yaml

# Tune double-click/triple-click detection if your desktop/app needs a different
# inter-click budget.
vhk record-x11 --duration-ms 5000 --optimize --optimize-max-multiclick-gap-ms 300 > macros/recorded.yaml
```


`vhk optimize` is a small post-processor that rewrites a macro YAML file into a
more compact, readable form.

### What it does

- **Merge consecutive delays** (`Delay` fragments become one `Delay`).
- **Squash redundant mouse moves** (keeps the last move in a run).
- **Collapse simple click sequences** into `MouseClickAt` when the press/release
  happens quickly at (roughly) the same coordinates.
- **Collapse repeated `MouseClickAt` runs** into explicit multi-click steps such as
  `MouseClickAt(clicks=2, delay_between_clicks_ms=80)` when repeated clicks land
  at the same coordinates within a small time budget.
- **Collapse key down/up pairs** into a single `Key` step.
- **Collapse modifier chords** (e.g. `KeyDown(ctrl) ... KeyUp(ctrl)`) into a
  single chord like `Key(keys="ctrl+l")`.
- **Optionally collapse plain text typing** (runs of `Key(keys="a")`, `Key(keys="b")`, or shifted printable chords such as `Key(keys="shift+h")`)
  into a single `TypeText(text="ab")` step. This now also understands small in-run edits such as `hex` + `Backspace` + `llo`, cursor-local corrections such as `helo` + `Left` + `Left` + `l` + `Right` + `Right`, whole-word cleanup via `Ctrl+Backspace` / `Ctrl+Delete`, selection-to-boundary replacements such as `Shift+Home` / `Shift+End`, short shift-selection replacements such as `hellp` + `Shift+Left` + `o`, and control-text keys like `Enter`/`Tab` when they are part of a short literal text sequence.
- **Optionally promote long literal text** into `TypeText(backend="clipboard")` when it is clearly paste-friendly. This is intentionally opt-in because pasting is faster for large text, but it also changes clipboard ownership and can differ from typed Return/Tab semantics.
- **Optionally segment structured text** into a hybrid lane where long literal field chunks become `TypeText(backend="clipboard")` but `Tab`/`Enter` separators stay explicit `Key(keys="tab"|"enter")` steps. This keeps form-navigation semantics visible while still speeding up the big field bodies.

### Profiles

- `safe`: only merges delay fragments (no semantic rewriting).
- `balanced` (default): merges delays + mouse/key/click compaction.
- `aggressive`: like balanced, but also caps large delays (default cap: 250ms).

When using the aggressive profile, the optimizer also enables text collapsing
by default. This mirrors how many macro tools treat a rapid stream of
characters as an "insert text" action (sometimes by typing, sometimes by
pasting). Keyboard Maestro, for example, explicitly exposes both strategies in
its Insert Text action.

- https://wiki.keyboardmaestro.com/action/Insert_Text

### Examples

Optimize into a new file:

```bash
vhk optimize macros/recorded.yaml --out macros/recorded_optimized.yaml
```

In-place rewrite:

```bash
vhk optimize macros/recorded.yaml --in-place
```

Aggressive cleanup (caps long delays):

```bash
vhk optimize macros/recorded.yaml --profile aggressive

# Explicitly control repeated-click collapsing. Useful if a recorded workflow
# contains slow double-clicks that should still stay grouped.
vhk optimize macros/recorded.yaml --max-multiclick-gap-ms 300

# Enable text collapsing explicitly on balanced. This now catches common
# shifted text such as Hello!, Foo_Bar, or ?, plus simple corrected text
# streams such as hex<Backspace>llo, helo<Left><Left>l<Right><Right>,
# hello wrong<Ctrl+Backspace>world, hellx<Home><Right><Right><Right><Right><Shift+End>o,
# hellp<Shift+Left>o, and short Enter/Tab-rich snippets:
vhk optimize macros/recorded.yaml --compress-text

# Explicitly promote long literal single-line text to clipboard-paste mode
# when you want recorder cleanup to bias toward throughput instead of
# per-character typing semantics.
vhk optimize macros/recorded.yaml --compress-text --promote-paste-text --paste-text-min-chars 80
```

### Review mode: `--check` and `--diff`

If you'd like to review changes without rewriting files (similar to how code
formatters like Black expose `--check` and `--diff`), you can run:

```bash
# Exit with code 1 if the macro would change.
vhk optimize macros/recorded.yaml --check

# Print a unified diff of what would change (no file write).
vhk optimize macros/recorded.yaml --diff

# Combine both: diff output + CI-friendly exit code.
vhk optimize macros/recorded.yaml --check --diff
```

## Notes

- This optimizer is intentionally conservative: it focuses on readability and
  authoring ergonomics. Cursor-navigation edits, whole-word deletes, and short
  selection replacements are only folded when VHK can still prove the final
  caret would end at the logical end of the reconstructed text and no live
  selection remains; mid-buffer caret placement stays as explicit key steps.
- `--promote-paste-text` is also conservative on purpose: only literal text is
  eligible (no `${...}` interpolation), steps with `delay_ms_per_char` stay as
  typed text, and any text containing `Enter` / `Tab` stays in the typed lane so
  recorder cleanup does not flatten form-navigation semantics into a paste.
- For true robustness, prefer replacing long `Delay` blocks with explicit
  waits (`WaitForImage`, `WaitForText`, `WaitForWindow`, etc.).


## `vhk optimize-project`

For bulk cleanup after recording multiple macros, optimize every YAML file under
`macros/`:

```bash
vhk optimize-project . --out-dir macros_optimized
```

Or overwrite in-place:

```bash
vhk optimize-project . --in-place
```

You can also run `optimize-project` in review mode:

```bash
# Exit with code 1 if any macro would change.
vhk optimize-project . --check

# Print diffs for macros that would change (no file write).
vhk optimize-project . --diff
```

## Hybrid structured-text segmentation

When a macro already contains one literal `TypeText` step with embedded `\t` / `\n`, VHK can now split it into a more explicit mixed lane:

```bash
vhk optimize macros/form.yaml --segment-paste-text --segment-paste-min-chars 24
```

That rewrite is still conservative:
- no `${...}` interpolation
- no `delay_ms_per_char` choreography
- no steps already pinned to `backend=clipboard` / `xvkbd`
- no steps carrying retry/repeat/delay execution controls that would become ambiguous when split

Example shape:

```yaml
- type: TypeText
  text: "Email:	person@example.com\nCompany:	Very Long Company Name"
  backend: native
```

can become:

```yaml
- type: TypeText
  text: "Email:"
  backend: native
- type: Key
  keys: tab
- type: TypeText
  text: "person@example.com"
  backend: clipboard
  selection: clipboard
  preserve_clipboard: true
  paste_shortcut: auto
- type: Key
  keys: enter
- type: TypeText
  text: "Company:"
  backend: native
- type: Key
  keys: tab
- type: TypeText
  text: "Very Long Company Name"
  backend: clipboard
  selection: clipboard
  preserve_clipboard: true
  paste_shortcut: auto
```


## Planner/lint feedback loop

`vhk lint-project` and `vhk plan-project` now surface long literal typed-text
steps explicitly so the authoring loop can catch throughput-heavy snippets even
when they were written by hand rather than recorded.

That means text optimization is no longer only a recorder-cleanup trick; it is
part of the supported runtime-planning story for Linux-native text automation.
