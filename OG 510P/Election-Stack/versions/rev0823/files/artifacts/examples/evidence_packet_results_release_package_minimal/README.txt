Example evidence packet for hfv.results.release_package.
- Payload: schemas/ResultsReleasePackage.json

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_results_release_package_minimal

Notes:
- Demonstrates the recommended publication shape after docs/238: ResultsReleasePackage is published as an EvidenceEnvelope payload.
- Includes required attachments (transparency_receipt + gossip_summary) per artifacts/registries/envelope-attachment-requirements.csv.
- Signatures are placeholders.
