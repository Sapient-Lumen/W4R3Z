# Rev359: plugin info should distinguish dependency state, not just loaded vs missing

Recent plugin-loop work made plain inventory, reload, error inspection, and searchable picker flows all reuse one compact state dialect. `plugin info NAME` already began with that same summary line and now shows current error detail directly too.

One small trust gap still remained inside the dependency list itself. Required plugins were printed as only `loaded` or `missing`, which was truthful in the broadest sense but too lossy in practice: a dependency that existed but failed to load looked too similar to one that was not present at all.

## What changed

`plugin info NAME` now keeps dependency rows in the same tiny state dialect used elsewhere in the plugin loop:

- loaded dependency: `a [loaded, v1.0.0]`
- broken dependency: `c [error, v0.3.0, deps:missingdep]`
- truly absent dependency: `missingdep [missing]`

The parent plugin detail stays intentionally small, but it no longer hides whether a required plugin exists, failed, or is simply absent.

## Why it matters

The ordinary detail path should answer the obvious next question without forcing reconstruction:

1. what does this plugin require?
2. which of those requirements are healthy?
3. which are broken?
4. which are not present at all?

That is a trust/flow improvement more than a feature expansion. It keeps plugin detail legible for people and future LLMs without widening the plugin surface area.
