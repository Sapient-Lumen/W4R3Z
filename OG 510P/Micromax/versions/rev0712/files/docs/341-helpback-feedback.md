# Rev399 - helpback typed feedback

## What changed

- `helpback` now reports `helpback: back stack empty` when there is no prior docs page.
- Successful return now reports `helpback: TOPIC @ line:col` instead of generic `help:` wording.
- Stale missing-doc history stays unchanged; rev415 keeps the failed action visible there too, so the miss now reports `helpback: missing doc: TOPIC` instead of generic `help docs:` wording.

## Why

The docs browser had already become one of the editor's real headless-first navigation loops:
open docs, follow links, copy links, go back, and inspect the exact landed target in tests.
But `helpback` still lagged behind the typed dialect around it. The two direct paths people
inspect most — ordinary return and empty history — still collapsed to generic `help:` messages.
That made logs, tests, and future LLM traces slightly less searchable right at the moment users
are trying to retrace where they were.

This keeps the change deliberately small. No semantics change, no stack policy change, no new UI.
It only makes docs back-navigation identify itself as clearly as `helpfollow`, `helpjump`, and
`help docs` already do.
