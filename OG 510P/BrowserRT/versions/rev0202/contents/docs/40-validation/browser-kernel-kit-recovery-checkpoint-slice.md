# Browser Kernel Kit recovery checkpoint slice

Revision: rev0107

The browser-heavy proof `browser:kernel-kit-recovery-checkpoint-proof` aggregates three managed Chromium probes instead of duplicating their browser choreography:

1. `browser_opfs_abrupt_kill_boundary_probe.mjs` launches a managed profile/origin, writes acknowledged OPFS blocks, interrupts an in-flight write by killing the browser process, relaunches on the same profile/origin, and verifies that acknowledged blocks remain readable while the interrupted write is absent, complete-valid, or rejected by checksum/read validation rather than silently accepted as corrupt data.
2. `browser_opfs_block_store_open_failure_recovery_probe.mjs` injects transient `navigator.storage.getDirectory` failures, verifies root-open retry recovery, performs a later write/read, and proves the guarded Web Locks path releases/drains after the failure boundary.
3. `browser_opfs_web_lock_unsettled_orphan_review_probe.mjs` imports an unsettled timed-out guarded OPFS operation, verifies that recovery stays blocked, rejects unsafe/stale/scope-overridden finalization, then requires a reviewed/fingerprint-bound orphan finalization plus fresh late-failure clearance before accepting and verifying more work.

The aggregate checkpoint records compact proof booleans only. It is intentionally browser-heavy because process kill/relaunch, OPFS profile reuse, transient browser storage failure behavior, and real OPFS/Web Locks orphan cleanup cannot be represented honestly by a release-light unit test.

This proof does not claim crash durability, fsync safety, power-loss safety, automatic orphan cleanup, eviction survival, persistent-storage retention, abandoned-lock recovery, or cross-browser behavior.

This is not production recovery evidence; it is bounded managed-Chromium evidence only.

The exact SIGKILL, open failure, and reviewed orphan/fingerprint phrases are preserved so audits can distinguish process interruption, transient OPFS open failure retry, and operator-gated orphan cleanup.
