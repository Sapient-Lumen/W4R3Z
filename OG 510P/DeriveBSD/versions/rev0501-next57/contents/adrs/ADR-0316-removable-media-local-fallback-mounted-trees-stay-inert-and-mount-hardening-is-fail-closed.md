# ADR-0316: Removable-media local fallback mounted trees stay inert and mount hardening is fail-closed

- Status: Accepted
- Date: 2026-03-26

## Context

`adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed **where** the first imperfect-hardware B/C fallback executes:
attach and read-only mount authority stay on the host, while a disposable no-network jail consumes a projected tree instead of raw block-device nodes.
`adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` fixed **which filesystem families** the first cut may admit.

That still left one implementation-expensive ambiguity open:

> once the host has admitted and mounted the medium, what is that mounted tree allowed to *mean*?

If the archive leaves that vague, several bad outcomes stay live at once:

- the mounted tree quietly becomes a direct app-open or binary-exec surface,
- mount helpers or adapters silently relax hardening flags in the name of compatibility,
- side-effect launch metadata on the medium (`autorun.inf`, desktop launchers, similar artifacts) gets treated like ambient instructions instead of bytes,
- and B/C fall back toward ordinary automounter folklore even though the lane was already narrowed to storage-only, quarantine-first ingest.

The archive already has enough structure to make a smaller decision:

- `device.attach.*` already carries the reviewed storage lease,
- `mount.view` already models the projected read-only ingest tree,
- `content.import.plan` / `content.import.receipt` already model typed safe-open / sanitize / classify work,
- and the local fallback already depends on the host-mount + disposable-jail boundary rather than on raw device exposure or host-open convenience.

## Decision

1. **The admitted removable-media tree stays inert input, not a direct execution or host-open surface.**
   The mounted tree is for classification, scanning, sanitize/import, and offline-kit intake. It is **not** a direct application-launch, interpreter, or “just open it from the host” lane.

2. **The first local-fallback mount requires a fixed hardening tuple.**
   The reviewed host-side mount posture for this lane is:
   - read-only (`ro`)
   - `nodev`
   - `nosuid`
   - `noexec`
   - `nosymfollow`

3. **Mount hardening is fail-closed, not best-effort.**
   If the host-side helper / adapter for an admitted filesystem family cannot realize the reviewed hardening tuple for this lane, the lane denies the mount instead of silently dropping flags.

4. **Side-effect launch metadata on the medium is treated as bytes, not instructions.**
   `autorun.inf`, desktop autostart files, shell launchers, or similar artifacts found on the mounted tree do not gain special execution meaning in this lane.

5. **Any later viewing or execution must begin with an explicit later lane, not by reopening the mount.**
   In the first cut, the mounted tree feeds `content.import.plan` (or verified offline-kit intake) and the resulting outputs. It does not itself become a reviewed runtime source.

6. **The canonical first-cut examples now pin this posture explicitly.**
   The archive updates:
   - `spec/examples/device.attach.grant.removable-media-local-ingest.json`
   - `spec/examples/mount.view.removable-media-local-ingest.json`
   - `spec/examples/content.import.plan.removable-media-local-ingest.json`

## Consequences

- B and C keep a usable local fallback without quietly rebuilding ambient automount semantics.
- Support and UX surfaces can now explain denials cleanly: an admitted family can still fail because the reviewed inert-mount posture could not be realized.
- The archive stays honest that mount flags are **defense in depth around an already bounded lane**, not a replacement for the host-controlled mount authority plus disposable-jail ingest boundary.
- The first implementation target becomes narrower and more buildable: mount an admitted family with the fixed hardening tuple, project it into the disposable jail, run typed import work, and detach.

## What this ADR intentionally does not decide

This ADR does **not** settle:

- whether a later explicit lane may view some document classes directly from removable media,
- whether a later compatibility lane may allow narrower hardening tuples for specific filesystem adapters,
- whether image-in-file or archive-in-file traversal deserves a later typed lane,
- or how a future local authorization daemon / trusted-UI prompt should render these denials.
