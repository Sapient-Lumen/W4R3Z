# Salvage export page — at-risk residue selection, destination, and claim-ceiling interface spec

## Purpose

The destructive review shell already offers `export residue` and the approval barrier already offers `Approve after export`.
What the archive still lacked was the page that makes that promise concrete.

This page exists to answer:

> before I approve destructive action, what exact at-risk residue am I preserving, where is it going, what does that export actually prove, and what stronger claim does it still not earn?

## Core decision

AnonSync must expose one first-class **Salvage export** page whenever an operator chooses to preserve at-risk local residue before destructive action.
This is not a generic export feature.
It is part of the dangerous-workflow grammar.

## Fixed page order

1. **Export purpose and scope**
2. **Residue selection matrix**
3. **Destination and packaging review**
4. **Post-export claim ceiling**
5. **Actions and next path**

### 1) Export purpose and scope

Show:

- `salvage_export_page_id`
- destructive action this export supports
- scope slice
- current endpoint and acting seat summary
- strongest honest export purpose sentence

Examples:

- `Preserve local edited variants before source-authoritative healing.`
- `Preserve local additions as side-survival before encrypted-seat reset.`

### 2) Residue selection matrix

Show candidate rows for:

- edited local variants
- local renames needing side survival
- local additions that will not rejoin same-line history
- archive-bearing remnants worth lifting out now
- proof-only material whose bytes are not all present locally

Each row must state:

- selected or not
- current holder/locality
- export shape (`full copy`, `manifest only`, `metadata + path proof`, `unknown`)
- same-line vs side-survival consequence
- reason to export now

### 3) Destination and packaging review

Show:

- chosen destination
- packaging class (`directory copy`, `sealed bundle`, `successor branch seed`, `evidence bundle`)
- privacy / audience posture
- integrity witness method
- storage headroom and failure risk

The operator must be able to answer:

> where will the preserved residue live, in what shape, and how will I know the export actually succeeded?

### 4) Post-export claim ceiling

Show:

- strongest safe sentence after this export
- stronger rejected sentence
- what the export does **not** prove
- whether same-line restoration is still absent

Examples:

- safe: `local variants will survive as side residue after destructive heal`
- forbidden: `local variants are now fully restored into shared history`

### 5) Actions and next path

Controls may include:

- `Create salvage export`
- `Create export and return to barrier`
- `Cancel export`
- `Promote successor instead`

A successful export must emit a salvage-export receipt and update the danger context rail.

## Public object

### Salvage export page

Fields:

- `salvage_export_page_id`
- `destructive_action_ref`
- `scope_ref`
- `endpoint_ref`
- `acting_seat_ref`
- `residue_rows[]`
- `destination_review_rows[]`
- `claim_ceiling`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `continuation_controls[]`
- `generated_at`
