# Feature harvest rubric (what to bake in vs leave to the ecosystem)

DeriveBSD’s core advantage is being greenfield enough to bake in “ops ergonomics” that other OSes bolt on later.

But greenfield projects also die from “design tourism”.
This rubric keeps the archive aggressive **and** disciplined.

## The rule of three artifacts

A feature is worth baking in only if we can define (at minimum):

1) **An input** (spec/policy) that declares intent
2) **A plan** that is diffable and reviewable
3) **A receipt/evidence object** that proves what happened

If we can’t express those cleanly, the feature should remain an external convention until we can.

## Bake-in checklist

### 1) Authority surface
- Does this feature change who can read/write/execute/egress/observe?
- Can we make that authority explicit (profiles, leases, grants, mount views)?

If authority is implicit, it’s not ready.

### 2) Failure and recovery semantics
- What is the safe default when inputs are missing or invalid?
- What is the “breakglass” story, and is it evidence-bearing?
- Can we rollback without losing critical state?

### 3) Determinism + reproducibility
- Does the feature introduce hidden time, network, or host-state dependencies?
- Can we quarantine/label impurity and keep it policy-controlled?

### 4) Explainability
- Can `derive explain` answer “why did this happen?”
- Can we produce a **minimal evidence bundle** for support/incident review?

### 5) Interop and exit strategy
- Can we model it as an adapter lane first?
- If this idea is wrong, can we remove it without breaking user state?

## How to harvest “brilliant but unpopular” ideas

When you find an ecosystem feature that looks like magic (but isn’t mainstream), ask:

- Is it a **data model win**? (e.g., indexed attributes + live queries)
- Is it an **authority routing win**? (e.g., capability routing, portals)
- Is it an **operational workflow win**? (e.g., signed patchsets, health gates)

Then map it onto the Derive pipeline:

- What’s the Spec input?
- What does the Plan look like?
- What receipts prove it?
- Which existing lanes does it plug into (store, activation, portals, networking)?

If you can’t answer those quickly, capture it as a *mile-high direction* with a single paragraph and references.

## Archive hygiene guidelines

- Prefer **one concept per file**.
- Add a link in `docs/110-juicy-os-lessons.md` if it’s a cross-ecosystem steal.
- Add it to `docs/266-open-questions-and-risk-register.md` only if it is a high-leverage unknown.
- When it becomes a decision, record it in an ADR.

Last updated: 2026-02-26
