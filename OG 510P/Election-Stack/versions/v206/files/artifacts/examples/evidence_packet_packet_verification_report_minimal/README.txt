Example evidence packet for hfv.verifier.packet_verification_report.

- Payload: schemas/PacketVerificationReport.json
- Intended use: a *publishable* packet-verification report (codes-only) emitted by
  tools/observer_verify_packet.py --emit-evidence-object.
- This example also ships the verifier policy profile object as a detached,
  content-addressed object (digest pinned in the report + envelope subject).
- Signatures are placeholders (alg=none).

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_packet_verification_report_minimal

Regenerate (if VERSION/pins drift):
  python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_minimal --json --public \
    --emit-evidence-object /tmp/out --policy-profile artifacts/templates/verifier-policy-profile.json \
    --issuer-id verifier:example
  # then copy /tmp/out into this example directory
