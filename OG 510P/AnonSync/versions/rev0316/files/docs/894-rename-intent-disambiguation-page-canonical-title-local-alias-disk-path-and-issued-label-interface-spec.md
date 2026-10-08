# Rename intent disambiguation page: canonical title, local alias, disk path, and issued label interface spec

## Purpose

The operator often starts with one vague sentence:

> I want to rename this.

This page exists to turn that sentence into one reviewed intent before any mutation happens.

## Core decision

Any workflow that begins from an ambiguous rename-like affordance must open one first-class **Rename intent disambiguation** page before apply.

The page owns:

- the operator's plain-language intent
- the closest matching verb family
- the likely wrong neighboring verb families
- the audience and continuity consequences for each option

## Fixed page order

1. plain-language intent
2. rename targets grid
3. audience and continuity comparison
4. blocked or projection-limited targets
5. explicit intent commit

### 1) Plain-language intent

Capture and restate the operator's request in ordinary language.
Examples:

- `Make the shared project title different for everyone.`
- `Only call it this on my laptop.`
- `Rename the folder path on disk here.`
- `Send this recipient a different outward label.`

### 2) Rename targets grid

Minimum rows:

- canonical subject title
- local alias on this seat
- disk path / basename on this mount
- future outward label template
- one-off issued artifact label

Minimum columns:

- what changes
- who sees it
- what definitely stays untouched
- whether continuity or receipts are affected
- availability on this projection

### 3) Audience and continuity comparison

This section compares the consequences side by side.
It must answer:

- does this change other active seats
- does this change only this seat
- does this change only future artifacts
- do older artifacts stay on the old wording
- does any filesystem path move or rename occur

### 4) Blocked or projection-limited targets

If the current projection cannot perform one of the target verbs, show:

- target name
- why blocked here
- safest alternative projection or workflow
- whether the alternate changes meaning or only availability

### 5) Explicit intent commit

The operator must choose one typed intent such as:

- `retitle canonical subject`
- `rename local alias only`
- `rename disk path here`
- `set future outward label template`
- `issue one-off outward label`

No generic `continue` button is allowed without a resolved intent.

## Rules

### Rule 1 — ambiguous language triggers choice, not inference

`Rename`, `retitle`, `fix the label`, and similar language must not silently map to one plane.

### Rule 2 — neighboring verbs stay visible

The page must keep the nearest likely misunderstandings adjacent so the operator can reject them consciously.

### Rule 3 — projection limits are compared, not hidden

If the chosen target is unavailable here, the page must say so before opening a different action path.

## Acceptance criteria

A later operator can:

- tell which rename intent was selected
- tell which neighboring intents were consciously rejected
- tell which audience changed
- tell whether any path rename occurred
- tell whether older artifacts kept the old label
