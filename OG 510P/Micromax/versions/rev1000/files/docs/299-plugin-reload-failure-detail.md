# Plugin reload failure detail (rev357)

## What changed

`plugin reload NAME` already had an honest success path after rev348: successful reload said what plugin state you actually landed in.

The failure path still lagged behind. Broken known plugins and unknown names both tended to collapse into a generic exception-shaped message, which made plugin refresh less inspectable than nearby plugin inventory and detail commands.

Rev357 keeps the change small and makes the failure path speak the same dialect as the rest of the plugin loop:

- broken known plugins now start with `plugin reload: NAME [...]`
- those failures list current recorded load errors directly
- unknown names now fail plainly as `plugin reload: no such plugin: NAME`

## Why it matters

The plugin loop is now much closer to one coherent trust surface:

- `plugin list` tells you what exists and the broad health shape
- `plugin info NAME` tells you what one plugin is and what errors it currently has
- `plugin errors [NAME]` focuses error inspection
- `plugin reload NAME` now tells you the resulting state on success and the current failure shape on failure

That matters for both humans and future LLMs working inside the repo. A failed refresh should not send the user on an immediate second-command scavenger hunt just to learn whether the target is broken, missing, or still healthy but unreloadable for some other reason.

## Example shapes

Successful reload still looks like this:

- `plugin reload: a [loaded, v1.0.0]`

Broken known plugin reload now looks like this:

- `plugin reload: b [error, deps:missingdep]`
- `  errors: 1`
- `    - missing dependency: missingdep`

Unknown target reload now looks like this:

- `plugin reload: no such plugin: missing`
