# Evidence packet lineage receipt page: custody, redaction, integrity, and audience boundary interface spec

## Purpose

After evidence has been shaped and exported, the next operator needs one compact receipt that answers:

- what source artifacts fed this packet
- what packet form actually left
- what was redacted or transformed
- who held custody
- what audience saw it
- what integrity and usability ceiling now survives

## Core decision

Every material evidence-packet lifecycle in AnonSync must end in one durable **Evidence packet lineage receipt**.

## Fixed page order

1. **Receipt header**
2. **Source-and-form summary**
3. **Custody-and-transformation summary**
4. **Export-and-validation summary**
5. **Integrity-and-boundary summary**

### 1) Receipt header

Show:

- receipt id
- source case id
- source packet sheet id
- live packet version
- receipt freshness horizon
- current safe packet claim

### 2) Source-and-form summary

Required rows:

- source artifacts used
- source world
- packet form exported
- audience class
- strongest reserve packet still retained locally
- raw source retained or not

### 3) Custody-and-transformation summary

Required rows:

- custody owner chain
- redaction class
- transformation steps
- diagnostic power weakened
- reconstructable from source or not
- recall path available or not

Hard rule:

The receipt must preserve both what the packet includes and what it no longer includes.

### 4) Export-and-validation summary

Required rows:

- transport path
- export state
- destination validation state
- packet usable for stated purpose or not
- superseded or recalled packet ids still relevant
- stale audience exposures still relevant

### 5) Integrity-and-boundary summary

Required rows:

- strongest safe evidentiary sentence
- strongest blocked evidentiary sentence
- reason the stronger sentence remains blocked
- event that would upgrade the ceiling
- event that would downgrade or revoke the ceiling

## Required interactions

- **Open source packet sheet**
- **Open export proof**
- **Mark packet stale**
- **Spawn stronger superseding packet**

## Failure state

If the packet cannot be trusted enough for ordinary reuse, show:

- `This receipt records a packet whose form, custody, or validation ceiling is too weak for normal reuse. Re-export or stronger source access is required.`
