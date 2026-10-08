# Applicability timeline page: facts learned, candidates promoted, and route reversal events interface spec

## Purpose

After the archive learned how to prove doctrine applicability, it still needed one chronology page for operators asking:

> how did this case move from symptom intake to a governing doctrine, and which later fact reversed or strengthened the route?

## Core decision

AnonSync must expose one first-class **Applicability timeline** page for every materially routed case whose doctrine fit evolved over time.

## Required event families

- intake symptom recorded
- candidate precedent surfaced
- candidate precedent disqualified
- primary discriminator chosen
- new fact learned
- evidence contradiction attached
- provisional route declared
- governing doctrine confirmed
- route reversed
- cross-route-safe containment entered
- human adjudication requested
- applicability rereview triggered

## Event-row schema

Each row must show:

- timestamp
- event family
- current leading route before event
- current leading route after event
- fact added or removed
- doctrine weight delta if any
- newly allowed claim
- newly blocked claim
- who caused the change

## Hard rules

### 1) Route reversal is a first-class event

If the leading route changes, the timeline must preserve both the old and new route plus the fact that forced the reversal.

### 2) Facts must precede stronger claims

A stronger doctrine-applicability sentence must not appear before the fact event that justified it.

### 3) Rejected routes remain historical truth

The timeline must preserve what routes were plausible earlier, even after they are disqualified.
That history matters for later doctrine refinement.

## Empty state

If the case never moved beyond obvious single-route intake, show:

- `No extended applicability timeline yet. Intake facts were sufficient for direct routing without live lookalike competition.`
