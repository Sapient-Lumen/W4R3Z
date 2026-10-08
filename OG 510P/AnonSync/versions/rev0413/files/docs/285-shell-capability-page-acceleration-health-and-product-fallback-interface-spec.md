# Shell capability page — acceleration health and product fallback interface spec

## Purpose

The archive already commits to local web, CLI, and API parity.
What it still lacked was one explicit page for a very ordinary question:

> on this seat, for this path class, which shell or file-manager accelerators are actually healthy, which actions do they accelerate, and what product-native path remains when the shell is absent or degraded?

This page exists so AnonSync can benefit from shell acceleration without making shell integration the semantic home of the product.

## Core rule

Shell integration is an accelerator, not an authority boundary.
The product may light up Finder / Explorer / file-manager gestures when available, but the product-native workbench and CLI must still own the canonical meaning.

## Fixed review order

Every serious shell-capability page should render the same sections in the same order:

1. **Current acceleration verdict**
2. **Action parity ledger**
3. **Health and blockers**
4. **Product-native fallback**
5. **Receipt and diagnostic export**

### 1) Current acceleration verdict

This section should answer:

- which seat and surface family are under review
- whether shell acceleration is `full`, `partial`, `unavailable`, or `intentionally disabled`
- whether the shell state changes any semantics or only the path of invocation

The operator must be able to answer: **is the shell helping, and if not, am I semantically blocked or just losing a shortcut?**

### 2) Action parity ledger

This section should list the ordinary file/subtree actions that matter most here, for example:

- materialize bytes
- evict local bytes
- reveal current availability
- open history / restore
- share / publish / copy offer artifact
- inspect exclusion/fidelity risk

For each action the page should show:

- `shell accelerator available` yes/no
- `product-native path available` yes/no
- `semantic parity class` (`full-parity`, `shortcut-only`, `shell-only-bug`, `product-only`)
- `recommended invocation path`

The operator must be able to answer: **what can I still do safely from inside the product even if the shell is broken?**

### 3) Health and blockers

This section should show:

- current shell integration health
- volume-class or filesystem-class blockers
- permission / registration / extension-state blockers
- known scope limits such as `only for placeholder-backed shares`
- whether a third-party shell provider conflict is suspected

The operator must be able to answer: **what exactly is broken or absent, and is the scope global, seat-local, or volume-local?**

### 4) Product-native fallback

This section should show a product-owned next-action ladder:

- `Use product browser instead`
- `Open availability review`
- `Open byte action review`
- `Open history access`
- `Open shell repair instructions`

The operator must be able to answer: **what is the product-native route that preserves truth even if the shell is gone?**

### 5) Receipt and diagnostic export

This section should show:

- the last known healthy shell state
- whether any health change was acknowledged or repaired
- a diagnostic bundle action with explicit redaction scope
- a receipt proving that semantics remained available through product-native paths even while acceleration was degraded

## States

Use a small stable vocabulary:

- `full acceleration`
- `partial acceleration`
- `shortcut unavailable`
- `scope-limited`
- `product-native only`

## Main surface

The subject workspace should expose a compact **Shell capability** card with:

- current verdict
- count of accelerated actions
- count of shortcut-only gaps that still need parity work
- a primary action: `Inspect shell capability`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- seat
- current shell family
- acceleration verdict
- primary recommended path

### Pane B — Action parity matrix

Columns:

- action
- shell accelerator
- product-native path
- semantic parity
- primary recommendation

### Pane C — Health blockers

Rows may include:

- extension not loaded
- extension registered but stale
- incompatible volume class
- permissions/elevation missing
- third-party provider conflict suspected
- intentionally disabled by policy

### Pane D — Repair versus bypass

Shows two explicit ladders:

- `Repair shell acceleration`
- `Continue without shell acceleration`

The product should never force shell repair before safe product-native completion unless the exact action is truly impossible without OS support.

### Pane E — Receipts

Shows:

- prior shell-health changes
- prior bypass acceptances
- diagnostic export receipts

## CLI parity

Minimum commands:

- `anonsync shell capability show --seat <seat>`
- `anonsync shell capability diagnose --seat <seat>`
- `anonsync shell capability repair --seat <seat> --review <review-id>`
- `anonsync shell capability bypass --seat <seat> --open <page>`

## Acceptance criteria

A user can:

- tell whether the shell is helping, missing, or misleading
- see which actions still have full product-native parity
- continue safely without shell integration when semantics do not require it
- distinguish repair of acceleration from repair of the underlying sync state
- prove later that a degraded shell did not silently change product meaning
