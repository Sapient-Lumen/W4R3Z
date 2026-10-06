# Firmware updates as artifacts (inventory + plans + receipts)

See also (current artifact shapes + schemas):
- `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- `spec/platform.report.schema.json`
- `spec/fw.update.plan.schema.json`
- `spec/fw.update.receipt.schema.json`

Most OS update systems stop at: kernel + userland + packages.
But real fleets fail in a different place:

- BIOS/UEFI updates
- NIC/SSD/BMC firmware
- microcode + device option ROMs

If firmware is “outside the system”, operators end up with:
- vendor EXEs / bootable ISOs / bespoke scripts
- unclear provenance (where did this blob come from?)
- poor auditability (what changed on this host?)
- bad rollback stories (did we brick it?)

DeriveBSD has a greenfield advantage: treat firmware as **first-class change material** with the same evidence posture as everything else.

## Goals

- Maintain a **typed inventory** of updatable firmware components.
- Represent firmware changes as explicit **plans**.
- Emit integrity-protected **receipts** for what happened.
- Integrate firmware updates into:
  - `change-set` orchestration
  - incident bundles
  - health gates
  - the structured event journal

## Evidence objects

### 1) Firmware device inventory (`fw-device-inventory`)

A compact host-local inventory of firmware-bearing components.

Optionally, a broader `platform-report` can reference this inventory by digest along with other platform provenance facts.
Key design rule: **avoid raw serials**; include stable hashes and policy tags.

Use cases:
- policy: “this host class may update these components only”
- reporting: “which hosts are on vulnerable firmware?”
- bundling: include inventory in `incident.bundle`

Schema: `spec/fw.device.inventory.schema.json`

### 2) Firmware update plan (`fw-update-plan`)

An explicit plan referencing firmware payload artifacts by digest, including:
- component ids
- expected current version(s)
- desired target version
- update mechanism (UEFI capsule, NVMe slot update, BMC channel, etc.)
- preconditions (AC power, battery %, maintenance window)
- reboot expectations

Firmware payloads may live in a dedicated store namespace (policy-gated) and may be distributed via:
- online channels (like other artifacts)
- offline signed bundles (`docs/138-offline-signed-update-bundles.md`)

Schema: `spec/fw.update.plan.schema.json`

### 3) Firmware update receipt (`fw-update-receipt`)

A receipt emitted by the apply engine (or firmware update worker), including:
- plan digest
- per-component status + observed versions
- reboot requirement + next-boot state
- pointers to event ids / segments in the structured journal

Schema: `spec/fw.update.receipt.schema.json`

## Execution model (how it plugs into DeriveBSD)

### Change sets

Firmware updates are just another optional step:

- `change-set.steps[].op = apply-firmware`
- `refs` includes the `fw-update-plan` digest

Default ordering recommendation:

1) snapshot (state/config) + holds (if relevant)
2) apply config
3) run migrations
4) **apply firmware** (if present)
5) reconcile services
6) health gate
7) commit

Why after migrations? In many systems the new OS expects a firmware floor.
Why before health gate? The gate should be able to see the firmware receipt.

See: `docs/219-change-sets-and-apply-engine.md`

### Event journal

Firmware operations should emit typed `event.record` milestones, e.g.:
- `fw.update.started`
- `fw.update.staged`
- `fw.update.pending-reboot`
- `fw.update.succeeded`
- `fw.update.failed`

See: `docs/215-structured-event-log-as-evidence.md`

### Incident bundles

Default bundle contents should include:
- `fw-device-inventory` digest (safe by design)
- recent `fw-update-receipt` digests (if any)

See: `docs/216-incident-snapshots-and-support-bundles.md`

### Health gating

Health gates may require:
- “firmware plan applied successfully”
- “firmware is at or above required floor”

See: `docs/112-health-gated-updates.md`

## Security + policy notes

- Firmware payload artifacts are high-risk (vendor blobs). Treat them like a **separate trust lane**:
  - allowlists by vendor/device class
  - signatures required
  - optional transparency publication
- Never treat “inventory presence” as permission to update.
  - updating requires an explicit plan + a policy decision.
- Prefer update mechanisms with strong platform semantics:
  - UEFI capsule update + ESRT exposure (where available)

See also:
- `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- `docs/336-uefi-capsules-esrt-and-fwupd-practice-notes.md`

References:
- UEFI spec: Firmware Update and Reporting (ESRT + capsule status): https://uefi.org/specs/UEFI/2.9_A/23_Firmware_Update_and_Reporting.html
- LVFS intro: https://lvfs.readthedocs.io/en/latest/intro.html
- fwupd overview: https://fwupd.org/
- fwupd UEFI capsule plugin notes (real device constraints): https://fwupd.github.io/libfwupdplugin/uefi-capsule-README.html
- Windows UEFI firmware update platform (OS-initiated capsule guidance): https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/windows-uefi-firmware-update-platform

Last updated: 2026-02-26
