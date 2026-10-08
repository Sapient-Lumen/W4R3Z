# Rev791 — contained help/docs paths

Rev0791 audits the help/docs browser as a filesystem-adjacent surface.  The bug was small in code size but severe in shape: docs help buffers are readable through normal editor/hostcall text surfaces, so a docs resolver that accepts arbitrary paths can become a quiet `cap.fs-read` bypass.

## Audit finding

`Editor.find_doc_path(...)` treated path-like help topics specially.  If a target ended in `.md` or contained a slash, the old resolver expanded it through the ambient process filesystem and accepted any existing file.  That meant calls such as `help docs /tmp/secret.md`, `ed.help-doc`, or script-origin `ed.command "help docs /tmp/secret.md"` could open a non-doc local file as a protected help buffer.  Once opened, ordinary editor text hostcalls could inspect the buffer contents even when the script did not hold file-read capability.

The docs catalog had a related containment gap.  Top-level `*.md` entries were accepted with `Path.is_file()`, which follows symlinks.  A symlink inside the docs root pointing at an outside markdown file could therefore appear as a normal docs topic and be opened through the help browser.

Relative markdown links in help pages had a third usability/trust issue: when a link resolved to a real file outside the docs root, the follow path could fail silently instead of reporting that the target was not an accepted docs document.

## What changed

`src/micromax_editor/editor.py`

- Adds `_contained_doc_path_from_explicit_target(...)`.
- Explicit path-like help targets are accepted only when they resolve to an existing `.md` file whose final path remains inside `docs_root()`.
- Common legitimate spellings still work: docs-root relative paths such as `00-vision.md` and repo-root paths such as `docs/00-vision.md` are both accepted when they stay inside the docs root.
- Absolute paths are accepted only when they point back into the configured docs root.
- `find_doc_path(...)` now treats help/docs as a documentation resolver, not a general file resolver.
- `helpfollow` relative-link handling now falls through to the normal `help docs: no such doc: ...` message when a real path exists but is refused by the docs containment rule.

`src/micromax_editor/docs_index.py`

- Top-level docs scanning now rejects symlinks whose resolved target escapes the docs root.
- Normal non-symlink docs keep the fast path so the rev0759/rev0760 docs-cache performance fix is not undone.

`tests/test_editor_help_docs_boundary.py`

- Proves direct/interactive help does not open an arbitrary absolute markdown path.
- Proves `ed.command` and `ed.help-doc` cannot use help/docs as a script file-read bypass.
- Proves docs-root and repo-root relative legitimate docs still open.
- Proves the docs catalog ignores symlink entries that point outside the docs root.
- Proves `helpfollow` cannot escape via a relative `../outside.md` link and reports the refused target.

`tools/mxdoctor.py`

- Adds the focused help/docs boundary test file to the bounded doctor risk lane.
- Removes the broader prompt-completion unit file from the default lane so the preflight remains bounded rather than growing every time a focused trust-boundary test is added.

## Remaining risk

The docs root is still a configured trust boundary.  A user or wrapper that intentionally sets `MICROMAX_DOCS` to a sensitive directory is choosing what the help browser treats as documentation.  This revision prevents help/docs from escaping that root; it does not try to infer whether the chosen root itself is safe.

Help buffers remain readable editor buffers by design.  That is why the resolver must stay docs-contained.  Future docs/help extensions should preserve the rule: help may resolve topics, docs-root markdown paths, and safe external URL prompts, but it must not become a general file viewer.

The symlink check is an application-level containment check.  It is suitable for docs inventory and help navigation, but high-risk write/read operations still need the stronger fd/dirfd containment seams added in the file-capability revisions.

## Validation

Focused validation for this landing included:

- `py_compile` for `editor.py`, `docs_index.py`, bridge/plugin/value-snapshot files, context/doctor tools, and focused tests;
- `23 passed in 1.21s` for `tests/test_editor_help_docs_boundary.py`, `tests/test_docs_index.py`, and `tests/test_mxdoctor.py`;
- `92 passed in 2.65s` for the adjacent mark-authority, mutable-value, plugin-callback, with-undo, and core VM rollback set;
- `178 passed in 15.74s` for existing help-doc buffer/navigation/link-picker/history tests;
- `tests/test_revision_index.py` passed after the rev0791 handoff refresh.

`python tools/mxdoctor.py` was attempted; the first bounded child reported `106 passed`, then the cloudtainer delivered SIGTERM during the second child.  This revision therefore does not claim a fresh default-doctor aggregate pass or a full-suite pass.  The handoff refreshes `docs/revision-index.json`, `MICROMAX-CONTEXT.json`, README/TODO/worklist notes, and the archive manifest for rev0791.
