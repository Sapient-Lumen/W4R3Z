# Remedy-cutover contract sheet page — authoritative switch, writer freeze, and conflict fence

## Purpose

This page is the operator's compact contract for whether a landed cure has actually become the live authoritative state.
It exists so the product can distinguish `the repair landed` from `the repair is now the state that downstream writers and readers are supposed to treat as current`.

## Core fields

- case identifier
- source remedy-landing receipt identifier
- current remedy-cutover posture rung
- intended authoritative object identifier
- intended authoritative target and namespace
- intended writer cohort
- intended reader cohort
- current writer-freeze posture
- current reader-switch posture
- live lock-holder posture
- unlocked-writer exposure posture
- timestamp-rebound exposure posture
- database-time versus mtime ambiguity posture
- conflict-artifact posture
- read-only invalidation posture
- platform lock-coverage posture
- app-semantic lock-coverage posture
- strongest blocked stronger cure sentence
- next strengthening trigger
- next weakening trigger

## Remedy-cutover posture rungs

The page must model at least these distinct rungs:

- cutover requested
- landed pending writer freeze
- landed pending reader switch
- split live state detected
- cutover blocked by live lock holder
- cutover blocked by unlocked writer risk
- cutover blocked by timestamp-rebound risk
- authoritative pilot cutover
- authoritative required-cohort cutover
- cutover collapsed by conflict rebound
- cutover verification collapsed

## Required distinctions

The page must keep these truths separate:

- landed object versus authoritative live object
- writer freeze versus reader visibility
- lock present versus cutover safe
- no lock present versus no writer risk
- latest mtime versus latest database-time winner
- conflict artifact present versus authoritative switch complete
- pilot cutover versus required-cohort cutover
- read-only display of the fixed state versus safe live participation in the cutover

## Operator promises

The contract sheet must let the operator say things like:

- `the repair landed, but one editor still holds the file open, so cutover remains pending writer freeze`
- `the landed fix is visible to all readers, but live Windows locking does not cover one required non-Windows writer cohort, so authoritative cutover remains blocked`
- `the object landed and old readers switched, but simultaneous edits can still rebound by database-time or mtime rules, so the stronger sentence remains blocked`
- `a .Conflict artifact exists, so the honest sentence is split live state rather than clean authoritative cutover`
- `the read-only cohort now reflects the repaired state, but that does not count as a symmetric writer-side cutover`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- live exclusive lock holder
- absent or partial writer freeze
- timestamp or database-time rebound risk
- conflict artifact or split-state residue
- non-covered platform or application lock lane
- read-only invalidation instead of true participation
