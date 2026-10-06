# Priority-0 clean-response custody README — 2026-06-16

Use this with the submission kit. Before response completion, the responder receives only `handoffs/priority-zero-custody-hardened-external-replay-responder-bundle-2026-06-16.zip`. After the response is complete, freeze the file and compute its SHA256. Then fill `assays/priority-zero-clean-external-response-evidence-record-template-2026-06-16.json` with the response hash, responder/custodian IDs, timestamps, and exposure attestations.

Only after the response hash has been recorded should the scorer open `assays/priority-zero-custody-hardened-external-replay-scorer-intake-2026-06-16.json`. A response that only self-attests cleanliness inside its own JSON is not clean external evidence without this separate custody record.

Scoring command after response and evidence record exist:

```bash
make score-external-response RESPONSE=<completed-response.json> EVIDENCE=<custody-record.json>
```

Non-claim: custody readiness is not external certification, not deletion authority, not benchmark authority, and not compact-cue confirmation.
