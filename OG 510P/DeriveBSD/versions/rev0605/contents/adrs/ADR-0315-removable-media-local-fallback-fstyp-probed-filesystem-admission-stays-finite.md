# ADR-0315: Removable-media local fallback `fstyp`-probed filesystem admission stays finite

- Status: Accepted
- Date: 2026-03-26

## Context

`adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` fixed what the imperfect-hardware B/C fallback is allowed to be.
`adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` fixed the first buildable execution boundary: host-controlled read-only mount, then a disposable no-network jail consuming a projected tree instead of raw block-device nodes.

That still left one expensive implementation choice unresolved:

> after the host has the device, which filesystem families is the first cut actually allowed to admit?

If the archive leaves that vague, several bad outcomes stay live at once:

- implementation work quietly drifts toward “mount whatever the kernel or installed helpers happen to recognize”,
- B secure-workstation pressure normalizes a growing compatibility surface without a reviewed floor,
- C general-purpose pressure keeps asking whether modern Linux/Windows/macOS filesystems are “probably fine” even though the first local fallback was supposed to stay narrow,
- and support/export surfaces lose a crisp answer for why some media mounted and others failed closed.

The archive already has enough existing pieces to choose a smaller first cut:

- `device.profile` classifies the removable storage session,
- `device.attach.*` already records the explicit storage lease,
- FreeBSD already provides `fstyp(8)` as a machine-parsable filesystem probe, and it runs sandboxed using Capsicum,
- the first cut already keeps all mount authority on the host,
- and the archive already distinguishes baseline lanes from later compatibility adapters instead of pretending every product shape must accept the same parser surface immediately.

## Decision

1. **The host must probe the inserted medium with `fstyp` before any local-fallback mount.**
   The first cut uses a typed probe result, not file-extension heuristics, mount-try roulette, or remembered “last time this device worked” folklore.

2. **The first admitted filesystem-family set is finite and small.**
   The first host-local B/C fallback admits only:
   - `msdosfs`
   - `exfat`
   - `ufs`
   - `cd9660`

3. **`exfat` is allowed, but only as an explicit adapter-backed case.**
   This keeps common removable-media interoperability viable without pretending the helper/module dependency is ambient baseline behavior.

4. **The first cut fails closed on richer or more misleading families.**
   The local fallback does **not** admit, in this first cut:
   - `ext2fs`
   - `ntfs`
   - `zfs`
   - `geli`
   - `unknown` / unrecognized probe results
   - filesystem/container images discovered as ordinary files inside the mounted tree

5. **All admitted families stay host-mounted read-only and then projected into the disposable jail.**
   This ADR does not reopen in-jail mounting, raw block-device exposure, or automatic write support.

6. **The canonical example stack now includes an explicit exFAT probe/admission path.**
   The archive adds:
   - `spec/examples/device.profile.removable-media-local-ingest.exfat.json`
   - updated `spec/examples/device.attach.grant.removable-media-local-ingest.json`
   - updated `spec/examples/mount.view.removable-media-local-ingest.json`
   - updated `spec/examples/content.import.plan.removable-media-local-ingest.json`

## Consequences

- The first implementation target now has a finite mount-admission table instead of an open-ended compatibility argument.
- B gets the high-value cross-platform removable-media cases (`msdosfs`, `exfat`) without ambient automount drift.
- C keeps a viable baseline without forcing the first local fallback to absorb every host-compatibility ask.
- The archive stays honest that Linux/Windows/macOS richer filesystems, encrypted providers, and pool import semantics are later explicit lanes or adapters, not hidden baseline behavior.

## What this ADR intentionally does not decide

This ADR does **not** settle:

- whether later compatibility adapters should add `ext2fs`, `ntfs`, HFS+, or other families,
- whether later stronger lanes should prefer microVM/device-domain parsing for a broader filesystem set,
- exact trusted-UI denial wording for unsupported filesystems,
- or whether image-in-file ingestion deserves its own later typed lane.
