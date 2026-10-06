# Current removable-media local fallback FreeBSD backend plan

Last updated: 2026-06-04r536

`removable.media.local.freebsd.backend.plan` is the host-side bridge between the cloudtainer safe-capture proof and a real FreeBSD removable-media backend. It is intentionally a dry-run host plan in this archive cut: no real block device was mounted in the cloudtainer.

The planned host sequence is concrete: probe the device with `fstyp`, admit only a finite filesystem family set, create a private 0700 mountpoint, mount read-only with the FreeBSD generic options this cube is willing to emit, capture one selected regular file through the same dirfd/openat no-symlink semantics proven by `tools/removable_media_safe_capture.py`, commit the preserved capture to CAS, run `/sbin/umount`, close the device path, and only then launch the post-detach worker with preopened descriptors.

The audit correction is deliberate: `nodev` is retained only as the audit finding for the old overclaim, not as active desired mount inertness. The active emitted FreeBSD option tuple is `ro,nosuid,noexec,nosymfollow,untrusted`. The absence of device exposure is represented by worker invisibility to the mountpoint, no device or mount path in argv/env, an empty `devfs_visible_devices` list, and post-detach descriptor delivery.

exFAT stays adapter-gated. The plan names `mount.exfat` helper candidates but treats them as preinstalled, digest-pinned, and blocked for production until FUSE/helper behavior and post-mount read-only/noexec/nosuid/nosymfollow semantics are verified on an actual FreeBSD host. No package install or network fetch is allowed inside the local fallback lane.

Validation entry points:

- `tools/removable_media_local_freebsd_backend_plan.py --write`
- `tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
- `spec/removable.media.local.freebsd.backend.plan.schema.json`
- `spec/examples/removable.media.local.freebsd.backend.plan.json`
- `spec/examples/invalid/removable-media/freebsd-backend-plan/`

Active FreeBSD mount options emitted by this plan are `ro,nosuid,noexec,nosymfollow,untrusted`.
