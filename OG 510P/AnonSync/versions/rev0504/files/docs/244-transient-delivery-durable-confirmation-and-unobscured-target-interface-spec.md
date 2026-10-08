# Transient delivery, durable confirmation, and unobscured target interface spec

## Purpose

The archive already had receipt continuity, attention delivery, review rhythm, and local-web shell language.
What it still lacked was one stronger contract for a message-layer honesty problem common to serious interfaces:

> if a consequential outcome is announced through a toast, badge glow, live-region update, snackbar, or other transient cue, where does that meaning live after the moment passes, and how does the operator recover it without trusting memory or timing luck?

Comparative reading made the problem sharper.
Transient delivery can be useful.
It becomes dishonest when the only surviving record of a changed truth, blocker, warning, or next step lived in a message that disappeared, stacked under another, or landed under persistent chrome where the target technically exists but is not actually visible.

## Core decision

AnonSync must treat transient cues as delivery accelerators, never as the sole durable home of consequential meaning.

The product must distinguish:

- transient announcement
- durable inline confirmation
- durable receipt
- next-step requirement
- anchored target reveal

The operator must be able to answer:

- what changed
- where that meaning now lives durably
- whether action is required
- what target the product wants them to inspect
- whether the target is actually visible without manual scrolling archaeology

## Fixed review order

Every consequential outcome surface must render the same sections in the same order:

1. **Outcome class**
2. **Transient delivery**
3. **Durable confirmation**
4. **Next-step boundary**
5. **Landing and visibility receipt**

### 1) Outcome class

Show one explicit class:

- `informational`
- `confirmed success`
- `partial success`
- `warning`
- `blocked`
- `requires review`
- `other`

Severity must describe the meaning of the outcome, not only its visual style.

### 2) Transient delivery

Show any transient layer used:

- toast
- snackbar
- badge glow
- live-region status
- OS notification
- none

If a transient layer fires, it must say:

- why it fired
- whether it auto-dismisses
- whether it may be replaced by a later message
- whether it includes only summary text or any call to action

### 3) Durable confirmation

Show where the meaning survives after the transient moment:

- inline outcome panel
- updated row state
- review queue entry
- durable banner in the same object
- receipt row
- other persistent surface

The same consequence must be recoverable here without needing the transient cue.

### 4) Next-step boundary

Show:

- whether the operator merely needs awareness or must take action
- whether the next step is advisory, required, or safety critical
- where the durable action path lives
- whether the transient layer contained any shortcut only, never the sole controlling path

A disappearing message must not be the only place a consequential control lives.

### 5) Landing and visibility receipt

Record:

- outcome class
- transient layer used or omitted
- durable surface id
- target anchor if any
- whether the target was unobscured on landing
- replacement/dismiss policy
- actor, seat, and time

## Main surface

Every serious workbench, local-web, CLI, and GUI projection should expose one **Last consequential outcome** surface.

That surface should answer:

- `what was the last thing that materially changed`
- `where is its durable explanation now`
- `what still needs attention`
- `did the product only announce this transiently or also preserve it inline`
- `if I followed a link or anchor, did the target actually land visibly`

## Public rules

AnonSync should hold the following rules:

- transient announcements may summarize but must not exclusively store consequential meaning
- warnings and blocked states must remain visible until the surrounding object is no longer in that posture
- anchored targets must remain visible below fixed or sticky chrome
- shortcut actions in transient layers are optional accelerators, never exclusive control points
- multiple transient messages must not overwrite the only durable explanation of a changed outcome

## Acceptance criteria

This spec is satisfied when:

- operators never need to remember a toast in order to reconstruct the last important outcome
- the same outcome remains available in durable inline state and receipt continuity
- target anchors are not considered successful if persistent chrome obscures the landed material
- transient layers can fail, dismiss, or be missed without erasing product truth


## Companion

- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`
