# Remedy-hardening-attestation actionable-remedy timeline page — stale found, corrected, trusted, acted, confirmed, and remediation horizon closed events

## Purpose

This page is the chronological surface for showing how outsider actionability evolved over time.
It exists to stop the archive from flattening `the correction was eventually trusted` into `late outsiders could remediate themselves at every meaningful moment`.

## Core question

The timeline must answer:

**across the remediation horizon, when did the corrected replacement become trustworthy, when did it become actionable without support, and when did any later dependency or environment break reopen the need for operator help?**

## Required event classes

The timeline must support at least:

- stale artifact encountered
- corrected replacement reached
- supersession trusted
- action path published
- client workaround published
- approval gate cleared
- outsider remediation started
- outsider remediation confirmed
- environment break reopened support need
- remediation horizon closed
- receipt superseded

## Required lanes

The page must show at least these lanes:

- outsider discovery lane
- trust and explanation lane
- remediation path lane
- friction and support lane
- sentence-ceiling lane

## Per-event payload

Every event must preserve:

- event timestamp
- actor or subsystem
- affected client or surface
- action consequence
- evidence source
- sentence consequence

## Visual rules

The timeline must make these differences obvious:

- trustworthy replacement versus actionable remedy
- linked instructions versus same-surface action path
- approval cleared versus operator-free path proven
- remediation started versus remediation confirmed
- quiet period versus support need positively checked and absent

## Required overlays

The interface must support overlays for:

- actionability strength over time
- support dependency count over time
- environment coverage over time
- strongest honest action sentence changes

## Hard rules

The page must never allow:

- a trust event to silently stand in for an action event
- one workaround publication to silently stand in for operator-free remediation
- one confirmed outsider action to silently stand in for horizon-wide actionability
- a quiet period to silently stand in for closed support risk
