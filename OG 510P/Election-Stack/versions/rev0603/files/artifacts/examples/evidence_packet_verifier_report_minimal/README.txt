Example evidence packet for hfv.verifier.report.

- Payload: schemas/VerifierReport.json
- Intended use: minimal publishable VerifierReport wrapped in an EvidenceEnvelope.
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_verifier_report_minimal
