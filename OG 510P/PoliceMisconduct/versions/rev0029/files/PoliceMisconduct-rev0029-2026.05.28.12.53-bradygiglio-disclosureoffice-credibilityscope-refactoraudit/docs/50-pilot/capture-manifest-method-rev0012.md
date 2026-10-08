# Capture manifest method — rev0012

Rev0012 introduces a capture manifest because the cube should not jump directly from citations to summaries.

The capture pipeline is:

`source label → URL resolved → HTTP metadata observed → private payload captured → SHA-256 digest → WARC/WACZ or equivalent archive → privacy scan → bounded summary → claim review`

Rev0012 opens only the first three steps for selected targets.

## Required metadata before payload review

Every future capture must record source URL, source owner, retrieval time, access result, content type, payload byte count, capture tool, SHA-256 payload hash, and privacy-scan state.

## Format posture

WARC remains the preferred long-term web archive family. WACZ is acceptable for packaged replay/distribution when paired with custody metadata. Neither format changes the evidence rule: capture enables later review but does not itself create a misconduct or current-status claim.

