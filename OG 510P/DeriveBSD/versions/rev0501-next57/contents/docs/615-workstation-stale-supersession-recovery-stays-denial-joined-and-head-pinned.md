# Workstation stale supersession recovery stays denial-joined and head-pinned

**Tier:** B (Base)  
**Profiles:** B  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt

Imported-document authoring on workstation profile **B** now has a coherent local source-lineage chain:

`docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` made edited working-copy bytes become an explicit **local successor candidate** instead of replacing the source in place.
`docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` then made each candidate an **immutable snapshot**.
`docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` then made candidate ordering **explicit** instead of recency-shaped.
`docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` then kept that relationship **same-origin** and **self-describing**.
`docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` then made supersession **current-head exact** and stale targets **fail closed**.
`docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` then made stale-target denials carry the **observed current head** plus the boring recovery answer.

This doc makes the next small but expensive cut:
**the fresh recovery act answering that stale denial must itself be typed, denial-joined, and head-pinned instead of being a generic retry.**

See also:
- ADR: `adrs/ADR-0205-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md`
- stale-denial evidence floor: `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md`
- canonical schemas: `spec/content.reintegrate.plan.schema.json`, `spec/content.reintegrate.receipt.schema.json`
- canonical retry profiles: `spec/content.reintegrate.plan.stale-target-retry.schema.json`, `spec/content.reintegrate.receipt.stale-target-retry.schema.json`

## Why this needs a hard decision

Once the archive says:

- stale supersession denial is first-class,
- the denial carries the observed current head,
- and the next answer must be a fresh explicit supersession act,

one more ambiguity still remains:
**how does that next act prove it is answering this denial and this observed head rather than becoming a generic “retry now” story?**

Without a typed join, the easiest implementation path becomes the real product:

- operators re-open live storage to rediscover what the denial already observed,
- tooling silently repoints the act at whatever head is current later,
- support bundles can prove the denial but not the later recovery lineage,
- and the local candidate lane drifts back toward ambient retry folklore.

## Decision

`content.reintegrate.plan` and `content.reintegrate.receipt` now carry a required `recovery` object.

### Ordinary path

For ordinary reintegration acts that are not answering a stale-target denial:

- `recovery.mode = none`

### Stale-target recovery path

For a fresh act that is explicitly answering a stale supersession denial:

- `recovery.mode = from-stale-supersession-denial`
- `recovery.stale_denial_receipt_digest`
- `recovery.expected_current_receipt_digest`
- `recovery.expected_current_candidate_digest`
- `recovery.expected_current_authoritative_origin_digest`

That means the fresh act is not just “another attempt.”
It is a typed answer to one exact denial and one exact observed current head.

## What the boundary means

### 1) Recovery stays fresh

The recovery act is still a **new** explicit reintegration/supersession act.
The archive does **not** mutate or resurrect the denied act.

### 2) Recovery stays denial-joined

The new act carries:

- `recovery.stale_denial_receipt_digest`

So detached tooling can answer:

**which stale denial was this act responding to?**

### 3) Recovery stays head-pinned

The new act also carries the exact head it expects to supersede:

- `recovery.expected_current_receipt_digest`
- `recovery.expected_current_candidate_digest`
- `recovery.expected_current_authoritative_origin_digest`

That keeps the recovery act pinned to the exact head the stale denial observed.

### 4) Supersession remains explicit

This does **not** replace the normal explicit supersession object.
Instead it tightens it.

When `recovery.mode = from-stale-supersession-denial`, the act must still be:

- `supersession.mode = supersede-prior-candidate`

and the explicit supersession target must match the expected current head carried by `recovery`.

That keeps recovery from decaying into a second vague pointer system.

## Practical model

1. attempt explicit supersession against the current predecessor
2. lose the race and emit a stale-target denial
3. denial carries the observed current head plus `fresh-explicit-supersession-required`
4. build a fresh explicit act
5. set `recovery.mode = from-stale-supersession-denial`
6. join that act back to the stale denial through `stale_denial_receipt_digest`
7. pin it to the observed current head through the `expected_current_*` digests
8. keep the ordinary supersession target equal to that expected current head

## Why this is still small enough for v0

This doc does **not** add:

- branching,
- merging,
- collaborative locking,
- background retry orchestration,
- or multi-head lineage semantics.

It only ensures that the first official recovery step after a stale denial is explicit enough to be support-bundle-queryable and boring to implement.

## Related docs

- `docs/605-workstation-file-open-import-and-bounded-document-roles.md`
- `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md`
- `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md`
- `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md`
- `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md`
- `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md`
- `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md`
- `spec/content.reintegrate.plan.schema.json`
- `spec/content.reintegrate.receipt.schema.json`
- `spec/content.reintegrate.plan.stale-target-retry.schema.json`
- `spec/content.reintegrate.receipt.stale-target-retry.schema.json`

Last updated: 2026-03-20r345
