# Bind outcome review page — attach, merge, fork, and empty-only lane interface spec

## Purpose

`497` through `505` now let AnonSync type imported artifacts and choose a destination world before bytes land.
`158`, `198`, `306`, and `487` already cover path continuity, reuse proof, relocation, and encrypted-target admission.
What still lacked one ordinary page was the semantic step in between:

> if I commit this chosen target tree right now, what exact branch outcome will exist afterward?

This page exists so `Connect`, `OK`, and `folder is not empty` stop hiding whether the product is attaching to the intended lineage, merging into an existing tree, forking a new sibling branch, hitting a same-ID collision, or requiring a fresh empty ciphertext root.

## Core rule

A chosen path is not yet an honest bind decision.
The product must also classify the **branch outcome**.

Every target selection that is not trivially empty-and-fresh must therefore render one first-class **Bind outcome review** page before commitment.

## Fixed review order

Every serious bind-outcome review should render the same sections in the same order:

1. **Selected world and proposed target**
2. **Current branch verdict**
3. **Why this verdict won**
4. **Byte-change and namespace consequence**
5. **Safer alternatives**
6. **Admissible actions**
7. **Receipt promise**

### 1) Selected world and proposed target

Show:

- imported artifact family
- selected destination world
- selected bind lane
- proposed target tree
- strongest current warning

The operator must be able to answer: **what am I trying to bind, where, and through what lane?**

### 2) Current branch verdict

Choose one primary verdict:

- `attach-same-lineage`
- `merge-into-existing-tree`
- `fork-new-sibling-branch`
- `blocked-same-id-already-present`
- `blocked-empty-only-required`
- `needs-more-evidence`

The page must not hide this verdict inside a generic confirmation prompt.

### 3) Why this verdict won

Show the strongest current evidence families, such as:

- remembered continuity root matches current target
- same subject already present on this seat
- non-empty target with no same-ID evidence
- same-name namespace collision at default root
- encrypted lane requires fresh empty root
- target tree contains conflicting lineage hints

The operator must be able to answer: **why is the product calling this attach, merge, fork, or blocked?**

### 4) Byte-change and namespace consequence

Show:

- whether identical bytes will be reused, compared later, or fetched anew
- whether same-path conflicts may resolve by stronger later evidence or merge rules
- whether a new sibling namespace will be created
- whether this outcome preserves one current lineage or creates a second local branch
- whether a later deeper review is mandatory before writable operation

The operator must be able to answer: **what concrete tree and lineage consequence follows if I proceed?**

### 5) Safer alternatives

Always compare the current verdict against nearby alternatives when available, such as:

- `attach to remembered tree instead`
- `reroute away from default root`
- `keep unplaced and gather more evidence`
- `choose fresh empty ciphertext root`
- `proceed as deliberate fork`

The page must not make the current draft look inevitable.

### 6) Admissible actions

Allowed verbs include:

- `Attach here`
- `Continue to merge review`
- `Fork deliberately`
- `Open existing-tree evidence`
- `Choose different target`
- `Choose empty ciphertext root`
- `Stay unbound`

### 7) Receipt promise

Before exit, show the receipt that will be emitted, including:

- selected branch verdict
- strongest evidence families used
- strongest rejected alternatives
- next deeper page handed off to

## States

Allowed top-level states:

- `draft-attach`
- `draft-merge`
- `draft-fork`
- `blocked-same-id`
- `blocked-empty-only`
- `evidence-incomplete`

## Main surface

A compact **Bind outcome review** strip should show:

- target path chip
- branch verdict chip
- strongest evidence chip
- primary verb

## Detailed surface

The detailed page should provide five panes.

### Pane A — World and target strip

Shows:

- artifact family
- destination world
- bind lane
- proposed target

### Pane B — Branch verdict pane

Rows may include:

- verdict
- confidence class
- strongest warning
- whether a later merge review is required

### Pane C — Evidence pane

Rows may include:

- remembered-root match
- same-ID detection
- non-empty target shape
- lineage-hint conflicts
- ciphertext-empty requirement

### Pane D — Alternative branches pane

Rows may include:

- alternative verdict
- what changes if chosen
- why it is safer or less safe

### Pane E — Receipt preview

Shows the receipt skeleton that will be emitted.

## CLI parity

Minimum commands:

- `anonsync bind-outcome explain <artifact-id> --world <world-id> --target <path>`
- `anonsync bind-outcome choose <review-id> --verdict <attach|merge|fork|empty-only>`
- `anonsync bind-outcome receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell whether the current target means attach, merge, fork, blocked, or evidence gap
- see why non-empty confirmation is not one generic meaning
- interrupt a default-root fork before a `(1)` sibling is created
- leave with a receipt that preserves branch truth separately from later merge or custody proof
