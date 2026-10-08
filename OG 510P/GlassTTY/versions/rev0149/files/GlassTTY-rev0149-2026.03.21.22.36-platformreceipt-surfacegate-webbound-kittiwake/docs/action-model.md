# Action model

GlassTTY needs a stable action vocabulary before agent mode grows.

## Core actions

- `focus-surface`
- `resolve-receiver`
- `read-composer`
- `write-composer`
- `append-composer`
- `replace-composer`
- `submit-turn`
- `read-latest-turn`
- `read-generation-state`
- `capture-support-bundle`

## Action plan shape

A future action plan should be able to say:
- what action is intended
- which surface/session/receiver it targets
- why it is being attempted
- whether approval is required
- what evidence should be emitted
- what success looks like
- what stop conditions apply

## Action outcome shape

Every meaningful action should emit an outcome with:
- identity of the attempted action
- target surface/session/receiver
- attempt timestamp
- result classification: `success`, `noop`, `degraded-success`, `failure`, `blocked`, `aborted`
- reason code
- linked evidence artifacts
- suggested next action when known

## Why this matters

Without a stable action/outcome model:
- agent work becomes hard to audit
- support evidence stays noisy
- future implementers keep inventing incompatible result vocabularies
