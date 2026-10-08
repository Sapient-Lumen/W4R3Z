# Inherited-versus-excepted value explanation interface spec

## Purpose

This document defines the value-row contract for policy, runtime, and effective-setting surfaces.
The problem is simple:

> showing the current value is not enough if the operator cannot also tell whether the value is still inheriting and what would happen if the baseline changed tomorrow.

That is now one of the strongest lessons from the current Resilio pass.

## Why this matters now

Current official Resilio docs show several layers of behavior at once:

- per-share settings
- host-level defaults
- power-user defaults
- configuration-mode copied values
- local/share-specific special cases
- support rituals for undoing or rejoining a preferred baseline

The small but load-bearing example is the current download-priority behavior: a share can stop following the global default after local manual change even if the visible per-share value later looks like `None` again.
That means the interface needs one more fact than `value = None`.
It also needs `source = no longer inheriting`.

## Core decision

Every non-trivial value row should expose at least these fields:

- property label
- effective value
- source state
- source reference, if one exists
- baseline effect if the parent changes later
- rejoin posture
- freshness / confidence

Dense views may compress these into chips or columns.
Narrow and textual views may stack them.
The semantics must remain intact.

## Source states

The row should classify itself into one of these states:

### `baseline`

This subject is the authoritative baseline for this property.
There is no higher parent in the relevant scope.

### `inherits`

The subject currently follows a parent value and will change when that parent changes.

### `pinned-local`

The subject currently has a direct local pin.
It does not follow parent changes until the pin is removed.

### `exception`

The subject differs through an approved durable exception.
The row should link directly to that exception object.

### `temporary-override`

The subject differs through a leased override with an expiry or other end condition.
The row should show what happens at expiry.

### `copied-static`

The subject started from a template/profile/config value but is no longer linked to ongoing parent change.
This state should be used sparingly and rendered prominently because it is easy to misread as inheritance.

### `computed`

The value is derived from other visible values rather than directly set here.
The row should link to the compute explanation.

### `unsupported-fallback`

The requested semantic is not fully supported on this subject, so the effective value is an approximation or fallback.
The row should explain the downgrade.

### `unknown-drift`

Observed state differs, but the product cannot yet prove whether that came from pin, exception, stale copy, unsupported behavior, or ordinary drift.
This is a reviewable state, not just a weak badge.

## Row anatomy

A good default row should read like this:

- **Property:** `Download priority`
- **Effective:** `None`
- **Source:** `Pinned locally` / `Inherits from baseline` / `Exception` / etc.
- **If baseline changes:** `No effect` / `Would update` / `Needs review` / `Unknown`
- **Rejoin:** `Remove pin` / `Expires automatically` / `Close exception` / `Already inheriting`

This is intentionally verbose in concept.
Clients may render it more compactly.

## Explanation drawer

Opening a value row should reveal one fixed explanation drawer with these sections:

1. **Why this value is true now**
2. **What object supplied or derived it**
3. **Whether parent changes still flow here**
4. **What would happen under a proposed parent change**
5. **How this subject would rejoin baseline**
6. **What other subjects share the same source or exception**
7. **Recent receipts affecting this value**

That order should stay stable.

## Allowed mutations from the row

A value row may offer these actions where relevant:

- `Edit baseline`
- `Pin here`
- `Create exception`
- `Create temporary override`
- `Restore inheritance`
- `Promote exception to baseline`
- `Explain downgrade`

It should not offer a vague `Customize` action if the choice between pin, exception, lease, and baseline edit materially changes future behavior.

## Baseline-change preview rule

When editing a baseline, the product should be able to classify dependent rows into at least:

- would change automatically
- would not change because pinned
- would not change because excepted
- would change only after lease expiry
- cannot be predicted safely yet

This preview is one of the main reasons the row model exists.

## Table and narrow-surface rules

### Dense table views

Dense tables may abbreviate source states into chips, but they should still preserve:

- effective value
- source chip
- baseline-effect chip
- quick explain affordance

### Narrow / textual views

Textual views may render rows like:

`download-priority: none | source: pinned-local | baseline: no-effect | rejoin: restore-inheritance`

The wording can vary.
The semantic fields should not.

## Result

A good value-row model prevents several common operator mistakes:

- mistaking a copied static value for an inherited one
- assuming a visually neutral value still follows baseline
- forgetting that a special case is temporary rather than durable
- forgetting how to rejoin baseline later
- editing a baseline without understanding real blast radius

If the interface only shows the current value and hides the source story, it is not honest enough for AnonSync.
