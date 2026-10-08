# 862. Verification-policy external-time and publication-receipt firewall

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

rev0850 closes a replay foot-gun in the strict verification-policy lockfile fast path. A strict policy lockfile must not embed `verification_time`; otherwise stale status evidence could keep passing by carrying its own old clock. The verifier now allows `--verification-time` alongside `--verification-policy-lockfile` and uses that caller-supplied time for policy validity and status-freshness checks.

The strongest synthetic path can also require an external publication receipt for the policy lockfile itself:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --verification-policy-lockfile artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0850.json \
  --verification-policy-lockfile-sha256 sha256:0a8bbdc821a59cc206eac605d8b47c284e3f6ed895605e18fb414b0beace6f4e \
  --verification-policy-lockfile-receipt artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0850.publication-receipt.json \
  --verification-policy-lockfile-receipt-sha256 sha256:a732eddacb59e23369134f7cd88c9186afdbedf7d2bbd8c4ab3dc26f87e46ba8 \
  --require-verification-policy-lockfile-receipt \
  --verification-time 2026-06-04T12:45:00Z
```

Fail-closed cases added or preserved in `scripts/check_signature_verifier_ed25519.py`:

```text
strict policy embeds verification_time
strict policy omits caller-supplied verification time
required policy publication receipt is missing
policy publication receipt pin mismatches
policy publication receipt digest mismatches
policy publication receipt independent-channel quorum fails
packet-contained policy lockfile remains rejected
manual trust-chain flags mixed with policy-lockfile mode remain rejected
```

Boundary: this is synthetic verifier hygiene only. It does not establish real election-office signer authority, signer employment, legal delegation, procurement approval, HSM custody, production key ceremony quality, independent publication governance, live online revocation freshness, current voter instruction, certification, legal reliance, or live-pilot readiness.


rev0850 also requires strict policy selector consistency to be exact across observed packet/election/jurisdiction scope values; see `docs/861-verification-policy-exact-scope-selector-and-ambiguous-metadata-firewall.md`.
