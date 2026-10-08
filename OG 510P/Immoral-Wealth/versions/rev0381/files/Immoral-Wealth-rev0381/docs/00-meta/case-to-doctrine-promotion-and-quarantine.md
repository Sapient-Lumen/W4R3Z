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

# Case-to-doctrine promotion and quarantine

## What this note is for

The archive now has rules for **which cases deserve memo work**, **how many case memos may stay live**, **when old memos go stale**, and **how doctrine should be routed once it already exists**.
What it still needed was one compact bridge for the next problem dense archives hit:
**when a case seems to teach a wider lesson, when does that lesson earn promotion into live doctrine, and when should it stay quarantined as case-local knowledge instead?**

Without that rule, case work can fail in two opposite ways:
- one vivid case gets overgeneralized into permanent doctrine,
- or a genuinely repeated lesson stays trapped in local memos and keeps being rediscovered from scratch.

If the pressure runs the other way—if repeated case work starts straining an already-live rule—route that follow-on problem through [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md) rather than treating promotion and demotion as the same question.

This note gives the archive a compact rule for deciding when case work should remain:
- a **local memo**,
- an **exemplar**,
- a **proof-building support case**,
- a **bridge-worthy recurring lesson**,
- or a **true anchor-level doctrine update**.

Use this note with:
- [`archive-policy.md`](archive-policy.md)
- [`research-triage-and-closure-rules.md`](research-triage-and-closure-rules.md)
- [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md)
- [`doctrine-precedence-and-conflict-repair.md`](doctrine-precedence-and-conflict-repair.md)
- [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md)
- [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md)
- [`../20-program/case-portfolio-triage-and-memo-selection.md`](../20-program/case-portfolio-triage-and-memo-selection.md)
- [`../20-program/case-portfolio-caps-and-retirement.md`](../20-program/case-portfolio-caps-and-retirement.md)
- [`../20-program/case-application-protocol.md`](../20-program/case-application-protocol.md)

## Default rule

A case does **not** become doctrine merely because it is vivid, well-written, recent, politically salient, or emotionally clarifying.
The archive's default stance should be:
**quarantine first, promote later.**

That means a case lesson should stay local unless the revision can show, explicitly, that it is doing more than narrating one place or one moment.
To earn promotion beyond the memo, a case lesson should usually clear all four questions:

1. **Does it name a recurring decision problem rather than a one-off scene?**
2. **Does the lesson travel by mechanism, not by atmosphere?**
3. **Does promoting it reduce future re-synthesis more than it creates new route weight?**
4. **Is there a clear destination for the lesson: existing anchor, bridge, or truly missing anchor?**

If the answer to any one of those is no, the default answer should usually be:
**keep the lesson inside the case memo, exemplar, or proof-building note for now.**

## The three normal statuses for a case lesson

### 1. Quarantined local lesson

Use this when the observation matters inside the case but has not yet earned wider authority.
This is the default status.

Typical signals:
- the lesson depends heavily on one institutional quirk,
- the evidence is still thin or one-sided,
- the lesson sounds important but has not yet been forced through another case,
- or the archive cannot yet say where the rule belongs without creating route confusion.

A quarantined lesson may still be stated clearly.
It just should not yet be treated as general archive doctrine.

### 2. Bridge-worthy recurring lesson

Use this when the archive keeps encountering the same downstream operator problem across more than one case or more than one anchor, but the lesson is still narrower than a full anchor-level rewrite.

Typical signals:
- multiple cases keep tripping the same routing gap,
- a compact decision rule would prevent repeated memo drift,
- the lesson has a clear limited job,
- and a small bridge would reduce rereading across several future revisions.

This is the normal route for promotion.
The archive should usually prefer **one narrow bridge** over declaring a new anchor too early.

### 3. Anchor-level doctrine update

Use this only when the case work reveals a **stable upstream rule** the archive clearly needs across many settings, and that rule properly belongs in an existing anchor or in a truly missing anchor-level note.

Typical signals:
- the lesson changes how the archive should read verdicts, targets, floors, mode, package choice, rails, confidence, or archive governance across many future uses,
- the lesson is no longer case-dependent in its core form,
- and folding it into the relevant anchor would simplify, not complicate, the archive's main path.

Anchor promotion should be rarer than bridge creation.
If a lesson can live cleanly as a bridge, it usually should.

## The six promotion tests

Run a candidate case lesson through these tests in order.

### 1. Recurrence test

Has the archive encountered this lesson in more than one serious place?
That can mean:
- more than one case,
- one case plus an already-live doctrine tension,
- or one case plus a repeated operator failure in revision work.

A single vivid case can still justify future attention.
It rarely justifies immediate doctrine by itself.

### 2. Mechanism test

Can the lesson be stated as a **mechanism or decision rule** rather than as a scene description?

