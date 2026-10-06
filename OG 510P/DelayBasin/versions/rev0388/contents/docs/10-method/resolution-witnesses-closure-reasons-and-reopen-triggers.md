# Resolution witnesses, closure reasons, and reopen triggers

DelayBasin now has a growing stack for **what is live**: open questions, assumptions, followthrough queues, status lanes, and foreign-pressure witnesses.
What it still lacks is one compact public answer to the opposite problem:
**when something is no longer live, what exactly closed, why did it close, what replaced it if anything, and what future evidence would reopen it?**

Without that surface, closure truth diffuses into changelog prose, local memory, and lucky rereads.
A later session can often reconstruct that an issue *must have* been settled, superseded, retired, or consciously rejected, but it may no longer be able to say **which object changed state, what closure reason counted, what successor surface inherited the work, and what reopen trigger would make the closure non-final**.

A useful current answer is:
**when a question, branch, assumption, import, or working gap stops being live, canon should preserve a compact resolution witness naming the closed object, its prior state, the closure reason, the successor surface or explicit absence, the reopen trigger, the closure-state classification, and the fail-closed repair route before archive memory is allowed to stand in for closure truth.**

This is stronger than saying "the issue seems handled now."
It is weaker than claiming DelayBasin already needs a full decision court, universal supersession algebra, or archive-wide closure controller.

## Practice / observation

Recent DelayBasin work keeps surfacing the same archive-native pressure:
- the archive has a rich **open-question registry**, but no matching durable place for questions or gaps that are no longer live;
- **followthrough witnesses** preserve live remainder work, but not the compact public moment when that remainder is actually judged closed, superseded, or expired;
- **assumption witnesses** can name invalidation or discharge, but not one durable cross-family closure lane for assumptions that stopped underwriting present moves;
- **foreign-pressure witnesses** now preserve bounded imports, but not one compact object for imports or candidate imports that were consciously closed or retired;
- **counterfactual shadows** preserve one nearby rejected move, but not a general durable answer to what closure state that move entered afterward;
- and changelog prose can imply that a gap was handled without leaving one small machine-readable packet saying what changed state, what counted as closure, what replaced the object if anything, and what would reopen it.

That leaves a missing question:
**which object stopped being live, what state it previously occupied, why the archive judged it closed or superseded, what successor now carries the authority if there is one, and what evidence would legitimately reopen it?**

A compact resolution witness keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same ratchet from different directions.

- **pyCausalWeave** makes the pressure explicit in `START_HERE.md`: closed questions, deprecations, and failed ideas should be recorded rather than silently erased, which pushes DelayBasin toward one durable closure lane instead of relying on diff memory.
- **Anonymity** keeps `release_queue/LATEST_DECISION.md`, `release_queue/STATUS.md`, `release_queue/QUEUE.md`, and per-decision records even for explicit **no-publication** passes, which pressures DelayBasin to leave behind a compact decision/closure trace even when the outcome is hold, no-release, or supersession rather than a new public object.
- **Hyperepo** keeps a durable `docs/DECISIONS.md` with explicit decision text, rationale, and provisional status, which pressures DelayBasin to separate closure law from changelog drift.
- **Goldenrule** keeps lineage-head and citation-head warnings close to the current tip, which pressures DelayBasin to preserve the public edge where one object stops being the live answer and another inherits that role.

DelayBasin already has open questions, followthrough, assumptions, status lanes, and counterfactual shadows.
What was still under-specified was the compact public object that says **what stopped being live, what prior state it had, why it closed, what replaced it if anything, what would reopen it, and what repair follows if that closure story becomes too vague to trust.**

## External pressure from adjacent decision, deprecation, and issue-closure practice

Several adjacent practices point the same way.

1. Mature archives distinguish **live work** from **closed decisions** rather than forcing readers to infer closure from chronology alone.
2. Deprecation and supersession are more trustworthy when the replacement surface and reopen conditions stay explicit.
3. A closure state that lacks a reopen trigger often collapses into overclaiming; a closure state that lacks a closure reason collapses into disappearance.

