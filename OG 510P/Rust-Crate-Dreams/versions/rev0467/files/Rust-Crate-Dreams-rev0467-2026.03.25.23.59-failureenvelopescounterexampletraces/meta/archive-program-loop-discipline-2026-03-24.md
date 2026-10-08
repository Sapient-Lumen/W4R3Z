# Archive program-loop discipline — 2026-03-24

## Why this note exists

The repo now has enough front-door machinery that future passes can easily drift into fake continuity:
- a new profile report looks like a new decision,
- a later stage looks like the crate was always ready for that stage,
- or a carried-forward exception looks like solved evidence.

This note exists to keep the archive from doing that.

## Required program-loop questions

Before a pass says a leading crate idea is “more buildable now”, ask:
1. what earlier stage or packet bundle is being inherited?
2. what new stage is being entered or attempted?
3. what evidence is genuinely new?
4. what exceptions or unresolved gaps are still open?
5. what exit posture is being claimed?
6. what trigger would reopen this stage later?

## Required artifact separation

Keep these artifacts distinct:
- `policy-profile.pack`
- `profile-satisfaction.report`
- `decision-program.runbook`
- `profile-progression.report`
- `policy-exception.receipt`
- `decision-carryforward.receipt`
- `recheck-ticket.manifest`

Do not compress them into one “latest answer”.

## Progression discipline

When a new stage is entered:
- preserve the earlier basis lock,
- preserve prior adjudications,
- preserve prior exceptions unless they were explicitly removed,
- add a progression report,
- and state whether the new stage ended in `keep`, `conditional_keep`, `hold`, `split_boundary`, `replace_later`, or `stop_and_reopen_compare`.

## Archive guardrails

- Do not let “team-default” silently become “enterprise-offline”.
- Do not let “enterprise-offline” silently become “safety-onramp”.
- Do not let a later stage retroactively change what the earlier stage knew.
- Do not let one program exit imply that all receivers should do the same thing.

## Repo implication

Future archive refreshes should prefer:
- deepening runbooks,
- clarifying stage gates,
- tightening progression reports,
- and refining exit vocabularies

before inventing another top-level frontier lane.
