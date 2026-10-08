# Overlapping-subject lineage receipt page: parent-child claim class, seed gap, and blocked stronger sentences interface spec

## Purpose

After any serious overlap-affecting change, a later operator must be able to answer:

> which parent/child claim was admitted or refused, what seed gap survived, what residue cost was accepted, and what stronger sentence stayed blocked?

This receipt exists so overlapping subject topology remains inspectable long after the original decision.

## Core decision

Every serious overlap-topology mutation emits one first-class **Overlapping-subject lineage receipt**.

The receipt records:

- scope and time
- overlap claim before and after
- admission verdict
- seed-gap verdict
- dual-index cost
- strongest safe sentence
- stronger rejected sentence

## Fixed receipt sections

1. header
2. before / after summary
3. admission evidence
4. topology residue
5. blocked stronger sentence
6. reopen conditions

### 1) Header

Show:

- receipt id
- target scope
- operator / runtime label if known
- timestamp
- action class

### 2) Before / after summary

Show rows for:

- parent subject
- child subject
- overlap class
- materialization posture
- claim boundary class

### 3) Admission evidence

Show:

- permission-floor verdict
- same-ID or contains-subject verdict
- non-empty reconnect confirmation if relevant
- proof freshness

### 4) Topology residue

Show:

- parent-only → child-only seed-gap verdict
- child-only → parent-only propagation residue
- dual-index / rescan cost verdict
- service-interior conflict residue if any

### 5) Blocked stronger sentence

Examples:

- `Blocked stronger sentence: the parent and child now behave as one subject everywhere.`
- `Blocked stronger sentence: any peer that sees descendant bytes can seed the descendant subject.`
- `Blocked stronger sentence: the larger root was admitted without swallowing an existing subject boundary.`

### 6) Reopen conditions

Reopen automatically when:

- the child is removed or re-shared separately
- selective-sync is enabled on either overlapped subject
- the containing root is changed or remounted
- the `.sync/ID` boundary is regenerated
- the runtime world or storage world changes

## Rules

### Rule 1 — receipts must preserve claim-class truth, not just the clicked action

The receipt records whether the action was nested admission, blocked expansion, reconnect, or collision.

### Rule 2 — topology residue must preserve both seed-gap and cost truth

A receipt without both route residue and indexing residue is incomplete.

### Rule 3 — stronger blocked sentence is mandatory

The receipt must retain the claim that the product explicitly refused to make.
