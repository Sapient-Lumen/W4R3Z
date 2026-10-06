# USB quarantine + removable media workflow (Qubes USB-qubes lessons)

Removable media is the universal footgun:
- a hostile USB device can attack the USB stack and drivers
- a “normal” USB stick is an untrusted file container (malicious PDFs, exploit documents, weird filesystem images)
- automount makes it all ambient and invisible

DeriveBSD should ship a *boring, safe default*:
- **no automount into the trusted domain**
- USB controller stacks are **quarantined** (device isolation domain)
- using a device requires an explicit **lease grant** + evidence
- opening files from removable media should route through the **sanitization portal** (`docs/267-sanitization-portal-and-disposable-sandboxes.md`)
- imported files should carry **origin labels + quarantine metadata** (`docs/280-origin-labels-and-quarantine-attributes.md`)

See also the accepted profile baseline: `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`, `docs/458-removable-media-and-usb-posture-by-profile.md`.

Prior art worth stealing:
- Qubes OS: isolate USB stacks/drivers in an unprivileged VM (`sys-usb`) and attach devices to other domains on demand.  
  References:
  - https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-usb-devices.html
  - https://doc.qubes-os.org/en/latest/developer/system/architecture.html

## Default posture ("greenfield win")

### 1) USB controllers belong to a device domain
- Create one (or more) **USB quarantine domains** that own USB controllers (passthrough).
- The trusted domain never loads USB device drivers.
- Device domains have *no secrets* and minimal connectivity.

See also: `docs/204-device-isolation-domains.md`.

### 2) “Attach” is a lease with constraints
When a USB device appears:
- it is classified (`device.profile`) with risk tags: removable, hid, firmware-opaque, etc.
- it is not usable elsewhere until a `device.attach.grant` exists

This keeps “who had the device when” answerable in incident bundles.

### 3) Default workflow for files: sanitize, then import
For USB sticks and other file media:

1) Attach device **read-only** to a disposable “media-scan” domain.
2) Use the sanitization portal to export a sanitized copy into a safe staging area.
3) Only then import into a persistent domain, emitting a `content.import.receipt` that records whether provenance metadata was preserved, rehydrated, or laundering-suspected.

This is the “dangerous documents” workflow made first-class.

### 4) Default workflow for block use: constrained and visible
For “I need to copy files / do a backup”:
- attach partitions (not whole disk) when possible
- prefer read-only by default
- require explicit writable grants + TTL
- emit attach/detach receipts and include them in support bundles

### 5) Airgap updates: removable media feeds quarantine→promote
USB is a common airgap transport. DeriveBSD already has:
- signed mirror kits + quarantine→promote (`docs/273-airgap-mirror-kits-and-sneakernet-updates.md`)

The USB posture should make the safe path easy:
- mount kit media in a quarantine domain
- import kit into quarantine store
- verify signatures + freshness
- then promote into the trusted update channel

## Footguns to design around (be explicit)

- “My system boots from USB”: do not isolate the boot media controller into a device domain that would break boot.
- “I need a keyboard at early boot”: HID/input is special-danger; handle via secure attention / trusted path (`docs/207-input-authority-secure-attention-and-hid-risk.md`) and avoid making early-boot input depend on untrusted USB domains.

## Suggested cross-links
- device grants + /dev authority: `docs/278-device-grants-and-devfs-rulesets.md`
- device domains: `docs/204-device-isolation-domains.md`
- safe untrusted files: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- airgap kits: `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`


Last updated: 2026-03-07r213
