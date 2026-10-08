# Plugin runtime root summary

Rev606 keeps one small trust/taste cleanup for the umbrella `plugin` command.

Before this change, Micromax had already learned to show live plugin inventory
truth almost everywhere around the root plugin dispatcher:

- plain `plugin` command-bar completion already previewed live plugin inventory
- `plugin list` and `showplugins` runtime paths now distinguished a missing
  plugin subsystem from a real empty configured manager
- narrow `plugin info NAME` / `plugin errors NAME` / `showplugin NAME` runtime
  paths already preserved calm loaded/available/error state witnesses

But after Enter, raw `plugin` still fell straight back to a generic usage line.
That made the narrowest root plugin entry point less truthful than its own
preview row.

Rev606 keeps the fix deliberately tiny:

- raw `plugin` now prints one compact runtime inventory summary first
- then it still prints the existing usage line
- the summary stays count-aware and honest about the three broad states:
  - `plugin: no plugin manager`
  - `plugin: 0 plugin(s)`
  - `plugin: N plugin(s) (...) · e.g. ...`

The goal is simple: the umbrella plugin dispatcher can remain usage-shaped while
still telling the truth about the live plugin subsystem before it asks the user
to choose a subcommand.
