Example evidence packet bundle.

- Envelopes: hfv.public.notice (initial + correction)
- Payload schemas: schemas/PublicNotice.json
- Attachments: transparency_receipt + gossip_summary
- Signatures are placeholders (alg=none).

Comms drill skeleton:
- Scenarios: conflicting_reports_overload / political_pressure_unverified_claims / forged_official_statement_time_to_refute.
- Keep: epistemic tags (218), next_update_at (219), correction/supersedes links (220).
- Publish digest-first: notice digest short-form + packet manifest digest (MAPT; 187/195).

Publishable drill outcome: pair with at least one independent PacketVerificationReport (see evidence_packet_packet_verification_report_minimal) and record digests in the AAR.

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_public_notice
