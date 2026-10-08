# Projection parity and surface capability contract interface spec

## Purpose

This document decides how AnonSync should behave across GUI, local web, TUI, and CLI projections.
The goal is not pixel uniformity.
The goal is:

> operators should not need support lore to know whether a given projection can explain, draft, or apply the same semantic action.

This matters because the current Resilio evidence is not just about settings layers.
It also shows meaningful surface differences: WebUI is the default path on Linux and service installs, some help pages still explain browser-specific UI quirks, and some affordances are documented through projection-specific recovery advice.
AnonSync should not repeat that kind of capability folklore.

## Core decision

Every AnonSync projection must preserve the same **capability classes**, even if the rendering differs.
The capability classes are:

- `read-state`
- `explain-state`
- `assemble-draft`
- `review-draft`
- `apply-authorized`
- `export-proof`
- `handoff-to-other-projection`

A projection may vary in layout, density, and interaction style.
It may not quietly change which semantic class exists.

## What parity means here

Parity does **not** mean:

- every shortcut exists everywhere
- every page looks identical
- every projection is equally convenient for every workload

Parity **does** mean:

- the same subject truth can be inspected everywhere
- the same draft object can be reopened everywhere
- unavailable apply paths are declared explicitly rather than silently omitted
- a handoff to another projection is a first-class, truthful action rather than a hidden limitation

## Linux-first implication

Because AnonSync is Linux-first, the **local web projection** is a primary surface, not a fallback.
That means local web must support the full semantic contract for ordinary operation.
It cannot be the place where explanation quality, draft visibility, or mutation clarity becomes second-class.

## Capability matrix rules

### `read-state`

All projections must read subject state, lists, value rows, lanes, receipts, and history summaries.

### `explain-state`

All projections must open proof/explanation for a selected subject.
A CLI may do this as structured text rather than a drawer.
A web UI may do it as a side panel.
The semantic payload must remain the same.

### `assemble-draft` and `review-draft`

All projections must be able to create and reopen draft objects for non-trivial work.
A narrow projection may use sheets or stacked steps.
A CLI may use explicit plan objects and handles.
But the draft cannot become projection-local hidden state.

### `apply-authorized`

If a projection cannot safely complete apply because of current device posture, missing local capability, or policy, it must say so explicitly and offer a handoff that preserves subject, draft handle, and proof context.
It must not merely omit the button and hope the operator guesses.

### `export-proof`

Every projection must be able to export or hand off proof bundles in some legible way, even if the exact affordance differs.

### `handoff-to-other-projection`

Handoff is legitimate.
But it must be explicit, named, and state-preserving.
For example:

- `Open this draft in local web`
- `Print CLI apply command for this reviewed draft`
- `Continue on seat with custody authority`

## Things the product should refuse

- projection-specific truth vocabulary
- features that only exist in one projection without an explicit model reason
- support articles that become the real source of projection semantics
- browser quirks that silently remove a primary action with no substitute explanation
- apply paths that exist only in the desktop projection while Linux/web operators get weaker semantics

## Surface-declared limitation rules

Sometimes a projection really is limited.
That is fine.
But it must declare the limitation in one fixed grammar:

- `what you can inspect here`
- `what you can draft here`
- `what cannot be applied here and why`
- `what exact handoff preserves continuity`

The product should never leave the operator asking whether the action is impossible, merely unavailable in this projection, or hidden behind a different ritual.

## Result

A good projection contract gives AnonSync two benefits at once:

- Linux-first and automation-friendly operation without semantic second-class citizens
- multiple interface forms without capability folklore

If users can truthfully say `the web UI tells a different story than the CLI`, the product has already regressed.
