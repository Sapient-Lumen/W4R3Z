# ZFS boot environments as system generations (receipt-backed)

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD treats host deployments as immutable generations (like Nix profiles), but on FreeBSD the *physical* primitive for atomic upgrades is often a ZFS **boot environment** (BE).

This doc tightens the contract: how a generation maps to a BE, what evidence/receipts must be emitted, and how health-gated rollback interacts with the bootloader.

## Goals

- Atomic switch to a new generation
- Fast rollback (operator-driven or automatic)
- A generation is explainable: “what dataset did we boot from and why?”
- GC/retention integrates with Derive roots/pins

## Model

- Each **system generation** has:
  - a closure digest (what must be present)
  - an activation plan digest (what was intended)
  - a BE identity (dataset + optional snapshot) when ZFS-backed

- A boot environment is a ZFS dataset (typically under `zpool/ROOT/...`) that can be selected at boot.

FreeBSD tools:
- `bectl(8)` and `libbe(3)` are the native BE interface
- FreeBSD wiki overview: https://wiki.freebsd.org/BootEnvironments
- `bectl(8)` man page: https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8
- `libbe(3)` man page: https://man.freebsd.org/cgi/man.cgi?query=libbe&sektion=3

## Naming and identity (recommended)

Avoid opaque, operator-only names.

Recommended dataset naming:
- `zpool/ROOT/derive/<short_plan>-<short_object>-<label>`
  - `short_plan`: first 8–12 chars of the plan digest
  - `short_object`: first 8–12 chars of the activated system object digest
  - `label`: human hint (channel/version); non-authoritative

Receipts must record the *full* dataset identity and digests; names are convenience only.

## Activation protocol (ZFS-backed)

1) **Build** the new system closure (no host mutation).
2) **Prepare** a new BE:
   - clone from a known base BE or snapshot
   - mount it at a staging mountpoint (not `/`)
3) **Apply activation** into the staging mount:
   - write config/materialized manifests
   - apply idempotent migrations that are allowed at activation time
   - write “boot assessment seed” state (try counters, health policy id)
4) **Seal**:
   - unmount
   - set bootloader entry / `nextboot` semantics for a *tentative* boot
5) **Reboot** into the new BE.

The activation run emits:
- `host.activate.plan` (inputs + intended BE mutations)
- `host.activate.receipt` including:
  - BE dataset id (+ snapshot id if created)
  - the generation/closure digests
  - boot selection intent (nextboot vs committed)
  - boot-try counter parameters
  - policy decisions used

## Health-gated commit (“A/B semantics”)

A successful reboot is not enough; “boot success” is a separately recorded fact.

Recommended flow:

- Boot into new BE with **try counters** enabled.
- Early userspace runs the health probe:
  - verify closure proofs / signatures
  - verify required services
  - verify required state migrations
- If healthy:
  - bless/commit the boot (clear counters; mark BE as default/active)
  - emit `boot.bless.receipt`
- If unhealthy:
  - mark bad and rollback (automatic)
  - emit `boot.rollback.receipt` with failure evidence

See: `docs/112-health-gated-updates.md`, `docs/241-boot-try-counters-and-boot-assessment.md`, `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`.

## Retention and GC

BEs are “big objects”; deleting them must be policy-governed.

- Every bootable generation is a **root** (`root.system.bootmenu`).
- Pins can retain specific generations indefinitely.
- GC should:
  - compute reachability from roots
  - destroy unreachable BEs (and associated snapshots) with receipts

See: `docs/175-pins-roots-and-garbage-collection.md`, `docs/225-storage-health-and-scrubbing-as-evidence.md`.

## Non-ZFS backends (later)

If the host is not ZFS-backed, DeriveBSD can still provide:
- A/B partitions or image slots
- filesystem snapshot/rollback lanes where supported

But ZFS should be the “happy path” for FreeBSD-first DeriveBSD.

Last updated: 2026-02-27r117
