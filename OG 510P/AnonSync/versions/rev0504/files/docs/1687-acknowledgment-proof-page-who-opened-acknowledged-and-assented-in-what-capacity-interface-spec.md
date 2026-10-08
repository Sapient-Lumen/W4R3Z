# Acknowledgment proof page — who opened, acknowledged, and assented in what capacity

## Purpose

This page is the durable proof object for the strongest honest recipient-action sentence earned by a given act version.
It exists so later operators can see not merely that the system emitted a signal, but who actually opened the material, who acknowledged it, who assented to it, in what capacity, and what stronger consent sentence remained blocked.

## Sentences this page may support

- `all named participants were notified, but only some opened the corrected publication`
- `the designated principal opened and acknowledged this version, while binding assent remains blocked pending countersign`
- `an owner-approved device action enabled operational continuity, but person-attributed assent was not yet proved`
- `remembered certificate trust allowed reconnect behavior, but fresh assent was still required for the narrowed waiver`
- `the adjudicator acknowledged the recall package, while participant assent was intentionally not required`

## Mandatory proof blocks

### A. Act-and-version proof block

- source act identifier
- source version identifier
- highest recipient-action sentence honestly earned
- strongest blocked stronger sentence
- exact reason the earned sentence stops where it does

### B. Recipient ladder block

- named recipient or audience class
- delivery status
- open status
- acknowledgment status
- assent status
- strongest recipient-specific sentence honestly earned

### C. Capacity proof block

- actor identity used
- whether the actor was a human principal, delegate, linked identity surrogate, owner role, device custodian, or adjudicator
- whether that capacity is sufficient for the exact typed act
- whether substitution was expressly authorized
- strongest blocked stronger sentence if capacity proof remains incomplete

### D. Freshness-and-memory block

- whether prior approval or certificate memory existed
- whether that memory influenced delivery or approval flow
- whether fresh assent was required
- whether fresh assent was actually obtained
- exact reason remembered trust was accepted or rejected for this act

### E. Audit block

- notification evidence bundle identifiers
- open evidence bundle identifiers
- acknowledgment or assent evidence bundle identifiers
- dispute / reopen / supersession identifiers
- next event that could strengthen or weaken the proof

## Required badges

- `notified`
- `opened`
- `acknowledged`
- `assented`
- `fresh-assent-obtained`
- `memory-relied-on`
- `capacity-proven`
- `capacity-under-challenge`
- `person-specific-consent-blocked`
- `binding-effect-blocked`

Badges must stack instead of collapsing meaning.
For example, `notified`, `opened`, and `memory-relied-on` may coexist with `person-specific-consent-blocked`, while `assented` may coexist with `capacity-under-challenge` if the actor identity is later disputed.

## Proof obligations

- prove opening separately from mere delivery
- prove acknowledgment separately from opening
- prove assent separately from acknowledgment
- preserve the exact actor capacity that made each step count
- preserve whether remembered trust was accepted only for a lower-risk rung
- preserve why the product refused a stronger `everyone knowingly agreed` sentence

## Stronger-sentence guard

This page may say `the corrected notice was delivered to all required recipients, one named principal opened and acknowledged it, and one linked-device owner supplied an operational approval, but final person-specific assent remains blocked for the irreversible waiver`.
It may not say `the parties knowingly consented` unless that stronger sentence was actually earned.
