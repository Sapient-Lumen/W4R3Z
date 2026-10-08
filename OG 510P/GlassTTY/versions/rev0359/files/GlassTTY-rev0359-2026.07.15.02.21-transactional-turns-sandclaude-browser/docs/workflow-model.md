# Workflow model

GlassTTY support should be described in terms of workflows, not only surfaces.

## Core workflow set

Every official surface should eventually report against the same minimum workflow set:

1. **surface-detect**
   - detect that the current tab is a supported surface
2. **receiver-resolve**
   - locate the active compose/interaction target
3. **composer-read**
   - read the current prompt draft
4. **composer-write**
   - write or replace prompt-draft text
5. **turn-submit**
   - submit the current turn
6. **generation-read**
   - detect whether the surface is currently generating, idle, blocked, errored, or unknown
7. **latest-turn-read**
   - read the latest assistant turn in a structured way
8. **support-capture**
   - emit a support bundle or equivalent evidence artifact

## Secondary workflows

These are valuable but not required for first experimental support:
- generation-stop
- turn-regenerate
- conversation-read
- conversation-list-read
- selection-read
- attachment-state-read
- attachment-add
- model-state-read
- export-read

## Workflow design rules

- A workflow should have a clear success condition.
- A workflow should have a known evidence output.
- A workflow should degrade honestly when a surface lacks enough stable cues.
- A workflow claim should be per surface and per browser lane.
- A workflow should use canonical keys from `docs/canon-keys.md`.

## Where the details live

Use `docs/workflow-catalog.md` for per-workflow:
- inputs and preconditions
- success signals
- degradation cases
- common failure classes
- state outputs
- evidence expectations

## Why workflow language matters

“Support ChatGPT” is not precise enough.
“ChatGPT supports `surface-detect`, `receiver-resolve`, `composer-write`, `turn-submit`, and `latest-turn-read` experimentally on `chromium-live`” is precise enough to guide implementation and QA.
