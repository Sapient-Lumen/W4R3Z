# RFC-0139: Device isolation domains (driver VMs)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Even with strong sandboxing, the system can lose if:

- a risky bus (USB) is handled by the most trusted domain
- device drivers and firmware form a large, shared attack surface
- “passthrough exceptions” become the default way to make things work

DeriveBSD needs a **repeatable pattern** for isolating device classes while keeping the “authority as data” posture.

## Proposal

Introduce an **optional first-class lane**: *device isolation domains* (“driver VMs”).

Key properties:

1) **Passthrough is restricted to device domains**
   - workloads remain virtio-only by default (aligns with ADR-0006)
   - device domains may receive passthrough only via explicit plan + policy

2) **A host-side broker mediates attachment**
   - enumerates devices/controllers
   - enforces policy for allowable attachments
   - issues leases (time-bounded and revocable)

3) **Attachments are evidence-bearing**
   - emit `device.attach.grant` for policy-approved leases
   - emit `device.attach.receipt` / `device.detach.receipt` from the runtime

4) **Device services are exported, not devices**
   - other domains consume devices via narrow services (RPC, virtio bridges, forwarding protocols)

## Non-goals

- standardizing one universal forwarding protocol for all device classes in v0
- making passthrough a “normal app feature”

## Spec objects

- `device.attach.grant` (policy-approved lease)
- `device.attach.receipt` (runtime acknowledgement)
- `device.detach.receipt` (runtime acknowledgement)

See: `docs/204-device-isolation-domains.md`.

## Open questions

- device class taxonomy and policy UX
- ergonomics for laptop-integrated devices
- how to represent IOMMU group constraints in plans (without leaking host topology unnecessarily)
