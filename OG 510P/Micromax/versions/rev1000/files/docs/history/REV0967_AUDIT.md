# Revision 0967 audit

## Priority judgment

The highest-risk unfinished product work was not another registry or policy
layer. Micromax already held multicursor selection state and produced Micromax
syntax spans, but neither reached the reference TUI. A destructive selection
could therefore be active yet visually indistinguishable from ordinary text.
That breaks direct manipulation and makes query-replace or multicursor edits
hard to trust.

## Corrected findings

1. **Invisible active ranges:** primary and secondary selections now project
   through the shared viewport model, compact contract, and curses renderer.
2. **Invisible selected line breaks:** a selected logical newline now occupies
   one blank-cell cue when its EOL cell is visible, including empty lines.
3. **No stable overlap order:** syntax, docs, whitespace, diagnostics, search,
   selections, and current search now resolve through one tested finite order;
   selection emphasis replaces conflicting lower bold/underline state.
4. **Headless/TUI divergence:** `syntax-*` and `selection-*` cue values come from
   the same bounded rows that curses paints; no renderer-only selection truth is
   required.
5. **False visible-range accounting:** the diagnostic count now includes only
   retained non-empty selections that intersect at least one viewport row;
   off-screen ranges are not called visible.
6. **Softwrap source/display ambiguity:** wrapped rows expose the exact boundary
   between continuation indentation and file text. All source-owned spans align
   through that seam.
7. **Repeated cursor normalization:** selection presence, range enumeration,
   status counts, and screen projection normalize sidecars once per read path.
8. **Repeated screen status traversal:** infobar and statusline share one status
   snapshot during screen assembly.
9. **Prompt cursor contaminated by edit scroll:** curses formerly reread status
   and subtracted the edit viewport's horizontal offset from a prompt that is not
   horizontally scrolled. It now uses the composed screen cursor.
10. **Unbounded generated handoff growth:** the current revision pushed the
    generated context list to 68 documents. Core and recent-revision evidence now
    displace lower-priority stable reading, keeping the normal handoff at 64
    paths without silently dropping current work.

## Research reviewed on 2026-07-18

CodeMirror's reference manual explicitly notes that allowing multiple selection
ranges does not make secondary selections visible without a drawing extension.
VS Code documents separate selection, find-current, find-match, and selection
highlight colors and warns against hiding underlying decorations. The W3C CSS
Custom Highlight API defines explicit priority for overlapping highlights. VS
Code's syntax guide separates tokenization from rendering/theme choice. Exact
links and Micromax implications are recorded in
`docs/923-visible-selection-syntax-hierarchy.md`.

## Waste removed or avoided

The repair reuses the existing selection state, Micromax tokenizer, viewport
rows, compact schema, and curses attribute vocabulary. It does not add a theme
engine, parser framework, style registry, selection owner registry, cache, or
schema version. Renderer-owned copies of trailing-whitespace, tab-error, brace,
and color-column geometry were removed from the live paint path. The generated
handoff now reuses revision-index evidence under a fixed 64-document budget
instead of accumulating another permanent reading layer. Compatibility wrappers
remain for callers and tests, but shared editor geometry is authoritative.

## Explicit work bounds

- At most 4096 cursor sources are considered, always retaining the primary.
- At most 4096 characters are syntax-scanned per visible logical line.
- Existing public limits still cap lines, columns, cells, and projected cues.
- Unknown/malformed syntax rows and cue spans are ignored or rejected by their
  existing strict boundary rather than expanding work silently.

These limits bound screen projection after normal cursor-list normalization.
They are not hostile Python/native containment.

## Residual risk

- Python code-point coordinates can disagree with terminal-cell and grapheme
  geometry for wide or combining text.
- The syntax producer is line-local and Micromax-only; multiline lexical state
  and embedded languages are not represented.
- Multiple secondary ranges are unioned per row and lose individual cursor
  identity in the visual contract.
- Terminal color, underline, and reverse rendering vary by curses implementation.
- A pathological private cursor list can still make application normalization
  expensive before the visible-source cap applies.
- The focused evidence is not a complete repository-suite result.
