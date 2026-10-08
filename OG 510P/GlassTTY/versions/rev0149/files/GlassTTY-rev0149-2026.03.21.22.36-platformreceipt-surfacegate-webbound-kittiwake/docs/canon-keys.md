# Canon keys

This file locks the main vocabulary used across the repo.

## Surface keys

- `claude`
- `chatgpt`
- `aistudio`
- `grok`
- `kimi`
- `zai`

## Browser-lane keys

- `chromium-live` — real Chromium/Chrome profile lane
- `chromium-managed-profile` — managed GlassTTY profile lane
- `playwright-persistent` — Playwright persistent-context lane
- `cdp-lab` — direct CDP inspection or lab lane
- `fixture-replay` — offline or quasi-offline replay against captured fixtures

## Workflow keys

Core:
- `surface-detect`
- `receiver-resolve`
- `composer-read`
- `composer-write`
- `turn-submit`
- `generation-read`
- `latest-turn-read`
- `support-capture`

Secondary:
- `generation-stop`
- `turn-regenerate`
- `conversation-read`
- `conversation-list-read`
- `selection-read`
- `attachment-state-read`
- `attachment-add`
- `model-state-read`
- `export-read`

## State-family keys

- `surface`
- `session`
- `receiver`
- `composer`
- `generation`
- `conversation`
- `turn`
- `selection`
- `diagnostics`
- `support`
- `evidence`
- `action_outcome`

## Support tiers

- `unsupported`
- `investigated`
- `experimental`
- `provisional`
- `supported`

## Drift severities

- `informational`
- `low-risk`
- `degraded`
- `blocking`
- `unknown`

## Artifact kinds

- `state-snapshot`
- `probe-capture`
- `fixture-capture`
- `smoke-run`
- `support-bundle`
- `workflow-proof`
- `operator-handoff`
- `operator-attempt`
- `comparison-bundle`
- `release-gate-artifact`
- `drift-report`
- `support-record`
- `support-update`
- `execution-report`
- `approval-record`

## Agent modes

- `human-piloted`
- `assisted`
- `approval-required-agent`
- `bounded-autonomous-agent`

## Action kinds

- `state-read`
- `composer-write`
- `turn-submit`
- `generation-stop`
- `support-capture`
- `navigation-open`
- `selection-read`
- `conversation-read`
- `attachment-add`

## Usage rule

Prefer these exact keys in docs, support records, ledgers, and future schemas. If a new key is needed, add it here deliberately instead of inventing synonyms in passing.
