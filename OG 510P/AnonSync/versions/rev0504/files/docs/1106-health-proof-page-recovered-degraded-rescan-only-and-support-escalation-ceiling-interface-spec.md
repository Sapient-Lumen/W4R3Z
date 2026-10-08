# Health proof page: recovered, degraded, rescan-only, and support-escalation ceiling

This page exists so a cleared badge or resumed movement does not overclaim full health.
After a repair rung, the product still needs to prove whether the subject returned to live healthy observation, only fell back to rescan-only degraded operation, remains locally blocked, or merely reached the point where support escalation is now the strongest safe move.

## Operator question

> What health claim is actually proven after the attempted repair, and what stronger `fixed` sentence is still blocked?

## When this page must appear

Render whenever:

- a warning clears after repair
- transfer resumes after a lock or restart
- watcher budget changes or rescans are triggered
- a subject is reconnected or re-added
- memory-pressure mitigation is attempted
- support escalation becomes the next strongest move

## Fixed page order

1. **Repair rung just attempted**
2. **Observed post-repair signals**
3. **Proven health rung**
4. **Blocked stronger sentence**
5. **Escalation / watch boundary**

## 1) Repair rung just attempted

Show:

- receipt id of the attempted repair
- whether the attempt was nondestructive, destructive-local, or coordinated-destructive
- when it completed

The operator must be able to answer: **what exact intervention is this proof evaluating?**

## 2) Observed post-repair signals

Show:

- warning cleared or persisted
- transfers resumed or remained blocked
- live watcher posture or rescan-only posture
- lock list cleared or unchanged
- state-spine recreation success or failure
- memory-pressure symptom reduced, unchanged, or unknown

The operator must be able to answer: **what changed afterward, and what did not?**

## 3) Proven health rung

Allow only one proof verdict:

- `fully-recovered-live-observation-proven`
- `recovered-transfer-but-detection-still-degraded`
- `warning-cleared-but-proof-still-thin`
- `still-blocked-locally`
- `still-suspended`
- `escalate-with-evidence`
- `unknown`

The operator must be able to answer: **what is the strongest honest health sentence right now?**

## 4) Blocked stronger sentence

Show the next stronger sentence that remains blocked, such as:

- `fully healthy again`
- `safe to close the incident`
- `no more local blocker`
- `no state was lost`
- `no further escalation needed`

And show exactly which witness is missing.

The operator must be able to answer: **why is `fixed` still maybe too strong?**

## 5) Escalation / watch boundary

Offer:

- `Keep watching`
- `Return to triage`
- `Escalate with captured evidence`
- `Cross next repair rung`

Show:

- minimum evidence bundle required for escalation
- watch window after which proof expires or must be rechecked

## What this page must never imply

It must never imply that these are the same:

- warning gone and health proven
- resumed transfer and live watcher restoration
- recreated sidecar and restored continuity of all hidden history
- reduced pressure and durable future safety
- escalation-ready and diagnosis-complete

## Receipt / audit consequence

The proof receipt must preserve attempted rung, post-repair signals, proven health rung, blocked stronger sentence, and escalation/watch boundary.
