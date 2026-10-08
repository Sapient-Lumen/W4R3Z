# Rev661 / rev720 — replace-family flag hygiene

Rev720 is a small bulk-edit trust cleanup for the command-bar replace family.
Micromax already had the important surrounding behavior: `replace` and
`replaceall` report success counts and no-op failures, `replaceall` keeps its own
identity through failure and undo, and `qreplace` now refuses invisible
zero-width confirmation targets. One smaller boundary was still too permissive:
trailing arguments after the replacement value were treated as a loose set of
known flags, and anything unknown was silently ignored.

That made typo cases too ambiguous for text-changing commands:

- `replace one X --literal` could still run as regex-mode `replace`.
- `replace one X -a --literal` could still run as `replaceall`.
- `replaceall one X --literal` could still bulk-edit while ignoring the typo.
- `qreplace one X --all` could still enter the confirm-each capture loop even
  though `--all` is not part of the command's tiny flag surface.

The fix keeps the surface deliberately small:

- a shared helper reports the first unknown flag in command order;
- `replace` accepts only `-a` and `-l` after `SEARCH VALUE`;
- `replaceall` reaches the same helper through its existing `replace -a` wrapper;
- `qreplace` accepts only `-l` and rejects unknown flags before capture mode;
- failure messages keep the invoked command family visible, for example
  `replace: unknown flag: --literal`, `replaceall: unknown flag: --literal`, and
  `qreplace: unknown flag: --all`.

The behavior change is intentionally conservative. It does not add new replace
flags, alter regex or literal semantics, or change successful replacement text.
It only makes unknown option text a clear failed command instead of a best-effort
edit. For bulk editing, that is the safer default: when the user writes an option
Micromax does not understand, the editor should preserve the buffer and say so.

## Focused tests

- `tests/test_editor_core.py`
- `tests/test_editor_query_replace.py`
