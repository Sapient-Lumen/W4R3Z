# 357 — help navigation missing-doc command honesty

Micromax already had the right *model* for stale docs replay by rev408: blocked
`helpresume`, `helpback`, and `helpforward` targets stayed witnessable,
`help_*_warning` named the exact blocked action, and `help_actions=` stopped
advertising replay commands that were no longer actionable.

But one command-level seam still lingered underneath that model. When a user
actually ran the stale replay command, the failure still collapsed back to the
generic direct-doc lookup dialect:

- `help docs: no such doc: TOPIC`

That wording was understandable, but it forced humans, logs, and future
headless callers to reconstruct *which* replay action had failed from surrounding
state even though Micromax already knew the answer.

## Rev415 rule

When a stale docs replay target no longer resolves, the command path should keep
the replay action visible too:

- `helpresume: missing doc: TOPIC`
- `helpback: missing doc: TOPIC`
- `helpforward: missing doc: TOPIC`

## Why this is the right-sized move

This is deliberately tiny. It does **not** change stack/session semantics, and
it does **not** introduce a richer error subsystem. It just closes the last
split between:

- the inspectable blocker model (`help_*_warning`)
- and the direct command/hostcall failure surface

That keeps the docs-navigation lane aligned with the repo's recent sequence:

1. witness local state exactly
2. distinguish remembered from actionable
3. keep the exact replay action visible all the way through failure
