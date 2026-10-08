# Presence contract sheet page — row, path, placeholder, byte residency, and source guarantee

## Purpose

Give the operator one first surface for any serious `this file exists here` or `this folder is available here` claim.
The page must stop the product from collapsing UI visibility, path binding, placeholder namespace, local bytes, and future fetchability into one vague `available` status.

## The page must answer

1. Is this object only a remembered row, or does it have a local path?
2. If there is a path, does it contain placeholders, local bytes, or both?
3. Is there at least one currently proven source for full materialization?
4. What destructive or non-destructive gesture is actually allowed from here?
5. What stronger sentence is blocked?

## Core model

### A. Presence class

Represent exactly one current class:

- **Row only / no local path bound**
- **Bound path, namespace empty or unresolved**
- **Placeholder namespace only**
- **Mixed placeholder and materialized content**
- **Fully materialized local content**

### B. Source-guarantee class

Represent exactly one current class:

- **Local bytes self-sufficient**
- **Remote source currently proven online**
- **Remote source known but currently offline**
- **Source not currently proven**
- **Ghost namespace / bytes not known to exist anywhere**

### C. Gesture-authority class

Represent exactly one current class for the action under review:

- **Residency-only mutation allowed**
- **Materialize-on-demand allowed**
- **Delete-from-all authority allowed**
- **Delete-from-all authority blocked**
- **Manual review required before any destructive gesture**

### D. Dependency class

Represent whether this object depends on another source object for bytes:

- **Independent local authority**
- **Depends on parent share for bytes**
- **Depends on remote peer for bytes**
- **Dependency currently unresolved**

## Required warnings

The page must warn when:

- the object is visible in UI but has no bound local path;
- the object has only placeholders and no proven live source for bytes;
- a delete-like gesture would propagate beyond the device;
- `Remove from this device` would only change residency, not shared existence;
- safety rails are altering placeholder deletion semantics;
- the object may be a ghost announcement rather than a retrievable file.

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `visible here means stored here`
- `placeholder means recoverable later`
- `connected means fetchable now`
- `delete from this surface is local-only`
- `local derived copy can materialize bytes without its parent source`

## Required outputs

This page must emit a compact contract object preserving:

- presence class
- source-guarantee class
- gesture-authority class
- dependency class
- strongest safe sentence
- blocked stronger sentence
