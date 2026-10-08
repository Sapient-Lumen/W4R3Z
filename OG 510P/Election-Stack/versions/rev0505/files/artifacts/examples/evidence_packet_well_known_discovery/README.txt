Example evidence packet for hfv.public.well_known_discovery.

- Payload: schemas/WellKnownElectionStackDiscovery.json
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_well_known_discovery
