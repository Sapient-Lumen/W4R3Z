# Rev0956 research notes

Reviewed against the current official pages on 2026-07-31.

## Runtime readiness versus health

systemd's notification protocol uses `READY=1` for startup completion and
`STATUS=` for free-form runtime state. AnonSync can truthfully update runtime
status after a later integrity alarm, but rev0956 does not claim to retract the
manager's historical startup-ready transition.

- <https://www.freedesktop.org/software/systemd/man/sd_notify.html>
- <https://www.freedesktop.org/software/systemd/man/systemd.service.html>

A future service-manager integration could add a watchdog or a separate health
consumer. It should not reinterpret one-time startup readiness as a continuously
revocable storage-health bit.

## Current status and recent errors are different products

Syncthing exposes current runtime status separately from a recent-error list.
Rev0956 takes the smallest compatible architectural step: the active alarm is
current authority state, while one recovered exact event is bounded history. It
avoids creating another persistent database before retention, privacy, and
redaction policy exist.

- <https://docs.syncthing.net/rest/system-status-get.html>
- <https://docs.syncthing.net/rest/system-error-get.html>

## Scrub state is ordinary operator state

Btrfs and OpenZFS expose scrub progress and summarized results. Their ability to
repair from redundant filesystem copies does not transfer to AnonSync's current
sole-copy content-addressed payload store, but their operator model reinforces
that integrity work should remain observable after completion.

- <https://btrfs.readthedocs.io/en/latest/btrfs-scrub.html>
- <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-scrub.8.html>
- <https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html>

## Speculation

The next safe operator slice is likely an explicit owner-only `recheck` request
that advances the retry deadline without granting authority. A rooted payload
wake could reduce repair-detection latency, but metadata events alone must never
clear an alarm. Quarantine and remote restore should wait until version
retention, durable in-flight/reachability pins, peer availability, and crash-safe
garbage collection are designed as one policy.
