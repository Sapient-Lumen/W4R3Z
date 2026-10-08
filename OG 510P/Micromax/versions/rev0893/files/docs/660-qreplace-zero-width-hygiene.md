# Rev660 / rev719 — qreplace zero-width hygiene

Rev719 is a small trust/failure-mode fix for the interactive query-replace loop.
The existing `qreplace` path already selected the current match, used a capture
keymode, reported progress, and recorded the confirmed edits as one undo step.
One edge still violated the same trust rule: query replace could accept searches
that do not identify a visible, advancing match.

The sharp cases were small but important:

- `qreplace '' X -l` started from an empty literal search.
- `qreplace '$' X` selected a zero-width regex match.
- mixed patterns like `abc|$` could count a visible first match and then still
  encounter a zero-width match later.
- the `a` / replace-all confirmation path could keep applying a replacement to a
  match with no width, making the operation non-terminating or visually
  confusing.

The fix keeps the command intentionally boring:

- empty searches fail before capture mode with `qreplace: empty search`.
- regex match counting refuses zero-width matches before the interactive session
  starts.
- the selection loop has a defensive zero-width guard in case a future path ever
  constructs such a session directly.
- focused tests pin the empty-search, zero-width-only, and eventually-zero-width
  regex cases.

The policy is deliberately narrower than ordinary non-interactive regex replace.
For an interactive confirm-each loop, every prompt should point at visible text
that can advance after a decision. If there is no visible span to confirm, the
editor should say so instead of pretending the prompt is actionable.
