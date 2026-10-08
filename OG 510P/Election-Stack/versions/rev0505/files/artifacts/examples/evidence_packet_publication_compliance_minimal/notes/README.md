# Evidence packet example: publication compliance (minimal)

**Track:** Shared (cross-cutting)


This packet demonstrates the *deadline promise → measurable compliance* path:

- a PublicationContract rule says: if `incident_declared` occurs, publish a `hfv.public.notice` within 30 minutes.
- a `hfv.publication.trigger_event` anchors the deadline.
- a `hfv.public.notice` is published within the window.
- `tools/publication_compliance.py` computes a `hfv.coverage.publication_report`.

All core artifacts include the required attachments (receipt + gossip) per registry.
Receipts and gossip summaries are **synthetic examples**.

Try:

```bash
python tools/observer_verify_packet.py artifacts/examples/evidence_packet_publication_compliance_minimal
python tools/publication_compliance.py artifacts/examples/evidence_packet_publication_compliance_minimal
```
