# Removable media and USB posture by profile

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** A, B, C, D
**Pillars:** isolation, supply-chain, operability
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate

Removable media is one of the easiest ways for an archive like this to become incoherent:
USB convenience pressures product **B**, air-gap workflows pressure **D**, break-glass habits pressure **A**, and consumer hardware constraints pressure **C**.

This doc records the smallest durable answer:

> no profile gets ambient automount into its most trusted plane, and removable media stays quarantine-first even when hardware support differs.

See `adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md`.

## Baseline rule

Across all profiles:

- removable media is **never** ambient by default,
- discovery/classification may be automatic, but **mount/use is explicit**,
- untrusted files prefer **sanitize → import**,
- block devices prefer **read-only first**,
- and attach/import activity is receipted so “who had the device?” stays answerable.

This keeps USB/removable-media behavior aligned with DeriveBSD’s wider model: authority is leased, explained, and evidenced.

## Profile defaults

| Profile | `removable_media` default | `usb_isolation` default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `deny-or-quarantine-only` | `prefer-device-domain-no-host-automount` | Fleet hosts should not normalize local USB workflows; if media is used at all, it stays explicit, receipted, and ideally isolated from the core host. |
| **B workstation** | `quarantine-first-no-automount` | `device-domain-required-when-supported` | The host keeps trusted UI/HID authority; storage/media flows go through quarantine/device domains and sanitize/import paths, not direct automount into the trusted desktop plane. |
| **C general_os** | `quarantine-first-local-fallback` | `prefer-device-domain-fallback-to-local-policy` | General-purpose installs still prefer isolated controllers, but imperfect consumer hardware may use a bounded local authorization fallback instead of ambient automount. |
| **D appliance_factory** | `offline-ingest-quarantine-first` | `device-domain-or-ingest-station` | Regulatory/offline ingest should happen through a quarantined path or dedicated ingest station, then quarantine→promote into trusted update/evidence lanes. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## The hard decision hidden inside the table

The archive is now choosing **against** a universal “USB is just storage” mental model.
That means:

- no trusted-plane automount as the default convenience path,
- no requirement that every laptop magically support perfect controller isolation,
- but also no excuse for returning to ambient local attach semantics.

Instead, profile **C** gets the only explicit fallback:

- classify the device,
- apply a local authorization policy,
- default block/deny unknown devices until the user or policy engine authorizes them,
- keep mounts explicit and read-only-first,
- and route imported content through origin/quarantine handling.

That fallback should look like a **policy engine**, not like an automounter with a scary dialog.
The useful lesson from USBGuard is the posture, not the Linux implementation: explicit allow/block/reject decisions against stable device attributes, with a default that blocks until a decision is made.

## How this fits the existing workstation boundary

For profile **B**, this decision composes directly with `ADR-0047`:

- the host owns raw HID, focus, and trusted prompts,
- general interactive apps are AppVM-first,
- and removable-media access is another brokered/device-domain crossing, not a reason to run general apps on the host.

So “open this file from a USB stick” should normally become:

1. detect/classify in the device domain,
2. attach read-only to a scan/import domain,
3. sanitize or import with origin labels,
4. hand the resulting object into the destination AppVM through portals/brokers.

That is more steps internally, but fewer trust ambiguities externally.

## How this fits A and D

### A) Fleet host

A fleet host should not silently become a “sometimes desktop” because a human plugged in a drive.
Local removable-media use is a narrow exception path:

- no automount into the host,
- explicit break-glass or maintenance workflow if policy allows,
- receipts bound into incident/support bundles,
- and preference for signed network paths or mirror kits over ad-hoc local copying.

### D) Appliance factory / regulatory

For regulated or offline factories, removable media is often real, not optional.
The correct move is not pretending it will disappear; it is forcing it into a stable ingest lane:

- quarantine/device domain or dedicated ingest station,
- signed kit / provenance verification,
- quarantine→promote into trusted channels,
- deterministic evidence retention and redaction.

## What remains open

The baseline is decided, but several implementation details remain open:

- how to detect “device-domain supported” hardware robustly,
- what the BSD-native local fallback authorization daemon/UI looks like,
- how remembered local approvals expire/review/revoke,
- and how integrated devices (Bluetooth radios, webcams, FIDO/smart-card readers) map onto the same posture without creating carve-outs.

Those belong in future RFC/ADR work, not in the baseline profile contract.

## Related docs

- `docs/411-product-profiles-as-compilation-target.md`
- `docs/412-product-profile-matrix.md`
- `docs/204-device-isolation-domains.md`
- `docs/207-input-authority-secure-attention-and-hid-risk.md`
- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/280-origin-labels-and-quarantine-attributes.md`
- `docs/273-airgap-mirror-kits-and-sneakernet-updates.md`

Last updated: 2026-03-06r187
