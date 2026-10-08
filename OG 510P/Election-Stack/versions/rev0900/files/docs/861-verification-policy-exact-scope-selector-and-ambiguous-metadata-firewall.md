# 861. Verification-policy exact-scope selector and ambiguous metadata firewall

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

rev0850 tightens the strict verification-policy lockfile selector. A strict policy is no longer satisfied merely because the expected `packet_id`, `election_id`, or `jurisdiction` appears somewhere in packet metadata. The observed packet scope must be exact and unambiguous:

```text
observed packet_ids == {expected packet_id}
observed election_ids == {expected election_id}
observed jurisdictions == {expected jurisdiction}
```

This closes a replay/substitution foot-gun: a packet could contain the expected scope in one place and a conflicting election or jurisdiction in another place. That should fail closed, not be treated as a match.

Current strict policy fixture:

```text
artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0850.json
sha256:0a8bbdc821a59cc206eac605d8b47c284e3f6ed895605e18fb414b0beace6f4e
```

The public packet-verification report now exposes:

```text
verification_policy_lockfile_packet_selector_actual_packet_ids
verification_policy_lockfile_packet_selector_scope_consistency_status
verification_policy_lockfile_external_verification_time
verification_policy_lockfile_temporal_context_status
verification_policy_lockfile_embedded_verification_time_present
```

rev0850 also requires caller-supplied temporal context for strict policy validation; the policy fixture must not embed `verification_time`.

Boundary: this is synthetic verifier scope hygiene only. It does not prove real election-office signer authority, signer employment, legal delegation, procurement authorization, HSM custody, production key ceremony quality, independent publication governance, live online revocation freshness, current voter instruction, certification, legal reliance, or live-pilot readiness.
