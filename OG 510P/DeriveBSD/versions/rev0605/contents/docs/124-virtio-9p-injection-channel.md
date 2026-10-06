# virtio-9p (VirtFS) as a restricted host↔guest file channel (optional)

DeriveBSD’s baseline contract avoids host filesystem mounts into guests.
However, bhyve supports virtio-9p (“VirtFS”), which can be useful as a **policy-gated**, **read-only**, **non-secret** channel.

## Platform reality

- bhyve includes a virtio-9p device type.
  - bhyve(8): https://man.freebsd.org/bhyve%288%29
- virtio-9p support was upstreamed to bhyve (review trail).
  - FreeBSD review: D10335 (virtio-9p/VirtFS): https://reviews.freebsd.org/D10335
- FreeBSD guest support for mounting 9p shares has historically lagged; a kernel 9p filesystem and `virtio_p9fs` driver exist upstream.
  - dev-commits entry (9P filesystem added): https://lists.freebsd.org/archives/dev-commits-src-all/2024-June/042558.html
  - p9fs(4) man page: https://cocalc.com/github/freebsd/freebsd-src/blob/main/share/man/man4/p9fs.4
- Operationally, users still report guest-version gaps.
  - vm-bhyve issue: https://github.com/churchers/vm-bhyve/issues/552

## Allowed uses (DeriveBSD v1)

virtio-9p is **optional** and allowed only when *all* are true:
- policy explicitly enables it
- the share is **read-only**
- contents are **non-secret**
- share digest is recorded for explainability

Good fits:
- instance config (non-secret)
- an opt-in “debug view” of the artifact (read-only)

Not allowed:
- secrets delivery
- mutable host↔guest shared state

## Evidence objects

When used, the runtime report records:
- share label/name
- host path digest (tree hash)
- read-only flag
- policy decision id

## Why this stays optional

Even when the device exists, guest filesystem support and performance characteristics vary.
DeriveBSD must keep the metadata-disk + control-channel path as the baseline.

Last updated: 2026-02-23