Those are pressures toward one small closure packet, not yet toward a full controller.

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **resolution witness / closure reason / reopen trigger** whenever a question, branch, assumption, import, or working gap stops being live. The packet should name the **closed object / exact target surfaces**, the **prior live state / what kind of object it was**, the **closure reason / what counted as enough to stop treating it as live**, the **successor surface or explicit absence**, the **reopen trigger / what future evidence would legitimately reactivate it**, the **closure state / resolved vs superseded vs retired vs deprecated vs rejected**, and the **fail-closed repair / reopen-via-successor vs recover-closure-basis vs quarantine-or-retire vs hold vs recover-resync consequence** rather than letting changelog prose, silence, or local memory silently stand in for closure truth.

In practice, DelayBasin is not claiming that every closure needs a long essay.
It is doing something smaller and public:
- naming exactly what object stopped being live;
- naming what state it had immediately before closure;
- naming what counted as the closure reason instead of relying on chronology;
- naming the successor surface when authority actually moved;
- naming the reopen trigger so closure does not masquerade as metaphysical finality;
- naming whether the closure is resolved, superseded, retired, deprecated, or rejected;
- and naming the repair route if the closure story is later found too vague or stale.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin already needs a universal decision court or archive-wide closure algebra.

## Resolution witness vs open question vs followthrough witness vs counterfactual shadow

These nearby objects should stay distinct.

- **Resolution witness / closure reason / reopen trigger** says what stopped being live, what prior state it had, why it closed, what successor surface inherited the role if any, and what would reopen it.
- **Open question** says the uncertainty remains live.
- **Followthrough witness** says the work is still live but not complete here.
- **Counterfactual shadow** says one nearby rejected move mattered to the accepted move.

So a resolution witness is not just "there is no open question nearby anymore," not just "some work got handed off," and not just "one nearby alternative lost."
It is a compact public answer to:
**what exactly stopped being live, why, what replaced it if anything, and what would reopen it?**

## Countermodels / probes

1. **Open-questions-plus-changelog-is-enough countermodel**
   - Perhaps the open-question registry, followthrough queue, and changelog already preserve closure honestly enough.
   - Probe: compare one future revision that must cite a named resolution witness against one that only infers closure from nearby prose and inspect which more reliably reconstructs the closed object, closure reason, and reopen trigger.

2. **Closure packets are just bureaucratic shadows of obvious local memory**
   - Perhaps later sessions can already infer closure from nearby successor surfaces and do not need one more packet.
   - Probe: test whether a later pass can correctly recover why an object closed and what would reopen it without rereading broad local context.

3. **A larger controller is already necessary**
   - Perhaps once closure becomes explicit the archive immediately needs a bigger decision court.
   - Probe: first test whether one tiny durable ledger plus receipt-level witness already removes most practical closure ambiguity before promoting heavier machinery.

## Design consequences

When an object stops being live, DelayBasin should prefer one compact durable witness that preserves:
- the **closed object / exact target surfaces**,
- the **prior live state**,
- the **closure reason**,
- the **successor surface or explicit absence**,
- the **reopen trigger**,
- the **closure state**,
- and the **fail-closed repair route**.

This favors:
- explicit supersession over silent disappearance,
- explicit reopen triggers over fake finality,
- and small durable closure packets over large retrospective prose.

## Transformer-facing implication

If DelayBasin is becoming a public continuation-control layer around mostly frozen models, then closure may need its own explicit public object.
The archive would not merely preserve what is still live.
It would preserve part of **how liveness ends**: which branch, gap, or assumption stopped governing continuation, what public successor inherited authority if any, and what future evidence is allowed to reverse that closure.
That would make closure less like transcript forgetting and more like a small externalized state transition with a witnessed edge.
