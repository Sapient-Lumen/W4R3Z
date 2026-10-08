# rev0022 persistent-lane notes

## What was proven

- `scripts/doctor.py --pretty` now exposes the Playwright launch strategy directly.
- In this container, Playwright is installed but there is no bundled Chromium cache under the usual Linux locations.
- The current fallback launch strategy would therefore be `system-executable` via `/usr/bin/chromium`.

## What was not proven

- No successful live Playwright persistent-context browser proof was captured in this revision.
- No successful native-host/socket round-trip was captured in this revision.

## Why this still matters

The launch-strategy ambiguity itself was blocking honest progress. rev0022 converts that ambiguity into explicit machine-readable evidence so future sessions can tell whether a failed Playwright run is a missing browser bundle problem or a deeper Chromium/native-messaging problem.
