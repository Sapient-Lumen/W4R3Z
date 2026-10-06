# Disk layout plans and receipts (partitioning as evidence)

Partition tables, filesystems, and pool topology are part of the system’s security and recovery story.
If they are created by an installer script and then forgotten, incidents become archaeology.

DeriveBSD should treat disk mutation like any other state transition:

- **`disk.layout.plan`**: a typed intent for partition/pool/filesystem layout
- **`disk.layout.receipt`**: what was actually applied, with device identity and stable IDs

This enables:
- idempotent (retryable) installs
- audited “what changed my disks?” answers
- safe additive evolution (grow, add partitions) without shrink footguns
- portable fleet imaging: identical plans applied across similar hardware

Related:
- Installation/recovery as derived operations: `docs/309-installation-and-recovery-as-derived-operations.md`
- Host generations and ZFS boot environments: `docs/69-host-generations-bectl.md`, `docs/284-bootenv-switching-as-evidence.md`
- Sealed secrets + attested unsealing (for encrypted pools): `docs/272-sealed-secrets-attested-unsealing.md`


## 1) What counts as “disk layout” in DeriveBSD?

At minimum:
- GPT partition table (partition GUIDs, type GUIDs, sizes, labels)
- which partitions are:
  - EFI system partitions
  - swap
  - ZFS pool members / boot pool
  - data partitions
- pool topology (single vs mirror, ashift)
- encryption posture (if any): key source and policy reference
- bootloader placement constraints (UEFI paths, loader config constraints)

Out of scope for v0.1 (but should remain compatible):
- complex RAID topologies beyond mirror
- multipath / SAN
- exotic boot chains


## 2) Plan semantics (how the plan behaves)

Product-shape note: `docs/473-installation-and-recovery-posture-by-profile.md` decides where additive apply is merely the default vs where stronger breakglass/confirmation/offline-reset rules apply, `docs/483-destructive-reprovisioning-and-reset-authority.md` decides the official authority contract for destructive reprovision, and `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md` fixes the product-shaped evidence/detail/export default for that destructive lane; this doc stays focused on the typed plan/receipt substrate.

### Additive-by-default
Borrow a key idea from systemd-repart: declarative layouts should be **safe to apply repeatedly**.

Default rules:
- Create missing partitions.
- Grow partitions/filesystems when marked growable.
- Never shrink or reformat existing partitions without explicit breakglass approval.

### Stable identifiers
Plans should avoid “partition 3 is swap”. Prefer:
- labels
- partition UUIDs
- role tags (`efi`, `zfs`, `factory-reset`)

Receipts should capture:
- actual partition UUIDs
- actual sizes
- device identifiers (WWN/serial if available)


## 3) `disk.layout.plan` shape

A useful v0.1 plan can be simple and still high value:

- `target_device` selector:
  - allow matching by WWN/serial/path
  - allow size bounds (avoid applying a layout to the wrong disk)
- `table`: `gpt`
- `partitions[]`:
  - `name` (human label)
  - `role` (efi/swap/zfs/data/factory-reset)
  - `size` mode (fixed/min+grow)
  - `content` (fat32/zfs/ufs/raw)
- optional `zfs` stanza for `role=zfs`:
  - `pool_name`
  - `topology` (single/mirror)
  - `ashift`
  - `encryption_policy_ref` (digest or policy handle)

The plan is intentionally *not* an imperative script.
If something requires imperative logic, express it as:
- a higher-level Spec frontend that compiles to the plan, or
- a change set with explicit gates.

See schemas:
- `spec/disk.layout.plan.schema.json`
- `spec/disk.layout.receipt.schema.json`


## 4) Receipts (what we must capture)

A `disk.layout.receipt` should be sufficient to answer:

- Which disk(s) were touched?
- What was created/modified?
- What stable identifiers were assigned?
- Which plan and toolchain did the operation use?

Minimum receipt fields:
- plan digest + plan id (if present)
- applied_at / finished_at
- host_id (if known) / session id
- device identifiers and size
- partition list with UUIDs and final sizes
- pool identifiers (zpool GUID) when applicable
- outcome + error list


## 5) Factory reset as a first-class marker

Factory reset features are dangerous when they are implicit.
Instead:

- reserve an explicit `factory-reset` partition role, or
- require a hardware/firmware marker plus explicit operator consent.

The important narrowing is that these are now only **authority inputs** to `reset.authorization` / `reset.receipt`, not standalone reset folklore.
This aligns reset behavior with typed evidence and avoids “oops, it auto-wiped because a script decided to”.


## 6) Future extensions (keep the door open)

- a normalized disk-layout diff object (plan vs observed)
- `disk.layout.lint`: warnings (e.g., no redundancy on a fleet profile that expects it)
- support for “discoverable disk images” layouts (consistent type GUIDs, minimal boot-time assembly)
- integration with a “recovery image always present” policy (keep a known-good tooling boot path on disk)

The key meta-rule: **disk topology is too important to remain outside the evidence model.**

Last updated: 2026-03-21r349
