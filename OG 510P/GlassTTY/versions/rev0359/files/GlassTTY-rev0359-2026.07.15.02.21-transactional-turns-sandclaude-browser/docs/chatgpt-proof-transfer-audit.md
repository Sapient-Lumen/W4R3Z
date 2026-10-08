# ChatGPT proof transfer audit

`proof-transfer-audit` is the first CLI check for a downloaded side-panel proof JSON. It is intentionally earlier than `proof-attempt-audit` and `proof-ingest`.

Its job is to catch transfer/container failures before the cube treats a file as a live proof candidate:

- invalid or missing JSON,
- recovery-vault preview records passed as proof captures,
- missing `actions` or `raw_envelopes`,
- mismatch between action order and raw-envelope order,
- non-contiguous `sequence_index` values,
- inconsistent `attempt_id` values,
- missing final `proof.operator_readiness` envelope,
- missing or placeholder visible-tab screenshot when requested.

Typical live command:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-transfer-audit \
  --input ~/Downloads/GlassTTY-<attempt>-chatgpt-first-proof-capture.json \
  --require-ready-to-download \
  --require-full-screenshot \
  --pretty
```

`proof-autopilot --execute-live --input <json>` now runs this audit before attempt-order audit and ingest. A failed transfer audit means the operator should re-download the proof JSON from the side panel or promote a full recovery-vault record with `proof-recovery-vault`.
