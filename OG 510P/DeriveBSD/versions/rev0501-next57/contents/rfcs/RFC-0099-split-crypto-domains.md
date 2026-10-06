# RFC-0099: Split crypto domains (keys out of risky compartments)

Status: **draft**

## Problem

If private keys exist in networked or build compartments, compromise leads to catastrophic signing or decryption.
DeriveBSD’s hostile-builder posture needs a concrete, enforceable mechanism for key use.

## Proposal

Introduce a standard “crypto-domain” service (service-jail or microVM) that:
- holds key material
- exposes narrowly scoped operations (sign, decrypt, tls auth)
- is invoked via policy-governed RPC (qrexec-style policy)

Callers never receive raw private key bytes.

## Evidence

Every granted operation emits `crypto.op.receipt.json` bound to:
- request digest
- key id
- result digest
- policy decision digest

## Rollout

- v0: service-jail implementation
- v1+: microVM implementation

## References

- Qubes split GPG: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html

See: `docs/164-split-crypto-domains.md`, `docs/151-factotum-style-credential-broker.md`.
