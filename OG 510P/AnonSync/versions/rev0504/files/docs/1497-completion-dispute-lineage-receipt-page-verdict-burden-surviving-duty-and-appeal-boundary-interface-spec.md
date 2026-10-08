# Completion dispute lineage receipt page: verdict, burden, surviving duty, and appeal boundary interface spec

## Purpose

After a challenged completion claim is adjudicated, the next operator still needs one compact handoff answer:

> what exactly was challenged, what verdict won, what acceptance still survives, what burden remains unmet, and what may still change on appeal?

## Core decision

AnonSync must expose one first-class **Completion dispute lineage receipt** whenever a completion dispute reaches a stable verdict, even if that verdict is only partial or still appealable.

## Fixed page order

1. **Receipt header**
2. **Challenge summary**
3. **Verdict summary**
4. **Residual-duty summary**
5. **Appeal boundary summary**
6. **Receipt sentence**

### 1) Receipt header

Show:

- dispute id
- source fulfillment attestation id
- latest verdict id
- current stability class
- next review horizon

Supported `stability_class` values:

- `stable-no-appeal-open`
- `stable-appeal-window-open`
- `provisional-pending-rework`
- `provisional-pending-recall`
- `reopened`

### 2) Challenge summary

Required rows:

- challenged sentence
- challenger
- dispute basis
- decisive witness families
- weaker losing witness families

### 3) Verdict summary

Required rows:

- verdict class
- upheld scope
- overturned scope
- narrowed or split scope
- stronger blocked sentence

### 4) Residual-duty summary

Required rows:

- surviving accepted residue
- rework now owed
- downstream packet or certificate weakened
- next forbidden overclaim

### 5) Appeal boundary summary

Required rows:

- appeal owner class
- appeal deadline or no-deadline basis
- new witness needed to reopen
- what remains frozen absent appeal

### 6) Receipt sentence

Render one sentence only:

- `This dispute [verdict] the challenged completion for [scope], leaves [residue-or-none] still accepted, and keeps [overclaim] forbidden unless [appeal basis].`

## Hard rules

- the receipt must survive even when the original completion claim was overturned
- the receipt must tell the next operator what weaker sentence still survives
- the receipt must never hide rework or recall obligations behind a generic `resolved` label

## Required interactions

- **Open source dispute**
- **Open source fulfillment attestation**
- **Open rework mandate**
- **Open recalled packet or downgraded certificate**
- **Open appeal**
