# Rev350: filtered plugin error inspection should begin with honest state

Rev347 through rev349 made the plain plugin loop increasingly legible:

- `plugin list` became a concise state inventory
- `plugin reload NAME` began reporting the resulting state instead of only the attempted action
- `plugin info NAME` began with the same inventory-style summary line

That still left one older-feeling detail path behind: `plugin errors NAME`.

Before this revision, filtered error inspection had two trust problems:

- unknown names looked the same as “no recorded errors”, because `plugin errors missing` just said
  `plugin errors: (none)`
- known plugins with no current errors had no summary line, so the path did not share the same
  state dialect as `plugin list` / `plugin reload` / `plugin info`

Rev350 keeps the change deliberately small:

- `plugin errors NAME` now starts with `plugin errors: name [state, ...]`
- unknown names now fail plainly as `plugin errors: no such plugin: NAME`
- known plugins with no current errors now say `  errors: (none)`
- known plugins with recorded errors now say `  errors: N` and then list the recent error lines

That matters because error inspection is still part of ordinary plugin trust. A person should not
have to infer whether they queried the wrong plugin, a healthy plugin, or a broken plugin from the
same `(none)` result.

## Rev390 follow-up

When the plugin subsystem itself is absent, `plugin errors [NAME]` now fails as `plugin errors: no plugin manager` instead of a context-free `no plugin manager` line. That keeps the error-inspection surface visible in logs and scripted debugging.
