# Reviewed mutation commit barrier and receipt continuity interface spec

## Purpose

The archive already says risky work should become a reviewed draft object.
What it still lacked was a precise answer to the very last seam:

> once a draft has been assembled and reviewed, what exactly is the interface object that turns `this looks right` into `apply this now` without collapsing into a vague confirmation modal?

This document answers that seam.

## Core decision

Every non-trivial draft that is ready to apply must pass through a **commit barrier**.
The commit barrier is not the same thing as the draft summary.
It is a short, fixed, semantics-heavy review step whose only job is to make the final consequences plain.

The barrier exists because the last click is where products most often hide:

- irreversible scope
- future inheritance consequences
- authority widening
- cleanup side effects
- whether the post-state will be proven by one receipt or by several successor objects

AnonSync should not hide those things in a footer.

## What the barrier must answer

A good commit barrier must answer five questions in order:

1. **What changes immediately if I apply now?**
2. **What does not change yet, even if the action succeeds?**
3. **What becomes harder to undo afterward?**
4. **What receipts or successor objects will exist right after apply?**
5. **What continuity claim will the product make once apply finishes?**

If any of those answers are missing, the operator is not yet at a safe apply boundary.

## Barrier anatomy

### 1) Draft reference and acting seat

Show:

- draft handle
- acting seat
- action kind
- subject count or subject family
- freshness summary

This is the answer to `which reviewed intent am I about to commit from which authority position?`

### 2) Immediate-change summary

This region should say, in plain language, what changes now:

- `Baseline for 17 still-inheriting members will change`
- `This one subject will stop inheriting and become pinned locally`
- `A temporary override lease will become active until 18:00`
- `This path will be rebound to the remembered local directory`
- `Two blocked outliers will remain unchanged`

This must be human-legible and scope-specific.

### 3) Non-change summary

The barrier must also say what will **not** change yet.
Examples:

- `No remote residue claim is made yet`
- `No sibling shares are widened`
- `No local bytes are fetched by this action`
- `Existing blocked outliers remain blocked`
- `Publication policy is unchanged`

This section prevents false confidence.

### 4) Hard-to-undo consequences

Not every apply is equally sticky.
The barrier should classify sticky aftermath such as:

- authority widened
- destructive delete propagated
- inheritance broken
- remembered path superseded
- duplicate namespace created
- irreversible external publication already performed
- old capability epoch left behind and cleanup still pending

The operator should never have to infer these from the button label alone.

### 5) Predicted aftermath objects

The barrier should name the immediate resulting objects:

- one receipt
- one receipt plus one active lease
- one partial-apply receipt and one blocked remainder draft
- one path-repair receipt plus one post-apply recompute report
- one rotation receipt and one follow-on cleanup review

This keeps `apply` from feeling like a blind jump.

### 6) Continuity claim

The product must say what honest statement it expects to make after success, for example:

- `These subjects now follow the new baseline`
- `This subject now diverges locally until restored`
- `This subject is rebound to the remembered path`
- `This repair established path continuity but not yet byte equivalence`
- `This authority widened, but older residue still requires cleanup review`

This is the crucial anti-magic line.

### 7) Final controls

The barrier should normally offer:

- `Apply now`
- `Back to draft`
- `Export / hand off`
- `Cancel draft` when still appropriate

Danger outcomes should still be visually distinct even here.

## Barrier classes

### Class A — low-risk single-subject change

Examples:

- one local pin
- one inheritance restore
- one low-risk path rebind with strong proof

The barrier may be compact but must still preserve the same five questions.

### Class B — wide but routine reviewed change

Examples:

- baseline edits
- multiple-subject publication changes
- multi-member exception updates

The barrier should emphasize blast radius, outliers, and expected subgroup receipts.

### Class C — destructive or authority-widening change

Examples:

- replicated delete
- broader share authority
- retained-copy recall claims
- topology or disclosure widening
- risky rebind against non-empty target

The barrier should require stronger acknowledgement wording and may require extra reason capture.

## Things the product should refuse

- generic `Are you sure?` confirmation as the only final review
- final apply controls that omit blocked outliers or non-effects
- button labels that imply stronger continuity than the product can yet prove
- receipts that cannot be reopened from the barrier outcome
- final review that depends on remembering what the draft said on a prior page

## Receipt continuity rules

The barrier and resulting receipt must stay linked.
After apply, the operator should be able to open:

- the receipt
- the originating draft
- any surviving blocked remainder
- the post-apply recompute report

This matters because many expensive mistakes happen when `apply` severs narrative continuity.

## Cross-projection rules

GUI, local web, TUI, and CLI may render the barrier differently.
But every projection must still expose:

- immediate change
- non-change
- hard-to-undo consequence
- predicted aftermath objects
- continuity claim

CLI may print a structured review block.
Local web may use a page or side sheet.
The semantic payload must stay the same.

## Result

A good commit barrier prevents four expensive failures:

- treating final apply as a mere button instead of a semantic boundary
- assuming success means stronger cleanup or continuity than the product actually proved
- forgetting which outliers or blockers remained after apply
- losing the story that links reviewed intent to final receipt

If a reviewed draft still ends in a generic confirmation modal, the product has not actually solved the last dangerous seam.
