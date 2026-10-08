---
status: active_bridge
claim_kind: archive_governance
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
supersedes: null
depends_on: []
source_refresh_due: '2026-12-31'
case_pressure: rev0304_portfolio_calibration
---

# Doctrine revision and demotion under case pressure

## What this note is for

The archive now has a compact rule for **when a case lesson earns promotion into doctrine**.
What it still needed was the mirror rule:
**when repeated case work or better evidence starts pressing against an already-live doctrine note, what should the archive do?**

Without that rule, dense archives fail in two opposite ways:
- they treat one surprising case as if it automatically falsifies a settled rule,
- or they keep reusing a strained rule long after good case work has shown that its boundary, weight, or downstream routing no longer fits.

This note gives the archive a compact repair rule for when live doctrine is under **evidence pressure** from real cases, better comparative work, or repeated routing misses.
It distinguishes five outcomes:

1. **no doctrine change**,
2. **boundary clarification**,
3. **bridge patch**,
4. **anchor revision**,
5. **demotion or quarantine of the old rule**.

Use this note with:
- [`archive-policy.md`](archive-policy.md)
- [`research-triage-and-closure-rules.md`](research-triage-and-closure-rules.md)
- [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md)
- [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md)
- [`doctrine-precedence-and-conflict-repair.md`](doctrine-precedence-and-conflict-repair.md)
- [`case-to-doctrine-promotion-and-quarantine.md`](case-to-doctrine-promotion-and-quarantine.md)
- [`../20-program/case-work-decision-path.md`](../20-program/case-work-decision-path.md)
- [`../20-program/case-application-protocol.md`](../20-program/case-application-protocol.md)

## Default rule

The archive should neither let **one vivid case overthrow doctrine by drama** nor let a strained rule survive by inertia.
Its default stance should be:
**local pressure first, explicit repair next, doctrine demotion only when the pressure is real, repeated, and upstream enough to matter.**

That means a case or cluster of cases should first be read as a possible:
- boundary problem,
- downstream bridge gap,
- implementation-specific exception,
- or evidence-quality problem.

But if the same pressure keeps recurring, travels by mechanism, and changes how the archive should judge future cases, the archive should not keep pretending the doctrine is fine.
It should revise, narrow, or demote the rule explicitly.

## The five normal outcomes

### 1. No doctrine change

Use this when the live doctrine still looks sound and the pressure is better explained by:
- poor evidence quality,
- a local institutional quirk,
- a misread metric,
- or an implementation failure the doctrine already knew how to classify.

In this case the archive may still improve the case memo.
It should not pretend the doctrine changed when it did not.

### 2. Boundary clarification

Use this when the rule is still live, but the archive has learned a clearer limit, exception, or scope condition.

Typical signals:
- the doctrine is broadly right but overclaims its travel range,
- several cases expose the same boundary,
- or readers keep making the same false inference from an otherwise sound rule.

Boundary clarification is the archive's cheapest honest repair.
Prefer it when the upstream rule survives but its edges need tightening.

### 3. Bridge patch

Use this when the doctrine's upstream claim still holds, but case work keeps exposing the same downstream operator gap.

Typical signals:
- the anchor remains right in substance,
- but the archive keeps needing one extra tie-break, watch rule, or routing step,
- and the missing step is narrow enough to live in one bridge rather than rewriting the anchor.

Prefer a bridge patch when the pressure is real but downstream.
Do **not** use a bridge patch to avoid revising an anchor that is actually wrong at its own level.

### 4. Anchor revision

Use this when the pressure hits the doctrine's actual upstream claim.

Typical signals:
- several serious cases show the rule misclassifies failure or comfort,
- the current doctrine keeps sending future case work down the wrong route,
- or the archive cannot preserve the rule without adding so many caveats that the old wording is no longer honest.

An anchor revision may be small or large.
What matters is that the governing claim changes in the file that actually owns it.

### 5. Demotion or quarantine of the old rule

Use this when the pressure is strong enough that the prior rule should no longer remain live doctrine in its old form.

Typical signals:
- the rule repeatedly fails its travel claims,
- the rule is now mostly historical or illustrative rather than governing,
- or keeping it live would create false passes, false package confidence, or repeated memo drift.

Demotion is rarer than boundary repair and rarer than anchor revision.
But it is sometimes the honest move.
The archive should prefer a short explicit demotion to letting a broken rule linger as undead guidance.

## The six pressure tests

Run a pressured doctrine through these tests in order.

### 1. Evidence-quality test

Is the pressure coming from high-quality, well-specified case evidence or from a thin anecdote, noisy comparison, or temporary measurement blur?

The archive should not revise live doctrine because of dramatic but thin evidence.
But it also should not demand impossible proof before admitting a rule is under strain.
If the evidence is good enough to change future case routing, it is good enough to trigger explicit review.

