# ChatGPT surface oracle userscript

`tools/chatgpt-surface-oracle.user.js` is the preferred live-surface probe
when DevTools paste transport is noisy or too small for the full report.
Install it in Tampermonkey on `https://chatgpt.com/*`.

The userscript is a companion probe, not the production extension. It exists to
turn the current ChatGPT DOM into repeatable evidence for the ChatGPT-only
adapter.

## Privacy and safety posture

Default behavior is local and passive. It does not read cookies,
`localStorage`, `sessionStorage`, or IndexedDB. It does not send network
requests. It does not submit prompts unless the explicit `ARMED checkpoint
proof` menu command is selected and two browser confirmations are accepted.

Message text and editable text are fingerprinted by length/hash by default.
UI labels are sampled because they are needed to distinguish send, tools,
upload, model picker, stop, and continue controls.

## Menu commands

- `GlassTTY: capture capsule` prints `GLASSTTY_USER_SURFACE_CAPSULE_JSON=...`.
- `GlassTTY: capture full report` prints `GLASSTTY_USER_SURFACE_REPORT_JSON=...`.
- `GlassTTY: run safe send-state drill` writes a harmless probe into the
  composer, snapshots send controls, restores the composer, and prints
  `GLASSTTY_USER_SURFACE_DRILL_JSON=...`.
- `GlassTTY: start mutation observer` records selector/state changes while the
  app rerenders or streams.
- `GlassTTY: stop mutation observer` stops recording.
- `GlassTTY: copy last report` copies the latest report when the userscript
  manager allows it.
- `GlassTTY: export last report` downloads the latest JSON locally.
- `GlassTTY: ARMED checkpoint proof` writes the checkpoint prompt, asks again,
  clicks the strict send candidate, then waits for the checkpoint response.

## Console API

The script also exposes:

```js
window.__GLASSTTY_SURFACE_ORACLE__.captureCapsule()
window.__GLASSTTY_SURFACE_ORACLE__.captureFull()
window.__GLASSTTY_SURFACE_ORACLE__.runSendDrill()
window.__GLASSTTY_SURFACE_ORACLE__.startObserver()
window.__GLASSTTY_SURFACE_ORACLE__.stopObserver()
window.__GLASSTTY_SURFACE_ORACLE__.exportLast()
window.__GLASSTTY_SURFACE_ORACLE__.copyLast()
window.__GLASSTTY_SURFACE_ORACLE__.armedCheckpointProof()
```

## Why this exists

The live rev0329 capsule showed a real prompt editor at `#prompt-textarea`,
explicit message author roles, and a false send candidate at
`#composer-plus-btn`. That means the useful next probe is not another huge
static DOM dump; it is a before/after send-state drill that tells us what
button appears or enables only after composer text exists.


## rev0332/rev0333 behavior

The userscript now auto-copies prefixed JSON lines with `GM_setClipboard` when
`auto_copy_results` is true. The safe send-state drill should place a
`GLASSTTY_USER_SURFACE_DRILL_JSON=...` line on the clipboard and show a small
GlassTTY note in the page. It also probes the observed strict send lock:
`#composer-submit-button` / `data-testid="send-button"` / `Send prompt`, while
continuing to block `#composer-plus-btn` as a non-send composer tool.

## rev0333 drift verdict behavior

The userscript now embeds a compact expected-surface contract and adds a
`surface_contract_drift` block to capsule/full/drill output. The menu command
`GlassTTY: copy drift verdict` copies only that compact verdict as:

```text
GLASSTTY_USER_SURFACE_DRIFT_JSON=...
```

Use this before a live proof attempt. A `surface-contract-ok` verdict means the
known ChatGPT proof selectors are still present. A `surface-drift-blocker`
means the extension should not submit a proof until the adapter or contract is
updated.

## rev0334 note

The oracle remains the live-surface capture tool. The new proof rehearsal command is separate and should be used when live ChatGPT execution is unavailable; it does not replace fresh oracle reports when drift is suspected.
