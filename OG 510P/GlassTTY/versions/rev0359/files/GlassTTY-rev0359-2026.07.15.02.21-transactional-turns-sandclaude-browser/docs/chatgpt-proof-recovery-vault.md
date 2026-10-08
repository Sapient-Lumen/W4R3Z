# ChatGPT proof recovery vault

The side panel stores the latest assembled proof document in a local recovery vault so a page reload does not force the operator to restart a live attempt.

The primary transfer remains **Download proof JSON**. The recovery vault is a fallback.

## Inspect or extract a vault

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-recovery-vault \
  --input ~/Downloads/glasstty-chatgpt-proof-recovery-vault.json \
  --require-full-document \
  --require-integrity-match \
  --pretty
```

The command accepts either:

- a normal side-panel proof JSON,
- a full recovery-vault record containing `document`, or
- a preview-only vault record.

Preview-only records are blocked because they do not contain raw proof envelopes or screenshot data.

## Promote recovered JSON into the normal live path

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-recovery-vault \
  --input ~/Downloads/glasstty-chatgpt-proof-recovery-vault.json \
  --require-full-document \
  --require-integrity-match \
  --require-live-candidate \
  --ingest \
  --pretty
```

For a full live run, continue with:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot \
  --execute-live \
  --input validation/latest/chatgpt-first-proof-capture.json \
  --clean \
  --pretty
```

## Important safety behavior

The recovery-vault command does not widen proof claims. It only classifies, validates, extracts, and optionally delegates to `proof-ingest`. A rehearsal vault remains rehearsal-only, and a preview-only vault cannot become a live proof.
