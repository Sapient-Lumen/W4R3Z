# Inferno lessons: Styx/9P everywhere + per-process namespaces

Inferno (Bell Labs/Vita Nuova) is a “Plan 9 ideas for real deployments” system:
- resources as files
- per-process namespaces
- one protocol (Styx/9P) to reach both local and remote resources

DeriveBSD already borrows some Plan 9 concepts (union views, plumbing, factotum-shaped brokers),
but Inferno is a reminder that **"everything is a file" can be an inter-process and inter-machine API**,
not just a local OS metaphor.

## What to steal (selectively)

### 1) Namespaces are an isolation boundary and a UX surface

Inferno treats the namespace as *programmable policy*:
- processes see only the resources mounted into their tree
- remote services are mounted like local devices

**DeriveBSD mapping:**
- keep using jails/microVMs for isolation
- make the *filesystem view* for a unit a compiled artifact (`docs/264-mount-namespaces-and-union-views.md`)
- represent “mounted service endpoints” as capability-granted objects, not ambient paths

### 2) A file-protocol API is a great control-plane substrate

A file-like API (open/read/write/close) has nice properties:
- debuggable with ordinary tools
- stream-friendly
- capability-friendly (file descriptors are already handles)

**DeriveBSD mapping (where it fits):**
- control-plane and brokers that want a simple, inspectable API surface
  - lease broker
  - portal broker
  - policy query/explain endpoints
  - trace session capture

This doesn’t require “9P everywhere”. It suggests a pattern:
- provide a *file-shaped* control API locally (Unix socket + `openat`-style endpoints, or a small FUSE view)
- optionally expose it cross-compartment over an explicit transport (vsock, virtio-fs/9p)

### 3) "Mounting" is a powerful composition mechanism

In Plan 9/Inferno, composition is often expressed as:
- mount A here
- bind B there
- union them

DeriveBSD can express analogous composition as a **derived view graph**:
- store view minimization (`docs/152-store-view-minimization.md`)
- origin labels/quarantine views (`docs/280-origin-labels-and-quarantine-attributes.md`)
- portal-granted file capabilities (`docs/198-persistent-file-capabilities-bookmarks.md`)

The key is: *view changes are diffable artifacts*, not ad-hoc mounts.

## A concrete “greenfield bake-in” feature

**File-shaped broker interfaces** (optionally exported)

Define a convention:
- each broker exposes a virtual tree rooted at something like:
  - `/run/derive/brokers/<name>/...`
- everything under the tree is a capability-guarded endpoint
- reads/writes yield structured JSON (JCS when signed)

This gives us:
- stable introspection and scripting surface
- fewer bespoke admin protocols
- a natural place to hang receipts and session logs

(Transport is an implementation choice: local only at first, then vsock/9p later if it pays off.)

## References

- Inferno OS (project site): https://inferno-os.org/inferno/
- “The Inferno Operating System” (Ritchie et al., Bell Labs Technical Journal, 1997): https://www.mrynet.com/FTP/os/inferno/paper01.pdf
- Inferno overview (Wikipedia, for quick orientation): https://en.wikipedia.org/wiki/Inferno_(operating_system)

Last updated: 2026-02-27
