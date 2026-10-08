# Support-lane proof page: self-serve, business support, and escalation eligibility interface spec

## Purpose

The investigation sheet says what support lane appears to exist.
This page proves *why* that sentence is safe and *which stronger support promise remains blocked*.

## Core decision

AnonSync must require a **Support-lane proof** whenever the interface names a support receiver, suggests escalation, or implies that a human reviewer can or will inspect evidence.

## Proof layout

1. **Support verdict headline**
2. **Eligibility evidence stack**
3. **Receiver-path table**
4. **Runtime explanation sentence**
5. **Blocked stronger sentence**

### 1) Support verdict headline

Show:

- subject or incident ref
- current support-lane verdict
- strongest safe sentence
- blocked stronger sentence
- proof freshness

Supported verdicts:

- `direct-business-support-eligible`
- `self-serve-feedback-export-only`
- `community-help-lane-only`
- `billing-or-license-web-form-lane`
- `local-retain-only`
- `support-lane-unknown`

### 2) Eligibility evidence stack

Supported evidence classes:

- `edition-or-plan-witness`
- `documented-intake-path-witness`
- `feedback-form-availability-witness`
- `receiver-class-witness`
- `operator-export-success-witness`
- `manual-path-only-witness`
- `unknown-evidence`

Each item must show:

- source
- timestamp
- scope
- confidence
- which lane verdict it governs

The operator must be able to answer:

> what exactly proves that someone can receive this evidence, rather than me merely being able to save it locally?

### 3) Receiver-path table

Each row must show:

- path (`direct ticket`, `feedback form`, `community forum`, `help-center self-serve`, `billing/licensing web form`, `local only`)
- current availability
- expected receiver class
- artifact classes accepted
- limitations
- uncertainty note

### 4) Runtime explanation sentence

This section must emit one exact sentence reusable across surfaces.
Examples:

- `This seat can export evidence automatically, but the documented lane is self-serve rather than direct technical support.`
- `Direct technical support is documented for this lane, but the proof does not establish who will review this artifact or when.`
- `The product can retain evidence locally, but no supported remote intake path is currently proven.`

### 5) Blocked stronger sentence

Examples:

- `An engineer will definitely review this bundle` blocked because the proof only established an export path
- `This community post is equivalent to a support ticket` blocked because receiver class differs
- `This artifact is shareable now` blocked because redaction posture or accepted artifact class was not proven

## Hard rules

- support proof must separate entitlement from mere export capability
- receiver class must stay visible
- local retention may not be misdescribed as escalation
- missing proof must lower the sentence rather than be hidden inside a generic `contact support` label
