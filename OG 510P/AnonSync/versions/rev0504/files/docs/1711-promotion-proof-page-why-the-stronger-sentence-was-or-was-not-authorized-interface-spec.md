# Promotion proof page — why the stronger sentence was or was not authorized

## Purpose

This page is the durable proof artifact for any claim that a stronger sentence was either authorized or correctly withheld.
It exists so the product can later prove not only that lower rungs existed, but why promotion happened, who allowed it, and what still constrained it.

## Mandatory proof fields

### 1. Source linkage

- case identifier
- source lower-sentence receipt identifier
- source stability proof identifier
- source authority receipt identifier
- source time-authority receipt identifier
- promotion rule version

### 2. Gate status

- stronger sentence under review
- smallest already-earned sentence
- current gate rung
- whether the sentence is blocked, manual-ready, auto-armed, promoted, override-promoted, denied, or demoted
- exact blockers still present, if any

### 3. Decision basis

- prerequisites satisfied
- prerequisites missing
- warnings, residue, or reopen powers considered material
- confidence or cleanliness floor used, if any
- whether linked identity, owner status, or generic role were rejected as insufficient

### 4. Decision authority

- actor who decided
- actor class
- capacity in which they decided
- whether the decision was manual, automatic, or override-based
- whether countersign or quorum was required and satisfied

### 5. Override and aftermath

- override reason, if used
- override expiry and re-review date, if any
- debt, probation, or residue surviving the promotion
- strongest blocked sentence still unavailable
- exact demotion triggers known at issuance time

## Required proof statements

The page must be able to state sentences like these:

- `the stronger sentence is not yet eligible because stability was earned but a required authority receipt is still missing`
- `the stronger sentence is manual-review ready, but automation is blocked because hidden-work and delayed-rescan warnings still leave the confidence floor unmet`
- `the stronger sentence was auto-promoted under rule version R7 after all prerequisites cleared and no material blockers remained`
- `the stronger sentence was override-promoted for 48 hours by a named adjudicator, with probation and mandatory re-review preserved`
- `the stronger sentence was demoted after a no-source residue warning surfaced, while the earlier lower sentence remains true`

## Proof ceiling

This page may prove `why this stronger sentence was or was not authorized under the current promotion rule version`.
It may not on its own prove that an even stronger downstream sentence is available unless the relevant gate for that stronger row separately agrees.

## Preservation rules

The proof must preserve:

- the lower sentence that remained true regardless of the promotion outcome
- the exact promotion rule version used
- the deciding authority or automation policy
- blockers that kept the sentence weaker, if denied
- override debt or residue, if granted exceptionally
- demotion exposure known at the time of issuance

## Demotion rule

If later evidence shows the gate was armed on a mistaken basis, this page must downgrade into explicit demotion or invalid-promotion proof rather than silently disappearing.
