Example evidence packet bundle.

- Envelopes: hfv.public.notice; hfv.publication.contract; hfv.publication.trigger_event; hfv.coverage.publication_report
- Payload schemas: schemas/PublicNotice.json; schemas/PublicationContract.json; schemas/PublicationTriggerEvent.json; schemas/PublicationCoverageReport.json
- Intended use: minimal publication-compliance run (promise → trigger → coverage) with receipted+gossiped evidence.
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_compliance_minimal
