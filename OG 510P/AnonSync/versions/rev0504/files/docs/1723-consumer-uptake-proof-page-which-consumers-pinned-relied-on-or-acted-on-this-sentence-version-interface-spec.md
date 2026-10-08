# Consumer-uptake proof page — which consumers pinned, relied on, or acted on this sentence version?

## Purpose

This page is the durable proof artifact for any claim about who consumed a sentence version and how far that consumption progressed.
It exists so the product can later prove not only that a sentence was current, but how deeply different consumer cohorts actually relied on it.

## Mandatory proof fields

### 1. Source linkage

- case identifier
- current-sentence receipt identifier
- sentence version handle
- rule version for uptake classification
- any superseding sentence identifiers already known

### 2. Consumer-by-consumer strongest state

For each named consumer or cohort:

- strongest evidenced uptake class
- evidence time and trusted time basis
- whether evidence is direct, inferred, or contested
- pinned version, if any
- whether the pinned version still matched current at decision time
- whether any action began or completed under that version

### 3. Decision and action basis

- decision type bound to the sentence
- reversibility class of that decision
- downstream action identifiers, if any
- whether rollback would halt, compensate, annotate, or merely record residue
- whether any human or agent executed under stale or superseded sentence basis

### 4. Blast-radius statement

- cheapest rollback cohort
- most expensive rollback cohort
- irreversible cohort, if any
- surviving residue after rollback or supersession
- strongest blocked reversal sentence

## Required proof statements

The page must be able to state sentences like:

- `the sentence was current for cohort A, but only rendered there; no pin or bound decision was proven`
- `cohort B pinned sentence version S-17 and kept it cached, but no decision was bound before rollback`
- `cohort C used S-17 as decision basis for a reversible action and can still be rolled back by compensation rule R-4`
- `cohort D completed an irreversible downstream act under S-17 before supersession; rollback is blocked for that act and only residue annotation remains`
- `one consumer acted on a stale pinned version after the newer sentence became current; the uptake proof downgrades that path into contested decision basis`

## Proof ceiling

This page may prove who consumed a sentence version and how far that reliance progressed.
It may not by itself prove that rollback or compensation is normatively acceptable unless the relevant rollback policy separately agrees.

## Preservation rules

The proof must preserve:

- the strongest current sentence
- the exact sentence version actually used by each cohort
- direct vs inferred consumption evidence
- reversible vs irreversible downstream acts
- the strongest blocked rollback sentence
- the next event that would strengthen or weaken the uptake claim
