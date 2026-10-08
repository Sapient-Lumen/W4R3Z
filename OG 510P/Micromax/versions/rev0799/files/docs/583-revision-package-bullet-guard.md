# Rev642 - guard the TODO package bullet against stale rev drift

## What changed

The newest `# TODO (revN)` block now has one tiny machine-checkable invariant:
if it includes a checklist bullet like `package revNNN`, that packaged rev must
match the current archive rev inferred from the top README/TODO breadcrumbs.

Rev642 keeps the fix deliberately small.

- `tools/mxcontext.py` now parses the newest TODO checklist block, extracts the
  `package revNNN` bullet when present, and reports a revision warning if that
  bullet drifts from the current rev.
- `mxcontext --check` and archive-manifest generation now inherit that warning
  automatically because they already trust the shared `revision_sources()`
  snapshot.
- The current TODO block was refreshed so its package bullet matches the new rev.

## Why it matters

This is mostly a trust and archive-hygiene cleanup.

The top TODO block is the closest thing Micromax has to a handoff contract for
what the latest loop actually did. A stale `package rev...` line is easy for a
human to skim past, but it is also exactly the kind of breadcrumb future LLMs
and offline archive readers may over-trust. Catching that mismatch early keeps
release notes, context checks, and packaged manifests boringly consistent.

## Tests

Focused repo-tooling tests now pin the new invariant by asserting that:

- `mxcontext --json --check` reports the current TODO package-bullet rev and
  keeps revision warnings empty, and
- `mkrevzip` embeds that same clean revision snapshot in `MICROMAX-CONTEXT.json`.
