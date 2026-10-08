# Turnout-oracle / turnout surveillance risk quickcheck

**Track:** B (Remote return / hard-mode research)

Use this when proposing or changing **eligibility/revocation transparency** surfaces or any public aggregation that could leak who voted/when.
This is a *privacy + coercion* boundary: if you can derive turnout timing or participation from the public surface, you may enable intimidation.

References: `docs/75-revocation-and-eligibility-transparency.md`, `docs/81-privacy-preserving-eligibility-token-minting-protocol.md`, hazard **HZ‑026**.

## Quickcheck (bounded)

- ☐ **Metadata budget defined:** name the public fields that will exist (and explicitly name what will *not* be published: per-person timestamps, fine geography, stable identifiers).
- ☐ **Batching rule defined:** specify minimum batch size / delay / grouping so updates cannot be joined to individuals by timing.
- ☐ **Joinability test:** write one paragraph describing the most plausible join attack (public updates + external signals) and why the metadata budget + batching rule reduce it.
- ☐ **Private dispute lane preserved:** ensure individuals can resolve status via private proof lanes (e.g., `VoterStatusProof`) without forcing public disclosure.
- ☐ **Incident trigger named:** define what evidence would indicate deanonymization risk and how to respond (reference **HZ‑026** + `artifacts/playbooks/coercion-response-playbook.md`).

## Recordkeeping (bounded)

- ☐ Log a row in `artifacts/registries/turnout-oracle-risk-assessments.csv` (store pointers/digests only; do not paste long analyses).
