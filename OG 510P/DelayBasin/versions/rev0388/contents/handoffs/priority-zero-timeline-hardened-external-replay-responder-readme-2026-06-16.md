# Priority-0 timeline-hardened external replay responder bundle — 2026-06-16

Use this bundle as the only pre-response material for `OQ-0263`.

Responder steps:

1. Open only the responder-only JSON packet and response template in this bundle.
2. Do not open any scorer intake, answer key, full archive, prior conversation transcript, or receipt ledger before writing the response.
3. Fill the response template with substantive packet answers, run start/completion timestamps with timezone offsets, hashes observed, attestation booleans, and operator cost.
4. Freeze the completed response before any scorer material is opened.
5. Hand the frozen response to a separate custodian. The responder must not self-custody the clean evidence record.

Non-claim: this bundle is not a completed response, not independent certification, not deletion authority, not benchmark authority, not compact-cue confirmation, and not a review court.
