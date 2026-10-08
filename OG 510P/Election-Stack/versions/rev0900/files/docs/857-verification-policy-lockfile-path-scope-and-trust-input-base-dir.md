# 857. Verification-policy lockfile path scope and trust-input base directory

**Track:** Shared / verifier boundary  
**Revision:** v848

## Why this exists

rev0847 made the strongest synthetic verifier path easier to run by moving a long list of trust-chain flags into a byte-pinned verification-policy lockfile. That was useful, but it introduced a new operator-error surface: a lockfile that can point at arbitrary filesystem routes can become a local substitution gadget.

rev0848 adds a path-scope firewall for strict policy lockfiles. A strict policy must declare `trust_input_base_dir`, and each trust input path must be a child path under that packet-external base directory before the verifier will apply the downstream trust-keyset, receipt, governance, status, and signer-authorization gates.

## Strongest synthetic command

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --verification-policy-lockfile artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0848.json \
  --verification-policy-lockfile-sha256 sha256:431ded784beca5ab4c034314335c95978712d1785565e000994452e66c3b559a
```

Successful public reports expose the bounded path result:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "verification_policy_lockfile_status": "matched",
  "verification_policy_lockfile_path_policy_status": "bounded",
  "verification_policy_lockfile_trust_input_base_dir": "../trust_keysets",
  "verification_policy_lockfile_input_paths_bounded_count": 7
}
```

## Fail-closed path cases

The verifier now rejects strict policy lockfiles that use:

- URL-style trust input paths;
- absolute local paths;
- Windows drive or UNC-style routes;
- shell-home routes;
- NUL-containing path strings;
- parent-segment trust input paths under the declared base;
- missing `trust_input_base_dir`;
- packet-contained policy lockfiles; or
- policy lockfiles mixed with manual trust-chain flags.

The public problem code for this new route is:

```text
signature_verification_policy_lockfile_path_scope_violation
```

## What changed in the fixture

The rev0848 policy uses this shape:

```json
{
  "trust_input_base_dir": "../trust_keysets",
  "trust_inputs": {
    "trust_keyset": {
      "path": "trust-keyset-ed25519-threshold2-demo.json",
      "sha256": "sha256:bff832d10da7444ec05d7e429a47c62c4ac9a65cd7ec2ac675f50a67a1422810",
      "required": true
    }
  }
}
```

Trust-input paths are no longer broad policy-relative paths like `../trust_keysets/...`; they are child names under the declared base.

## Boundary

This is still a synthetic local verification boundary. It reduces local substitution and copy/paste risk for the example trust chain, but it does not prove real election-office authority, signer employment, legal delegation, HSM custody, production key ceremony, live online revocation freshness, current voter instruction, certification, live-pilot readiness, or legal reliance.

See also `schemas/VerificationPolicyLockfile.json`, `schemas/PacketVerificationReport.json`, `artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0848.json`, `artifacts/reports/verification-policy-path-scope-audit-rev0848.md`, and `scripts/check_signature_verifier_ed25519.py`.
