# Priority-0 custody-hardened external replay responder README — 2026-06-16

Give the responder only this bundle before the response is complete. The bundle should contain exactly:

- `assays/priority-zero-custody-hardened-external-replay-responder-only-2026-06-16.json`
- `assays/priority-zero-custody-hardened-external-replay-response-template-2026-06-16.json`
- `handoffs/priority-zero-custody-hardened-external-replay-responder-readme-2026-06-16.md`

The responder should fill only `responder_stage` in the response template. Do not provide scorer-intake material, answer-key material, the full archive, prior conversation context, or this package receipt before the response is frozen.

After the completed response exists, the custodian records its hash in the custody evidence template and only then releases scorer-only material for scoring.

Non-claim: this README and responder bundle are not a clean external replay result, not independent certification, not deletion authority, not benchmark authority, and not compact-cue confirmation.
