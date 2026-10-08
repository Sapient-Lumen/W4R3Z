# Verification policy verifier-requirements and report-version binding

**Track:** Shared

rev0853 adds a strict-policy semantics guard: a byte-pinned verification-policy lockfile must declare which archive version, PacketVerificationReport version, and auth profile are allowed to interpret it.

This closes a dangerous class of replay/substitution errors where a still-valid policy digest could be interpreted by a later verifier whose public report fields or auth-profile meaning changed. The guard is executable in `tools/observer_verify_packet.py` and release-gated by `scripts/check_signature_verifier_ed25519.py`.

Current synthetic policy fixture:

`artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0853.json`

The policy is still synthetic. It does not prove production change control, real election-office authority, signer employment, legal delegation, online revocation freshness, certification, current voter instruction, or live-pilot readiness.
