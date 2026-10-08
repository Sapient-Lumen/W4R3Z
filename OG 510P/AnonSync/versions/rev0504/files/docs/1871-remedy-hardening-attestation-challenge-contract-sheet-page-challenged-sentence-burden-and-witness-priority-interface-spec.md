# Remedy-hardening-attestation-challenge contract sheet page — challenged sentence, burden, and witness priority

## Purpose

This page is the operator's compact contract for a case whose strongest current attestation sentence has been challenged after the product already achieved seal, freshness, and corroboration.
It exists so the product can distinguish `a problem report arrived` from `the previously strongest sentence is now frozen, narrowed, overturned, or restored under explicit burden and witness rules`.

## Core fields

- case identifier
- source attestation-corroboration receipt identifier
- challenged sentence identifier
- exact challenged sentence text
- current pre-challenge highest honest sentence
- challenge type
- challenger class
- challenge opening time
- temporary freeze scope
- allowed weaker sentence during challenge
- forbidden stronger sentence during challenge
- burden class
- required witness priority ladder
- required evidence planes for ruling
- current decisive witness family
- current losing witness family set
- support-only evidence flag
- restart-gated evidence flag
- fresh capture required flag
- rework required flag
- reseal required flag
- current ruling posture
- narrowed surviving sentence
- strongest blocked stronger sentence
- next strengthening trigger
- next weakening trigger

## Challenge types

The page must model at least these distinct challenge families:

- freshness challenge
- integrity or tamper challenge
- world-continuity challenge
- storage corruption challenge
- invalid-clock or chronology challenge
- source-absence or fetchability challenge
- stale-presentation challenge
- contradiction-between-planes challenge
- support-log-only challenge
- operator-workflow contamination challenge

## Required distinctions

The page must keep these truths separate:

- challenge opened versus challenge upheld
- challenge-open sentence freeze versus sentence collapse
- weaker sentence surviving versus no safe sentence surviving
- support evidence captured versus adjudicated ruling earned
- repair attempted versus challenge resolved
- restart or re-add performed versus continuity preserved
- one plausible witness versus winning witness by rule
- historical corroboration versus current standing after challenge

## Operator promises

The contract sheet must let the operator say things like:

- `the strongest corroborated sentence is frozen while the challenge is reviewed, but a narrower sentence still survives`
- `the challenge currently defeats only freshness, not historical integrity`
- `the service-file or database warning reopened continuity, so the old world-specific sentence cannot keep speaking`
- `support logs were captured, but the ruling is still provisional because the decisive witness has not yet outranked the contradictory plane`
- `the challenge was adjudicated and the stronger sentence is restored only after reproof and reseal`

## UI behavior

The page must visually scar any blocked stronger sentence with the exact blocker class:

- challenge open
- decisive witness missing
- burden not yet met
- only support-lane evidence present
- continuity break unresolved
- contradiction still open
- rework pending
- reseal pending
- appeal or reopen window active
