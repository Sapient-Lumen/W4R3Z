# Self-edge derivation contract sheet page: source, self-peer lane, loop ceiling, and lifecycle coupling

This page exists so same-host derivation stops hiding behind `Sync local folders`, `create local copy`, or a bare path picker.
A self-edge derivative is not just a destination choice.
It is a reviewed object with topology, rights, materialization, and entitlement meaning.

## Operator question

> I want one source on this machine to feed one or more local targets. What exactly am I creating, what is the safe topology ceiling, what rights can the target carry, and what events will suspend or tear it down later?

## When this page must appear

Render this page whenever the operator is about to create, inspect, repair, or resume a same-host derivative that is materially sourced from another managed subject on the same machine.
That includes:

- first-time self-edge creation
- adding a second or later derived target from the same source
- changing target class or materialization posture
- repairing a derivative removed after source disconnect/removal
- recovering from entitlement expiry or source reattach gaps

## Fixed page order

Every self-edge contract sheet should render the same sections in the same order:

1. **Source and derivative target**
2. **Topology class and loop ceiling**
3. **Rights ceiling**
4. **Lifecycle coupling**
5. **Materialization and entitlement dependencies**
6. **Receipt promise**

## 1) Source and derivative target

Show:

- source subject id, local path, and current mode
- requested target path and target tier
- derivative class: `self-edge`, `ordinary copy`, `detached export`, `unknown`
- self-peer lane status: `self-only`, `ambiguous`, `not-self-edge`
- discovery class: `discovery-bypassed`, `ordinary-peer-discovery`, `unknown`

The operator must be able to answer: **am I creating a true self-edge derivative and from which exact source?**

## 2) Topology class and loop ceiling

Show:

- relationship between source and target: `disjoint`, `child`, `parent`, `overlap`, `same-path`, `ambiguous`
- loop verdict: `safe`, `blocked`, `warning`, `unknown`
- fanout count already attached to this source
- whether the proposed target is itself already a local derivative
- strongest allowed sentence: `loop-safe self-edge`, `fanout-safe but review-bound`, `blocked for loop risk`, `blocked pending topology proof`

The operator must be able to answer: **is this topology admissible, and why or why not?**

## 3) Rights ceiling

Show:

- source rights
- maximum derivative rights
- whether `Owner` is impossible on the derivative
- whether rights changes are inline-editable or require remove-and-re-share
- whether downstream rights automatically lower when source rights lower

The operator must be able to answer: **what is the highest authority this derivative can ever carry?**

## 4) Lifecycle coupling

Show:

- what happens if the source is disconnected
- what happens if the source is removed
- what happens if the source later returns
- whether the derivative is propagated to linked same-identity seats or remains strictly local
- reconnect class: `auto-heals`, `manual-reattach-required`, `recreate-required`, `unknown`

The operator must be able to answer: **what future source events will remove, strand, or require manual reattachment for this derivative?**

## 5) Materialization and entitlement dependencies

Show:

- source byte posture: `full`, `partial`, `placeholder-heavy`, `unknown`
- derivative byte promise: `mirrors source bytes only`, `independent full bytes`, `on-demand only`, `blocked`
- whether source and derivative Selective Sync policies may diverge
- whether policy divergence still leaves byte presence dependent on the source
- entitlement dependency: `requires-pro-tier`, `independent`, `unknown`
- suspension effect on expiry/removal: `ceases syncing`, `degraded`, `none-known`, `unknown`

The operator must be able to answer: **will the target really have bytes, and what license cliff can suspend it later?**

## 6) Receipt promise

Show:

- which receipt id will be written
- what the receipt will preserve about source, target, topology verdict, rights ceiling, lifecycle coupling, and entitlement posture
- what stronger sentence was blocked
- what later event should reopen review automatically

## Primary actions

Use only actions that match the reviewed truth.
Examples:

- `Create self-edge derivative`
- `Block for loop risk`
- `Create narrower read-only derivative`
- `Resume after source reattach review`
- `Detach into ordinary copy instead`

Do not use vague primaries such as `Sync here`, `Use this folder`, or `Mirror now`.

## What this page must never imply

It must never imply that these are the same thing:

- self-edge derivative and ordinary remote share
- independent Selective Sync policy and independent byte availability
- rights inheritance and rights equality with the source
- source return and derivative auto-heal
- path admissibility and loop safety
- local existence and entitlement-independent continuity

## CLI projection expectation

A headless projection such as `anonsync derive self show <id> --view contract` must be able to render the same sections and verdicts without requiring GUI-only nuance.
