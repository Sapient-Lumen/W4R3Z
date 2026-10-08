# Research — qutebrowser userscript packs and browser-native entrypoints

qutebrowser is a good example of why VHK needs app-native browser adapter packs
instead of flattening browser workflows into generic window focus + key replay.

## What current upstream docs say

- qutebrowser userscripts are an official extension surface which can be called
  with `:spawn --userscript ...` or via key bindings.
- qutebrowser also supports hint-driven userscript execution via
  `:hint links userscript ...`, which means a userscript can receive the URL and
  selected element context chosen by the browser.
- userscripts receive a substantial `QUTE_*` environment surface including
  `QUTE_MODE`, `QUTE_URL`, `QUTE_CURRENT_URL`, `QUTE_TITLE`,
  `QUTE_SELECTED_TEXT`, `QUTE_SELECTED_HTML`, and `QUTE_FIFO`.
- normal qutebrowser commands can be written back to `QUTE_FIFO`, which makes
  userscripts more than a one-way spawn hook.

## Product lesson for VHK

The strongest Linux-native move here is not to pretend VHK should become a
browser extension runtime. Instead:

- qutebrowser owns browser context, hint selection, and userscript launching
- VHK owns macro semantics and cross-tool automation logic
- a thin reviewed pack should bridge those two worlds explicitly

That is why this revision adds `vhk gen-qutebrowser-pack` as a thin userscript
adapter pack instead of another generic backend claim.

## Design choices this revision encodes

- export one reviewable userscript per qutebrowser-targeted macro
- pass browser context into VHK via `vhk run ... --vars <json>`
- keep hint-mode compatible by preserving `QUTE_MODE` / `QUTE_URL` /
  `QUTE_CURRENT_URL` rather than collapsing them to one fake URL variable
- use `QUTE_FIFO` only for lightweight status feedback, not as a place where VHK
  macro semantics get reimplemented

## Next researchable follow-up

A future revision should study whether VHK can safely generate richer
qutebrowser-native helpers for:

- hint-focused URL collection flows
- browser-side open/copy/message commands derived from reviewed macro intent
- more structured userscript argument templates without inventing a second DSL
