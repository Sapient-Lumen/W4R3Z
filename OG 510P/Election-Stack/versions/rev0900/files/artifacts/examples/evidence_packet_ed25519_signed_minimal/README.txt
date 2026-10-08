Example evidence packet for hfv.coverage.report.
- Payload: schemas/CoverageReport.json
Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_ed25519_signed_minimal

Authenticated fixture check: add --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-demo.json. The packet-contained trust-keyset copy is intentionally rejected as a self-supplied trust root.
