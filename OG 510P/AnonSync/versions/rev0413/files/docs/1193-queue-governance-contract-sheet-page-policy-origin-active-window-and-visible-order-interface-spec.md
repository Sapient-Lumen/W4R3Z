# Queue-governance contract sheet page — policy origin, active window, and visible order

## Purpose

Give the operator one first surface for any serious download-priority claim.
The page must stop the product from collapsing `default`, `override`, `queue order`, `UI order`, and `completion promise` into one badge.

## The page must answer

1. What policy origin currently governs this subject?
2. Does the subject still inherit the current global default, or has inheritance already been severed by a past manual change?
3. What comparator is actually in force now: none, smaller first, larger first, older first, or newer first?
4. Is the subject currently inside the active prioritized window or outside it?
5. Is the visible queue order a faithful witness of scheduling order or only a convenience list?
6. What stronger sentence is blocked?

## Core model

### A. Policy origin

Represent exactly one current origin:

- **Global default, live inheritance**
- **Per-share manual override**
- **Former-manual sticky local state**
- **Single-file inherited default**
- **No priority policy active**

### B. Comparator truth

Represent exactly one current comparator:

- `None`
- `Smaller first`
- `Larger first`
- `Older first`
- `Newer first`

### C. Active-window scope

Represent whether the item is:

- inside the active prioritized window
- outside the active prioritized window
- not yet admitted
- admitted but scheduler exceptions currently apply

### D. Visible-order trust

Represent whether:

- visible order matches effective order
- visible order may differ from effective order
- visible order is unknown / not inspectable on this surface

## Required warnings

The page must warn when:

- a share was ever manually altered and therefore no longer inherits later global default changes
- `None` is being shown after a manual override, because operators often misread this as `back to inherited`
- the active queue is at or above its practical cap and waiting files are outside current prioritization scope
- current files are non-splittable or otherwise covered by documented exception ceilings
- visible queue order is not trustworthy evidence of actual scheduler order

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `this share is back on the global default`
- `everything in backlog is prioritized`
- `what you see listed first will download first`
- `higher priority guarantees uninterrupted completion`

## Required outputs

This page must emit a compact contract object preserving:

- policy origin
- comparator
- inheritance status
- active-window scope
- visible-order trust
- blocked stronger sentence
