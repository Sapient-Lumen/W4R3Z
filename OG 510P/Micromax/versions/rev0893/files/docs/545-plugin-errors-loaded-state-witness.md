# Plugin errors exact loaded-state witness

## Goal
Keep exact `plugin errors NAME` inspection rows/runtime feedback concrete in the calm zero-error loaded case.

## Change
- exact command-bar `plugin errors a` rows now say `0 load errors · loaded plugin`
- runtime `plugin errors a` now says `errors: 0 · loaded plugin`
- available-but-unloaded targets keep the existing `available plugin · not loaded` wording

## Why
`showplugin NAME` and `plugin info NAME` already preserved the tiny `loaded plugin` witness. `plugin errors NAME` was the remaining exact-inspection outlier that flattened back to a bare zero count.
