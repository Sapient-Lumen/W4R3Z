# Legal/reuse, attribution, third-party, contributor, derivative, and compliance-boundary review runbook v1

## Scope

Use this runbook before repeating any claim about license status, reuse permission, attribution, third-party content, contributor provenance, derivative redistribution, or compliance boundary.

## Required checks

1. Read `LICENSE_REUSE_POLICY.yml` and confirm that no package-level public legal license grant is inferred unless a real license file and expression are deliberately added.
2. Read `ATTRIBUTION_CITATION_LEDGER.yml` and confirm citation/attribution language does not imply endorsement, sponsorship, official status, or legal sufficiency.
3. Read `THIRD_PARTY_CONTENT_REGISTER.yml` and confirm external anchors, quotations, generated text, and third-party content are not collapsed into clearance.
4. Read `CONTRIBUTOR_PROVENANCE_LEDGER.yml` and confirm local provenance rows do not imply assignment, CLA/DCO, warranty, or external contributor approval.
5. Read `DERIVATIVE_REDISTRIBUTION_POLICY.yml` and confirm derivative-use notes do not create downstream permission, support, compatibility, or compliance guarantees.
6. Read `COMPLIANCE_BOUNDARY_LEDGER.yml` and confirm legal advice, regulatory review, certification, warranty, indemnity, and jurisdictional approval remain forbidden.
7. Run `python3 tools/check_legal_reuse.py .`.
8. Run `python3 tools/run_query_regression.py .`.
9. Run `python3 tools/run_fixture_corpus.py .`.
10. Run `python3 tools/validate_archive.py .` after reports and manifest are regenerated.

## Stop conditions

Stop local release language if any checker reports an unsafe license grant, endorsement claim, IP-clearance claim, contributor-assignment claim, derivative-authorization claim, or legal/regulatory compliance claim.

## Not claimed

This runbook is not legal advice, licensing advice, copyright clearance, public license selection, contributor agreement, compliance program, warranty, indemnity, or downstream redistribution authorization.
