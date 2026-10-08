Example evidence packet bundle.

- Envelopes: hfv.publication.contract; hfv.publication.suppression_report
- Payload schemas: schemas/PublicationContract.json; schemas/PublicationSuppressionReport.json
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_contract
