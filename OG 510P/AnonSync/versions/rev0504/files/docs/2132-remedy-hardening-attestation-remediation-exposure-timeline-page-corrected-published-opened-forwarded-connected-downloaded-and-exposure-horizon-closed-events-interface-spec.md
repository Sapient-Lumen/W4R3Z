# Remedy-hardening-attestation remediation-exposure timeline page — corrected published, opened, forwarded, connected, downloaded, and exposure horizon closed events

## Purpose

This page is the chronological surface for showing how outsider remediation and exposure budget changed over time.
It exists to stop the archive from flattening `a late outsider could remediate` into `the remediation path stayed safely bounded throughout the exposure horizon`.

## Core question

The timeline must answer:

**across the exposure horizon, when did the corrected replacement become self-service, when did that path remain bounded, and when did forwarding, permission widening, or durable residue reopen exposure beyond budget?**

## Required event classes

The timeline must support at least:

- corrected replacement published
- remediation carrier issued
- approval posture changed
- outsider opened carrier
- outsider connected or downloaded
- outsider forwarded carrier or copy
- permission widened
- peer disconnected or revoked
- residue retired
- exposure exception discovered
- exposure horizon closed
- receipt superseded

## Required lanes

The page must show at least these lanes:

- carrier issuance lane
- outsider remediation lane
- forwarding and widening lane
- residue retirement lane
- sentence-ceiling lane

## Per-event payload

Every event must preserve:

- event timestamp
- actor or subsystem
- affected carrier or surface
- exposure consequence
- evidence source
- sentence consequence

## Visual rules

The timeline must make these differences obvious:

- remediation available versus remediation bounded
- approval gate changed versus exposure retired
- download complete versus residue retired
- revocation of future updates versus removal of prior copies
- quiet period versus positive proof that leak budget is closed

## Required overlays

The interface must support overlays for:

- effective audience breadth over time
- permission-widening posture over time
- residue count over time
- strongest honest safe-remedy sentence changes

## Hard rules

The page must never allow:

- a remediation event to silently stand in for an exposure-safe event
- a revocation event to silently stand in for residue retirement
- a single narrow download to silently stand in for horizon-wide boundedness
- a quiet period to silently stand in for closed leak budget
