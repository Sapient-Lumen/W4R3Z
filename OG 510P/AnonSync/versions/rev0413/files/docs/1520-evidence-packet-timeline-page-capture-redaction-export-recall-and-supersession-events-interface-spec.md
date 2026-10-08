# Evidence packet timeline page: capture, redaction, export, recall, and supersession events interface spec

## Purpose

Operators need one durable chronology that explains how a packet changed over time:

- when raw evidence was captured
- when it was redacted or transformed
- when it was exported
- when it failed, was recalled, or was superseded
- which audiences saw which version

## Core decision

Every material evidence-packet lifecycle in AnonSync must have one first-class **Evidence packet timeline**.

## Fixed page order

1. **Timeline header**
2. **Packet-version ladder**
3. **Custody events card**
4. **Audience exposure card**
5. **Supersession-and-recall card**
6. **Timeline sentence**

### 1) Timeline header

Show:

- timeline id
- source packet sheet id
- current live packet version
- current audience exposure posture
- current strongest safe packet statement

### 2) Packet-version ladder

Each version row must show:

- version id
- packet form
- redaction class
- created from which predecessor
- current status
- current audience scope

Supported `current_status` values:

- `draft-only`
- `held-local`
- `exported-live`
- `partially-received`
- `validated-live`
- `recalled`
- `superseded`
- `retired-archive-only`

Hard rule:

Later versions may not erase earlier exposures.
The timeline must preserve which weaker or riskier packet actually left the system.

### 3) Custody events card

Supported event kinds:

- `captured`
- `reshaped`
- `redacted`
- `checksummed`
- `exported`
- `receipt-confirmed`
- `opened`
- `validated`
- `rejected`
- `recalled`
- `superseded`
- `deleted-local-copy`

Hard rule:

Every transformation and export must preserve who performed it and against which packet version.

### 4) Audience exposure card

Required rows:

- audience that saw each version
- first exposure time
- last confirmed usable time
- audience still holding stale packet or not
- re-notification needed or not

Hard rule:

Audience exposure is not binary.
Different audiences may hold different packet generations at once.

### 5) Supersession-and-recall card

Required rows:

- active superseding packet
- stale packet versions still in the wild
- recall path attempted
- acknowledgment of recall or not
- strongest sentence still unsafe because stale packets persist

Hard rule:

Recall must preserve uncertainty.
A recalled packet is weaker than a definitely withdrawn packet from every destination.

### 6) Timeline sentence

Render one sentence only:

- `Packet lineage is currently at [live version]; earlier packet [older version] is [status], and audience exposure remains [exposure posture], so the safe packet statement is [sentence].`

## Required interactions

- **Add packet version**
- **Log transformation event**
- **Log export or validation event**
- **Mark packet recalled or superseded**
- **Record stale-packet exposure**

## Failure state

If version history is broken, show:

- `Packet chronology is incomplete. Audience reliance must stay below the normal export ceiling until custody continuity is restored.`
