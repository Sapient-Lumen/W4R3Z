# 898 — Public-fingerprint profile 1.4 current-policy fixture audit

**Track:** Shared / Verifier / Release gate

rev0862 refreshes the current strict synthetic verification-policy fixture so verifier-requirements binding, PacketVerificationReport version, and public-fingerprint profile remain coherent after the oversized-file warning change.

Current fixture pins:

- policy: `sha256:6d72a8b932f1c704faeb5ada963ddf9cdb803f9bac2450f133d6e8f00817c1c3`
- policy receipt: `sha256:eaaec5f873f24edf6523f2f649deefbbd5e16a1748356ddfe03ca7b0092b0705`

Audit artifact: `artifacts/reports/public-fingerprint-oversized-file-audit-rev0862.json`.

The trust-chain fixture surface remains deliberately small: the strongest synthetic path is a fixed packet-external set of byte-pinned fixtures rather than a hand-copied CLI pile.

Boundary: the refreshed policy proves only synthetic local verifier behavior for this archive revision. It does not prove signer employment, election-office authorization, HSM custody, independent publication governance, online revocation freshness, current voter instruction, legal reliance, certification, or live-pilot readiness.
