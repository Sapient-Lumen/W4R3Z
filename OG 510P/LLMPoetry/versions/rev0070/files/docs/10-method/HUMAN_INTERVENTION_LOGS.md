# Human intervention logs

Current policy: use summary-level human-intervention logs for drafts. Escalate to line-level logs only when a poem enters anthology/evidence consideration, when the human directly edits a line, or when a claim depends on exact intervention timing.

## Why summary-level now

The human owner indicated that future browsing will generally happen with LLM aid. Therefore the cube should prioritize compact, queryable, machine-readable records over heavy human-facing diff ceremonies.

## Minimum fields

- turn and revision
- human instruction or answer
- operator interpretation
- affected files or decisions
- whether line-level intervention occurred

`registries/human_intervention_log.json` is the canonical log.
