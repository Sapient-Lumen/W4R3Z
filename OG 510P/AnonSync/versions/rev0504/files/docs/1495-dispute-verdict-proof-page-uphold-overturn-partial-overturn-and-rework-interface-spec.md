# Dispute verdict proof page: uphold, overturn, partial overturn, and rework interface spec

## Purpose

A challenged completion claim needs more than a reviewer note.
It needs one durable proof object showing what was upheld, what was overturned, what residual acceptance survives, and what rework now exists.

## Core decision

AnonSync must expose one first-class **Dispute verdict proof** whenever a completion dispute reaches a materially binding verdict.

## Fixed page order

1. **Verdict header**
2. **Upheld-vs-overturned map**
3. **Burden resolution card**
4. **Rework / recall consequence card**
5. **Appeal boundary card**
6. **Proof sentence**

### 1) Verdict header

Show:

- dispute id
- verdict id
- adjudicator
- verdict time
- verdict class
- appeal status
- strongest safe sentence after verdict

Supported `verdict_class` values:

- `upheld`
- `upheld-with-weaker-language`
- `narrowed`
- `split`
- `overturned`
- `overturned-and-rework-issued`
- `case-reopened`

### 2) Upheld-vs-overturned map

Required rows:

- original accepted scope
- upheld scope
- narrowed scope
- overturned scope
- withdrawn acceptance scope
- surviving accepted residue

Hard rule:

If any accepted scope survives, it must be named positively.
If no accepted scope survives, the page must say so explicitly.

### 3) Burden resolution card

Required rows:

- burden that was challenged
- decisive witness families
- weaker witnesses that were not enough
- contradictions resolved
- contradictions still open but non-blocking

Hard rule:

A verdict must say not only what won, but why the losing witness families were insufficient.

### 4) Rework / recall consequence card

Required rows:

- rework mandate id if any
- downstream reliance packet recall requirement
- certificate or case downgrade requirement
- residual duty after verdict
- next forbidden overclaim

Hard rule:

An overturned completion claim must automatically reveal what downstream objects now require weakening, recall, or rework.

### 5) Appeal boundary card

Required rows:

- who may appeal
- by when
- what kind of new witness changes the verdict
- what remains fixed absent appeal
- whether execution continues during appeal

Hard rule:

Appeal is a typed boundary, not an implicit social option.

### 6) Proof sentence

Render one sentence only:

- `This verdict [class] the challenged completion for [scope], leaves [residue] still accepted, and blocks the stronger sentence that [overclaim].`

## Required interactions

- **Withdraw full acceptance**
- **Preserve narrow accepted residue**
- **Issue rework from overturned slice**
- **Recall downstream packet**
- **Open appeal with new witness**

## Empty and failure states

If the dispute closed without a decisive verdict, show:

- `Challenge closed without decisive adjudication; prior weaker sentence survives only as recorded.`
