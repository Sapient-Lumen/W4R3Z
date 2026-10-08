# Remedy-hardening-attestation affected-party-closure contract sheet page — notice, delivery, acknowledgement, objection, and closure

## Purpose

This page is the compact contract for a case whose operational remediation may already be complete, but whose closure still depends on whether materially affected parties were actually reached, acknowledged the remedy, accepted it, or left the matter contested.
It exists so the product can distinguish `remedy issued`, `delivery attempted`, `delivery proven`, `acknowledgement received`, `objection window still live`, `accepted for named cohort`, and `contested or reopened`.

## Core fields

- case identifier
- source downstream-effects receipt identifier
- current governing receipt identifier
- current affected-party-closure class
- required materially affected cohort definition
- named materially affected parties count
- unknown materially affected parties flag
- required notice channels
- notice attempt count
- delivery-proven count
- delivery-unproven count
- hard-bounced or unreachable count
- acknowledgement-required count
- acknowledgement-received count
- acknowledgement-refused count
- silent-after-delivery count
- objection-window policy class
- earliest open objection deadline
- latest open objection deadline
- contested-party count
- accepted-party count
- timed-out-uncontested count
- reopened-after-acceptance count
- dispute owner
- escalation owner
- strongest currently safe closure sentence
- strongest blocked closure sentence
- next evidence that upgrades closure confidence
- next evidence that forces contest, escalation, or downgrade now

## Affected-party-closure classes

The page must model at least these distinct classes:

- materially affected cohort not yet defined
- notice obligation defined, no delivery attempt yet
- notice attempted, delivery proof incomplete
- delivery proven for named cohort only
- acknowledgement pending for named cohort
- acknowledgement received, objection window open
- contested by named cohort
- accepted for named cohort only
- objection window lapsed uncontested for named cohort only
- broader closure blocked by unreachable or unknown cohort
- reopened after prior closure sentence

## Notice channel classes

The page must support at least these channel types:

- in-product notification surface
- email or message delivery
- API or webhook notice
- exported report or receipt delivery
- human meeting or call summary
- regulator or contractual notice lane
- customer or partner support lane
- unknown historical notice lane

## Fixed rendering order

Every affected-party-closure contract sheet must render the same sections in the same order:

1. **Strongest currently closure-safe sentence**
2. **Required materially affected cohort and notice coverage**
3. **Delivery proof, acknowledgement state, and objection windows**
4. **Contest, acceptance scope, and blocked stronger closure language**
5. **Next evidence that upgrades or collapses the closure claim**

## Hard rules

The page must never silently upgrade:

- `remediation issued` into `affected parties reached`
- `notification surfaced somewhere` into `delivery proven`
- `delivery proven` into `acknowledged`
- `acknowledged` into `accepted`
- `accepted by one named cohort` into `uncontested global closure`
- `no contest observed yet` into `objection window closed`
- `disconnect or permission change` into `affected-party acceptance`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- who materially had to be told
- how delivery was attempted and what actually landed
- who had to acknowledge versus who only needed notice
- whose objection windows are still open
- who accepted, who contested, and who remains silent
- whether the strongest honest sentence is operational closure only, acknowledged closure for a named cohort, uncontested closure for a named cohort, or contested / reopened status
