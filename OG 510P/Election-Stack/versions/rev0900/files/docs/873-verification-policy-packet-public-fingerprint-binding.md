# 873 — Verification-policy packet public fingerprint binding

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

rev0854 closes a replay/substitution gap in the strict synthetic policy-lockfile lane.

Before this change, the strongest policy lockfile was bound to packet scope by `packet_id`, `election_id`, and `jurisdiction`. That prevented many wrong-packet uses, but it did not bind the policy to the selected packet's bounded publishable bytes. A same-selector packet with different public content was still the dangerous shape.

rev0854 adds `packet_public_fingerprint_sha256` to the strict policy fixture and teaches `tools/observer_verify_packet.py` to compute the packet's bounded public fingerprint through `tools/public_fingerprint_report.py`. A strict policy now fails closed if the fingerprint is missing, malformed, unavailable, warning-bearing, or mismatched.

Current strict fixture:

```text
artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0854.json
artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0854.publication-receipt.json
```

Current bounded packet public fingerprint:

```text
sha256:a0d2485f3e8746cf8cdeae8017278046d4b9c409788d8dc07c03c03c2d3f6346
```

The policy-publication receipt also carries the same packet-public-fingerprint value, so the receipt cannot silently describe the same policy digest while omitting the packet-byte binding.

This remains a synthetic verifier boundary. It binds a local strict policy to bounded publishable packet bytes; it does not prove legal signer authority, election-office employment, procurement delegation, HSM custody, independent production publication governance, live online revocation freshness, current voter instruction, certification, or live-pilot readiness.
