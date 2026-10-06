# Sealed secrets + attested unsealing (TPM policy lane)

This is an **optional** lane that turns “store a secret somewhere” into:

- **seal**: bind secret material to a host and (optionally) a measured boot posture
- **unseal**: release secret bytes only when policy conditions are satisfied
- **evidence**: emit receipts so operators can answer *why did this key unlock?* and *when did it stop unlocking?*

The goal is not “TPM everywhere”. The goal is a *clean, reviewable, failure-mode-aware* way to support:

- unattended disk unlock / ZFS dataset key release
- host identity keys that should exist only on known-good boots
- portable home areas that can unlock on a small set of approved devices

Related:
- measured boot + attestation lane: `docs/176-measured-boot-attestation.md`
- PCR separation + phase markers: `docs/245-boot-measurement-phases-and-pcr-separation.md`
- secrets broker + receipts baseline: `docs/223-secrets-and-key-management-as-evidence.md`
- ZFS encryption key-use evidence: `docs/146-zfs-native-encryption-for-generations.md`

## The footgun we must design around: PCR brittleness

If you seal directly to “these PCR values”, you will eventually brick yourself:
- firmware updates
- bootloader updates
- kernel or init changes

A greenfield OS can avoid this by baking in a first-class concept of **seal policy evolution**.

### Policy-authorized PCR policies

TPM2 supports policy composition where a *signing authority* can authorize a changing PCR policy.
The mental model:

- The secret is sealed to **(A) the platform key** and **(B) a policy digest**.
- The policy digest can include:
  - “PCRs must match X”
  - AND “PCR policy must be authorized by signing key K”

This lets DeriveBSD ship a new PCR policy (new expected values) without re-sealing the secret, as long as:
- the policy is signed by the configured authority
- the host’s measurements satisfy the new policy

This is the difference between:
- *fragile sealing* (works until your first boot-chain update)
- *operable sealing* (evolves with signed policy updates)

## DeriveBSD objects (fit into the evidence spine)

We reuse the existing secret lane objects, but specialize some fields for “sealed providers”.

### 1) `secret-policy` (declares sealing intent)
Add provider variants such as:
- `provider: tpm2-sealed`
- `provider: tpm2-sealed+authorized-policy`

Include:
- which PCRs/banks are referenced (by name, not raw values)
- which policy authority key(s) can authorize updates
- whether a user factor is required (PIN/passphrase / FIDO2), if any

### 2) `seal.policy` (derivable policy input)
A content-addressed object that describes:
- PCR selection + bank
- policy structure (PCR-only, PCR+authorize, PCR+phase markers, etc.)
- which signing authority key is used (if applicable)

This is not a secret. It is safe metadata.

### 3) `secret.receipt` (seal/unseal evidence)
Use `spec/secret.receipt.schema.json` with:

- `action: "unseal"`
- `provider: "tpm2"`
- policy digests (`seal.policy` digest; optional authorized policy digest)
- selected PCR set *at time of unseal* (values are metadata; consider redaction policy)
- linkage to:
  - a `boot.attestation` digest (if measured boot lane is enabled)
  - a `change-set` step if unseal was part of activation

### 4) `secret.snapshot` (health = “would unseal succeed?”)
A secret can be “configured” but unhealthy.
Track health states explicitly (e.g., `unseal-failed`) without ever exposing secret bytes.

## Workflows

### Enrollment (seal)
1) Operator chooses the lane:
   - TPM-only (host-bound)
   - TPM + measured boot posture
   - TPM + authorized policy (recommended if sealing to PCRs)
   - TPM + user factor (optional)
2) Derive emits:
   - `seal.policy` (digest)
   - a provider-specific sealed blob (opaque)
   - `secret.receipt` (`action=provision`) referencing the above

### Boot/activation (unseal)
- A small, least-authority component requests unseal from the credential broker.
- On success:
  - secret bytes are delivered only via an approved delivery channel (memfd/ramfs/FD)
  - a `secret.receipt` (`action=unseal`) is emitted
- On failure:
  - a failure receipt is still emitted (reason codes)
  - the system follows a defined fallback ladder (below)

### Boot-chain update without bricking
If the system changes the boot chain (new loader/kernel/init), Derive should treat that as a *policy transition*:

- compute the new acceptable PCR policy
- sign it with the configured policy authority
- ship it as part of the generation’s activation plan
- record the update as evidence (receipt + linkage)

### Fallback ladder (must be explicit)
A sealed-secret lane is only safe if it has predictable recovery:

1. **Primary**: TPM policy unseal
2. **Secondary**: user factor (PIN/passphrase/FIDO2) if configured
3. **Tertiary**: recovery key (printable / escrowed), with mandatory receipts
4. **Breakglass**: `docs/236-breakglass-and-recovery-mode.md` with explicit audit trail

## Integrations that pay off immediately

- **Portable home areas** (`docs/269-…`): allow “unlock home on approved devices” without keeping the home always mounted.
- **State datasets** (`docs/217-…`): schema migration tools can require secrets only when needed and show evidence of use.
- **Incident bundles** (`docs/216-…`): include snapshots/receipts so debugging “why won’t it boot?” is fast.

## Non-goals (v1)

- inventing a new TPM library stack
- requiring measured boot for all devices
- assuming stable PCR values across hardware families

## References (primary)

- tpm2-tools policy primitives (PCR policies, policy authorize):
  - https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policypcr.1/
  - https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_policyauthorize.1/
- systemd-cryptenroll TPM2 enrollment UX (good “operator ergonomics” inspiration):
  - https://www.freedesktop.org/software/systemd/man/systemd-cryptenroll.html

Last updated: 2026-02-25
