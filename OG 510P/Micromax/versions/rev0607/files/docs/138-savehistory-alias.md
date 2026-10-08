# Micro-esque `savehistory` option alias (rev197)

Rev197 makes Micromax's existing prompt-history persistence feature available
through the more micro-esque option name `savehistory`.

## Why

Micromax already had the behavior: optional prompt-history persistence behind
`cap.persist`, using `history.persist`, `history.file`, and `history.limit`.
The awkward bit was the option spelling. micro's current options docs still use
`savehistory`, so carrying only the repo-local `history.persist` name made ported
config snippets and future LLM handoffs needlessly harder.

## What changed

- the option registry now supports tiny aliases that resolve to one canonical
  option key for reads, writes, and toggles
- `savehistory` is now an alias for `history.persist`
- command-bar option completion now includes aliases too
- local/global option storage still uses the canonical target key, so aliases do
  not fork state or create duplicate persistence settings

## Current scope

This is intentionally narrow:

- `savehistory` aliases only the enable/disable toggle
- `history.file` and `history.limit` remain the explicit Micromax config knobs
- `show` with no arguments still lists canonical options only, so aliases do not
  spam the inspection surface

## Examples

```text
set savehistory true
set history.file history.json
```

That enables prompt-history persistence using the same existing `cap.persist`
boundary and JSON file format as before.

## Related portability follow-up

Rev197 also adds a tiny JSON portability case for another already-promised map
contract: `m@` returns `0` for a missing key.
