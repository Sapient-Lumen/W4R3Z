# Settings-layer collapse and effective-truth interface spec

## Purpose

The archive already has value-row explanation rules.
What it still lacked was a concrete answer to the navigation and editing seam created by layered settings:

> if one property can be influenced by subject policy, seat defaults, machine defaults, rollout config, and emergency overrides, what single surface tells the operator the **effective truth** without sending them on a scavenger hunt?

Current Resilio docs keep this problem vivid.
Meaning still spans Sync Preferences, Folder Preferences, power-user defaults, and configuration mode.
AnonSync should not clone that layer archaeology.

## Core decision

Every non-trivial mutable property must have one canonical **effective-truth surface**.
That surface shows both:

- the current answer
- the stack of layers that produced it

The operator should never need to cross-reference several dialogs merely to understand one present value.

## The value-stack model

A property should be explainable through one ordered stack.
A typical stack may include:

1. emergency or maintenance override
2. reviewed local exception / pin
3. subject-local durable setting
4. seat or workspace default
5. machine / host default
6. rollout profile or imported config baseline
7. built-in product default

Not every property uses every layer.
But every property should still render in the same grammar.

## The fixed explanation order

The effective-truth surface should render the same sections in the same order:

1. **Effective answer now**
2. **Winning source layer**
3. **Full layer stack**
4. **Future-parent effect**
5. **Severed-or-following status**
6. **Where to edit safely**
7. **How to rejoin higher truth**

## 1) Effective answer now

Show:

- property label
- effective value
- strength / confidence if computation or downgrade is involved
- whether the value is ordinary, degraded, blocked, or temporary

The top line answers `what is true right now?`

## 2) Winning source layer

Show:

- which layer currently wins
- which object or receipt established it
- whether it is durable, temporary, inherited, copied, or computed

This is the antidote to a surface that merely says `None`, `Default`, or `Auto` without telling the operator what kind of truth that actually is.

## 3) Full layer stack

The stack drawer should show every relevant layer in order, including:

- active value at that layer
- whether the layer is currently winning, shadowed, stale, or severed
- whether the layer still receives parent changes
- the last receipt or review object that touched it

A collapsed row may hide detail.
It may not hide the fact that multiple layers exist.

## 4) Future-parent effect

The surface should answer questions like:

- if the machine default changes later, will this subject change too?
- if the rollout baseline changes later, is this seat still following it?
- if a temporary override expires, which layer becomes effective next?

This is where the product proves it understands the difference between `same visible value` and `same inheritance posture`.

## 5) Severed-or-following status

The product must explicitly classify whether the subject is:

- still following a parent layer
- pinned locally
- excepted durably
- temporarily overridden
- copied from a higher layer but no longer following it
- uncertain due to drift or unsupported behavior

This matters because a visually neutral value can still be semantically detached.

## 6) Where to edit safely

The surface should not just say `Edit`.
It should tell the operator what kind of edit they are about to perform:

- edit baseline
- pin here
- create exception
- create temporary lease
- restore following
- inspect rollout source

This is how the product avoids turning layer choice back into hidden semantics.

## 7) How to rejoin higher truth

Every severed value should expose the cleanest honest rejoin action:

- `Restore following`
- `Remove local pin`
- `End override now`
- `Close exception`
- `Reapply rollout baseline`

The operator should never have to infer rejoin from a visually neutral value alone.

## Settings entry points that must converge

The product may still expose convenient page families such as:

- subject settings
- seat defaults
- machine defaults
- rollout profile view
- imported config view

But all of them must converge on the same effective-truth sheet for any specific property.

The operator should be able to start from any one of those pages and still answer:

> why is this property true here right now, and what happens if the higher layer changes tomorrow?

## Table rules

Dense tables may show compact chips like:

- effective value
- source layer
- follow / sever status
- future-effect chip

Expanding the row should open the full stack.
The operator should not need to navigate to four different settings pages to reconstruct that stack.

## CLI rules

CLI should render an equivalent stack, for example:

```text
anonsync setting show share.vault.download_priority --subject shr_vault --explain
```

The output should name:

- effective value
- winning layer
- shadowed layers
- future-parent effect
- restore-follow action when relevant

A textual operator should not be second-class here.

## What the product must refuse

- separate dialogs whose combined meaning is required to understand one value
- `Default` labels that fail to say which layer is actually winning
- neutral values that hide severed inheritance
- edit buttons that obscure whether the operator is editing baseline, pin, exception, or override
- rollout/config views that stamp values without exposing the later effective stack

## Result

A good settings-layer surface prevents five failures:

- current-value archaeology across several menus
- confusing a copied value with an inherited one
- failing to notice when local manual touch severed future parent updates
- changing the wrong layer because the edit surface hid scope
- treating rollout config and live settings as separate truths instead of one layered truth

If the product still requires several settings pages plus a help article to explain one property, AnonSync has not yet collapsed the layer split into a usable contract.
