# Session deep audit — rev0302

Priority chosen: axis hygiene and public-finance cube compression.

Rev0301 ended the actor-accountability placeholder phase. The next practical risk was that the cube still allowed valid-looking but semantically weak axes: `new_calibration_file`, `unclassified_anti_pattern`, and `not_remedy_specific`. These are process artifacts, not substantive routing facts.

## Work performed

- Audited all 155 route records for blocked placeholder axes and generic public-finance sentinels.
- Refactored 66 review triggers out of `new_calibration_file`.
- Refactored 41 public-finance-core records so remedies, channels, markets, and burden mechanics are concrete.
- Added a standalone axis-hygiene audit and wired it into release validation.
- Regenerated declared axis values directly from live route usage so unused vocabulary no longer silently persists.

## Validation expectation

`make audit`, `tools/check_archive.py .`, `make package`, and a fresh extraction check should pass.
