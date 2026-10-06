# Boot-chain revocation and component allowlists (SBAT-shaped)

Secure Boot answers one question: **did we boot something signed by a key we trust?**

Operations needs a second question: **is the signed component still allowed today?**

Modern ecosystems learned this the hard way (key compromise, bypass classes, "can't revoke without revoking everything").

DeriveBSD should treat **boot-chain revocation** as a first-class *policy surface* whose decisions are expressed as receipts.

## Goals

- Allow **targeted revocation** of specific boot components (or component generations) without burning the whole key hierarchy.
- Make "what is allowed" a **diffable artifact** (like everything else) with a clear rollout path.
- Ensure every boot/attestation decision can answer: *which allowlist and which revocations were in force?*

## Core idea: SBAT-shaped component identity

Borrow the SBAT lesson: components should carry a stable identity tuple and a **generation** counter.

DeriveBSD boot-chain components (examples):
- boot manager (e.g. `deriveboot`)
- loader (UEFI app / ZFS loader)
- kernel+initrd container format (if used)
- platform shims (if applicable)

Each component emits:
- `component_id` (stable string)
- `vendor_id` (stable string)
- `generation` (monotonic integer)
- `build_digest` (content digest)

Policy can then express:
- allow `component_id` at generation **>= N**
- revoke any generation **< N**
- revoke a specific build digest

This gives us targeted revocation without making key rotation the only hammer.

## Where this plugs into DeriveBSD

### 1) Policy artifact: `bootchain.policy`

Introduce a dedicated policy object:
- `spec/bootchain.policy.schema.json`
- `spec/examples/bootchain.policy.json`

This object is *fleet policy*, not per-host evidence.

### 2) Attestation references carry the bootchain policy digest

Extend `attestation.reference` so verifiers can prove which bootchain policy they used.

### 3) Receipts mention the policy digest

- `attestation-receipt` already supports `reference_digest` and `policy_digest`.
- add `bootchain_policy_digest` inside `attestation.reference` (and optionally surface it in receipt reasons when violated).

### 4) Incident bundles include relevant bootchain policies

If a boot fails or is quarantined due to revocation, the support bundle must include the exact bootchain policies in force.

## Non-goals

- Replacing UEFI db/dbx or pretending revocation is portable across firmware.
- Mandating shim/GRUB/systemd-boot; DeriveBSD may ship its own boot manager.

## Certificate rotation is not optional

Real ecosystems rotate Secure Boot signing CAs and update enrolled trust anchors (db/KEK/PK).
Revocation policy (SBAT-shaped) helps avoid ‘rotate everything or nothing’, but it does not remove the need to plan for key refresh.
DeriveBSD should treat trust-anchor updates as derived, receipted operations (UEFI variable set plans + receipts).

See: `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`.


## Notes

- Bootchain revocation works best when paired with **boot assessment** (`docs/241-boot-try-counters-and-boot-assessment.md`) so failures fall back deterministically.
- Treat "revocation rollout" like any risky change: support **confirmable change-sets** (`docs/242-confirmable-change-sets-and-auto-revert.md`).

## References

- SBAT (generation-based revocation) in shim: https://github.com/rhboot/shim/blob/main/SBAT.md
- GRUB manual on SBAT: https://www.gnu.org/software/grub/manual/grub/html_node/Secure-Boot-Advanced-Targeting.html
- Microsoft Secure Boot certificate expiration + CA updates (2011→2023): https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e
- LWN: Linux and Secure Boot certificate expiration (shim key expiry context): https://lwn.net/Articles/1029767/
