Example evidence packet for hfv.time.beacon.

- Payload: schemas/TimeBeacon.json
- Intended use: minimal time-beacon envelope illustrating timestamp-style evidence objects.
- Signatures are placeholders; tools/observer_verify_packet.py checks digests and pointers only.

Verify: python3 tools/observer_verify_packet.py artifacts/examples/evidence_packet_time_beacon_minimal
