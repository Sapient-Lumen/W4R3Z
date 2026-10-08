# Archive profile pack discipline — 2026-03-24

## Why this note exists

The archive now has enough packet families that future passes could easily drift into one of two bad habits:

1. pretending the same crate-choice answer works for every adopter,
2. or inventing endless new profiles without stable floors or packet outputs.

This note is the guardrail against both.

## Rules for future passes

### 1. Keep task and adopter profile separate

Do not answer:
- “the task is embedded”
when what you really mean is:
- “the adopter is safety-onramp and therefore needs stricter floors.”

A task can stay constant while the adopter profile changes.

### 2. Prefer a small stable profile family

Until the archive proves otherwise, prefer reusing:
- `explore-default`
- `team-default`
- `enterprise-offline`
- `safety-onramp`

Do not create a new profile just because one scenario is interesting.
Create a new profile only when:
- the evidence floor is materially different,
- the receiver is materially different,
- and the output packet would change in a durable way.

### 3. Require explicit evidence floors

Every new profile note should say:
- what is required,
- what is optional,
- what can be conditional,
- and what still demands manual review.

Do not let “this is stricter” stand in for a floor.

### 4. Keep non-claims visible

Every profile should say what it does **not** prove.

Examples:
- not certification,
- not standards compliance,
- not long-term maintenance guarantee,
- not offline parity guarantee,
- not target support proof.

### 5. Keep exception budgets profile-scoped

An exception acceptable for `explore-default` may be unacceptable for `safety-onramp`.

Do not let one global exception story erase that difference.

### 6. Record profile diffs rather than silently replacing answers

If a later pass changes which floors apply to a profile, record:
- what changed,
- why,
- and which existing scenarios are affected.

Do not silently rewrite earlier profile packs as if they always meant the new thing.

## Preferred packet outputs

The archive should now prefer front-door proposals that can emit:

- `policy-profile.pack.json`
- `profile-satisfaction.report.json`
- later: `profile-diff.report.json`

If a pass cannot say how a proposal would emit at least the first two, it should not claim the profile layer is implemented.

## LLM-facing reminder

When future LLM passes summarize top crates, they must not flatten:
- profile identity,
- evidence floor,
- current satisfaction,
- and non-claims
into one generic “recommended” statement.

The right question is no longer only:
> “what crate is best?”

It is also:
> “best for whom, under which floor, with which surviving ceiling?”
