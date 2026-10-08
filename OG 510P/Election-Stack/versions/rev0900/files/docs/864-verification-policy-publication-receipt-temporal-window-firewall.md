# 864 — Verification-policy publication-receipt temporal window firewall

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

**Release:** `v851`  
**Boundary:** synthetic verifier fixture only; not production signer authority, legal delegation, current voter instruction, certification, or live-pilot authorization.

## What changed

Strict verification-policy lockfiles now fail closed unless the policy-publication receipt is external, byte-pinned, and temporally coherent. The verifier now treats strict policy mode as receipt-required even when an operator forgets the explicit receipt-required flag, and it also fails closed when a receipt is supplied without a caller-side SHA-256 pin.

The receipt checks are intentionally operational rather than doctrinal:

- policy bytes must match the receipt’s policy digest
- the receipt must be outside the packet under verification
- the receipt must satisfy independent publication-channel quorum
- channel observation times, receipt issuance, validity windows, and caller-supplied `--verification-time` must be coherent
- unknown `trust_inputs` keys in the policy fail closed instead of being ignored

## Current synthetic fixture

```text
policy_lockfile: artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0851.json
policy_lockfile_sha256: sha256:16331c372ab6b2d1dcb83b65de11bbb0aaf443080f971847fba83b417c2503b1
policy_receipt: artifacts/examples/trust_policies/verification-policy-lockfile-ed25519-authorized-threshold2-rev0851.publication-receipt.json
policy_receipt_sha256: sha256:bde6b21ce5ce3cf137425207da7a99f9c1500abeca84ae294f799a4e97b61c76
```

## Executable coverage

`scripts/check_signature_verifier_ed25519.py` covers the positive strict policy path and negative controls for missing policy receipt, missing receipt pin, receipt pin mismatch, receipt digest mismatch, weak publication-channel quorum, impossible receipt temporal order, unknown policy `trust_inputs`, unsafe policy paths, wrong packet selectors, and stale policy validity windows.

A passing synthetic path authenticates bytes against local public fixtures and bounded synthetic policy. It does not prove signer employment, legal delegation, HSM custody, production key ceremony, real independent publication governance, live online revocation, jurisdiction-appropriate threshold policy, current voter instruction, certification, or live-pilot readiness.
