Minimal evidence packet example.
- payloads are detached content-addressed JSON objects in objects/
- envelopes in envelopes/ reference payloads via EvidencePointer
- manifest.json lists both payloads and envelopes
Use: python tools/observer_verify_packet.py artifacts/examples/evidence_packet_minimal
