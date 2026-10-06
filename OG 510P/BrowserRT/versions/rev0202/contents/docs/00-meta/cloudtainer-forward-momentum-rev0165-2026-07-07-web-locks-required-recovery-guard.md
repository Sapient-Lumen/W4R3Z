# Rev0165 forward momentum — Web Locks required recovery guard

Linked revision rev0165 keeps current runtime office `rev0125` / `0.0.125`. This pass deliberately avoids another registry-only expansion and hardens a runnable consumer seam.

## Risk taken

The next brittle edge was the shared-browser-local OPFS path when Web Locks are required but unavailable. Before this pass, `opfsWebLockGuardedBlockStoreWithPosture()` failed before mutation, but the package consumer did not get the same structured recovery payload used for quota/admission failures. That made the safe next action less copyable.

## Change

- `src/browserrt.mjs` now attaches `createBrowserStorageRecoveryGuidance()` to the `BRT_BROWSER_WEB_LOCKS_REQUIRED` rejection before any OPFS posture/store mutation.
- The error detail carries `preMutationRejected: true`, `mutationAttempted: false`, category `coordination-unavailable`, phase `coordination-admission`, and action `provide-web-locks-or-explicit-single-owner-fallback`.
- `tools/package_installed_consumer_smoke_probe.mjs` proves the behavior from a locally installed `browserrt` tarball and package-root import.
- `tools/browser_storage_posture_contract_audit.mjs` now fails if the Web Locks required branch drops recovery guidance or the installed smoke stops proving it.

## Audit/refactor note

The browser-storage posture audit still carried an obsolete installed-runtime method-count sentinel (`109`) while the package-installed smoke and support-bundle audit already expected `113`. Rev0165 corrects that drift while adding the new recovery-path assertion.

## Non-claims

No runtime promotion, package publication, semver change, Web Lock availability guarantee, hidden single-owner fallback authorization, OPFS quota reservation, eviction-survival proof, Service Worker lifetime guarantee, Web Lock fairness guarantee, or cross-browser claim.
