# Removable-media local fallback mounted trees stay inert and mount hardening is fail-closed

**Tier:** B (Implementation floor)  
**Profiles:** B, C  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Plan→Apply→Receipt, Registry→Diff→Gate

`docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md` already fixed *where* the first host-local fallback executes.
`docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md` fixed *which filesystem families* the first cut may admit.

This page fixes the next smaller but still costly choice:

> once the host has admitted and mounted the medium, what is that mounted tree allowed to *mean*?

The answer is intentionally narrow:

> **the mounted tree stays inert input only, the host must realize the fixed hardening tuple `ro,nodev,nosuid,noexec,nosymfollow`, and the lane fails closed instead of silently relaxing into direct open/exec convenience.**

See also:
- ADR: `adrs/ADR-0316-removable-media-local-fallback-mounted-trees-stay-inert-and-mount-hardening-is-fail-closed.md`
- previous boundaries: `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`, `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- workflow doc: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- workstation posture: `docs/458-removable-media-and-usb-posture-by-profile.md`
- origin/import lane: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/605-workstation-file-open-import-and-bounded-document-roles.md`

## Accepted boundary

### 1) The mounted tree is inert input, not a runtime source

The first local-fallback mount is there to feed typed import work:

- classify the mounted tree,
- scan/sanitize/import selected content,
- verify offline kits,
- receipt origin and quarantine state,
- then detach.

It is **not** the reviewed lane for:

- directly executing binaries from the removable medium,
- directly host-opening documents from the removable mount,
- treating the removable tree as a library/interpreter/runtime source,
- or reviving ambient automount semantics under more careful wording.

So the mounted tree is an **input surface**, not a general-use namespace.

### 2) The host-side mount posture is fixed and small

The first local-fallback lane now requires the host to realize this hardening tuple when it mounts an admitted family:

- `ro`
- `nodev`
- `nosuid`
- `noexec`
- `nosymfollow`

This tuple is intentionally paired with the already-decided execution boundary:

- mount authority stays on the host,
- the ingest worker is still a disposable no-network jail,
- `devfs.view.plan` stays block-empty there,
- and the mounted tree is projected read-only through `mount.view`.

Mount hardening is therefore **supporting posture around the already bounded lane**, not a substitute for that lane.

### 3) If the hardening tuple cannot be realized, the lane denies

The archive chooses **fail closed** over compatibility folklore.
That means an admitted filesystem family may still be denied in this lane if the concrete host-side adapter/helper cannot realize the reviewed inert-mount posture.

So the first cut is not:

- “mount best effort and drop whichever flags do not work”,
- “mount it on the host and trust users not to open things directly”,
- or “it is fine because the medium was already on the allowlist”.

Instead it is:

- admit the family,
- require the hardening tuple,
- deny if that tuple cannot be realized,
- then feed only the disposable ingest path.

### 4) Side-effect launch metadata stays bytes only

The first local-fallback lane does not give special meaning to medium-provided launch hints such as:

- `autorun.inf`
- desktop autostart launchers
- shell wrappers / helper launch files
- similar side-effect metadata discovered in the mounted tree

Those artifacts are just content.
They may be classified, scanned, sanitized, or copied as evidence, but they do not become ambient instructions in this lane.

### 5) Later view/exec needs a later explicit lane

If DeriveBSD later decides that some document classes or signed media deserve a narrower direct-view lane, that should be a later explicit RFC/ADR decision.
It should **not** arrive by quietly teaching the removable-media mount to behave like an ordinary local filesystem again.

So the first cut remains:

- host mount with the reviewed hardening tuple,
- read-only projection into the disposable jail,
- typed `content.import.plan` / `content.import.receipt` work,
- and explicit later transfer/promotion of resulting outputs.

## Canonical first-cut example stack

The canonical stack now says the inertness decision literally:

- `spec/examples/device.attach.grant.removable-media-local-ingest.json`
- `spec/examples/devfs.view.plan.removable-media-local-ingest.json`
- `spec/examples/mount.view.removable-media-local-ingest.json`
- `spec/examples/content.import.plan.removable-media-local-ingest.json`

Together they now pin:

- the fixed host-side mount-hardening tuple,
- fail-closed posture if that tuple cannot be realized,
- inert `/ingest` semantics,
- and no direct host-open / exec from the mounted tree.

## Why this cut is worth making now

Without this decision, the archive still pays a repeated implementation tax:

- coding cannot tell whether `/ingest` is just an input root or also a convenience runtime surface,
- support cannot explain why an admitted medium was still denied,
- workstation pressure reintroduces “just open it from the stick once” folklore,
- and compliance/forensics lose a crisp answer for why removable media stays bounded even on imperfect hardware.

This cut keeps B/C viable while still protecting A/D from baseline drift.
It is small enough to implement and small enough to explain.

## Related docs

- `docs/723-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md`
- `docs/724-removable-media-local-fallback-first-cut-keeps-mount-authority-host-controlled-and-the-ingest-lane-disposable-jail-shaped.md`
- `docs/725-removable-media-local-fallback-fstyp-probed-filesystem-admission-stays-finite.md`
- `docs/278-device-grants-and-devfs-rulesets.md`
- `docs/279-usb-quarantine-and-removable-media-workflow.md`
- `docs/458-removable-media-and-usb-posture-by-profile.md`

Last updated: 2026-03-26r457
