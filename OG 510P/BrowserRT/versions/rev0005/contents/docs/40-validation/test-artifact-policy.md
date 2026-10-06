# Test artifact policy

Revision: rev0005.

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
