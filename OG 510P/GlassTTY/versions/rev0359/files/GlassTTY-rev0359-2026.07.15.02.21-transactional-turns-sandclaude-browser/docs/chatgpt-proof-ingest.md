# ChatGPT proof ingest

`proof-ingest` is the first command to run after downloading proof JSON from the side panel.
It checks that the downloaded file is intact enough to become the source for evidence-pack
finalization, writes a normalized capture copy, and writes a redacted preview that removes
embedded PNG base64 while preserving screenshot hashes and dimensions.

## Why this exists

A live proof JSON can contain a full visible-tab screenshot as a data URL. That makes
clipboard transfer and manual editing risky. Ingest gives the operator a stable handoff:

1. download the side-panel proof JSON,
2. run ingest on the downloaded file,
3. finalize the normalized output.

The command does not make a live claim. It only decides whether a downloaded capture is a
live candidate or a rehearsal/non-live artifact.

## Commands

For a downloaded live candidate:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest \
  --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json \
  --require-live-candidate \
  --pretty
```

Then finalize the normalized copy:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack \
  --input validation/latest/chatgpt-first-proof-capture.json \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --require-live \
  --clean \
  --pretty
```

One-command ingest plus finalization is also available. Pass the live pack directory explicitly for live use:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest \
  --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json \
  --require-live-candidate \
  --finalize \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --clean \
  --pretty
```

## Outputs

Default outputs:

- `validation/latest/chatgpt-first-proof-capture.json` — normalized full capture.
- `validation/latest/chatgpt-first-proof-capture.redacted.json` — safe preview; screenshot data URLs are redacted to hashes/dimensions.
- `validation/latest/chatgpt-proof-ingest-summary.json` — ingest verdict, blockers, warnings, and next actions.

## Live-candidate checks

A live candidate must include:

- `prompt.write`, `prompt.submit`, and `transcript.latest` actions.
- exact checkpoint prompt readback before submit.
- exact `GLASSTTY-CHECKPOINT` latest output.
- proof live gate evidence before submit.
- strict send evidence for `#composer-submit-button` / `send-button` / `Send prompt`.
- single ChatGPT tab / route continuity evidence when supplied.
- a valid non-placeholder PNG screenshot data URL.
- no rehearsal/dry-run flags anywhere in the capture.

Rehearsal captures may pass ingest for plumbing, but their verdict stays non-live.
