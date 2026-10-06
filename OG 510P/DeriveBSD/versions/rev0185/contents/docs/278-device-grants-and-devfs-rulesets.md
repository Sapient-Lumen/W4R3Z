# Device grants + devfs rulesets: treat `/dev` as authority (v0)

Most “sandboxed” systems accidentally smuggle ambient authority through **device nodes**.

On FreeBSD, the jail man page is blunt: exposing inappropriate device nodes can let a jailed process bypass sandboxing, and recommends using **devfs rules** to limit what appears in a per-jail `/dev`.  
References:
- https://man.freebsd.org/cgi/man.cgi?query=jail&sektion=8
- https://man.freebsd.org/cgi/man.cgi?query=devfs&sektion=8
- https://man.freebsd.org/cgi/man.cgi?query=devfs.rules&sektion=5

DeriveBSD should make device access:
- **explicit** (no “whatever /dev happens to contain”)
- **lease-based** (revocable, TTL'd, logged)
- **reviewable** (diffable, linted)
- **evidenced** (attach/detach receipts + inventory bindings)

This doc tightens the device story by connecting:
- device isolation domains (`docs/204-device-isolation-domains.md`)
- lease registry (`docs/249-lease-registry-and-cross-lane-revocation.md`)
- promise profiles (`docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`)
- existing device artifacts (`spec/device.profile.schema.json`, `spec/device.attach.grant.schema.json`, `spec/device.attach.receipt.schema.json`, `spec/device.detach.receipt.schema.json`)

## Design principle: "device nodes are capability handles"

A device node is effectively a *handle to privileged kernel surface* (ioctl spaces, DMA setup, raw disk access, keystroke injection, etc.).
If a sandbox has access to the node, it often has access to the authority.

Therefore DeriveBSD should treat `/dev` exposure as **first-class authority**, not a filesystem detail.

## The three-layer model

### 1) Device identity + risk classification (inventory lane)

All devices that may ever be attached cross-domain should have a `device.profile`:
- stable device_id (derived from transport address + serial where possible)
- class (block/audio/video/usb-controller/net/tpm/...)
- risk tags (hid, dma, firmware-opaque, removable, untrusted-bus, etc.)

Schema + example:
- `spec/device.profile.schema.json`
- `spec/examples/device.profile.json`

### 2) Attachment is a lease (authority lane)

Cross-domain attachment is **never implicit**:
- `device.attach.grant` (lease, permissions, constraints)
- `device.attach.receipt` (what actually happened at runtime)
- `device.detach.receipt` (cleanup and revocation evidence)

Schemas + examples:
- `spec/device.attach.grant.schema.json`, `spec/examples/device.attach.grant.json`
- `spec/device.attach.receipt.schema.json`, `spec/examples/device.attach.receipt.json`
- `spec/device.detach.receipt.schema.json`, `spec/examples/device.detach.receipt.json`

### 3) Inside-domain visibility is a compiled view (enforcement lane)

Even after a device is “attached”, *visibility* inside a jail/VM should be a compiled, minimal **device view**:

- For **service jails**, default `/dev` should be near-empty:
  - `null`, `zero`, `random`/`urandom` (or a brokered RNG handle), `log` (or a logging socket)
  - no raw disk, no `usb*`, no `bpf`, no `mem`/`kmem`, no gpu nodes by default

- A promise profile + attach grant should compile into:
  - a **devfs view plan** (`devfs.view.plan`) and rendered ruleset (for jails)
  - an apply receipt (`devfs.view.receipt`) and drift/deny events (`devfs.view.event`)
  - (optionally) portal/broker endpoints instead of direct nodes

See: `docs/323-devfs-views-plans-and-receipts.md`, `spec/devfs.view.plan.schema.json`.

This is where DeriveBSD earns “pledge ergonomics” on BSD primitives:
**profiles describe intent; compilation selects concrete primitives**.

## Compilation sketch (what the system does)

Inputs:
- `sandbox-profile` (what the service says it needs)
- `device.profile` (what the hardware *is*)
- `device.attach.grant` (what authority is allowed right now)
- host policy (global constraints, “never allow X in jail Y”)

Outputs:
- `devfs.view.plan` compiled intent + rendered ruleset applied to the jail's devfs mount (when jailed)
- `devfs.view.receipt` emitted after apply (ruleset id + observed node digest)
- `devfs.view.event` for drift/deny incidents
- portal routes for dangerous classes (HID, raw block, GPU control surfaces)
- evidence receipts bound into the incident bundle lane (`docs/216-…`, `spec/incident.bundle.schema.json`)

## Lint rules we should enforce

- **No silent device expansion**: a profile that requests any device class beyond the curated “safe pseudo-dev set” must name it explicitly.
- **HID is special-danger**: input device grants should require secure attention / interactive consent (`docs/207-input-authority-secure-attention-and-hid-risk.md`).
- **Block devices default read-only** unless an explicit `writable` constraint exists in the lease grant.
- **Raw disk implies breakglass**: profiles requesting raw block access should be flagged as high-risk and require a policy decision record.
- **DMA-capable devices must not land in the “trusted” domain** unless explicitly allowed (prefer device isolation domains).

## Open questions (push into an ADR when decided)

- Should “device portals” be mandatory for certain classes (HID, webcam, microphone), even when a node exists?
- How do we express “this service may use *a* webcam” without creating ambient authority (device selection + consent UX)?
