# Flake and chaos policy

Revision: rev0028.

BrowserRT will eventually need tests that intentionally crash workers, cancel
jobs, corrupt blocks, simulate quota pressure, and exercise browser/GPU loss.
Those tests are valuable only if they do not poison the release tier.

## Flake states

- `none`: normal test, expected to pass deterministically.
- `suspected`: a failure has been seen; keep it visible and narrow the slice.
- `quarantined`: temporarily excluded from normal runs with an expiry revision
  and reason in `test/quarantine.json`.

## Retry rule

Retries may classify a failure. They must not convert a flaky failure into a
silent release pass without trace evidence.

## Chaos rule

Chaos tests belong in their own tier until they are small, bounded, and leave
clear artifacts. A chaos test without cleanup is not a test; it is a state leak.
