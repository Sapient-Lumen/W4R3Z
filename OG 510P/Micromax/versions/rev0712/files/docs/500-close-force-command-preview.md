# Rev558 - force close-family command previews

## What changed

Plain `close!`, `closeall!`, and `only!` now preview the same live buffer target/count truth as their non-force siblings before Enter, while making the force semantics explicit in the command bar.

Examples:

- `close!` -> `target NAME @ line:col | dirty · force close · next NEXT @ line:col`
- `closeall!` -> `N buffers | dirty=M · force close all · then *scratch* @ 1:0`
- `only!` -> `keep NAME @ line:col · close K other buffers | dirty=M · force close`

## Why

Rev555 made the non-force close-family rows honest, but the force aliases still fell back to generic exact-command metadata. That left one adjacent trust gap exactly where destructive intent is highest: the user could type `close!` or `closeall!` and still not see the real target/count/landing state before Enter.

This landing keeps the fix deliberately small. It reuses the existing close-family preview helper, teaches it about the `!` aliases, and routes exact command completion for those aliases through the same truthful row path.

## Notes

- non-force commands still keep the ordinary double-tap guard previews
- force aliases bypass the guard preview and instead advertise the forced action directly
- no execution semantics changed; only the pre-Enter exact command rows became more honest
