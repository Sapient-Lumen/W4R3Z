# Slot-based A/B updates and boot assessment (Android/ChromeOS lessons)

DeriveBSD’s default story is **ZFS boot environments + health-gated switching**.
It’s still worth stealing a specific operational lesson from Android/ChromeOS:

> Always keep a known-bootable system on disk while updating.

A/B systems make this mechanical with explicit **slots**:

- booted slot = active
- updated slot = inactive
- switch happens at reboot
- automatic rollback happens if boot assessment fails

## Why this matters for DeriveBSD

ZFS boot environments already provide the “two roots” property.
The extra lesson is the *discipline*:

- treat “next boot target” as a **staged commit**
- require an explicit **boot success signal** before marking it permanent
- make rollback automatic, not operator folklore

DeriveBSD already has the pieces:
- boot try counters: `docs/241-boot-try-counters-and-boot-assessment.md`
- health gates: `docs/112-health-gated-updates.md`
- rollback workflows: `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`

This doc exists to keep the mental model crisp and to justify the defaults.

## References

- Android A/B (seamless) system updates:
  https://source.android.com/docs/core/ota/ab
- ChromeOS update engine A/B overview:
  https://chromium.googlesource.com/aosp/platform/system/update_engine/+/upstream/README.md
- ChromiumOS Verified Boot design docs:
  https://www.chromium.org/chromium-os/chromiumos-design-docs/verified-boot/

Last updated: 2026-02-27r101
