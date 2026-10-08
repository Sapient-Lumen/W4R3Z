Example evidence packet for hfv.results.enr_update.

- Payload: schemas/ENRUpdate.json
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_enr_receipted
