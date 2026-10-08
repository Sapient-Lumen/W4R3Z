# Special object lineage receipt page — object kind, fidelity ceiling, and blocked stronger sentences

## Purpose

Emit a durable receipt whenever the product accepts, preserves, degrades, blocks, or re-models a special filesystem object.

## Required fields

- receipt id
- subject id
- object id
- object path at review time
- detected object kind
- reviewed peer horizon
- reference fidelity ceiling
- metadata fidelity ceiling
- bundle fidelity ceiling
- chosen action
- compatibility residue expected (`none`, `streams-stub`, `conflict-risk`, `plain-directory-collapse`, `other`)
- strongest safe sentence
- blocked stronger sentence
- invalidators / reopen triggers
- successor receipt pointer if later re-reviewed under a different cohort

## Receipt language rules

The receipt must never collapse any of these distinct outcomes:

- preserved reference object
- target intentionally excluded
- metadata propagated through residue only
- bundle degraded to ordinary directory view
- object blocked from current cohort

`Synced successfully` is forbidden if the reviewed fidelity ceiling is weaker than full ordinary-object preservation.
