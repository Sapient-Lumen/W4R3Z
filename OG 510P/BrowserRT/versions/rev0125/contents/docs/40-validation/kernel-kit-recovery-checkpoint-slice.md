# Kernel Kit recovery checkpoint slice

Revision: rev0107

This slice makes recovery after interruption visible in the Kernel Kit path without turning it into a production crash-recovery claim.

The checkpoint now binds three previously separated browser-heavy boundaries into one support-bundle/lifecycle row:

- abrupt managed-Chromium kill and restart over the same origin/profile, where acknowledged OPFS blocks are re-read after relaunch and an interrupted write is not silently accepted as corrupt state;
- transient OPFS root/open failure retry, where the root promise resets, a later open succeeds, and the guarded Web Locks storage path drains after retry;
- reviewed unsettled-timeout orphan cleanup, where imported unsettled provider work blocks recovery until a fingerprint-bound review finalizes the orphan, a fresh review clears the resulting late-failure quarantine, and later guarded writes verify again.

Release-light support bundles carry these rows as explicitly deferred until browser-heavy evidence is sealed. Synthetic release-light input can exercise the observed state, but the browser-heavy command remains the source of truth for actual managed-Chromium interruption and orphan-review behavior.

Required non-claims stay visible:

- No production crash-recovery claim.
- No OPFS fsync durability claim.
- No power-loss durability claim.
- No quota or eviction survival claim.
- No automatic orphan cleanup or abandoned-lock recovery claim.
- No cross-browser recovery conformance claim.

This is not production recovery evidence; it is a bounded release/browser checkpoint.

The browser-heavy aggregate is expected to preserve the exact SIGKILL boundary language from the abrupt-kill probe and the reviewed orphan/fingerprint language from the unsettled-orphan review proof.
