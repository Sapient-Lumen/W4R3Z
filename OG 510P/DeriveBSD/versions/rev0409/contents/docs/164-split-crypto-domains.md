# Split crypto domains (Qubes “split GPG” lesson): keep keys out of risky compartments

DeriveBSD already treats **builders as hostile** and prefers **credential brokering** (operations, not raw keys).
This document adds a concrete, proven pattern from Qubes OS: **split GPG** — delegate cryptographic operations to a more-trusted, network-isolated domain.

In DeriveBSD terms: *anything that can touch the network should not hold long-lived private keys*.

## Pattern

- A dedicated **crypto-domain** holds private keys (or unlock material) and exposes narrow operations:
  - `Sign(digest, key_id)`
  - `Decrypt(blob_ref, key_id)` (if policy permits)
  - `TLSClientAuth(handshake_ref, identity_id)`
- Callers (fetch-domain, publish-domain, devshells) never receive raw private key bytes.
- Requests cross compartments via a policy-governed RPC boundary (see `docs/135-qrexec-style-rpc-policy.md`).

This is the same shape as Qubes split-GPG: a less-trusted domain (mail client, build worker) delegates signing/decryption to a more-trusted, isolated domain.

## Why it’s worth baking in

This is “low-hanging Qubes-ness”:
- it sharply reduces key theft risk from compromises in networked compartments
- it is compatible with microVM-first designs
- it makes “no secrets in builders” enforceable in a way humans can understand

## DeriveBSD mapping

### Where it runs

- v0: crypto-domain as a **service-jail** (fast, simple)
- v1+: crypto-domain as a **microVM** (preferred)

Transport:
- `vsock` for microVM mode
- Unix domain socket for service-jail mode

### Policy surface

- Requests are authorized by derived policy (capability routing manifests).
- Policy binds:
  - which caller compartments may invoke which operation
  - which keys are usable
  - rate limits / budgets
  - whether the operation requires a human presence check (optional)

### Evidence

Every granted operation emits a small, canonical record:
- `crypto.op.receipt.json`
  - request digest (binds to caller Plan or Artifact)
  - operation type
  - key_id
  - result digest
  - policy decision digest
  - timestamp (trustworthy-time optional)

This receipt becomes an input to:
- provenance attestations
- promotion rules (publish only if signatures were produced by approved crypto-domain)

## Non-goals

- Building an interactive GPG UX in v0.
- Supporting arbitrary agent forwarding patterns; we want one auditable, policy-governed mechanism.

## References

- Qubes OS “Split GPG”: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html
- Qubes OS “Split GPG-2” (updated variant): https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg-2.html

See also: `docs/151-factotum-style-credential-broker.md`.

Last updated: 2026-02-23