Good promotion language sounds like:
- when X surface is present, treat Y comfort more skeptically,
- if A and B conflict, let C govern,
- or if a case repeatedly shows Q, route through R before certifying softer language.

Weak promotion language sounds like:
- this place is especially striking,
- this scandal feels paradigmatic,
- or this case really shows what the whole system is like.

The archive should promote mechanisms, not atmospheres.

### 3. Travel test

Would the lesson likely survive outside the originating case?
Ask whether it would still help in:
- another country,
- another sector,
- another cohort,
- or a later revision that never mentions the original case.

If the lesson only travels when the original case's specific political or legal quirks are carried with it, it usually remains local.

### 4. Destination test

Where would the lesson live if promoted?
The revision should be able to answer one of these clearly:
- **tighten an existing anchor,**
- **add one narrow bridge,**
- or **create one missing anchor** because no current anchor actually governs the question.

If the revision cannot name a clean destination, the lesson is probably not ready for promotion.
Unclear destination is often a sign of overexcitement rather than under-theorization.

### 5. Compression test

After promotion, would the archive become easier to use?
A promoted lesson earns its bytes only if it reduces future repetition, route-searching, or memo drift.
If promotion would merely create another note readers must open while the original case still needs to be read in full, the lesson has not yet earned archive-wide status.

### 6. Boundary test

Can the revision say what the promoted lesson does **not** claim?
A promoted case lesson should usually carry an explicit boundary:
- what remains case-local,
- what evidence would still change the rule,
- and what nearby question still belongs to another anchor or bridge.

If the boundary cannot be stated, promotion often becomes accidental overreach.

## The ordinary promotion path

When a case lesson clears the tests, the archive should usually choose the cheapest honest promotion path.

### A. Tighten an existing anchor first

If the lesson clearly belongs inside an existing anchor, prefer tightening that anchor over spawning a satellite note.
This is the default when the new lesson simply sharpens an already-governed upstream question.

### B. Add one narrow bridge second

If the lesson solves a repeated downstream operator problem that the anchor does not cleanly carry, add one bridge with an explicit limited job.
Do this when the archive needs reuse, but not a new anchor.

### C. Create a new anchor only last

A truly new anchor is justified only when the lesson governs a recurring upstream question that no current anchor handles well.
New anchors should therefore be rare.
A case should not create one unless the archive can clearly show a standing gap, not just one memorable prompt.

## Quarantine signals

A case lesson should usually stay quarantined when one or more of these are true:

1. **single-case vividness is doing most of the work**
2. **the lesson depends on an institution or legal quirk that barely travels**
3. **the evidence is too thin to know whether the pattern is real or temporary**
4. **the lesson would force a new term more than a new distinction**
5. **the archive cannot yet name the correct anchor or bridge destination**
6. **promotion would duplicate an existing rule rather than sharpen it**

Quarantine is not demotion.
It is the archive's way of saying: useful, visible, not yet doctrine.

## What a case memo should say when promotion is tempting

If a case seems to teach a wider lesson, the memo should usually end with a short block like this:

- **candidate wider lesson**
- **status:** quarantine / bridge candidate / anchor-tightening candidate
- **why it might travel**
- **what keeps it from full promotion yet**
- **where it would belong if later promoted**

That block is often enough.
It preserves the insight without forcing immediate doctrine growth.

## False moves this note is meant to stop

### 1. Anecdote law

A single vivid case feels so morally clarifying that the archive quietly starts treating it as universal law.
That is not discipline.
It is rhetorical overfit.

### 2. Permanent quarantine

The opposite failure is letting the archive rediscover the same lesson across many cases because no revision ever promotes the recurring rule.
That wastes bytes and attention too.

### 3. Creating a new anchor when a one-line anchor edit would do

Sometimes a case really does teach something.
But the cheapest honest fix is a tightening sentence in an existing anchor, not a whole fresh note.

### 4. Promoting local vocabulary instead of a real distinction

A case may invent memorable language for an old problem.
That is usually a term-cleanup issue, not a doctrine-creation event.

### 5. Using case count as a fake substitute for mechanism

Two or three similar memos do not automatically produce doctrine.
The archive still needs the mechanism, travel claim, and destination to be clear.

## Fast use rule

When a case seems to teach a wider lesson:

1. **default to quarantine first,**
2. **ask whether the lesson is recurring, mechanistic, and portable,**
3. **name the destination: existing anchor, narrow bridge, or truly missing anchor,**
4. **promote only if the archive becomes easier to use afterward,**
5. **state the boundary so the lesson does not overclaim,**
6. **and otherwise keep the lesson visible inside the case memo without letting it become doctrine by drift.**

## Bottom line

The archive should not let one vivid case write the theory for everyone else.
But it also should not keep relearning the same real lesson because no revision ever promotes it.
The right discipline is: **quarantine first, promote by mechanism, travel, destination, and compression, and prefer the cheapest honest promotion path that keeps the archive easier to use.**
