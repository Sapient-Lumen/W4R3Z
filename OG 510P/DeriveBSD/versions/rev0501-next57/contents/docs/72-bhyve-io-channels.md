# bhyve IO channels: console, virtio-console, and nmdm

Hypervisor-centric DeriveBSD must keep runtime IO paths:
- deterministic
- minimal by default
- auditable and reproducible (repro capsules)

## bhyve console defaults

FreeBSD’s handbook notes bhyve defaults to serial console access (no graphical console by default).
bhyve also supports:
- `-l com1,stdio` (stdio)
- `-l com1,/dev/nmdmXA` (null-modem devices via nmdm(4))
- `virtio-console` for multiple guest↔host char ports (bhyve(8))

## DeriveBSD mapping (v1)

- Always attach a single deterministic “control console”:
  - either stdio (debug mode) or nmdm for managed mode
- Optionally attach a virtio-console port reserved for:
  - structured guest logs
  - health pings
  - metadata queries

## AF_VSOCK (optional)

VirtIO sockets / AF_VSOCK support is evolving on FreeBSD.
DeriveBSD should treat vsock as:
- preferred when available (cleaner RPC than scraping consoles)
- optional in v1, with virtio-console/nmdm as the baseline

## Audit invariants

- record which channel types were attached:
  - stdio vs nmdm vs virtio-console
- record device identifiers and digests of any generated config

## Non-goals (v1)

- building a full guest agent protocol suite
- relying on fragile ad-hoc host scripting for console access

References:
- FreeBSD Handbook virtualization chapter
- bhyve(8)
- nmdm(4)
- libvirt bhyve driver notes on nmdm console

Last updated: 2026-02-23
