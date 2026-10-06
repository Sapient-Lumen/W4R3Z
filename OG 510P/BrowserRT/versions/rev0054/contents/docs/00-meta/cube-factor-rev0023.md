# Cube factor rev0025 — browser-light means no hidden browser artifact dependency

Revision: rev0028

This audit/factor is intentionally small. Rev0022 said the broad release was browser-light, but the cube check surface had drifted toward expecting current browser proof artifacts. That creates a hidden process-cost hazard: a future session may think it is running a cheap cube check while accidentally needing several Chromium/CDP launches.

## Change

`tools/check_cube.py` now treats browser/CDP proof JSON as optional carried evidence. Browser source/docs/manifest surfaces remain checked, but current browser proof artifacts are not required by the broad release gate.

## Why this is correct

Browser slices remain available by explicit id or browser tier. They should be refreshed when the browser surface changes. They should not be silently required every time a Node-only storage or scheduler slice changes.

## Non-claims

- This factor does not weaken the browser proof tasks themselves.
- This factor does not claim current browser artifacts were refreshed in rev0025.
- This factor does not prove cross-browser behavior.

## Late factor: release estimates recalibrated to observed timings

During package validation the deep audit correctly rejected a release-estimate sum that had drifted above the long-run budget even though observed release runtime was much lower. Rev0023 therefore tightens the manifest estimates for cheap Node/fake-provider proofs rather than loosening the audit. This keeps future sessions honest: estimates should be living scheduling data, not stale pessimistic folklore.

The audit principle is unchanged: if release estimates grow, decompose or demote slices before broad validation becomes expensive again.
