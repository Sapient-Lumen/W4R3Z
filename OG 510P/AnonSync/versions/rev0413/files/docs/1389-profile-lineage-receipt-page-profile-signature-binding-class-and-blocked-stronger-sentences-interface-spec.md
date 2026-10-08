# Profile lineage receipt page — profile signature, binding class, and blocked stronger sentences

## Purpose

This page is the durable handoff object for reusable policy:

> which exact profile and revision were involved, what binding class was proven, what action was taken or withheld, and what stronger profile sentence did the product refuse to make?

## Core decision

Every serious profile inspection, conformance review, or rollout must emit one durable **Profile lineage receipt**.
The receipt is the smallest artifact that later operators can trust without replaying the whole workflow.

## Required receipt fields

The receipt must include:

- canonical profile id
- profile title
- profile revision id
- field coverage hash or signature
- focused subject or cohort id
- world id or world scope
- proven binding class
- conformance grade if reviewed
- rollout action taken or withheld
- changed-field count
- blocked-subject count if applicable
- witness confidence
- strongest safe sentence
- blocked stronger sentence
- author and timestamp

## Rendering rules

### Header

Show:

- profile title
- profile id
- revision id
- receipt class: `inspection`, `conformance`, `rollout`, `rejoin`, `branch`, `retirement`

### Signature block

Show:

- field coverage signature
- supported world scope
- supported subject classes
- activation class summary

### Binding block

Show exactly one binding class verdict:

- `live-inherit`
- `field-pin`
- `frozen-snapshot`
- `branched-profile`
- `unbound`
- `unknown`

If more than one subject is included, show counts by class and explicitly mark the strongest class not universally proven.

### Action block

Show what happened:

- no mutation, inspection only
- bound live
- preserved pins
- snapshot captured
- branch created
- rejoined live profile
- left unbound
- rollout blocked

### Safety language block

The receipt must preserve:

- strongest safe sentence
- blocked stronger sentence
- reason that stronger sentence remains blocked

## Hard rule

A receipt may not use `on profile` or `matches profile` language without recording the exact binding class and conformance grade that justified it.

## Example strongest-safe sentence patterns

- `This subject is live-bound to profile backup-wan-safe rev13 for all covered fields.`
- `This subject currently matches profile rev13 values but remains a frozen snapshot outside future live adoption.`
- `This cohort was rolled to rev13 with pins preserved on two covered fields.`
- `This world remains outside supported profile scope, so no profile-membership claim is made.`

## Blocked stronger sentence patterns

- `Blocked: "all subjects are on profile rev13" — three subjects remain unbound value matches only.`
- `Blocked: "this subject will follow future profile changes" — binding class is frozen snapshot.`
- `Blocked: "profile governs this whole deployment" — service/config worlds remain outside supported scope.`
- `Blocked: "rejoin complete" — live inheritance has not yet been re-proven.`
