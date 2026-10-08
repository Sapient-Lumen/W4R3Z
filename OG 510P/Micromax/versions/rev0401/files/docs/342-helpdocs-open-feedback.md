# rev400 — explicit `help docs` success feedback

## Why

`help docs TOPIC` already had a good typed miss path:

- `help docs: no such doc: TOPIC`

But the matching success path still fell back to the generic docs-open dialect:

- `help: TOPIC @ line:col`

That was readable, but it hid the fact that the user asked for an explicit docs lookup rather than a broader `help QUERY` fallback, `helpback`, or `helpjump` move.

## What changed

Explicit docs opens now keep the command family visible on success too:

- `help docs: TOPIC @ line:col`

General `help QUERY` fallback remains unchanged and still reports:

- `help: TOPIC @ line:col`

## Why this is enough

This keeps the change intentionally tiny:

- explicit docs lookup now names itself on both success and failure
- broader `help` fallback keeps its existing dialect
- docs navigation (`helpfollow`, `helpback`, `helpjump`) keeps its already-typed wording

The result is a slightly clearer docs-discovery surface in logs, tests, and future LLM traces without widening behavior.
