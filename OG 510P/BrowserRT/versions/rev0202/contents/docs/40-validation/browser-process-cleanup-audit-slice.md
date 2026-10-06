# Browser process cleanup audit slice

Current revision: rev0060.

Task id: `facility:browser-process-cleanup-audit`.

This small release-tier audit scans the cloudtainer process table for BrowserRT-tagged managed Chromium/CDP processes that should have been terminated by browser proofs. It is a hygiene guard for long sessions where browser tests can fail or be interrupted.

## Claims checked

- `ps` is readable inside the cloudtainer.
- No live BrowserRT-tagged managed Chromium/CDP process remains after validation.
- The audit reports browser process samples without treating unrelated system browser processes as owned by this cube.

## Non-claims

This does not prove browser runtime semantics, OPFS durability, crash recovery, quota or eviction behavior, cross-browser conformance, or production lifecycle management. It is only a cloudtainer cleanup guard.
