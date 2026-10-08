# External attestation verifier refactor — rev0338

Active revision: rev0338. Codename: `external-attestation-verifier-streaming-audit-refactor`. Generated: 2026-06-18T20:13:00Z.

## Why this was the riskiest unfinished edge

Rev0337 correctly stopped archive-generated fixtures from becoming final determinations, but the promotion gate still had a hard-coded verifier absence. That was honest, but not enough forward motion: the system could say “no verifier configured,” yet it did not contain the verifier interface that would stop a future producer from simply writing `verified_external_attestation` into an evidence record.

Rev0338 turns that warning into executable boundary code. Implementation-grade evidence now needs a cryptographic proof over the exact evidence payload consumed by the adapter. The archive still ships no trusted production keys and still finalizes zero cases, but it now has a concrete ingress skeleton for externally supplied current-law, jurisdiction, model-input, floor-delivery, and no-go evidence.

## Runtime change

Added `tools/verify_external_attestation.py`:

- offline Ed25519 verification over canonical JSON;
- evidence-payload hash binding that excludes only the proof envelope itself;
- bundle-supplied trust store with key id, public key, issuer, producer allowlist, evidence-kind allowlist, and validity window;
- deterministic verifier statuses rather than exceptions;
- helper to build the exact signed payload producers must sign;
- fail-closed behavior when no trust store is configured.

The current profile is `ed25519_canonical_json_v1`. It is intentionally smaller than a Sigstore or W3C Verifiable Credential implementation. Sigstore bundles collect verification material such as signatures, transparency-log entries, and timestamps; Rekor supplies verifiable append-only log behavior; W3C Data Integrity defines cryptographic proof mechanisms for constrained digital documents.[S682][S683][S684] Those are the right future directions. Rev0338 implements the minimal local gate needed to prevent self-certifying evidence claims now.

## Adapter-execution change

`tools/execute_decision_adapters.py` now treats the following markers as implementation-grade claims that require verifier clearance:

- `evidence_origin == external_observed`;
- `external_source_attestation_status == verified_external_attestation`;
- `promotion_eligible == true`;
- implementation-grade model-input or authority flags.

If any such marker appears without a valid external attestation, the adapter execution returns:

`blocked_external_attestation_not_verified`

This means a producer-authored `verified_external_attestation` string is no longer even enough to satisfy adapter execution. It must be accompanied by a trusted signature over the same evidence payload.

## Replay and promotion change

The replay ledger now binds:

- `external_attestation_verifier_status`;
- `trusted_external_attestation`;
- external-attestation hash;
- external-attestation-verification hash;
- the expanded truth-boundary hash.

Promotion now checks the ledger’s verifier configuration status instead of relying on a hard-coded global no. Under the built-in archive-generated strict-schema evidence bundle the result is still fail-closed:

- trusted verifier status: `not_configured_fail_closed`;
- cryptographically verified external attestations: `0/1724`;
- promoted cases: `0/122`;
- held cases: `122/122`.

But a future externally supplied bundle can now move through the code path if and only if every record is replay-clean, externally observed, independently attested, promotion-eligible, nonblocking, and verified against a configured trust store.

## Audit added

Added `tools/audit_external_attestation_verifier.py`.

It generates an in-memory Ed25519 keypair, signs a current-law evidence payload, and verifies these cases:

- valid signed evidence is accepted as `verified_external_attestation`;
- missing trust store returns `not_configured_fail_closed`;
- tampered evidence returns `attestation_payload_mismatch`;
- producer-declared verified status without proof returns `missing_external_attestation`;
- expired trust or proof windows return `attestation_or_trust_entry_expired`;
- the adapter execution helper rejects forged verified status.

## What this still does not do

This is not a production public-key infrastructure. It does not yet validate Sigstore bundles, Rekor inclusion proofs, RFC3161 timestamps, certificate identity constraints, DID documents, revocation lists, or selective-disclosure credentials. It also does not fetch or preserve raw authority text.

That is deliberate. The archive should not pretend to be a trust root. Rev0338’s purpose is narrower and more important: establish the promotion seam where a real trust root can later be plugged in without changing the moral decision logic.

## Next work

The next substantive pass should implement a signed external evidence sample that can promote one deliberately tiny nonblocking adapter case in a quarantined fixture namespace, while proving that no archive-generated fixture can reuse that path. After that, the high-value work is streaming ledger construction one case at a time to cut peak memory.

[S682]: <https://docs.sigstore.dev/about/bundle/> "Sigstore — Bundle Format"
[S683]: <https://docs.sigstore.dev/logging/overview/> "Sigstore — Rekor transparency log overview"
[S684]: <https://www.w3.org/TR/vc-data-integrity/> "W3C — Verifiable Credential Data Integrity 1.0"
