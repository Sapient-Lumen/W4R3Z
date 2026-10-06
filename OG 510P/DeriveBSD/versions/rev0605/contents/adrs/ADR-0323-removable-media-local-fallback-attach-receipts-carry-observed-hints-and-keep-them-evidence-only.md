# ADR-0323: Removable-media local fallback attach receipts carry observed hints and keep them evidence-only

Date: 2026-03-28  
Status: Accepted

## Context

`ADR-0313` through `ADR-0322` already made the first honest host-local removable-media fallback for imperfect B/C hardware finite enough to implement:

- storage-only, session-scoped, quarantine-first,
- host-controlled `fstyp` admission and read-only mount,
- disposable no-network jail,
- inert mounted trees,
- physical root-pinned walk,
- one portable member-path grammar,
- path/kind/payload-first reviewed/import identity,
- single-selected-subject only,
- regular-file-only selected subjects in the first cut,
- and present-device-instance-only approval with fresh grant required after reattach.

One practical seam still remained half-open:
**what exactly should the first local-ingest `device.attach.receipt` record about the currently present medium, and how authoritative are those observations?**

Leaving that vague is expensive.
Implementations will either record too little to explain what was actually attached, or they will start treating serial/path/provider hints as if they were durable trust anchors.
That would quietly reopen the same remembered-device folklore that `ADR-0322` just rejected.

FreeBSD gives enough substrate to capture useful current-instance evidence without pretending continuity is solved:

- `devd.conf(5)` exposes USB attach/detach and VFS mount/unmount notifications.
- `usbconfig(8)` can identify the currently present USB device by `ugenX.Y` / unit+address and dump current descriptor/summary information.
- `diskinfo(8)` can surface the current disk ident and physical path.
- `camcontrol(8)` can print the device serial number for current storage hardware.

Those are good **current-presence hints**.
They are not a reason to let “same hints as last time” become auto-resume authority in the first buildable lane.
The first cut therefore needs one smaller evidence rule: capture a finite observed-hint bundle in the attach receipt, and mark it as evidence-only.

## Decision

For the first host-local removable-media ingest fallback described by `ADR-0313` through `ADR-0322`:

1. The canonical `device.attach.receipt` example for this lane must carry a finite **observed current-presence hint bundle** in `runtime.mapping.observed_hints`.
2. The first canonical bundle includes:
   - a current transport locator such as `ugenX.Y`,
   - the selected storage provider node,
   - and, when available, disk-ident / serial / physical-path hints.
3. The same receipt must explicitly mark those observations as **evidence-only current-presence hints**, not durable trust anchors.
4. Missing hints do not silently widen authority, and they do not force implementations to synthesize replacement identity.
5. Equality of observed hints across detach/reattach remains non-authoritative and must not auto-resume the prior grant.
6. Any future lane that wants stronger continuity semantics must return as a separate explicit RFC/ADR cut instead of widening this first fallback.

## Consequences

- The first removable-media fallback now says what support tooling and receipts should preserve for explanation and forensics.
- B/C implementations have a smaller coding target: record the current attach evidence, show it to the operator, and still require a fresh grant after detach.
- The archive no longer leaves room for one implementation to record nothing while another quietly builds a remembered-device trust system around serial/path hints.
- The current lane stays honest about uncertainty: hints help humans and receipts, but they are not durable authority.

## Alternatives considered

- **Record no current-instance hint bundle at all:** rejected because support and operator review need a concrete answer to “what was attached?”.
- **Treat serial/path/provider equality as durable continuity for the first cut:** rejected because it reintroduces remembered-device or auto-resume authority through the back door.
- **Design a richer durable hardware-identity subsystem now:** rejected because it is a bigger subsystem and belongs behind a later explicit RFC/ADR if we ever need it.

## Related

- `adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `adrs/ADR-0314-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `adrs/ADR-0315-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `adrs/ADR-0322-removable-media-local-fallback-approval-stays-present-device-instance-only-and-reattach-requires-fresh-grant.md`
- `docs/733-removable-media-local-fallback-attach-receipts-carry-observed-hints-and-keep-them-evidence-only.md`
