# AppVM storage: template + private + volatile (+ optional portable home areas)

The fastest way for “desktop compartments” to become insecure is letting persistence be ad-hoc.
Qubes’ template model stays usable because it makes the storage layout *predictable*:
- a shared immutable base
- a small persistent “private” disk for user state
- an explicitly disposable “volatile” disk for overlays and scratch

DeriveBSD already wants template microVMs (`docs/129-template-microvms-and-disposables.md`).
This doc tightens the **desktop AppVM** storage contract so persistence and sharing are reviewable.

## The model

For template-based AppVMs, define three storage classes:

1) **Template root (immutable)**
- read-only root filesystem supplied by a template image
- updated centrally by updating the template artifact

2) **Private (persistent)**
- per-AppVM writable storage
- defaults: `/home`, app configs, per-app secrets *references* (not raw secrets)
- snapshotted/rollbackable as part of the AppVM’s lifecycle

3) **Volatile (disposable)**
- overlay changes to root for the session
- scratch space and swap
- destroyed on AppVM shutdown (or on policy-triggered “scrub”)

Optional fourth:

4) **Portable home area (user-scoped)**
- a user’s portable home container (`docs/269-portable-home-areas-and-user-records.md`)
- mounted into an AppVM only under explicit policy (often via a Documents portal instead)

## Why DeriveBSD should standardize this early

- **Blast radius clarity:** “did this persist?” is answerable.
- **Centralized patching:** template updates don’t require touching private disks.
- **Disposables become cheap:** disposable AppVMs simply omit the private disk.
- **Forensics and support:** support bundles can include *only* private state digests, not session noise.

## Mapping to DeriveBSD artifacts

Extend the AppVM artifact target (`docs/268-desktop-appvms-and-portalized-apps.md`) so the runtime manifest declares:
- `template_root_digest` (what immutable base is used)
- `private_storage`:
  - type: `zfs-dataset` | `qcow2` | `raw`
  - size/quotas
  - snapshot policy
- `volatile_storage`:
  - size
  - wipe policy
- `mount_plan`:
  - where `/home` comes from by default
  - whether `/usr/local` is writable (recommended: private)

Evidence objects (minimal set):
- `appvm.storage.plan` (declares the partitioning contract)
- `appvm.storage.receipt` (what was actually attached at runtime)

## Default policy suggestions

- **Template-based AppVM (default for apps):**
  - persistent private: yes
  - volatile overlay: yes
  - no access to user-wide home area by default

- **Disposable AppVM (default for “open untrusted”):**
  - persistent private: no
  - volatile overlay: yes
  - file ingress only via portals / sanitization flow

- **Profiled disposable (usability compromise):**
  - persistent private: “seeded” from a signed seed artifact (fonts, locale, cert bundle)
  - volatile overlay: yes

## Interaction with portals

Portals remain the safe sharing boundary:
- Documents portal: pass explicit file handles into the AppVM
- Clipboard/drag&drop: explicit export events
- Sanitization portal: generate “safe outputs” outside the AppVM in a disposable conversion sandbox

If a user insists on mounting a portable home area inside an AppVM, require:
- explicit consent UX
- time-bounded lease
- receipts + export logs

## References

- Qubes template implementation (private + volatile disks; root is read-only): https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html
- Qubes templates overview (centralized updates; per-VM private storage): https://doc.qubes-os.org/en/latest/user/templates/templates.html

See also:
- Template microVMs + disposables: `docs/129-template-microvms-and-disposables.md`
- Desktop AppVMs + portal stance: `docs/268-desktop-appvms-and-portalized-apps.md`
- Portable home areas: `docs/269-portable-home-areas-and-user-records.md`

Last updated: 2026-02-25
