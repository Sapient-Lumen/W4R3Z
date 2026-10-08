Example evidence packet bundle.

- Envelopes: hfv.public.notice (2 envelopes: initial notice + correction notice)
- Payload schemas: schemas/PublicNotice.json
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice
