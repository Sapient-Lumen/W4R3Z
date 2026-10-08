# Pause language substitution page — freeze, stop, and quiesce claim rewrite interface spec

## Purpose

Operators do not merely apply control actions.
They also talk about them to teammates, incident leads, and future selves.
This page keeps the product from silently encouraging stronger language than the control state earned.

## Core decision

AnonSync should treat `pause` wording as a controlled language problem.
Whenever a requested or implied phrase overclaims the current quiescence class, the product should rewrite it into an earned sentence and explain the delta.

## Fixed page order

1. **Requested phrase**
2. **Earned phrase**
3. **Forbidden stronger phrases**
4. **Residual caveat**
5. **Audience-specific variants**

## 1) Requested phrase

Capture the exact wording, for example:

- `this share is paused`
- `it's frozen for maintenance`
- `nothing can move right now`
- `we stopped the sync`

The page must preserve the original wording so the rewrite is auditable.

## 2) Earned phrase

Render one sentence in large type, for example:

- `Payload transfer is paused; deletions and detection may still continue.`
- `This seat is traffic-quiet, not maintenance-isolated.`
- `Full-byte movement is stopped here; participation and readiness changes remain possible.`

This sentence must be copyable and exportable.

## 3) Forbidden stronger phrases

Show a short list of stronger sentences the product will refuse to endorse.
Examples:

- `Nothing can change now.`
- `The share is frozen.`
- `This is safe for evidence capture.`
- `No propagation can still occur.`

Each forbidden phrase must carry one short reason.

## 4) Residual caveat

The caveat line should name the strongest remaining live lane in one clause, such as:

- `Remote deletes can still alter local state.`
- `Local detection and indexing remain active.`
- `This seat still appears as participating.`

## 5) Audience-specific variants

The product should offer variants tuned for:

- self / notes
- teammate handoff
- admin / maintenance log
- external status note

Each variant must stay within the same truth ceiling.

## Example

```text
Requested phrase ............ The share is frozen.
Earned phrase ............... Payload transfer is paused; deletes and detection may still continue.
Forbidden stronger phrases .. Nothing can change now.
                              Safe for evidence capture.
Residual caveat ............. This seat still participates and may still index local changes.
```

## Commands

```text
anonsync quiesce language review <object>
anonsync quiesce language review <object> --phrase "the share is frozen"
```

## Export rules

Any exported receipt or status message that originates from a quiescence action should use the earned phrase, never the unchecked requested phrase.

## Success condition

A good language-substitution page ensures the operator can communicate quiescence truth without accidentally turning a partial stop into a stronger social claim.
