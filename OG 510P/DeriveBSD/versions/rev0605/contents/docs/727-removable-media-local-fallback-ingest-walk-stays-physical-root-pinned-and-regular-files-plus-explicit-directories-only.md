# Removable-media local fallback ingest walk stays physical, root-pinned, and regular-files-plus-explicit-directories only

**Tier:** B (Implementation floor)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate

`docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed *where* the first host-local fallback executes.
`docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` already fixed *which filesystem families* that first cut may admit.
`docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md` already fixed *what the mounted tree is allowed to mean* once admitted.

This page fixes the next smaller but still expensive ambiguity:

> once the ingest jail starts walking `/ingest`, what member kinds and path-resolution semantics are allowed to participate in the first cut?

The answer is intentionally narrow:

> **the first ingest walk stays physical and root-pinned, admits only regular files plus explicit directories, fails closed on symlink/device/FIFO/socket semantics, and does not preserve hardlink topology in the first cut.**

See also:
- ADR: `adrs/ADR-0317-removable-media-local-fallback-ingest-walk-stays-physical-root-pinned-and-regular-files-plus-explicit-directories-only.md`
- previous boundaries: `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`, `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`, `docs/726-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- related workstation lesson: `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`
- workflow doc: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- workstation posture: `docs/458-removable-media-and-usb-posture-by-profile.md`

## Accepted boundary

### 1) The walk is physical and root-pinned

The first local-fallback ingest worker is not allowed to rely on ambient path resolution.
The reviewed shape is:

- open the admitted mounted root,
- walk it **physically**,
- stay **beneath that root**,
- and resolve later opens relative to that rooted walk instead of through ambient current-working-directory or “whatever symlink resolution produced” folklore.

This keeps the lane consistent with the archive’s earlier choices:

- host keeps mount authority,
- the mounted tree is inert input only,
- the jail is disposable and no-network,
- and `/ingest` is a bounded input root rather than a general-use namespace.

### 2) First-cut member kinds are only regular files and explicit directories

The first ingest walk admits only:

- **regular files**
- **explicit directories**

That is enough for the first useful local-ingest stories:

- classify/scan/sanitize/import a chosen file,
- enumerate candidate content under a directory tree,
- preserve empty directories when a review surface needs them,
- and explain observed input shape in receipts/support output.

It is intentionally *not* trying to be a filesystem-preserving import subsystem.

### 3) Symlinks and special objects fail closed

The first cut rejects member kinds that would smuggle ambient resolution or active authority back in:

- symlinks
- device nodes
- FIFOs
- sockets
- and equivalent active or host-coupled objects

These are not “just more files.”
They are resolution or endpoint semantics, and they do not belong in the first boring import lane.

So the first cut does **not**:

- silently follow symlinks,
- preserve symlink objects for later receiver-side resolution,
- silently skip special members,
- or reinterpret them as ordinary content.

It fails closed instead.

### 4) Hardlink topology is out of scope in the first cut

The first local-ingest lane is content-import-shaped, not filesystem-topology-shaped.
So even when the underlying admitted filesystem exposes multiple paths to the same inode/content object:

- the lane does **not** preserve hardlink topology as a reviewed or exported property,
- link-count fidelity is out of scope,
- and any implementation that encounters alias-topology ambiguity must either treat the paths only as independent regular-file path selections or deny them.

That keeps the first cut honest about what it delivers: selected/imported content, not a faithful reproduction of source filesystem structure.

### 5) Later richer lanes need explicit follow-on decisions

If later practice proves a need for:

- symlink-preserving import,
- symlink-following with explicit policy,
- special-object capture,
- image-in-file traversal,
- or filesystem-fidelity-preserving ingest/export,

those should come back as later explicit RFC/ADR work.
They should not arrive by quietly widening this first local-fallback lane.

## Canonical first-cut example stack

The canonical stack now pins the new walk boundary directly:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/mount.view.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`

Together they now say:

- the host-mounted `/ingest` tree remains the only input root,
- traversal is physical and root-pinned,
- the first admitted member kinds are regular files plus explicit directories only,
- symlink/device/FIFO/socket semantics fail closed,
- and hardlink topology is not preserved in the first cut.

## Why this cut is worth making now

Without this decision, the archive still pays a repeated implementation tax:

- coding cannot tell whether the first ingest walk is allowed to follow symlinks or preserve them,
- support cannot explain why an admitted medium still denied certain members,
- operability/evidence surfaces cannot say whether observed tree shape matched imported content shape,
- and B/C convenience pressure can quietly reopen host-namespace semantics under “just import that folder” wording.

This page removes that ambiguity with one finite first-cut answer.

## Related docs

- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`
- `docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md`

Last updated: 2026-03-26r458
