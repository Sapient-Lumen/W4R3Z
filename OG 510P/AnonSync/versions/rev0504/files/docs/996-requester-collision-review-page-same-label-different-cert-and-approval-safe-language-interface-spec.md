# Requester collision review page — same label, different proof, and approval-safe language

## Purpose

Force a careful review whenever a requester arrives with a label or device name that looks familiar but the reviewed proof handle does not cleanly match prior trust memory.

This page is required when any of the following are true:

- same identity label, different proof handle
- same device label, different proof handle
- prior approval memory exists but handle bundle changed
- operator tries to reuse trust on label match alone

## Inputs

- current requester identity contract sheet
- any matching prior requester receipts
- collision class
- requested capability ceiling
- family-widening availability

## Must show

### 1. Collision summary

Use explicit language such as:

- `Same human label, different proof handle`
- `Same device label, different requester handle`
- `Stored approval memory does not match current proof`

Never compress this to `possible duplicate` alone.

### 2. Side-by-side comparison

Render current and prior requester facts in parallel:

- human label
- device label
- proof handle
- prior approved scope
- first seen / last seen provenance if available

### 3. Safe-language ladder

Show permitted sentences, for example:

- `The label matches; proof does not.`
- `This may be a renamed, relinked, or unrelated requester.`
- `Previous trust cannot be reused without fresh review.`

And explicitly reject stronger sentences, for example:

- `This is the same requester.`
- `This is just a harmless rename.`

### 4. Available actions

Offer reviewed choices in order:

1. approve as a **new distinct requester**
2. inspect provenance and compare receipts
3. reject and request out-of-band verification
4. bind as a successor only if lineage proof exists

### 5. Consequence block

Must say whether choosing a path would:

- create new trust memory
- replace prior trust memory
- preserve both as distinct handles
- escalate to family review

## Approval barrier

Approving from this page must require explicit confirmation against:

- current proof handle
- requested subject
- trust scope
- whether prior trust is reused, replaced, or left untouched

## Receipt obligations

The resulting receipt must preserve:

- collision class
- compared handles
- selected path
- whether prior trust survived
- stronger blocked sentence such as `same name means same requester`