# 858. Verification-policy selector, validity, and mixed-scope firewall

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

**Revision:** v849

rev0849 closes the next strict-policy-lockfile replay foot-gun. The strongest synthetic verifier path now rejects strict policy lockfiles unless the operator supplies a caller-side `--verification-policy-lockfile-sha256` pin. A matching policy pin is necessary but still not enough: strict policies must also carry `valid_from`, `valid_until`, `verification_time`, and a `packet_selector` whose `packet_id`, `election_id`, and `jurisdiction` match the packet under verification. Mixed-scope packet metadata fails closed.

This remains synthetic verifier hardening only. It does not prove production signer authority, legal delegation, HSM custody, live online revocation, current voter instruction, certification, legal reliance, or live-pilot readiness.
