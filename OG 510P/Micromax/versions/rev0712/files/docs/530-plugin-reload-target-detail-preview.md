# Rev588: exact `plugin reload NAME` previews should keep the real plugin error detail

## Why

Micromax already made the broad plugin command-bar entry points truthful before
Enter, and exact `showplugin NAME` rows already preserved richer one-plugin
state than grouped picker rows. But one exact plugin subcommand still stopped a
little short.

When `plugin reload NAME` targeted a known broken plugin, the completion row only
said `1 load error · not loaded` even though Micromax already knew the exact
recorded plugin error detail for that row. That was not wrong, but it made the
narrow exact reload path less informative than the neighboring exact inspection
surfaces.

## What changed

Exact `plugin reload NAME` completion rows now prefer the real recorded plugin
error detail when the target plugin is known and currently broken.

Example:

- before: `beta [error, deps:missingdep] | 1 load error · not loaded`
- after: `beta [error, deps:missingdep] | missing dependency: missingdep · not loaded`

If multiple load errors are recorded, the row keeps the count and names the last
one (`N load errors · last: ... · not loaded`). Healthy loaded plugins and known
unloaded plugins keep their older concise wording.

## Why this shape

This keeps the change tiny and local: one exact target row gets a little more
truthful without widening the plugin inventory surface or changing runtime
reload behavior. Future humans and LLMs can see the likely reload failure shape
before pressing Enter, which makes the command bar a better first inspection
loop for broken plugins.
