# Plugin runtime no-manager distinction

Rev605 keeps one small trust-first runtime cleanup adjacent to the recent
plugin inspection work.

Before this change, the broad after-Enter plugin inventory commands still
blurred two different states:

- `plugin list` said `plugin list: 0 plugin(s)` both when a plugin manager was
  configured-but-empty and when no plugin subsystem existed at all.
- `showplugins` said `showplugins: 0 section(s), 0 plugin(s)` in that same
  missing-manager state.

That made safe startup and stripped-down headless harnesses look like a real
empty plugin inventory instead of an unavailable subsystem.

Rev605 keeps the fix tiny and explicit:

- `plugin list` now fails as `plugin list: no plugin manager`
- `showplugins` now fails as `showplugins: no plugin manager`
- a real empty configured manager still keeps the counted zero-inventory path

The goal is simple: broad runtime plugin inventory should tell the truth about
whether plugin support exists before it tells the truth about how many plugins
are present.
