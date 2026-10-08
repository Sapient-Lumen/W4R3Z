# LLM ops

This repo is designed to survive multi-session work by humans and LLMs.

## First read order for a new session

1. `README.md`
2. `STATUS.md`
3. `ROADMAP.md`
4. `TASKS.md`
5. `TASK_QUEUE.md`
6. `DECISIONS.md`
7. `PROJECT_MAP.md`
8. `docs/repo-canon.md`
9. `docs/canon-keys.md`
10. `docs/workflow-model.md`
11. `docs/workflow-catalog.md`
12. `docs/state-api.md`
13. `docs/state-contracts.md`
14. `docs/adapter-model.md`
15. `docs/support-truth.md`
16. `docs/support-record-template.md`
17. `docs/drift-program.md`
18. `docs/evidence-and-ledgers.md`
19. `docs/implementation-program.md`
20. `docs/repo-transition-plan.md`

Only after that should a new session mine historical handoff docs for nuance.

## How to speak precisely

Always distinguish:
- implemented
- evidenced
- designed
- planned
- speculative

## What an LLM should preserve

When updating docs or plans, preserve:
- official surfaces
- workflow vocabulary
- state-family vocabulary
- support-tier vocabulary
- evidence-family vocabulary
- agent-policy language
- canonical keys

Avoid replacing those shared terms with one-off prose.

## What to leave behind after a strategic session

Prefer updating:
- top-level canon
- canonical design docs
- decisions
- support-record template or support records when support truth changed
- changelog
- one handoff summary

Do not leave major direction changes only in a worklog or handoff.

## What to leave behind after an implementation session

Prefer preserving:
- evidence bundle
- support-record delta
- workflow/support truth delta
- clear next-action recommendation
- changed assumptions or new risks

## Future rule

As GlassTTY becomes more agent-capable, LLM sessions should also preserve:
- action-plan changes
- policy changes
- stop-condition changes
- support-tier implications
