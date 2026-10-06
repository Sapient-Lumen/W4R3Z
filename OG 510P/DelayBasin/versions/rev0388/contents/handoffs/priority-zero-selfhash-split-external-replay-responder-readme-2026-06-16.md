# Priority-0 selfhash-split external replay responder bundle — 2026-06-16

Use this bundle as the only pre-response responder material for `OQ-0265`.

Responder steps:

1. Open only the responder-only JSON packet and response template in this bundle.
2. Do not open any scorer intake, answer key, score sheet template, handoff manifest, expected bundle digest, full archive, prior conversation transcript, receipt ledger, or prior response before writing the response.
3. Compute the SHA256 of the responder bundle file you were handed and paste that observed digest into `responder_stage.saw_responder_bundle_sha256`.
4. Fill the response template with substantive packet answers, run start/completion timestamps with timezone offsets, the responder-packet hash, attestation booleans, and operator cost.
5. Do **not** add `manual_metric_scores` to the response. The response file must remain hash-stable after freeze.
6. Freeze the completed response before any scorer material, handoff manifest, expected responder-bundle digest, or score sheet is opened.
7. Hand the frozen response to a separate custodian. The responder must not self-custody the clean evidence record.

Why the expected bundle hash is absent: a file inside a ZIP cannot stably contain the SHA256 of the ZIP that contains it. The expected digest is therefore held only in scorer/custody material that opens after response freeze.

Non-claim: this bundle is not a completed response, not independent certification, not deletion authority, not benchmark authority, not compact-cue confirmation, and not a review court.
