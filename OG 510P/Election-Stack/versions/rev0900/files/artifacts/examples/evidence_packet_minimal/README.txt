Example evidence packet bundle.

- Envelopes: hfv.coverage.report; hfv.inspection.suppression_report
- Payload schemas: schemas/CoverageReport.json; schemas/InspectionSuppressionReport.json
- Intended use: smallest runnable illustration of packet layout (objects/, envelopes/, manifest.json).
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_minimal
