# Unbind success feedback

## Why

Micromax already made missing `unbind KEY` / `unbindmode MODE KEY` targets fail plainly in rev374.
That tightened the *failure* side of small keymap surgery, but the success side still spoke an older,
less self-identifying dialect:

- `unbound Ctrl-x`
- `unbound Ctrl-g [mode nav]`

Those lines were understandable, but they were slightly harder to scan in long message logs than the
editor's newer `surface: target` style.

## Change

Successful key-removal commands now keep the command family visible too:

- `unbind KEY` -> `unbind: KEY`
- `unbindmode MODE KEY` -> `unbindmode: KEY@MODE`

## Why it matters

This is tiny, but it helps the same trust-first loop as the recent miss-cleanup passes:

- logs stay easier to grep
- headless tests can read one stable, typed dialect
- future humans/LLMs can tell *which* editing surface produced the line without extra context

## Scope

This change intentionally leaves the actual keymap behavior untouched:

- bindings are still removed through the existing keymap path
- missing targets still fail as `...: no such binding: ...`
- only the success wording changed
