# Native message budget

Chrome native messaging is generous from extension to host, but much tighter from host back to the browser.

GlassTTY now includes a small budget tool so future sessions can estimate whether a saved fixture or other JSON artifact is still safely below Chrome's host-to-extension ceiling before trying a live run. As of rev0086, the runtime native host also treats outbound overflows as a recoverable condition by spilling the full message to disk and returning a compact `error.report` instead of crashing the bridge.

## Why this exists

- GlassTTY's bridge depends on Chromium native messaging.
- Rich fixture captures can grow quickly once they include HTML samples, locator candidates, and semantic outline data.
- Budget drift is easy to miss in purely synthetic tests.

## Commands

```bash
python scripts/native-message-budget.py fixtures/corpus --pretty
python -m glassttyd.cli native-message-budget fixtures/corpus --pretty
```

The report includes:

- raw JSON size
- estimated payload size
- estimated native-message envelope size
- host-to-extension fit/status/margin
- extension-to-host fit/status/margin

## Current rule of thumb

Treat `warning` as a sign to trim fixture payloads before promoting richer capture fields into the live bridge. If a live run still crosses the line, inspect `GLASSTTY_HOME/state/latest/oversized-host-outbound.json` and the referenced fixture artifact under `GLASSTTY_HOME/state/fixtures/`.

If repeated live overflows start accumulating historical artifacts, use `python -m glassttyd.cli overflow-prune --keep 3 --max-disk-bytes 2000000` as a conservative dry-run first, then rerun with `--apply` after the evidence has been archived elsewhere.
