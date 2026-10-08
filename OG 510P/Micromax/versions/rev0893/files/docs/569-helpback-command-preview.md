# Rev628 — `helpback` command preview keeps the next docs replay truthful

## What changed

Plain `helpback` command-bar completion now previews the next docs-history replay target before Enter.

It reuses one tiny shared `_helpback_preview_summary()` helper built on top of `help_navigation_model()`, so the row can say:

- `next TOPIC @ line:col` when one replay target is ready
- `missing doc: TOPIC` when the top back-stack entry is still a visible stale blocker
- `back stack empty` when there is nothing to retrace

## Why it matters

Micromax already knew this state. `helpback` itself already reported typed success and typed empty/missing failures after Enter, and `help_navigation_model()` already exposed the same next-target/count/warning truth for headless status surfaces. The command bar was the last tiny blind spot: right before replay, it still showed only generic command metadata.

This is a small trust/flow cleanup:

- trust: the command bar tells the truth about what `helpback` would do
- flow: docs replay becomes easier to reason about before committing to Enter
- continuity: docs history now matches the same preview-first stance already used by nearby exact inspectors and actions

## Tests

Focused prompt tests pin both states:

- ready replay target preview
- empty-history blocker preview
