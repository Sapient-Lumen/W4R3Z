# ChatGPT proof operator handoff

- verdict: `rehearsal-proof-pack-finalized-not-live`
- ok: `True`
- require_live: `False`
- pack_dir: `validation/latest/chatgpt-proof-rehearsal-evidence-pack`
- attempt_id: `chatgpt-proof-rehearsal-001`
- artifact_count: `30` / `30`
- evaluator_verdict: `rehearsal-harness-ok-not-live`
- privacy_review_verdict: `privacy-review-rehearsal-not-live`

## Ready path

- Re-run `proof-check-pack --require-live` before making any live proof claim.
- Human privacy/redaction review must be `privacy-review-pass` before publishing screenshots or transcripts.

## Next commands

- `glassttyd proof-check-pack --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack --pretty`
- `glassttyd proof-finalize-pack --input <live-sidepanel-proof.json> --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --clean --pretty`
