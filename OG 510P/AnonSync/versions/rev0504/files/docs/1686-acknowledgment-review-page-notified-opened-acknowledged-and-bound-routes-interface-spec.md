# Acknowledgment review page — notified, opened, acknowledged, and bound routes

## Purpose

This page is the operator review surface for deciding what recipient-action sentence is honestly earned for a given act version.
It exists so the product can review lower rungs and stronger blocked rungs without collapsing them into a single approval story.

## Core questions

The review must let the operator answer all of the following without leaving the page:

- who merely had a notification delivered
- who actually opened the message or underlying act
- who acknowledged understanding of the relevant version
- who assented to be bound by the typed effect
- in what capacity each step was taken
- whether remembered approval, linked identity, or owner status was used as a substitute and whether that substitution is allowed
- which stronger consent sentence remains blocked and why

## Mandatory review routes

### Route 1 — Notification route

Use when the product must decide whether the act actually reached a target at all.
Expose separately:

- delivery attempted
- delivery confirmed
- delivery synced across devices only
- unreachable target
- ambiguous target identity
- notification stale

### Route 2 — Open-proof route

Use when notification alone is too weak.
Expose separately:

- not opened
- opened by device unknown actor
- opened by named actor
- open proof disputed
- open proof expired or stale
- open proof inherited from previous version and therefore too weak

### Route 3 — Acknowledgment route

Use when the actor must affirm awareness without yet binding themselves to the strongest effect.
Expose separately:

- acknowledged this version
- acknowledged earlier version only
- acknowledgment ambiguous on scope
- acknowledgment in wrong capacity
- acknowledgment withdrawn or superseded
- acknowledgment blocked pending clarification

### Route 4 — Assent route

Use when typed effects require actual consent or binding acceptance.
Expose separately:

- assent complete
- assent partial
- countersign missing
- assent executed by identity substitute
- assent executed by device-only actor and therefore too weak
- assent contested or reopened

### Route 5 — Freshness-and-memory route

Use when a prior approval, certificate, or remembered trust relation exists.
Expose separately:

- fresh assent not required
- fresh assent required because content changed
- fresh assent required because actor role changed
- fresh assent required because correction or recall narrowed rights
- remembered trust allowed only for connectivity or low-risk acts
- remembered trust forbidden for irreversible acts

## Required comparisons

The review must keep these comparisons explicit:

- `notification delivered` vs `opened by named actor`
- `opened by named actor` vs `acknowledged this version`
- `acknowledged this version` vs `assented to the typed effect`
- `device-level action` vs `human-capacity action`
- `historical approval memory` vs `fresh assent`

## Required badges

- `notified-only`
- `opened-actor-uncertain`
- `opened-named-actor`
- `acknowledged-this-version`
- `assent-partial`
- `assent-complete`
- `fresh-assent-required`
- `memory-too-weak`
- `capacity-disputed`
- `binding-effect-blocked`

## Failure modes the page must prevent

- collapsing delivery, reading, understanding, and assent into one step
- letting linked-device mirroring quietly erase who actually acted
- mistaking owner capability for sufficient assent to a fairness-critical act
- letting a remembered certificate relationship stand in for fresh assent after a correction or narrowed publication
- forgetting that a lower-rung truth may still coexist with a blocked stronger consent sentence

## Stronger-sentence guard

The review may say `notifications reached all linked devices, one named principal opened and acknowledged the corrected version, but final assent remains blocked because the second required releasor has not countersigned`.
It may not say `the correction was accepted by the cohort` unless the exact assent threshold is truly met.
