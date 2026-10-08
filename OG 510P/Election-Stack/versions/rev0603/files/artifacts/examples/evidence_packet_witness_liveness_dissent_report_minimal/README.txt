Example evidence packet for hfv.witness.liveness_dissent_report.

- Payload: schemas/WitnessLivenessDissentReport.json

Purpose:
- Demonstrates a compact, signed witness “behavioral health” report: cosign liveness + published dissent/refusal items.
- Intended to make “quiet capture” legible without long narrative.

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_witness_liveness_dissent_report_minimal
