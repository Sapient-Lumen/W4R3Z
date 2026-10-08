# portfolio-envelope-v0

This subdirectory contains the first shared-grammar examples for the archive's core portfolio.

The files here are intentionally small.
They exist to demonstrate:
- common outer honesty fields;
- role-specific differences between canonical pack, brief, diff, verify receipt, and lineage receipt;
- explicit partiality and escalation posture;
- and how seam-specific payloads stay distinct under a shared envelope.

Current files:
- `build-state-evidence-pack.example.json`
- `semantic-context-pack.example.json`
- `build-state-diff.example.json`
- `migration-public-api-verify.example.json`
- `package-intake-brief.example.json`
- `lineage-receipt.example.json`

Validation companion files:
- `fixtures/portfolio-envelope-v0/README.md`
- `fixtures/portfolio-envelope-v0/invalid/*.json`
- `tools/check_portfolio_envelope_contract.py`
