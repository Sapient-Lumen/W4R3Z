# 883 — Verification-policy public-fingerprint profile binding

**Track:** Shared / Verification / Policy lockfile
**Status:** v858 executable verifier hardening

rev0858 closes the next replay/portability gap after packet-public-fingerprint binding.

The strict synthetic policy lockfile already bound a selected packet by `packet_id`, `election_id`, `jurisdiction`, verifier/report requirements, validity window, and `packet_public_fingerprint_sha256`. That still left one subtle risk: the digest could be reinterpreted later if the bounded public-fingerprint helper changed its inclusion rules or report/profile version.

rev0858 adds `packet_public_fingerprint_profile` to the strict policy fixture and requires it to match `tools/public_fingerprint_report.py`'s current report-format/profile version before `SIGNATURE_VERIFIED` is possible. The policy-publication receipt must carry the same profile value, so the receipt binds both the digest and the digest-construction profile.

Current strict fixture:

```text
artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0858.json
artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0858.publication-receipt.json
```

Current bound packet public fingerprint:

```text
sha256:a0d2485f3e8746cf8cdeae8017278046d4b9c409788d8dc07c03c03c2d3f6346
```

Current public-fingerprint profile:

```text
1.0
```

The executable regression now proves fail-closed behavior for missing policy profile, wrong policy profile, and policy-publication receipt profile mismatch.

Boundary: this is a synthetic local-verifier control. It does not prove production verifier binary integrity, real signer authority, election-office employment, independent publication governance, online revocation freshness, certification, legal reliance, current voter instruction, or live-pilot readiness.
