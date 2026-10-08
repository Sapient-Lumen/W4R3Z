# 848 — Trust-key governance bundle and stale/substitution firewall

**Track:** Shared / Verifier / Trust-root governance  
**Status:** v844 synthetic verifier hardening  
**Scope:** `tools/observer_verify_packet.py`, `scripts/check_signature_verifier_ed25519.py`, `schemas/TrustKeyGovernanceBundle.json`, `artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0844.json`

## Why this exists

v843 made the authenticated verifier lane materially safer by requiring an external trust keyset, optional keyset digest pin, distinct-key-material quorum, and an external publication receipt. That still left one risky operator mistake: a verifier run could treat a copied, stale, or locally substituted governance story as persuasive even when the keyset bytes and receipt were correct.

v844 adds an optional external **trust-governance bundle** lane. It is still synthetic, but now executable: the verifier can require a separate JSON governance bundle whose bytes are pinned, whose keyset digest matches the supplied trust keyset, whose publication-receipt digest matches the verified receipt, whose key ceremony has a witness quorum, and whose key lifecycle events cover active keys plus at least one rotation or revocation event.

This follows the safer design instinct behind mature trust-root systems: trust roots should be governed out of band, thresholded where appropriate, and rotated/revoked through auditable metadata rather than inherited from the artifact being checked. Use `xref:tuf_spec_latest_html` and `source:nist_sp800_57_pt1_r5_pdf` as background references; this archive does **not** implement TUF or production key-management governance.

## New verifier surface

Positive synthetic command shape:

```bash
python3 tools/observer_verify_packet.py \
  artifacts/examples/evidence_packet_ed25519_threshold2_minimal \
  --json --public \
  --trust-keyset artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.json \
  --trust-keyset-sha256 sha256:bff832d10da7444ec05d7e429a47c62c4ac9a65cd7ec2ac675f50a67a1422810 \
  --trust-keyset-receipt artifacts/examples/trust_keysets/trust-keyset-ed25519-threshold2-demo.publication-receipt.json \
  --require-trust-keyset-receipt \
  --trust-governance-bundle artifacts/examples/trust_keysets/trust-key-governance-bundle-ed25519-threshold2-rev0844.json \
  --trust-governance-bundle-sha256 sha256:2e7746236b7ca776a944d4bf8dc5c027f94576b34a4409e60343d3a6430b1fc5 \
  --require-trust-governance-bundle
```

The bounded positive report can now expose:

```json
{
  "authentication_status": "SIGNATURE_VERIFIED",
  "signature_threshold": 2,
  "signature_verification": {
    "trust_keyset_receipt_status": "matched",
    "trust_governance_bundle_status": "matched",
    "trust_governance_bundle_pin_status": "matched",
    "trust_governance_witness_count": 3,
    "trust_governance_rotation_or_revocation_event_count": 1
  }
}
```

## Fail-closed rules added in v844

`SIGNATURE_VERIFIED` is unavailable when any required governance-bundle condition fails:

- governance bundle is required but not supplied;
- governance bundle path is inside the packet being authenticated;
- governance-bundle sha256 pin is malformed or mismatched;
- bundle `trust_keyset_sha256` does not match the supplied keyset bytes;
- bundle `publication_receipt_sha256` does not match the verified external receipt bytes;
- bundle is marked superseded, expired, revoked, or otherwise stale;
- witness quorum is not met;
- active keys lack matching activation/public-key-digest events;
- a rotation or revocation event is required but absent.

The regression gate is `scripts/check_signature_verifier_ed25519.py`.

## What this still does not prove

This lane does **not** prove real election-office signer authority, signer employment, legal delegation, hardware custody, HSM use, ceremony-room controls, identity proofing, independent publication governance, online revocation freshness, jurisdiction-appropriate threshold policy, live-pilot authorization, certification, current voter instruction, or legal reliance.

It only proves that the verifier can fail closed over a synthetic external governance object instead of accepting stale or packet-supplied trust stories.

## Maintainer rule

Do not add another trust-root prose page unless it adds an executable negative control or schema field used by the verifier. The next production-facing gap is not more explanation; it is an independent channel from which the governance-bundle digest can be obtained and compared without copying it from the same local folder.
