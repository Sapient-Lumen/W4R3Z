# Hardware inventory + driver binding as evidence (no ambient autodetect)

Most OSes have an implicit “hardware brain”:

- the kernel discovers devices
- userland tools scrape `dmesg` and sysfs-ish state
- init scripts load “whatever seems needed”
- admins debug failures by tribal knowledge

This works until it doesn’t:

- a new kernel drops/changes a driver and you brick remote hosts
- a surprise device appears (USB / PCI hotplug) and you silently gain new authority
- fleet operators can’t answer *what hardware is actually present* without SSHing in
- support bundles leak serials and unique identifiers by accident

DeriveBSD can do better by treating hardware facts and driver choices as **typed, digestable evidence**.

## Goals

- Capture a **privacy-safe** host hardware inventory with stable semantics.
- Make driver/module/firmware binding decisions **explicit** (planned) instead of ambient.
- Provide a reusable input to:
  - compatibility gates (before switching generations)
  - device grant policy and devfs rulesets
  - firmware update plans
  - rollout cohorting (hardware classes)
  - explainability surfaces and incident bundles

Non-goals (v0):
- full “device manager” redesign (keep this compatible with FreeBSD reality)
- per-device driver sandboxing (see driver VMs / device isolation domains)

## Evidence objects

### 1) Hardware inventory receipt (`hw.inventory.receipt`)

A periodic, policy-governed snapshot of what the host believes is present.

Key design rule: **avoid raw serial numbers**. If serial correlation is needed, store only an org-scoped hash (HMAC) and treat export as a budgeted, policy-gated action.

Schema: `spec/hw.inventory.receipt.schema.json`

Typical contents:
- platform facts (UEFI/legacy, TPM present/version, CPU model/features, memory)
- buses: PCI topology, USB tree, virtio devices
- device identities:
  - stable IDs: vendor/device/subsystem IDs, class codes, ACPI HIDs
  - instance IDs: BDF / bus:dev (useful locally, not globally stable)
- current bindings:
  - kernel driver name
  - loaded module (if any)
  - firmware payload identity (digest or `fw.device.inventory` component ref)

Collection sources (FreeBSD-shaped): `devinfo(8)`, `pciconf(8)`, `usbconfig(8)`, boot log segments.

The product-default meaning of this inventory lane is now explicit in `docs/479-hardware-compatibility-posture-by-profile.md`:
inventory is refreshed before switch/install/recovery decisions that rely on hardware truth, but the **strength** of the resulting gate depends on A/B/C/D.

### 2) Device classification profiles (`device-profile`)

Inventory answers “what exists”; profiles answer “how should we treat it?”

DeriveBSD already models signed device classification objects (risk tags, HID classes, etc.).
Inventory should be able to reference a `device-profile` digest when a device is known/curated.

See: `spec/device.profile.schema.json`, `docs/278-device-grants-and-devfs-rulesets.md`.

## Driver binding posture (planned, explainable)

Driver binding has two separable meanings:

1) **Kernel binding**: which driver attaches to which discovered device.
2) **Policy binding**: what authority we grant to workloads that want to *use* a device.

DeriveBSD’s greenfield win is to make both explainable:

- kernel binding is constrained by a *planned* module set (`kmod.load.plan`) + lockdown posture
- policy binding is constrained by explicit device grants and devfs rulesets

We do **not** try to eliminate kernel auto-attach in v0.
Instead we make *mutability* explicit:

- activation preloads required modules
- runtime module loads are denied by default (or restricted to maintenance leases)
- device hotplug events are typed and correlated to policy decisions

See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/230-lockdown-levels-and-securelevel.md`.

## Privacy and fingerprinting

Hardware inventory is useful — and also a fingerprint.
DeriveBSD should default to:

- **digest-first** inventories in evidence bundles
- hashed identifiers for correlation (org-scoped HMAC, key held in a crypto domain)
- export of detailed inventory only via export policy + receipts

Inventory access should be treated like a capability (budgetable), not an ambient “read `/dev` and scrape everything” primitive.

See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/251-export-policies-and-support-bundle-portal.md`.

## Where it plugs into the pipeline

- **Activation** emits (or refreshes) `hw.inventory.receipt`.
- **Activation** may also emit `fw.inventory.receipt` (firmware posture) when policy enables the lane.
- **Plan compilation** may consume inventory to:
  - select driver/firmware strata (explicitly recorded in the Plan)
  - decide which device grants must exist
- **Change sets** can include a compatibility gate (see `docs/320-...`).
- **Incident bundles** include the inventory receipt digest by default.

## References

- FreeBSD device tree: `devinfo(8)`
- FreeBSD PCI introspection: `pciconf(8)`
- FreeBSD USB tree: `usbconfig(8)`
- NixOS: hardware config generation (`nixos-generate-config`) as an existence proof for declarative hardware capture.
- Fuchsia driver binding docs (device topology + matching) as a useful conceptual model for “binding is a thing you can reason about”.

(See `docs/32-curated-references.md` for links.)

Last updated: 2026-03-06r208
