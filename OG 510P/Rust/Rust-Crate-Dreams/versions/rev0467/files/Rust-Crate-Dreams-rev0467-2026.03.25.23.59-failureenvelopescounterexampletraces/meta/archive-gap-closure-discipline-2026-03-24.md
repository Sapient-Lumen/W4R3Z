# Archive gap-closure discipline — 2026-03-24

## Why this note exists

The repo now has enough front-door machinery that future passes can easily drift into fake closure:
- a stage says `conditional_keep`,
- the next pass says “more evidence needed”,
- and the archive quietly pretends that was already a plan.

This note exists to keep the archive from doing that.

## Required gap-closure questions

Before a pass says a leading crate idea is “stronger now because it closes evidence gaps”, ask:
1. what exact stage or profile gate is still unsatisfied?
2. which existing packet exposed that gap?
3. can the gap be closed by local command, hosted import, manual review, or only upstream change?
4. what smallest bounded campaign is in scope?
5. what would count as partial closure versus full closure?
6. what stop condition ends the campaign?

## Required artifact separation

Keep these artifacts distinct:
- `profile-satisfaction.report`
- `decision-program.runbook`
- `profile-progression.report`
- `evidence-gap.report`
- `evidence-campaign.plan`
- `gap-closure.receipt`
- `policy-exception.receipt`
- `recheck-ticket.manifest`

Do not compress them into one “latest answer”.

## Closure discipline

When a gap changes state:
- preserve the earlier basis lock,
- preserve prior adjudications and exceptions,
- add a closure receipt,
- say whether the stage can progress or remains blocked,
- and keep other open gaps visible.

## Archive guardrails

- Do not let “we found the gap” silently become “we solved the gap”.
- Do not let “we wrote a campaign plan” silently become “the stage passed”.
- Do not let “one gap closed” silently become “all gaps closed”.
- Do not let one public metadata surface settle task fit, deployment readiness, or profile satisfaction.

## Repo implication

Future archive refreshes should prefer:
- tightening gap vocabularies,
- clarifying authority routes,
- refining stop conditions,
- and improving closure receipts

before inventing another top-level frontier lane.
