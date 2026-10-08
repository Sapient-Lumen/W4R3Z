# Redaction and public-publication checklist

Synthetic checklist only. This is not live election evidence, not legal advice, not a public-records ruling, and not authorization to publish private data.

Before publishing any evidence-derived public artifact:

1. Identify the evidence family and matching `RPP-*` row in `artifacts/registries/redaction-publication-policy.csv`.
2. Confirm the public fact being preserved: digest, timestamp, missingness, parity divergence, trust status, reviewer decision, or no-go state.
3. Remove or generalize voter, witness, staff, device, network, safety, legal-review, and private-contact details that are not needed for that public fact.
4. Preserve private/sealed material separately with retention and reviewer pointers.
5. Add a boundary sentence that avoids certification, fraud, motive, current-instruction, and legal-rights claims.
6. Record reviewer approval or keep the artifact in no-go public-release status.

Run:

```bash
python3 tools/redaction_publication_pack.py --json
python3 scripts/check_redaction_publication_pack.py
```
