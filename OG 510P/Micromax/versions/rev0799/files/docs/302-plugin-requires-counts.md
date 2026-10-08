# Rev360: plugin info should keep dependency inventory count-aware

Recent plugin-loop work made plugin inventory, reload, error inspection, picker previews, and even dependency rows speak one compact state dialect. `plugin info NAME` already showed dependency detail honestly after rev359, but the section shape still had one small inconsistency: dependency-free plugins omitted the section entirely, while dependencyful plugins printed both a raw-name summary and the more honest per-dependency state rows underneath it.

## What changed

`plugin info NAME` now keeps dependency inventory in one tiny count-aware shape:

- plugins with no declared requirements say `requires: 0`
- plugins with requirements say `requires: N`
- per-dependency rows still show the honest state summary for each requirement

So the detail view now looks like this:

- `plugin info: a [loaded, v1.0.0]`
- `  requires: 0`

And a dependencyful plugin now looks like this:

- `plugin info: b [error, deps:a,c,missingdep]`
- `  requires: 3`
- `    - a [loaded, v1.0.0]`
- `    - c [error, v0.3.0, deps:missingdep]`
- `    - missingdep [missing]`

## Why this matters

This is a tiny trust/flow improvement, not a new subsystem. The goal is simply to keep ordinary plugin detail structurally consistent: the dependency section should not disappear when the answer is zero, and it should not duplicate a lower-fidelity raw-name list when the answer is non-zero. Future users and future LLMs should be able to glance at `plugin info NAME` and immediately see whether a plugin depends on nothing, something healthy, something broken, or something absent.
