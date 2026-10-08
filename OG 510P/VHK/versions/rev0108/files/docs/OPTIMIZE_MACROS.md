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
```


`vhk optimize` is a small post-processor that rewrites a macro YAML file into a
more compact, readable form.

### What it does

- **Merge consecutive delays** (`Delay` fragments become one `Delay`).
- **Squash redundant mouse moves** (keeps the last move in a run).
- **Collapse simple click sequences** into `MouseClickAt` when the press/release
  happens quickly at (roughly) the same coordinates.
- **Collapse key down/up pairs** into a single `Key` step.
- **Collapse modifier chords** (e.g. `KeyDown(ctrl) ... KeyUp(ctrl)`) into a
  single chord like `Key(keys="ctrl+l")`.
- **Optionally collapse plain text typing** (runs of `Key(keys="a")`, `Key(keys="b")`)
  into a single `TypeText(text="ab")` step.

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

# Enable text collapsing explicitly on balanced:
vhk optimize macros/recorded.yaml --compress-text
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
  authoring ergonomics.
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
