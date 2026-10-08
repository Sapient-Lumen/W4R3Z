# Remedy-hardening-change-gate contract sheet page — mutation authorization, regression budget, and reseal discipline

## Purpose

This page is the operator's compact contract for whether a case that already achieved recurrence-hardened-and-retained discharge may safely undergo later intentional change without reopening the original cause family.
It exists so the product can distinguish `the hardening still exists now` from `future mutations are safely gated for this case now`.

## Core fields

- case identifier
- source remedy-hardening-retention receipt identifier
- triggering cause family
- current hardening-change-gate posture rung
- current retained-hardening baseline
- proposed change class
- change initiator class
- operational authority class
- cause-safe change authority class
- required review cohort for this change
- required approval threshold for this change
- change scope
- expected regression budget
- required reseal class after application
- change-specific carry-forward exposure
- linked-device spread impact
- standard-versus-advanced sharing impact
- manual-override interaction status
- peer-local rule divergence interaction status
- highest honest current change-governed sentence
- strongest blocked stronger change-governed sentence
- next strengthening trigger
- next weakening trigger

## Remedy-hardening-change-gate posture rungs

The page must model at least these distinct rungs:

- retained hardening achieved; future change gate unreviewed
- broad operational authority present; cause-safe change authority unproven
- proposed change outside current safe envelope
- proposed change review opened
- proposed change approved pending reseal
- proposed change applied under regression debt
- bypassed change reopened cause review
- reseal pending after applied change
- reseal complete; change-governed hardening restored
- recurrence-hardened-retained-and-change-gated discharge achieved
- hardening change gate collapsed or suspended

## Required distinctions

The page must keep these truths separate:

- retained hardening now versus future change safely governed
- broad owner or read-write authority versus cause-safe mutation authority
- proposal reviewed versus proposal approved
- approved without reseal versus approved with mandatory reseal
- change applied versus reseal complete
- harmless-looking local preference change versus change that reopens the original cause family
- one lane safe to change versus every required lane safe to change

## Operator promises

The contract sheet must let the operator say things like:

- `the case remains retained-hardened, but future permission edits are still ungated for this cause family`
- `the operator may change sync behavior broadly, but not in a way that weakens the recurrence guard without opening a new review`
- `this proposed change is allowed only if a reseal proof follows before stronger discharge language returns`
- `the change was applied under temporary regression debt because required-cohort reseal has not finished`
- `future mutation is now governed tightly enough that recurrence-hardened-retained-and-change-gated discharge is honest`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- future change gate unreviewed
- cause-safe authority not proven
- proposed change outside safe envelope
- required cohort not yet reviewed
- approval threshold not yet met
- mandatory reseal still pending
- regression debt active
- bypassed mutation reopened the cause family
- evidence basis too weak to claim governed future change
