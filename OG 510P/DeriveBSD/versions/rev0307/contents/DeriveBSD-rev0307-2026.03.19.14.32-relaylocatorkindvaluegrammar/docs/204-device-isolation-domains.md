# Device isolation domains (driver VMs) as a first-class pattern

DeriveBSD is hypervisor-centric enough that **hardware attack surface** should be treated as a *separate class* of workload.

A recurring failure mode in “sandboxed” systems is:
- apps are jailed, but the desktop still shares one giant device-driver surface
- a single hostile USB device (or buggy driver) becomes a whole-session compromise

This doc proposes an optional but first-class pattern: **device isolation domains** (“driver VMs”).

See also:
- Device grants + devfs rulesets (treat `/dev` as authority): `docs/278-device-grants-and-devfs-rulesets.md`
- USB quarantine + removable media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`

## Lesson to steal

- **Qubes OS** isolates risky device classes by attaching controllers to dedicated qubes (e.g., `sys-usb`) and brokering access to other domains.
  - The user never connects a USB device directly to the trusted domain; it is mediated through the USB qube.
  - This keeps potentially malicious devices/firmware away from the core.  
  References: https://doc.qubes-os.org/en/latest/user/how-to-guides/how-to-use-usb-devices.html

## Model

### 1) Device domains own passthrough, workloads do not

DeriveBSD already defaults to **no PCI passthrough** for general workloads (`adrs/ADR-0006-no-pci-passthrough-by-default.md`).

Device domains refine that rule:

- only a small set of **device domains** may receive passthrough devices (USB controllers, NICs, GPUs)
- normal workload microVMs remain virtio-only
- device domains export *services* (networking, USB forwarding, GPU remoting) to other domains

Think of them as “security buffers” that you can rebuild/replace like any other signed artifact.

### 2) A host-side device broker enforces attachment policy

A `derive-deviced` broker (name placeholder) is responsible for:

- enumerating host hardware and controllers
- applying policy for which devices may be attached to which device domains
- issuing **leases** for device attachments
- emitting attach/detach evidence objects

### 3) Mediation surfaces (how other domains consume devices)

Device domains should prefer mediation surfaces that preserve the “authority as data” model:

- capability-carrying RPC (see `docs/183-object-capability-rpc.md`)
- explicit intent routing (see `docs/199-intent-routing-and-plumbing.md`)
- narrow protocol bridges (e.g., USB device forwarding, network routing)

## Evidence objects

To keep device attachment explainable and reviewable, attachments are evidence-bearing:

- `device.attach.grant` — policy-approved lease to attach a device/controller to a device domain
- `device.attach.receipt` — runtime acknowledgement that attachment is active (maps host device IDs → domain)
- `device.detach.receipt` — runtime acknowledgement that lease ended (detach, revoke, or expiry)

Schemas:
- `spec/device.attach.grant.schema.json`
- `spec/device.attach.receipt.schema.json`
- `spec/device.detach.receipt.schema.json`

## Threat model notes (what this mitigates)

- **host driver bugs**: drivers run inside replaceable device domains, not in the core host
- **malicious device firmware**: risky buses (USB) can be isolated from the most trusted plane
- **DMA risk containment**: IOMMU boundaries + limiting passthrough scope reduce catastrophic blast radius

## Open questions / future work

- preferred device forwarding protocols (USB/IP-like vs bespoke)
- “device classes” taxonomy (USB storage vs HID vs network dongles)
- treat USB HID as a special danger class; prefer brokered input streams and secure attention (see `docs/207-input-authority-secure-attention-and-hid-risk.md`)
- how to handle laptop-integrated devices that cannot be cleanly isolated

See also:
- hypervisor-centric direction: `docs/23-hypervisor-centric-derivebsd.md`
- runtime blast-radius contract: `docs/94-runtime-blast-radius-contract.md`
