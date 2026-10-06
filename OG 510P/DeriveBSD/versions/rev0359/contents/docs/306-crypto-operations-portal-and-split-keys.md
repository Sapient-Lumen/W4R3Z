# Crypto operations portal + split keys (make private keys non-exportable by default)

Most "secrets" discussions focus on **passwords/tokens**, but the highest-value secrets are often **private keys**:
- signing keys (package/release, SSH, code-signing)
- decryption keys (age/GPG/S/MIME)
- node identity keys (mTLS, WireGuard, attestation identities)

If private keys are placed in files (even root-owned), the system tends to drift toward:
- ad-hoc key copies across hosts
- accidental exfiltration via backups/support bundles
- compromised app → compromised key (because key bytes are nearby)

A greenfield OS can do better by making **crypto operations** a first-class *portalized authority*:
- apps request *operations* (sign/decrypt/derive), not key bytes
- a broker enforces policy + user presence and emits receipts
- keys live in compartments/hardware whose job is to refuse export

## Prior art worth stealing

### Qubes “split GPG” + qrexec policy
Qubes popularized the idea that a less-trusted VM can delegate crypto operations to a more-trusted, network-isolated VM.
This is effectively a **"smart card as a VM"** pattern: the caller never sees key bytes; it just gets signatures/decrypt outputs.

- Split GPG concept: https://doc.qubes-os.org/en/latest/user/security-in-qubes/split-gpg.html
- qrexec framework (cross-domain RPC): https://doc.qubes-os.org/en/latest/developer/services/qrexec.html
- RPC policies (who may call what): https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html

### Platform keystores (non-exportable keys + usage restrictions)
Modern consumer OSes treat key use as a guarded operation:
- Apple Secure Enclave-backed keys: https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave
- Apple Platform Security (Keychain protection notes): https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
- Android hardware-backed keystore (KeyMint/Keymaster): https://source.android.com/docs/security/features/keystore

The lesson is not "copy their UI"; it's:
- **key usage constraints** (algorithm/mode/purpose)
- optional **user presence / auth gates** for key use
- a **stable API** that prevents apps from inventing bespoke key handling

## DeriveBSD model: `crypto.portal` (operations, not bytes)

Product-shape defaults for A–D now live in `docs/462-private-key-and-crypto-op-posture-by-profile.md`.

Treat crypto the way DeriveBSD treats network, file access, and export:

- A dedicated broker/service: `system.crypto` (or `system.crypto.portal`).
- Callers receive **handles** (leases) to request operations.
- Key material is stored in one of:
  - a **KeyVM** (microVM) with no network and tight storage policy
  - a TPM/HSM adapter lane (when present)
  - an external KMS adapter (org infra)

### Key policy as a first-class object (`crypto.key.policy`)
A key is defined by a signed **crypto key policy** object that declares:
- stable `key_id`
- purpose + allowed operations (sign/decrypt/derive)
- allowed algorithms/modes
- subject selectors (units/users) allowed to request operations
- whether **user presence** or **quorum approvals** are required
- export posture (default: **non-exportable**)
- audit posture (emit receipts, retention class)
- backend binding (KeyVM/TPM/PKCS#11/external KMS adapter)

Schema:
- `spec/crypto.key.policy.schema.json`

This composes with:
- `docs/223-secrets-and-key-management-as-evidence.md` (brokers + leases)
- `docs/272-sealed-secrets-attested-unsealing.md` (TPM policy lane)
- `docs/288-multiparty-approvals-and-separation-of-duties.md` (two-person signing)

### Requests + receipts
Add two evidence objects:

- `crypto.op.request` — an operation request (what, under what lease/policy).
- `crypto.op.receipt` — a signed record of the operation (inputs/outputs by digest, policy/grant correlation).

Key principle: receipts should be **high signal** but not privacy-toxic:
- record *digests* of payloads, not plaintext
- record caller identity + key id + purpose
- optionally record destination (e.g. "ssh" vs "release") as a structured tag

Schemas:
- `spec/crypto.op.request.schema.json`
- `spec/crypto.op.receipt.schema.json`

### UX: crypto operations should look like other portals
- requests can trigger `consent.request` flows (secure attention, multi-approver)
- approvals are time-bounded and captured as receipts
- default posture: **no background signing** without an explicit lease

## Implementation sketch (FreeBSD-first)

### 1) Day-0 adapter: KeyVM + RPC
- run `system.crypto` inside a dedicated microVM
- callers use a small, typed RPC protocol over an existing restricted channel (virtio socket / qrexec-like)
- policy enforcement happens at the broker boundary

### 2) Optional backend: PKCS#11 / TPM / external KMS
The broker abstracts backends:
- PKCS#11 tokens (HSM/smartcard)
- TPM-resident keys
- cloud KMS (when allowed)

The key is that **the OS policy model stays the same**:
- callers request operations
- receipts are uniform

## Wiring

- Component descriptors (`derive.unit`) should be able to declare crypto intent:
  - which key ids it may request ops for
  - whether user presence is expected
  - budget limits (ops/minute, receipts retention)

- Authority budgets should cover crypto ops explicitly:
  - rate limits
  - export posture (where may signatures/decrypt outputs go?)
  - receipt retention + redaction class

See: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`, `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/252-lease-envelope-and-cross-lane-joins.md`.

## Open questions

- What is the minimal per-op receipt that stays useful without turning into a surveillance log?
- How do we prevent "sign anything" footguns (operation-specific allowlists, structured destinations, human-readable prompts)?
- For release signing: do we require multiparty approval by default, or is that a policy profile?

Last updated: 2026-03-06r191
