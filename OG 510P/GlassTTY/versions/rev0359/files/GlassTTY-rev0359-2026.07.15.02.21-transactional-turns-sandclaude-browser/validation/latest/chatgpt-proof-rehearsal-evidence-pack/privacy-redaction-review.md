# Privacy/redaction review

- verdict: `privacy-review-rehearsal-not-live`
- ok: `True`
- generated_at: `2026-07-11T06:48:11Z`
- pack_dir: `validation/latest/chatgpt-proof-rehearsal-evidence-pack`
- publishable_without_additional_redaction: `False`

## Human attestation

- reviewer: `None`
- decision: `pending`
- attest_screenshot_reviewed: `False`
- attest_no_unrelated_content: `False`
- attest_local_only: `False`
- complete: `False`

## Screenshot

- exists: `True`
- sha256: `4ff6ab670a58c14270e034e2090d9a432caa263a14e0a25785386b0c12f880b5`
- dimensions: `{'ok': True, 'width': 1, 'height': 1}`
- placeholder_not_live: `True`

## Content checks

- probe_prompt_exact: `True`
- composer_after_exact: `True`
- submit_readback_exact: `True`
- assistant_latest_exact: `True`
- possible_sensitive_marker_count: `0`

## Blockers

- none

## Warnings

- surface-screenshot.png is placeholder-sized 1x1

## Recommendations

- This is a rehearsal pack. Keep privacy status not-live and do not publish it.
- For live proof, capture a real visible ChatGPT screenshot and rerun finalization.

## Machine-readable summary

```json
{
  "human_attestation_complete": false,
  "ok": true,
  "publishable_without_additional_redaction": false,
  "schema_version": 1,
  "tool": "glasstty-chatgpt-proof-privacy-review",
  "verdict": "privacy-review-rehearsal-not-live"
}
```
