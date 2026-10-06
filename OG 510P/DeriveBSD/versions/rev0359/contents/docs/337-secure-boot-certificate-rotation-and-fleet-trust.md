# Secure Boot certificate rotation (2011→2023) and fleet trust posture

Secure Boot is not “set it once and forget it”.
Key material expires, revocation lists evolve, and ecosystems rotate signing CAs.
If DeriveBSD treats UEFI trust roots as “firmware magic”, real fleets will accumulate drift and eventually hit a wall.

This note captures a concrete forcing function:

- Microsoft says the older Secure Boot certificates issued in 2011 begin expiring in **June 2026** and directs OEMs/admins to update devices in advance. https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-secure-boot
- Microsoft now also exposes fleet readiness/reporting for this through the Secure Boot status report in Windows Autopatch, reinforcing that certificate state is an operational readiness question rather than a niche firmware detail. https://learn.microsoft.com/en-us/windows/deployment/windows-autopatch/monitor/secure-boot-status-report

For Linux, an additional near-term pain point exists:

- shim has historically been signed by a Microsoft 2011 key that expires **September 11, 2025**, affecting bootability of some installation media unless updated shims are used. (Operational summary and discussion) https://lwn.net/Articles/1029767/

---

## What this means for DeriveBSD

### 1) UEFI trust roots must be represented as *evidence*

DeriveBSD already models “platform drift” lanes:

- firmware inventory receipts (`fw.inventory.receipt`) can summarize Secure Boot state via digests
- UEFI variable mutation is a planned operation (`uefi.var.set.plan` → `uefi.var.set.receipt`)

To survive certificate rotations, fleets must be able to answer:

- what Secure Boot keysets are enrolled (digest-first)
- which revocation lists/dbx are present (digest-first)
- whether key refresh steps have been applied

Day‑0 requirement:

- include Secure Boot summary digests in `fw.inventory.receipt` when policy enables it
- ensure `uefi.var.set.receipt` can prove changes without leaking raw blobs by default

See: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`

### 2) Key rotation is a *planned rollout*, not a hand-edit

UEFI DB/KEK/PK updates are the same class of risk as:

- upgrading BIOS
- changing the boot manager
- rotating OS signing keys

DeriveBSD should treat key refresh as a normal fleet change:

- represent it as a derived operation (UEFI var plan)
- gate it behind approvals/quorum by default
- stage it through cohorts and health gates (like other high-risk changes)

### 3) Firmware updates are inseparable from trust-root refresh

Many machines require firmware updates (or vendor tooling) to properly accept newer key material or updated db/dbx policies.
That means:

- firmware update plans (`fw.update.plan`) and UEFI var plans (`uefi.var.set.plan`) often ship together
- evidence must correlate them (plan digests + receipts + boot events)

See:

- `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`
- `docs/244-bootchain-revocation-and-allowlists.md`

---

## Recommended DeriveBSD “key rotation playbook” shape

This is not a full specification; it’s a *design pressure* checklist.

1) **Detect** (inventory)
   - emit `fw.inventory.receipt` with Secure Boot digests (policy-enabled)
   - flag “expiring CA present” vs “refreshed CA present” in a policy report (derived)

2) **Plan**
   - generate `uefi.var.set.plan` to enroll new trust anchors and/or update db/dbx
   - optionally pair with `fw.update.plan` if firmware must change

3) **Approve**
   - require digest-bound approvals/quorum for DB/KEK/PK and dbx

4) **Stage + apply**
   - apply plans under maintenance lease
   - log typed events (journal) and emit receipts

5) **Verify**
   - post-boot confirmation via inventory receipt + (optional) measured boot/eventlog replay

6) **Roll out**
   - cohort-based rollout with holdbacks
   - explicit “breakglass” posture if a key refresh creates boot failures

---

## Why this belongs in the ground floor

Secure Boot failures tend to show up as:

- “this install media won’t boot on some hardware”
- “this older box can’t accept updated signing material”
- “firmware/dbx updates happened outside our change model”

If DeriveBSD bakes in:

- digest-first Secure Boot posture capture
- planned, receipted UEFI variable mutation
- firmware updates as planned, staged operations

…then certificate rotations become boring fleet hygiene instead of existential incidents.

Last updated: 2026-03-21r351
