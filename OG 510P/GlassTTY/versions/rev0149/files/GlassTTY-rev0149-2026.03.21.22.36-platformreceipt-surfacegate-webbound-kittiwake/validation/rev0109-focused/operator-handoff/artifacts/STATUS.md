# Status update — rev0109

- Added interrupted browser-launch forensics to `scripts/e2e-fixturelab.py`: the smoke report now preserves an in-flight `browser_attempt_inflight` snapshot and finalizes interrupted launches into durable `browser_attempts[]` entries instead of losing the most useful launch evidence.
- Extended `scripts/e2e-fixturelab-capture.py` summaries/history to track termination state, interrupted browser-attempt counts, the last attempted browser mode, and whether a launch was still in flight when the run ended.
- Refreshed archive luxury for future sessions with a new handoff note, research notes, focused validation outputs, readiness/operator-handoff captures, and a clearer memory/worklog trail around what was actually proven here.

## Why this matters

GlassTTY's remaining uncertainty is still concentrated in real browser launches. In this container, the highest-leverage next improvement was not another speculative adapter tweak but better evidence preservation when browser startup gets cut off. Future sessions now inherit a real interrupted-launch narrative instead of a vague failed smoke summary.

## Honest state

- Focused e2e-forensics tests passed locally in this container.
- `./scripts/smoke.sh` passed again after the report/capture changes.
- A fresh successful live browser/native-messaging round-trip is still **not** proven here.
- The honest live-testing record for this session is:
  - one pre-fix live attempt reached browser launch and was externally terminated during that phase;
  - one post-fix rerun caused the container runtime itself to reset during browser launch, so there is no trustworthy new browser-proof artifact from that rerun.