### 2. Mechanism test

Can the pressure be stated as a recurring mechanism rather than as a memorable scene?

Good pressure language sounds like:
- when X condition is present, this rule over-certifies comfort,
- when A and B combine, the current routing skips a necessary washout screen,
- or this rule travels only when C administrative condition is also present.

Weak pressure language sounds like:
- this case feels like an exception,
- this example is especially disturbing,
- or this one country seems different in spirit.

The archive should revise doctrine by mechanism, not by mood.

### 3. Upstreamity test

Is the pressure hitting:
- a local application,
- a downstream bridge,
- or the anchor's actual upstream claim?

This matters because not all pressure deserves anchor surgery.
If the live problem is downstream, fix the bridge.
If the live problem is upstream, fix the anchor.
If the archive cannot name the level of the miss, it should not yet pretend to know the correct repair.

### 4. Recurrence test

Has the same strain appeared more than once?

That can mean:
- more than one serious case,
- one case plus repeated revision-work friction,
- one case plus an already-visible doctrine tension,
- or one case plus a strong external evidence update that clearly changes the archive's prior footing.

Single-case pressure can still justify a boundary note or explicit watch.
It rarely justifies full demotion by itself.

### 5. Route-cost test

Would keeping the current doctrine live force future readers to do repeated private reconciliation?

A pressured rule earns explicit repair when readers would otherwise have to keep remembering unwritten caveats, route around the rule by feel, or quietly ignore it in later memos.
A doctrine that only works for readers who already know when to disobey it is already partly broken.

### 6. False-comfort test

If the archive leaves the rule live as written, what kind of mistake does that make more likely?

The most serious pressures are the ones that create:
- false passes,
- false de-escalations,
- false package confidence,
- or fake portability of a case lesson that does not really travel.

The archive should spend more repair energy on pressure that prevents **premature comfort** than on pressure that only refines an already-hardline diagnosis.

## The ordinary repair ladder

When live doctrine is under real pressure, the archive should usually try these moves in order:

1. **clarify the boundary in the owning note,**
2. **add or tighten one bridge if the problem is downstream and repeated,**
3. **revise the anchor if the upstream claim is now wrong or overstated,**
4. **demote the prior wording to support or stub status if it no longer deserves live authority.**

This ladder matters.
It keeps the archive from either freezing doctrine or rewriting it too theatrically.

## What a pressured revision should say explicitly

If a revision changes, narrows, or demotes doctrine under case pressure, it should say briefly:

- **which live rule is under pressure,**
- **what kind of pressure it faces** — boundary / bridge / anchor / demotion,
- **what cases or recurring failures generated the pressure,**
- **what stays live after repair,**
- **what no longer governs as before,**
- and **why the chosen repair is cheaper and more honest than the nearest alternative.**

That keeps revision memory explicit.
It also stops later readers from confusing a repaired rule with the older one they may remember.

## What a case memo may say without rewriting doctrine by itself

A case memo may legitimately say:
- this live rule appears strained here,
- this may be a boundary failure,
- this looks like repeated downstream bridge pressure,
- or this case should be logged as possible doctrine-review pressure.

A case memo should usually **not** say, by itself:
- therefore the doctrine is overturned,
- therefore the old anchor is dead,
- or therefore this one case now governs archive-wide routing.

The memo may name the pressure.
A later revision still has to decide the repair level.

## Failure modes this note is trying to prevent

### 1. Drama-driven overthrow

A vivid case becomes a reason to rewrite doctrine before the archive has identified whether the problem is boundary, bridge, evidence quality, or true upstream failure.

### 2. Permanent strain normalization

Everyone quietly knows a rule is strained, so future memos keep adding private caveats, but no revision ever repairs the owning doctrine.

### 3. Bridge as avoidance

A bridge is added because the anchor is under pressure, but the bridge really functions as a shadow correction to an anchor that should have been revised directly.

### 4. Demotion panic

A rule with one bad travel result is demoted before the archive has checked whether the miss is actually local, noisy, or already explainable inside the rule's own boundary.

### 5. Historical residue masquerading as live doctrine

A repaired rule remains fully live in old wording, so readers encounter both the strained version and the repaired one and have to guess which governs.

## Bottom line

The archive should not let one dramatic case overthrow doctrine by force of vividness.
But it also should not keep strained doctrine alive by habit once repeated case work shows that the rule's boundary, downstream routing, or upstream claim no longer fits.

The right discipline is:
**treat case pressure as explicit review pressure, repair at the cheapest honest level, revise the owning anchor when the upstream claim is what failed, and demote old wording when leaving it live would keep generating false comfort or memo drift.**
