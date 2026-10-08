# Envelope canonicalization checklist

## Goal
Prevent *format drift* from breaking verification or enabling fake artifacts.

## Before publishing any public packet
- [ ] All evidence payloads are valid JSON and stay within the I-JSON subset (avoid NaN/Infinity; avoid ambiguous floats).
- [ ] Identifiers that might be large or ambiguous (device ids, reference values, counters) are encoded as **strings**.
- [ ] Each `EvidenceEnvelope` includes:
  - `canonicalization: RFC8785-JCS`
  - correct `payload_digest`
  - correct `tbs_digest` per `docs/176`
  - exactly one of `payload_inline` or `payload_pointer`
- [ ] Detached payload objects are stored as **canonical JSON bytes** (JCS output) and are content-addressed.
- [ ] Run offline verifier:
  - `python tools/observer_verify_packet.py <packet_dir>`
- [ ] If signature verification is in scope, verify signatures using an independent implementation and record tool versions.

## After publishing
- [ ] Mirror the packet to at least two independent hosts.
- [ ] Obtain at least one third-party observer report envelope that independently recomputes digests.
