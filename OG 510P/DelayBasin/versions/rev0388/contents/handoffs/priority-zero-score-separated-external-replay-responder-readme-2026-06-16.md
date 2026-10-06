# Priority-0 score-separated external replay responder bundle — 2026-06-16

Use this bundle as the only pre-response responder material for `OQ-0264`.

Responder steps:

1. Open only the responder-only JSON packet and response template in this bundle.
2. Do not open any scorer intake, answer key, score sheet template, full archive, prior conversation transcript, receipt ledger, or prior response before writing the response.
3. Fill the response template with substantive packet answers, run start/completion timestamps with timezone offsets, hashes observed, attestation booleans, and operator cost.
4. Do **not** add `manual_metric_scores` to the response. The response file must remain hash-stable after freeze.
5. Freeze the completed response before any scorer material is opened.
6. Hand the frozen response to a separate custodian. The responder must not self-custody the clean evidence record.

Non-claim: this bundle is not a completed response, not independent certification, not deletion authority, not benchmark authority, not compact-cue confirmation, and not a review court.
