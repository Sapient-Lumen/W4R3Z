# ADR-0044: MicroVM launch receipts record attached IO channels

- Status: **accepted**
- Date: 2026-03-04

## Context

DeriveBSD treats runtime operations as evidence.
For microVMs, host↔guest IO channels (console/vsock/virtio-console/nmdm) are part of the **authority boundary**:

- they define what crossings exist between host and guest,
- they determine which debugging/telemetry paths were possible,
- and they are often the only way to recover forensics after a failure.

Different backends and deployments attach different channels:

- managed fleet hosts may prefer vsock + a managed console device,
- workstations may add debug consoles,
- appliances/regulatory shapes often require explicit, audited IO surfaces.

If launch receipts do not record which channels were actually attached, incidents turn into archaeology:

- "was a console attached?"
- "what control channel existed?"
- "could logs have escaped?"

We want a small, implementable contract that keeps A–D coherent without over-specifying backend details.

## Decision

`microvm.launch.receipt` MAY include `assigned.io_channels`, a list of attached host↔guest IO channels.

Each entry must include:

- `kind`: the channel class (`vsock`, `virtio-console`, `nmdm`, `stdio`, ...)
- `role`: what the channel is for (`control`, `console`, `logs`, ...)
- minimal endpoint details appropriate for that channel kind (e.g., `guest_cid` + `port` for vsock, a device path for nmdm).

This list is **evidence**, not a stable addressing contract:

- stable identity remains `instance.instance_id` (plus `plan_digest` for idempotency)
- endpoints such as vsock `cid:port` are backend-assigned and should be treated as ephemeral implementation details
- if higher-level discovery or brokering is needed, it should live in explicit broker/lease/receipt lanes (separately typed)

## Consequences

- Operators and incident tooling can reconstruct what host↔guest crossings existed for a given run.
- Fleet/workstation/appliance shapes remain aligned: the same receipt shape captures different channel attachments.
- If DeriveBSD later standardizes channel negotiation or endpoint brokering, it MUST be introduced as new typed artifacts (RFC/ADR), not by expanding ad-hoc fields.

See: `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.launch.receipt.schema.json`.
