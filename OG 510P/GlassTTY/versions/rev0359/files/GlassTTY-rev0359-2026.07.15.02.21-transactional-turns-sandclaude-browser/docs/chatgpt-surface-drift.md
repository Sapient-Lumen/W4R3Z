# ChatGPT surface drift recognition

The live proof cannot depend on stale ChatGPT selectors. This cube treats UI
change as expected operational input, not as a surprise. The current known-good
contract is:

```text
validation/latest/chatgpt-live-surface-contract-rev0335-2026.06.13.json
```

It was derived from the rev0331 Tampermonkey drill/full reports and locks only
the facts needed by the ChatGPT proof path:

- target host remains `chatgpt.com`;
- route posture remains `plain-chat`;
- prompt editor remains `#prompt-textarea`;
- strict submit remains `#composer-submit-button` with
  `data-testid="send-button"` and aria-label `Send prompt`;
- explicit `data-message-author-role` user/assistant nodes remain mounted;
- `#composer-plus-btn` / `Add files and more` remains a blocked non-send
  control.

## CLI flow

Audit a returned userscript, capsule, drill, or page-world JSON line:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts \
  glassttyd surface-audit path/to/report.json --pretty
```

Build a new contract from a known-good report:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts \
  glassttyd surface-contract-build path/to/report.json \
  --out validation/latest/chatgpt-live-surface-contract-revXXXX-YYYY.MM.DD.json \
  --pretty
```

Check a new report against the saved contract:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts \
  glassttyd surface-contract-check path/to/report.json \
  --contract validation/latest/chatgpt-live-surface-contract-rev0335-2026.06.13.json \
  --pretty
```

The checker returns:

- `surface-contract-ok`: proof path should be attempted if the operator is ready.
- `surface-drift-warning`: proof path may still work, but review the warning.
- `surface-drift-blocker`: do not submit a live proof until the adapter or
  contract is updated.

## Userscript flow

The Tampermonkey oracle embeds the same contract summary and adds a
`surface_contract_drift` block to capsule/full/drill output. Its menu command
`GlassTTY: copy drift verdict` copies only that compact verdict as
`GLASSTTY_USER_SURFACE_DRIFT_JSON=...`.

Use this when you only need to know whether ChatGPT still resembles the saved
contract. Use the full report when the verdict is a blocker and you need enough
DOM evidence to update the adapter.

## What counts as a blocker

- The tab is no longer a ChatGPT host.
- The route is not a plain chat route.
- The prompt editor is not the expected writable composer.
- The strict send button is missing or resolves to a known non-send composer
  control.
- Explicit author-role nodes disappear.

Counts shifting, menu IDs changing, or auxiliary controls appearing are warnings
unless they break the proof path.
