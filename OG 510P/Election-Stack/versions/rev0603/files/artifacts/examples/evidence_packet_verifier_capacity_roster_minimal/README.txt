Example evidence packet for hfv.verifier.capacity_roster.

- Payload: schemas/VerifierCapacityRoster.json
- Intended use: publishable directory of verifier capacity (who will look + where reports land) before the contested window.
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_verifier_capacity_roster_minimal

Attachments: gossip_summary + transparency_receipt (required per registry).

