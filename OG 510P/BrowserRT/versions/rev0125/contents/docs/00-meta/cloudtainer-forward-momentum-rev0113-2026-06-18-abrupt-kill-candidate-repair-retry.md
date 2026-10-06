# Cloudtainer forward momentum — rev0114 — abrupt-kill candidate repair retry

Current office remains rev0114 / OPFS Raw Composite AbortSignal.

## Product risk moved

The prior wedge proved that an unclosed partial OPFS content-addressed candidate was not silently accepted after a managed Chromium SIGKILL/relaunch. rev0114 adds the next repair invariant: the relaunch path reconstructs the intended full payload from the same deterministic recipe, writes it through the normal guarded OPFS storage-lane path, verifies and reads it by digest, deletes it, and proves it is absent after delete.

This closes a practical lifecycle gap: rejection alone can leave a namespace that is safe but not obviously reusable. The new proof requires safe reuse for the same digest through the public installed package boundary.

## Refactor/audit

Interrupted-candidate payload construction now lives in shared helpers used by both candidate creation and relaunch-side repair. The package-installed abrupt-kill probe and public API contract audit both check the repair/retry proof bits, so the behavior cannot silently become a one-off example.

## Non-claims

Managed Chromium only. No cross-browser claim, no organic quota or eviction survival claim, no fsync or power-loss durability claim, no arbitrary crash recovery claim, no browser-light production readiness claim, and no production readiness claim.
