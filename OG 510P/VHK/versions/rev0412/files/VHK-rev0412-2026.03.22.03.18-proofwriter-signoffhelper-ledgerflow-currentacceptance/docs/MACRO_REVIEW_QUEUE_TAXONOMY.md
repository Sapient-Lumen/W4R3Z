# Macro review queue taxonomy

`vhk macro-review-queue-json` now emits a stable issue taxonomy plus structured per-item evidence so recorder-review debt can be triaged mechanically instead of only summarized in prose.

## Root taxonomy

The payload now carries an `issue_taxonomy` map. Each code declares:

- `status_label` — compact human/operator label
- `severity` — current priority signal
- `action_lane` — the preferred class of next step
- `scope_class` — what part of truth the warning is actually about
- `truth_effect` — whether the issue is a gap, drift, reconciliation hint, or brittleness warning
- `summary` — the canonical explanation for that issue kind
- `non_claims` — what the warning explicitly does **not** prove

Current issue codes:

- `missing_recording_sidecar`
- `stale_recording_sidecar`
- `recording_newer_than_source`
- `exact_segments`
- `title_segments`

## Per-item shape

Each queue item now repeats the taxonomy through:

- `issue_code`
- `status_label`
- `severity`
- `action_lane`
- `scope_class`
- `truth_effect`
- `non_claims`
- `evidence`

`evidence` is intentionally compact. It names the macro source path, recording sidecar path or `<missing>`, freshness status, and relevant selector-segment counts so a private LLM or operator can explain *why* an item is in the queue without scraping multiple surfaces first.

## Why this matters

The macro review queue is no longer just a descriptive convenience. It is a triage contract for recorder debt: what issue is present, how serious it is, which lane should handle it, what the warning does **not** establish, and what evidence justifies the recommendation.
