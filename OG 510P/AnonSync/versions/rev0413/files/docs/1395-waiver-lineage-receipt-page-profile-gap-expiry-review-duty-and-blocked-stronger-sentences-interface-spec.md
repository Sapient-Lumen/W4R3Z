# Waiver lineage receipt page — profile gap, expiry, review duty, and blocked stronger sentences

## Purpose

This page provides the smallest durable artifact that later operators can read without reconstructing exception history from memory.

## Core decision

Every serious profile exception must end with one durable **Waiver lineage receipt**.
The receipt preserves:

- what profile was involved
- what subject or cohort diverged
- why the divergence was classified the way it was
- how long the exception is allowed to live
- who must review it
- what stronger claim remained blocked

## Fixed page order

1. receipt strip
2. profile-gap block
3. expiry-and-owner block
4. rollout consequence block
5. blocked-claim block

### 1) Receipt strip

Show:

- waiver id
- profile id
- profile revision
- subject/cohort id
- issue timestamp
- current status

### 2) Profile-gap block

Show:

- exception class
- affected fields
- affected worlds
- intended clean binding class
- currently blocked binding or conformance state
- strongest safe sentence

### 3) Expiry-and-owner block

Show:

- owner
- expiry or rereview timestamp
- renewal posture
- removal condition
- next verification step

### 4) Rollout consequence block

Show:

- blocked / proceed-around / partial-field / no-rollout verdict
- whether values changed
- whether governance changed
- whether conformance counts included or excluded the subject

### 5) Blocked-claim block

State the stronger sentence the product refused to make, for example:

- `This subject conforms to profile rev14.`
- `This rollout covers the full cohort.`
- `This field is supported and effective in Linux WebUI.`
- `This mobile share is governed by the desktop profile without local exceptions.`

## Copy rules

- Never emit a waiver receipt without expiry or stronger justification for no expiry.
- Never hide owner identity.
- Never record only the symptom; record the typed class.
- Never omit whether the subject counted as conformant.
- Never omit the blocked stronger sentence.

## Example strongest-safe sentence patterns

- `Waiver W-204 remains active as an ignored-runtime exception for one field on Linux WebUI; the subject is excluded from clean conformance counts until rereview on 2026-05-01.`
- `Waiver W-311 is a local-parallel mobile-lane exception covering two share-local fields; rollout of the desktop profile proceeds around this subject with no governance claim for the excluded fields.`
- `Waiver W-412 has expired; no stronger cohort-wide conformance sentence may be issued until rereview is completed or the exception is retired.`
