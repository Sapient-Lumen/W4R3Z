# Rev607 - raw `showplugin` runtime root summary

## What changed

Raw runtime `showplugin` no longer falls straight back to `usage: showplugin NAME`.
Before that usage hint, Micromax now prints one compact exact-plugin inventory summary:

- `showplugin: no plugin manager`
- `showplugin: 0 plugin(s)`
- `showplugin: N plugin(s) · e.g. NAME [state, ...]`

## Why it matters

The no-arg command-bar row for `showplugin` already exposed the same truth before
Enter. After Enter, the umbrella exact inspector was the odd one out: it hid
missing, empty, and live exact-plugin inventory state behind a generic syntax
message.

This keeps the runtime path aligned with the preview path and with rev606's raw
`plugin` runtime summary cleanup.

## Scope

This change is deliberately tiny:

- no new host boundary
- no change to exact `showplugin NAME` detail rows
- no change to grouped `showplugins [QUERY]` output
- only the no-arg runtime `showplugin` dispatcher changes
