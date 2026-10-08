# Visible selection, syntax, and one honest screen hierarchy

Rev0967 closes a product gap rather than adding another registry. Micromax
already stored multiple selections, produced Micromax syntax spans, exposed a
shared viewport model, and shipped a compact screen contract. The reference TUI
still painted neither syntax nor selection. A selected range could therefore be
active and destructive while visually indistinguishable from ordinary text.

That is not cosmetic. Selection is direct manipulation: it tells the user which
text the next insertion, deletion, query-replace answer, or multicursor command
will affect. Invisible secondary ranges also make multicursor state impossible
to audit from the screen. The highest-risk unfinished taste work was therefore
to connect existing truth end to end:

```text
buffer selections + existing syntax tokenizer
    -> bounded visible-row cues
    -> micromax.screen.v1 cue tokens
    -> restrained curses attributes
    -> one 80x24 edit/help/prompt journey
```

No theme engine, parser framework, schema version, or style registry was added.

## What landed

### Shared visible geometry

`selection.py` now projects a normalized half-open logical selection onto one
horizontal or soft-wrapped row fragment. Text spans use fragment-local Python
character coordinates. A selected logical newline is represented separately as
the blank cell immediately after end of line, so newline-only and empty-line
selections no longer disappear.

`highlight.py` now clips the existing full-line Micromax span model into the same
fragment-local coordinates. Unknown tags and malformed rows are ignored. The
producer remains deliberately small and line-local; the renderer does not own a
second tokenizer.

The shared viewport cue model emits, per visible row:

- `syntax_spans`: `[start, end, tag]`;
- `primary_selection_spans` and `secondary_selection_spans`;
- `primary_selection_eol_x` and `secondary_selection_eol_x` when a selected
  logical newline has a visible blank cell.

The model also reports normalized filetype, syntax scan budget, selection source
budget, and whether either projection was truncated. These are diagnostics, not
a new public theme API.

### Explicit finite work

A screen snapshot considers at most 4096 cursor sources, including the primary.
The primary is retained even when it is not among the first cursors. Omitted
source count is exposed as `selection_projection_truncated`.
`selection_ranges_visible` counts only retained non-empty ranges that actually
intersect at least one viewport row; an off-screen range is not mislabeled as
painted.

Syntax may need to scan from logical column zero to know whether a visible
fragment is inside a line comment or string. That prefix is capped at 4096
characters per visible logical line and scanned once. Visible text beyond the
cap remains plain rather than guessing. `syntax_truncated_rows` makes that loss
inspectable.

These bounds complement the existing public screen limits (256 lines, 512
columns, 65,536 cells and cues). They do not claim hostile-code containment or
bound private Python mutation of editor internals.

### One renderer/headless fact set

`micromax.screen.v1` already permits new valid cue-token values, so its closed
object shape did not change. The compact producer now emits `syntax-*`,
`selection-secondary`, and `selection-primary` cues from the same viewport rows
the TUI consumes. Independent consumers can therefore inspect the visual state
without importing curses or reconstructing selections from buffer internals.

The reference TUI resolves one low-to-high order:

```text
syntax
  < docs inline markup
  < visible whitespace
  < color column
  < whitespace diagnostics
  < brace match
  < ordinary search
  < secondary selection
  < primary selection
  < current search
```

Syntax is a reading layer. Direct selections replace lower-layer dim/bold/underline emphasis with one
canonical shape: secondary is reverse+underline and primary is reverse+bold. The
current search match then adds both bold and underline, so a query-replace target
remains distinguishable even when syntax or diagnostics underneath already used
those attributes. In monochrome terminals,
comments are dim, keywords bold, and definitions bold plus underline; strings
and numbers remain plain unless color support exists.

### Audit and refactor

