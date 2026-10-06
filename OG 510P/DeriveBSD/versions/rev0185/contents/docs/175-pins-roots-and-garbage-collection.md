# Pins, roots, and garbage collection (don’t lose the good stuff)

Nix’s garbage collector is effective because **liveness is explicit**: store objects survive if something outside the store points to them (a *GC root*). Profiles and generations are roots by default.

DeriveBSD needs an equivalent concept across:

* CAS store objects
* ZFS datasets/snapshots/boot environments
* microVM and DevShell artifacts

## Goals

* predictable disk usage management
* “keep this known-good generation forever” without hacks
* evidence-backed retention changes (auditability)

## Model

### Roots

DeriveBSD defines explicit **roots**:

* `root.system.current` — the currently booted generation
* `root.system.bootmenu` — generations listed as bootable
* `root.user.<uid>` — per-user environment generations
* `root.pins.<name>` — operator-defined pins

Roots are expressed as *references* to digests:

* `artifact_digest`
* `plan_digest`
* `zfs.snapshot` identifiers (when the artifact is a ZFS BE)

### Pins

Pins are user/operator actions that intentionally keep objects alive:

* `derive pin add <digest> --name <n>`
* `derive pin rm <n>`

Pins emit evidence objects:

* `pin.add.receipt`
* `pin.rm.receipt`

Policy can restrict pinning (e.g., only certain roles can pin system generations).

### Garbage collection

GC computes reachability from roots and deletes unreachable objects.

For ZFS-backed artifacts, this should use ZFS-native retention tools:

* snapshots are held while referenced
* bookmarks can preserve replication continuity

## UX principles (Nix pros will expect)

* list generations and sizes quickly
* show “why is this retained?”
* allow trimming by age/keep-last-N

Suggested CLI:

* `derive gc plan --json` (dry-run report)
* `derive gc run`
* `derive gc why <digest>`
* `derive generations list --scope system|user|vm|devshell`

## Receipted GC runs

GC should be treated as a first-class operation: produce a plan (dry-run), gate it under policy, and emit a receipt.

- Plan: `store.gc.plan`
- Receipt: `store.gc.receipt`

See: `docs/426-store-gc-plans-and-receipts.md`.

## References

* Nix manual — Garbage collection: https://nix.dev/manual/nix/2.26/package-management/garbage-collection
* Nix Pills — The Garbage Collector: https://nixos.org/guides/nix-pills/11-garbage-collector.html
