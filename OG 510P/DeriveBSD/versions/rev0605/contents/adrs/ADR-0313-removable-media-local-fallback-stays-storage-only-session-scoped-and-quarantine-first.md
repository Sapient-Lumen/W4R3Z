# ADR-0313: Removable-media local fallback stays storage-only, session-scoped, and quarantine-first

- Status: Accepted
- Date: 2026-03-25

## Context

`adrs/ADR-0048-removable-media-and-usb-posture-by-profile.md` already fixed the product-shape default:
DeriveBSD is quarantine-first for removable media, never ambient-automounts it into the most trusted plane, and prefers device domains where hardware supports them.

That large decision intentionally left one implementation seam open in `docs/266-open-questions-and-risk-register.md`:

> what does the BSD-native local authorization fallback actually look like when hardware cannot isolate controllers cleanly?

Without a narrower answer, the archive still has a dangerous ambiguity:

- profile **B** can quietly slide from “device-domain-required-when-supported” into host-local USB convenience that weakens the trusted UI / HID boundary,
- profile **C** can quietly treat “fallback” as a synonym for ambient automount,
- integrated USB/HID/network/debug gadgets can sneak through the same fallback as if they were just another thumb drive,
- and implementation work cannot tell whether it is building a small storage-ingest path or a general raw-device passthrough escape hatch.

The archive already has enough existing pieces to close this seam without inventing a new subsystem:

- FreeBSD `devd` / `devd.conf` can detect attach and detach events and trigger explicit host-side handling.
- FreeBSD `devfs` rules and jails already provide a small way to render per-jail device visibility.
- `device.profile`, `device.attach.grant`, `device.attach.receipt`, `device.detach.receipt`, `devfs.view.plan`, and `content.import.receipt` already exist as the right typed nouns.
- `docs/207-input-authority-secure-attention-and-hid-risk.md` already says raw HID is special-danger and must not be treated as ordinary convenience plumbing.

What was missing was one explicit boundary for the fallback lane itself.

## Decision

1. **The local removable-media fallback is only for storage-class removable media.**
   It is not a generic “USB fallback.”
   The first allowed fallback scope is limited to block-storage shaped ingest/export workflows.

2. **The fallback is session-scoped, not remembered ambient authority.**
   Each use requires a fresh explicit host-local authorization and a fresh `device.attach.grant` / receipt chain.
   Long-lived “always allow this USB device on this machine” posture is out of bounds for this lane.

3. **The fallback remains quarantine-first and read-only-first.**
   The first host-local implementation must attach the selected storage device or partition only into a disposable ingest lane, prefer read-only mount semantics, and route ordinary content through sanitize/import or verified-kit ingest rather than mounting the media directly into the trusted host UI plane.

4. **The fallback compiles to existing typed artifacts, not a new ambient automount helper.**
   The minimal implementation stack is:
   - `device.profile` classification,
   - trusted-UI or explicit local-admin authorization,
   - `device.attach.grant` + `device.attach.receipt`,
   - a minimal `devfs.view.plan` for the disposable ingest jail/lane,
   - `content.import.receipt` or the existing verified offline-ingest path,
   - `device.detach.receipt` on session end.

5. **Raw HID and non-storage device classes are out of this fallback lane.**
   Keyboard, mouse, composite HID, network dongles, serial/debug adapters, webcams, microphones, smart-card/FIDO devices, and generic USB passthrough stay on stricter lanes:
   device domains, dedicated brokers/adapters, or future RFC work.

6. **Profile consequences are now explicit:**
   - **B (`workstation`)** may use this narrow storage-only fallback when hardware lacks clean controller isolation, but only without weakening host-owned HID / trusted-UI authority.
   - **C (`general_os`)** may use the same narrow fallback as its explicit compatibility path.
   - **A (`fleet_host`)** does not gain a normal local-media convenience path from this ADR.
   - **D (`appliance_factory`)** keeps `device-domain-or-ingest-station`; this ADR does not turn production/factory ingest into ordinary host-local attach.

## Consequences

- The archive now has one honest answer for “best-effort viable without forks” on imperfect hardware: a small storage-ingest fallback, not general USB convenience.
- Workstation viability improves without reopening ambient HID or trusted-host automount.
- Implementation work can target a concrete first cut using existing FreeBSD/BSD primitives and existing DeriveBSD artifacts.
- Integrated-device handling remains open, but the dangerous storage-vs-everything-else ambiguity is gone.

## What this ADR intentionally does not decide

This ADR does **not** settle:

- the final trusted-UI prompt wording,
- whether the disposable ingest lane is a jail, microVM, or both per profile,
- the exact partition-vs-whole-device attachment policy for every filesystem type,
- integrated Bluetooth/FIDO/smart-card handling,
- or the final remembered-policy model for non-storage device families.

Those remain narrower follow-on decisions.

## Why this is the smallest useful hard decision

This ADR does not invent a new device manager.
It only closes the implementation-blocking loophole between “prefer device domains” and “fallback to local policy” by saying exactly what the fallback is allowed to be:

- storage only,
- explicit,
- session-scoped,
- quarantine-first,
- read-only-first,
- and typed in the existing evidence vocabulary.
