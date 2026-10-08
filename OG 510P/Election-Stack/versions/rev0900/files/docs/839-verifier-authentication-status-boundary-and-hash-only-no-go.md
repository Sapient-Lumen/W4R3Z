# 839. Verifier authentication-status boundary and hash-only no-go

**Track:** Shared / verifier / release gate  
**Status:** Normative for the default/no-trust-keyset PacketVerificationReport path as of v839; amended by v840 optional trust-keyset lane

## Why this exists

The stdlib observer verifier is useful, but it is easy to overclaim. It recomputes hashes, packet pointers, object names, envelope payload and TBS digests, manifest boundaries, receipt/profile identifiers, and public-output problem codes. It does **not** prove that the packet was signed by an authorized election office, reviewer, build system, witness, or publisher.

That distinction is now machine-readable. Every default `PacketVerificationReport` payload emitted by `tools/observer_verify_packet.py` without a supplied trust keyset carries:

```json
"authentication_status": "HASH_ONLY_NOT_AUTHENTICATED"
```

A report with `status: PASS` and `authentication_status: HASH_ONLY_NOT_AUTHENTICATED` means only: “the checked packet is internally coherent under this verifier profile.” It does not mean signer identity, authority, key custody, threshold approval, revocation status, or legal/publication authorization has been established.

## Required reader rule

For publishable or operator-facing reports, always read `status` and `authentication_status` together.

| `status` | `authentication_status` | Safe interpretation |
|---|---|---|
| `PASS` | `HASH_ONLY_NOT_AUTHENTICATED` | Hash/shape checks passed; signer identity and authority are still unverified. |
| `PASS_WITH_WARNINGS` | `HASH_ONLY_NOT_AUTHENTICATED` | Hash/shape checks produced warnings; signer identity and authority are still unverified. |
| `FAIL` | any value | Do not rely on the packet without remediation and re-verification. |
| `PASS` | `SIGNATURE_VERIFIED` | A bounded signature profile verified envelope bytes against a caller-supplied trust keyset and packet integrity checks also passed. As of v840 this exists only for the narrow Ed25519-JCS-TBS lane in `docs/841-*`; it still does not prove legal authority or live-pilot authorization. |
| any value | `SIGNATURE_FAILED` | Signature authentication was requested or required and failed, or packet integrity/policy failure downgraded authentication. Treat as no-go until remediated and re-run. |
| any value | `SIGNATURE_NOT_CHECKED_BY_PROFILE` | Reserved for non-authenticating profiles that intentionally omit signature checks. |

## Production signature-verifier floor

v840 adds a bounded offline Ed25519 trust-keyset lane, but a production verifier should emit `SIGNATURE_VERIFIED` for real operational reliance only if the profile records, at minimum:

1. the signature format and canonicalization boundary;
2. signer identity and trust-root policy;
3. key validity interval, rotation, and revocation handling;
4. threshold/quorum policy when more than one signer is required;
5. timestamp and clock-source rules;
6. detached-object and manifest coverage rules;
7. negative controls showing wrong key, expired key, revoked key, wrong authority, altered manifest, altered payload, and missing signature all fail closed.

References: NIST key-management guidance (`xref: nist_sp800_57_pt1_r5_pdf`), in-toto/DSSE envelope concepts (`xref: intoto_envelope_v1_md`), SLSA provenance policy-verification cautions (`xref: slsa_provenance_v1_2_html`), and the archive canonicalization/signing boundary in `docs/176-canonicalization-and-signing-rules-for-evidence-envelopes.md`.

## Go/no-go effect

- Synthetic/offline packet-shape rehearsal: **GO** when report status is acceptable and the packet remains clearly labeled synthetic.
- Public claim that an election office, reviewer, witness, or build system authenticated the packet: **NO-GO** under the default hash-only verifier and still **NO-GO** under the v840 fixture lane unless local trust-root governance, role authority, and packet provenance are independently established.
- Live pilot promotion: **NO-GO** until the local pilot intake, custody/provenance, independent-review, redaction/publication, accessibility/language, legal/local-authority, and production signature-verifier gates are all closed.

## Operator wording

Use this sentence in briefings and report cards:

> This verifier report confirms packet integrity checks only; it does not authenticate signer identity or legal/election authority.

Do not shorten it to “verified” without the authentication qualifier.
