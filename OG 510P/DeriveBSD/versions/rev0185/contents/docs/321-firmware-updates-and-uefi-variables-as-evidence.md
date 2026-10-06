# Firmware updates + UEFI variables as evidence (no "BIOS update folklore")

Platform firmware updates are security-critical, failure-prone, and often performed outside the OS' auditable change model.
If DeriveBSD treats firmware as “someone else’s problem”, fleets regress to:

- ad-hoc vendor utilities and one-off runbooks
- "it updated on reboot" uncertainty
- invisible Secure Boot database edits (`db/dbx`) and boot-option drift
- remote bricks (NIC/storage firmware regressions) with no preflight gate

DeriveBSD’s posture: **firmware is part of the platform contract**, so *firmware updates and UEFI variable mutation are derived operations with typed plans + receipts*.

This doc defines the minimum day‑0 lane:

- emit a privacy-safe firmware inventory receipt (`fw.inventory.receipt`)
- stage/apply firmware updates via a planned operation (`fw.update.plan` → `fw.update.receipt`)
- treat UEFI variable writes as a planned operation (`uefi.var.set.plan` → `uefi.var.set.receipt`)

---

## Design goals

1. **Make firmware changes reviewable**
   - the payload digest, targets, and expected post-state are explicit
   - high-risk changes require explicit approvals and (optionally) quorum

2. **Make firmware changes explainable**
   - after reboot, operators can answer: *what was attempted, what applied, what changed?*
   - failures are typed (`reboot-required`, `blocked-by-policy`, `apply-failed`, `postcheck-failed`)

3. **Avoid ambient firmware authority**
   - firmware mutation is mediated (maintenance lease + policy)
   - no long-running “always privileged updater daemon” by default

4. **Preserve privacy**
   - receipts are digest-first
   - raw serials and raw Secure Boot blobs are not default outputs

---

## Firmware inventory (fw.inventory.receipt)

DeriveBSD should be able to answer **what firmware is on this machine** without SSH.

`fw.inventory.receipt` is a periodic / on-demand inventory of firmware facts:

- system firmware: BIOS/UEFI vendor + version
- BMC / management controller firmware (when applicable)
- CPU microcode version (coarse)
- device firmware versions for critical attach points (NIC, storage controller, boot disk)
- optional Secure Boot *state summary* (enabled/disabled, keyset digests)

The receipt is **privacy-safe** by default:

- include stable device-class identifiers and version strings
- exclude raw serials / asset tags unless policy explicitly allows
- prefer hashed / HMAC-scoped correlation identifiers when needed

Inventory receipts feed:

- `hw.compat.report` preflight gates (avoid remote bricks)
- attestation/verifier policy (firmware posture constraints)
- support bundles ("this box runs firmware X")

To make posture *reviewable* across generations, optionally produce a typed diff surface:

- `fw.inventory.diff` (schema: `spec/fw.inventory.diff.schema.json`; see: `docs/428-fw-inventory-diff-as-drift-surface.md`)

---

## Firmware updates as derived operations

### Objects

- `fw.update.plan`: what we intend to apply (payload digests, targets, constraints)
- `fw.update.receipt`: what actually happened (pre/post inventory digests, per-target results)

### Multi-stage reality (capsules, reboot stages)

Many platforms use **UEFI capsule updates**: the OS stages a capsule, sets a boot indication, and firmware applies the update at early boot.
DeriveBSD models this explicitly:

1) **Stage** payload (CAS object → staging path / ESP `EFI/UpdateCapsule` or vendor-defined mechanism)
2) **Arm** firmware update intent (UEFI variables like `OsIndications`, sometimes `BootNext`)
3) **Reboot** into the update path
4) **Confirm** outcome on the next boot:
   - read update status
   - re-emit `fw.inventory.receipt`
   - emit `fw.update.receipt`

The applier must never claim “success” on stage alone.

### Policy & approvals

Firmware update plans are high-risk. Day‑0 defaults:

- require a **maintenance lease** (time-bounded authority)
- require explicit approvals for:
  - system firmware updates
  - Secure Boot db/dbx changes
  - downgrades
  - BMC updates

Approvals must be digest-bound to the plan.

### Postconditions

`fw.update.plan` can declare:

- expected firmware versions (or version ranges)
- whether a reboot is required
- optional coupling to attestation (`attestation.reference`) for high-assurance channels

If postconditions fail, the receipt must report `postcheck-failed` even if staging succeeded.

---

## UEFI variable writes as derived operations

UEFI variables are a long-term drift source:

- `BootOrder`/`Boot####` silently changes boot behavior
- Secure Boot keys (`PK/KEK/db/dbx`) change trust roots
- OS indication variables steer capsule updates

DeriveBSD treats **UEFI variable mutation as a planned operation**:

- `uefi.var.set.plan`: list of variable operations (set/delete/append), with payload digests
- `uefi.var.set.receipt`: what was changed, with old/new digests (not raw bytes by default)

Special handling for Secure Boot databases:

- record **digests** of the variable payloads
- optionally record parsed summaries (certificate fingerprints, count) under explicit policy
- require approvals/quorum by default

This makes “why did Secure Boot start rejecting X?” answerable.

### Forcing function: certificate rotation (2011→2023)

Secure Boot key material expires and ecosystems rotate signing CAs.
Microsoft has published guidance for Secure Boot certificate expiration beginning in **June 2026** and the rollout of newer **2023** certificates.
This is a practical reminder that UEFI trust roots need to be **inventoryable** and **mutable only via planned, receipted operations**.

DeriveBSD design implications:

- `fw.inventory.receipt` should (policy-gated) summarize Secure Boot posture (enabled + keyset digests).
- key refresh should be a normal fleet rollout: `uefi.var.set.plan` → `uefi.var.set.receipt`, approvals/quorum, cohort rollout.
- firmware updates and key refresh often ship together (some devices need firmware to accept new trust anchors).

See: `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`.


---

## Integration points

- **Non-negotiables:** firmware updates and UEFI variable writes must be receipted (no “run vendor tool as root”).
- **Hardware compatibility gates:** incorporate `fw.inventory.receipt` into `hw.compat.report` reasoning when firmware is a known risk.
- **Measured boot (optional):** some platforms measure capsule updates; event-log replay should be able to correlate firmware update receipts with boot events.
- **Trust bootstrap:** Secure Boot key updates are part of platform trust roots and belong in the evidence spine.

See also:

- `docs/320-hardware-compatibility-gates-and-safe-upgrades.md`
- `docs/313-boot-manifests-and-eventlog-replay.md`
- `docs/51-secure-boot-integration.md`
- `docs/155-trust-bootstrap.md`

Last updated: 2026-02-27
