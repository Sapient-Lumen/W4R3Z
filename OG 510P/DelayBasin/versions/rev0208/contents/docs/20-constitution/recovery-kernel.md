# Recovery kernel

This surface defines the **minimum recovery route** when DelayBasin suspects drift, corruption, stale reopen, or procedurally invalid progress.

## Legitimacy predicate

DelayBasin should treat itself as back in a legitimate continuation state only when all of the following hold:

- latest archive revision reopened as source of truth,
- `context-pack.json` regenerated from repo state,
- `make lint` passes,
- canon vs quarantine remains explicit,
- current revision can name its certified move classes,
- anything with unclear status has been quarantined or demoted rather than quietly preserved as canon.

## Kernel surfaces

- `START_HERE.md`
- `docs/00-meta/trajectory-map.md`
- `docs/00-meta/llm-runbook.md`
- `context-pack.json`
- `docs/20-constitution/claim-registry.md`
- `docs/20-constitution/open-question-registry.md`
- `docs/20-constitution/move-registry.md`
- `docs/50-promptcraft/prompt-pairs.md`
- `docs/90-quarantine/wild-speculations-2026-03-08.md`

## Recovery route

1. Reopen the kernel surfaces.
2. Regenerate bounded handoff state.
3. Run `make lint`.
4. If the issue was semantic or status drift, quarantine or demote the affected material explicitly.
5. Resume normal revision only after the legitimacy predicate is true again.

## Notes

- This is not a theorem of self-stabilization.
- It is a compact **recovery discipline** for a method archive.
- The kernel should stay small. If it becomes too large to reopen quickly, it has failed.