Softwrap rows previously forced downstream code to infer which leading spaces
were renderer-owned continuation indentation and which characters came from the
file. The inference happened independently in showchars and in renderer-owned
trailing-whitespace, tab-error, brace, and color-column calculations. Rows now
carry the exact `source_text_x` / `source_text_length` seam produced by the same
wrapping owner that built the fragment. Search, syntax, selection, showchars,
trailing whitespace, tab diagnostics, and brace spans all align through that
seam. The curses paint loop consumes the shared cue rows instead of recomputing
those geometries; compatibility wrappers remain, but there is no second live
renderer calculation. This both deletes repeated work and prevents continuation
indentation from being styled as file text.

Selection-heavy reads previously called the public normalizing accessor once per
cursor. Each call could repeat the full cursor-sidecar deduplication pass. The
editor now normalizes once and uses a non-normalizing accessor while computing
selection presence, all ranges, status selection counts, and viewport cues.

The same audit found screen composition rebuilding status truth for infobar and
statusline separately. Screen assembly now materializes one normalized status
snapshot and passes it through both layout owners.

A renderer-side reread remained after that refactor: curses called the full
`status_model()` again only to place the prompt cursor, then subtracted the edit
viewport's horizontal scroll even though prompts are not horizontally scrolled.
Opening a prompt after sideways editing could therefore shift its cursor left.
The renderer now uses the already-composed `screen["cursor"]` for both edit and
prompt modes. This removes the duplicate traversal and fixes the coordinate bug
without a cache or a second geometry owner.

## Research reviewed on 2026-07-18

The implementation follows four primary-source lessons:

- CodeMirror warns that allowing multiple ranges does not itself make secondary
  selections visible; a drawing extension is required. Micromax similarly had
  state without a painted contract:
  https://codemirror.net/docs/ref/
- VS Code distinguishes editor selection, inactive selection, selection
  occurrences, current find match, and other find matches. Its documentation
  repeatedly warns that secondary highlight backgrounds must not hide underlying
  decorations. A terminal cannot use alpha blending reliably, so Micromax keeps
  layers distinguishable through composable attributes instead:
  https://code.visualstudio.com/api/references/theme-color
- The W3C CSS Custom Highlight API gives overlapping highlights explicit
  priority and places built-in highlights above custom overlays. Micromax uses a
  small fixed tuple rather than registration order or accidental call order:
  https://www.w3.org/TR/css-highlight-api-1/
- VS Code separates tokenization from theming. Micromax keeps its existing tiny
  tokenizer in the model and maps stable tags to restrained curses attributes in
  the renderer:
  https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide

These sources support explicit layering and visible multicursor state; they do
not justify importing their theme systems or parser stacks.

## Evidence

Focused tests cover horizontal clipping, soft-row coordinates, selected logical
newlines and empty lines, malformed syntax rows, filetype normalization, long-line
scan truncation, off-index primary retention, bounded multicursor projection, off-screen selection accounting,
normalization-call counts, one status snapshot per screen assembly, compact
contract cues, renderer attributes, prompt cursor placement after horizontal
scroll, and a complete 80x24 edit -> help -> command-palette/status journey.

The journey uses the public compact screen contract. A separate fake-curses
renderer test proves that the same row cues paint syntax, primary selection,
secondary selection, and the selected newline cell.

## Honest residual boundary

- Coordinates remain Python code points, not terminal cells or grapheme
  clusters. Wide and combining text can still diverge across renderers.
- Syntax is Micromax-only and line-local. Multiline lexical state and embedded
  languages are not claimed.
- Multiple secondary selections are unioned per row; their individual identities
  are not a screen cue.
- Curses color and underline quality varies by terminal. The attribute-only
  fallback is tested, but no universal palette claim is made.
- The projection bounds screen work after editor cursor normalization; arbitrary
  hostile Python mutation remains outside the application boundary.

## What should happen next

The visual seam is now complete enough to stop expanding it. The next high-value
work should be an observed repeated editing loop—search/select/edit/macro or
project navigation—captured as a full headless transcript. A likely friction is
that users can now see multicursor ranges but still lack one compact way to
understand how a repeated command transformed each range. That is speculation;
it should be tested against a concrete journey before adding per-cursor labels,
preview panes, or another model family.
