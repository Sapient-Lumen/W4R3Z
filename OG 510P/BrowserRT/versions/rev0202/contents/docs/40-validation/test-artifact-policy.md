# Test artifact policy

Revision: rev0028.

BrowserRT tests should leave enough evidence to diagnose failures without rerun
roulette.

## Current artifacts

- proof witness;
- test harness timing report;
- timing history;
- timing analysis;
- surface inventory report;
- turn-start report;
- turn smoke report;
- release manifest.

## Future browser artifacts

- console log;
- screenshot on failure;
- CDP trace when useful;
- capability report;
- local server log;
- cleanup report.

Artifacts must be small enough to stay inside the cube unless a future revision
adds explicit external artifact policy, which is currently out of scope.

## Rev0022 current-artifact retention amendment

Generated proof artifacts should be current-prefix by default in the packaged cube. Historical evidence belongs in `CHANGELOG.md`, historical docs, or a deliberately named archive surface. Do not leave stale `REV####` validation JSON files in the active artifact set unless they are explicitly marked as historical and the foundation audit allows them.

Reason: future sessions often inspect whatever JSON artifact is nearby. Stale artifacts can look like current truth and cause overclaims.
