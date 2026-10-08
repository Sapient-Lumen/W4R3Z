# Local-truth assertion review page: ghost warning, reconnect-same-path, and pre-populated-tree branches

This page exists so three superficially similar buttons stop pretending to mean the same thing:

- `Ignore All` on a no-source / ghost warning
- `OK` on a non-empty destination / pre-populated tree attach
- `Proceed` on a reconnect to a location that already hosted this subject

All three require human judgment.
They do not require the same judgment.

## Operator question

> which local-truth assertion am I being asked to make here, what branch am I choosing, and what exactly happens if my assumption is wrong?

## When this page must appear

Render whenever the operator is about to:

- hide a ghost-file warning without world proof that the file is globally gone
- republish local bytes because they are believed to be newest despite absent peers
- connect a subject to a non-empty tree
- reconnect to a path that might be the same prior tree or might be an accidental merge target
- accept a merge where latest timestamp may replace existing content

## Fixed page order

1. **Branch chooser**
2. **What this branch asserts**
3. **Contradiction risks**
4. **Safer weaker alternative**
5. **Receipt consequence**

## 1) Branch chooser

Offer mutually exclusive branches such as:

- `Hide warning only; do not claim world absence`
- `Local tree is reviewed same-tree reconnect`
- `Local tree is pre-populated merge target`
- `Local bytes are believed newest; republish after attestation`
- `Abort and gather more proof`

The operator must be able to answer: **which branch am I actually choosing?**

## 2) What this branch asserts

For the chosen branch, show:

- assertion class
- reviewed scope
- what evidence was inspected
- what the branch does **not** prove

Examples:

- `Hide warning only` asserts only that warning visibility should change locally; it does not prove that no peer still has newer bytes.
- `Same-tree reconnect` asserts that the non-empty target is the previously bound tree, not an unrelated directory that would create a risky merge.
- `Pre-populated merge target` asserts willingness to let hash comparison, latest timestamp, and tree merge operate on a directory that already has material.
- `Local bytes are believed newest` asserts reviewed local superiority strong enough to justify touch or equivalent republish behavior despite incomplete peer truth.

## 3) Contradiction risks

Show contradiction rows such as:

- offline peer returns with newer content
- current path is similar-looking but not the same prior tree
- pre-existing files in target are overwritten or deleted by merge
- hidden Archive / history evidence contradicts local certainty
- current timestamps are not authoritative enough for the planned branch

Each row must show confidence, blast radius, and whether rollback is still possible.

The operator must be able to answer: **what exact contradiction could prove me wrong?**

## 4) Safer weaker alternative

Always show a weaker path, such as:

- `Keep warning visible and wait for peer return`
- `Inspect path lineage before reconnect`
- `Connect to empty sibling directory instead`
- `Inspect Archive and chronology before republish`
- `Export attestation receipt without commit`

The operator must be able to answer: **what is the least-strong action that still moves me forward?**

## 5) Receipt consequence

On commit, issue a receipt that preserves:

- chosen branch
- human assertion used
- evidence reviewed
- contradiction risks left open
- expiry trigger
- stronger blocked sentence

## Primary actions

Examples:

- `Hide warning only`
- `Proceed as same-tree reconnect`
- `Proceed as risky merge target`
- `Republish via reviewed local-newest attestation`
- `Back out and inspect more proof`

Do not use vague primaries such as `Continue`, `OK`, or `Proceed anyway` without the explicit branch phrase.

## What this page must never imply

It must never imply that these are the same:

- hiding a warning and proving absence
- reconnecting the same prior tree and merging into a fresh occupied tree
- reviewing local bytes and proving universal chronology superiority
- operator willingness to risk overwrite and machine proof that overwrite is correct
