# Rev663 / rev722 — replace template error hygiene

Rev722 is a small replace-family trust cleanup for regex replacement templates.
The surrounding runway already tightened three adjacent seams: `qreplace` refuses
empty and zero-width searches, the replace-family commands reject unknown flags,
and ordinary `replace` / `replaceall` refuse invisible matches before mutating.
One template seam still behaved inconsistently when the replacement referenced a
capture group that the regex did not define.

Before this slice, the same typo could fail in two very different ways:

- `replace 'a([0-9])' '$2'` and `replaceall 'a([0-9])' '$2'` raised out of the
  command implementation and were reported by the generic dispatcher as
  `command replace: error: ...` or `command replaceall: error: ...`;
- `qreplace 'a([0-9])' '$2'` caught the expansion error while selecting the
  match and quietly treated `$2` as literal replacement text.

Both paths are bad trust signals. The first loses the command's own failure
vocabulary; the second can make an interactive edit do something the user did
not ask for. Replacement templates are part of the edit request, so bad template
references should fail before any text changes and before an interactive capture
mode starts.

The fix keeps normal template behavior unchanged:

- `micromax.regex_tools.format_replacement_template_error(...)` gives the editor
  and related callers a shared one-line diagnostic formatter;
- single regex `replace` expands the matched template once before constructing
  the new buffer text and reports `replace: invalid replacement: ...` on failure;
- bulk regex `replace` / `replaceall` preflight each match's template expansion
  before calling `subn`, so a bad reference cannot leave a partial edit behind;
- `qreplace` preflights template expansion during its match-count pass before
  assigning `self.qreplace` or entering capture mode;
- the defensive qreplace selection path now stops with
  `qreplace: invalid replacement: ...` instead of falling back to the raw value.

This deliberately does not add new replacement syntax. `$1`, `$name`, `${name}`,
and `$$` keep their existing meanings. The change is only about making broken
replacement templates visibly recoverable and action-specific.

## Focused tests

- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
- `tests/test_regex_hostcalls.py`
