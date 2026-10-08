Example evidence packet for hfv.public.notice_signing_keyset.

- Payload: schemas/PublicNoticeSigningKeyset.json
- Required attachments included: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice_signing_keyset_minimal
