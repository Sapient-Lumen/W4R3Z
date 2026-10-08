# Permission request proof page — trigger origin, OS dialog, and feature boundary interface spec

## Purpose

The archive already has capture-source, alert-delivery, and settings provenance language.
What it still lacked was one exact page for the operator question:

> what exactly triggered this permission request, is it really for the feature I think it is, and how wide is the resulting platform power compared with the feature I was trying to use?

## Core decision

Any non-trivial permission prompt or system-settings handoff must render one first-class **Permission request proof** page.
That page is the semantic home of:

- trigger origin
- requested feature boundary
- broader OS permission scope
- safer nearby path if the operator declines
- prompt/hand-off receipt

## Primary page layout

The page always renders the same top-level regions in the same order:

1. trigger verdict strip
2. origin chain card
3. feature-vs-permission boundary card
4. safer-alternative card
5. handoff / receipt card

### 1) Trigger verdict strip

Show:

- current requested permission family
- triggering feature action
- whether the request is direct, deferred, or surprising
- strongest honest one-line summary

Allowed summaries:

- `QR scan asked for camera access; manual claim path remains available`
- `Write-arrival asked for storage access; inspect-only path still available`
- `Background freshness asked for startup/wake authority; foreground-only use remains viable`
- `Notification setup asked for alert delivery; sync core status remains separate`

### 2) Origin chain card

Show:

- initiating user action
- intermediate product layer that decided to request permission
- OS surface or settings handoff that will appear
- whether the prompt is first-time, repeat, or post-revocation

The operator must be able to answer:

> what action of mine actually caused this prompt?

### 3) Feature-vs-permission boundary card

Show side by side:

- requested feature the operator was trying to use
- broader OS/platform power being requested
- why the broader scope is necessary or legacy-bound
- strongest limitation if granted power exceeds immediate feature need

This card exists to keep product honesty when one small-seeming action needs a wider OS power.

### 4) Safer-alternative card

Show:

- nearest lower-power alternative
- capability lost by choosing it
- whether continuity is preserved
- whether another seat or surface can do the stronger action instead

### 5) Handoff / receipt card

Show:

- exact next system surface
- how to return safely
- whether denial is final or re-promptable
- last prompt receipt if any

## Behavior rules

- This page must appear when the feature boundary and permission scope are not obviously the same thing.
- The product must not pretend the operator requested the broader OS power directly when they only asked for one feature.
- If a same-goal fallback exists, it must be shown before the broader permission is treated as mandatory.
- A post-revocation prompt must show that it is revocation recovery, not first-time setup.

## Compact row contract

A compact row should preserve this order:

1. triggering action
2. permission family
3. feature boundary note
4. safest alternative
5. next honest action

Example:

```text
Scan QR     camera-scan     QR intake only; manual key entry still valid     Enter key manually     Review permission request
```

## Non-clone reason

Current official Resilio docs are candid about why permissions exist, but they still do not give one stable page proving trigger origin, wider OS scope, and fallback path together.
AnonSync should.
