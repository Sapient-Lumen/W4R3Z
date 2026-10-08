# 468 — Fused governance rollups, blocker inventories, and macrostate decomposition

## One-line thesis

Consequential public-AI dashboards, queue summaries, and readiness badges should decompose into named substates and live blocker inventories rather than one fused macrostate, so a green rollup cannot hide stale evidence, blocked disclosure, or missing review.

## Why this matters

Institutions eventually build one high-level surface that tries to answer a deceptively simple question: *where do things stand?* It may be a launch-readiness panel, an oversight queue, an executive dashboard, an incident board, or a reviewer worklist. Those surfaces are useful. People need one place to orient before diving into the archive.

But compressed status also creates a recurrent governance distortion. A system looks "green" because runtime health is fine even though the public record is stale. A case looks "under review" even though no live request exists and the blocker is actually missing evidence. A dashboard shows one healthy aggregate while the appeal packet lane, training lane, or disclosure lane is red. Review debt gets buried in inventory rollups. Missing sidecars, stale recorder evidence, or brittle proof surfaces become invisible until something fails publicly.

The datacube already rejects state compression, preview overclaim, weak coverage claims, and implementation-first completion myths. What it still lacked was one note specifically governing the **fused summary surface itself**: the macro queue, aggregate badge, or control-plane rollup that people use to decide what matters now.

## Pattern pack

### 1. Allow a top-line rollup only if the substate schema is named

A summary surface may show one overall state, but only if it also names the major substates it compresses, such as:

- runtime health,
- review-request state,
- approval freshness,
- disclosure currency,
- evidence-packet completeness,
- monitoring coverage,
- training or runbook currency,
- and open incident or appeal debt.

A fused answer without a visible decomposition is too easy to overtrust.

### 2. Carry both counts and the underlying blocker inventory

Summary counts are useful, but they should not be the only truth. A consequential rollup should let reviewers reach the current blocker inventory without guesswork, including which items are:

- stale,
- missing,
- blocked with reason,
- waiting on another owner,
- degraded but temporarily tolerated,
- or unknown due to missing telemetry.

The queue is not just a number; it is the live basis for action.

### 3. Keep heterogeneous debts separate even when one surface shows them together

A single dashboard may present many governance lanes together, but it should not let one lane's health erase another lane's debt. The archive should keep visible distinctions between, for example:

- healthy runtime and stale public notice,
- completed review and blocked release authority,
- current approval and missing packet joins,
- strong model metrics and weak subgroup evidence,
- or live service continuity and overdue operator retraining.

Mixed truth should survive compression.

### 4. Preserve explicit blocker classes instead of one vague red/yellow state

When something is not ready or not current, the rollup should say *why* in a typed way, such as:

- waiting for named reviewer,
- stale since date,
- source missing,
- packet incomplete,
- disclosure superseded,
- monitoring blind spot,
- integrity unresolved,
- or ownership unassigned.

A red badge without blocker class is usually only the beginning of governance truth.

### 5. Show the next honest action and fallback path

A summary surface should do more than report debt. It should identify the next honest action, such as:

- open the current blocker,
- request rereview,
- refresh the disclosure head,
- regenerate the packet,
- capture missing witness data,
- or route to the owner of the blocked lane.

If one helper or summary view is unavailable, the archive should still preserve a fallback path to the underlying lane truth rather than failing into blank reassurance.

### 6. Separate current macrostate from trend history

Trend lines and historical counts can be useful, but they should not be mistaken for the current blocking reality. The archive should keep:

- current substate,
- current blocker inventory,
- recent trend,
- and closed debt history

as distinct views.

A declining debt chart does not mean the remaining blocker stopped mattering.

### 7. Escalate orphaned or aging debt inside the rollup itself

When blocker items age past defined thresholds, remain ownerless, or recur after repeated closure, the summary surface should make that escalation visible. Otherwise a macro queue turns into a polite graveyard of known governance debt.

## Guardrails

- Do not let one green or healthy lane cancel another lane's unresolved blocker.
- Do not show counts without a route to the current blocker inventory.
- Do not collapse distinct blocker classes into one vague caution state.
- Do not let trend graphics impersonate current readiness.
- Do not hide ownerless or aging debt behind seemingly stable aggregate numbers.

## Failure modes

- **green-rollup camouflage**: one healthy lane makes the whole system look current.
- **queue-count opacity**: people can see how many blockers exist but not what they are.
- **mixed-truth laundering**: runtime, review, disclosure, and evidence debts collapse into one fuzzy badge.
- **trend-as-readiness**: improving history is mistaken for current closure.
- **orphan-debt burial**: long-lived blockers remain visible only as numbers without clear owners or action paths.

## Practical tests

A macrostate-honest governance surface passes when it can answer yes to all of the following:

1. Does every fused summary declare the substate categories it compresses?
2. Can reviewers move from counts to the live blocker inventory without guesswork?
3. Are heterogeneous debts kept visibly distinct even when one surface presents them together?
4. Do blocker states carry typed reasons and ownership rather than only color or badge state?
5. Does the summary surface state the next honest action and preserve a fallback route to lane-level truth?

## Compression rule for the archive

If a governance dashboard can say **overall status is green** but cannot also say **which substates were fused, which blockers remain live, and who owns the next action**, then it is still letting **macrostate convenience impersonate governance truth**.
