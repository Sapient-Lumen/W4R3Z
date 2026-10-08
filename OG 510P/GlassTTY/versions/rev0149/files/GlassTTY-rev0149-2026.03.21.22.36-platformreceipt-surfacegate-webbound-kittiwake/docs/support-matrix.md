# Support matrix

This file defines the support matrix the repo should grow into.

## Axes

### Surfaces
- Claude
- ChatGPT
- Google AI Studio
- Grok
- Kimi
- Z.ai

### Core workflows
- surface-detect
- receiver-resolve
- composer-read
- composer-write
- turn-submit
- generation-read
- latest-turn-read
- support-capture

### Browser lanes
- chromium-live
- chromium-managed-profile
- playwright-persistent
- cdp-lab
- fixture-replay

## Source of truth

The support matrix should roll up from:
- `docs/support-records/*.md`
- named evidence refs
- release-gate artifacts

The matrix is a summary view, not a substitute for support records.

## Reporting rule

Every row in the support matrix should carry:
- tier
- last verified date
- evidence ref or evidence posture
- known caveat summary
- lane scope

## Why this exists

The support matrix prevents the repo from collapsing all claims into:
- “it worked once”
- “Claude works, others later”
- “we think it should be fine”

It forces the project to talk in specific, inspectable claims.
