# Discriminator acquisition lineage receipt page: discriminator, evidence quality, burden, and blocked stronger sentences interface spec

## Purpose

After evidence collection work has happened, the next operator needs one compact receipt that answers:

- what question was actually asked
- what came back
- how good the evidence is
- what burden was spent
- what stronger sentence is now safe
- what stronger sentence is still blocked

## Core decision

Every material evidence-acquisition cycle in AnonSync must end in one durable **Discriminator acquisition lineage receipt**.

## Fixed page order

1. **Receipt header**
2. **Ask-and-return summary**
3. **Quality-and-burden summary**
4. **Route consequence summary**
5. **Blocked-stronger-sentences summary**

### 1) Receipt header

Show:

- receipt id
- source case id
- source acquisition sheet id
- governing route after receipt
- receipt freshness horizon
- current safe claim

### 2) Ask-and-return summary

Required rows:

- selected ask
- fallback used or not
- answer state
- returned fact or artifact class
- who provided it
- when it was captured

### 3) Quality-and-burden summary

Required rows:

- evidence quality
- burden rung spent
- restart or reproduction cost incurred
- privacy or ops intrusion incurred
- unavailable channels that still matter

Hard rule:

The receipt must preserve both value and cost.
A later operator should not re-spend a heavy burden unknowingly.

### 4) Route consequence summary

Required rows:

- route update achieved
- doctrine or intervention consequence
- newly permitted action
- action still blocked pending more evidence
- next best ask if ambiguity survives

### 5) Blocked-stronger-sentences summary

Required rows:

- strongest newly safe sentence
- strongest still blocked sentence
- reason it remains blocked
- event that would unblock it

## Required interactions

- **Open source capture proof**
- **Spawn follow-on acquisition sheet**
- **Mark freshness expired**

## Failure state

If the evidence return was too weak to matter, show:

- `This receipt records burden spent without a material route upgrade. The prior sentence ceiling largely survives.`
