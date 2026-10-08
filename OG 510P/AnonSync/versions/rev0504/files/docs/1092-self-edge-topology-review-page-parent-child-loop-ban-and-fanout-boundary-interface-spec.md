# Self-edge topology review page: parent-child loop ban, derivative fanout, and target admissibility

This page exists so same-host topology does not collapse into a `choose local folder` ritual.
The main job here is to prove whether the proposed target forms a safe disjoint derivative, a forbidden loop shape, or a fanout pattern that needs stronger disclosure.

## Operator question

> Is this target relationship safe, or am I about to create a child/parent/overlap arrangement that feeds back into itself or confuses later ownership?

## When this page must appear

Render whenever:

- the operator nominates a target path for a self-edge derivative
- a second or later local derivative is proposed from the same source
- an existing derivative is inspected after path relocation or target repair
- topology proof is partial or stale

## Fixed review order

1. **Candidate geometry**
2. **Loop and overlap proof**
3. **Fanout boundary**
4. **Blocked shapes and safer alternatives**
5. **Topology receipt promise**

## 1) Candidate geometry

Show:

- source path
- target path
- relationship verdict: `disjoint sibling`, `child`, `parent`, `same-path`, `partial overlap`, `unknown`
- target tier: `local-native`, `usb/removable`, `network-reviewed`, `unknown`
- whether target already belongs to another managed subject

The operator must be able to answer: **what exact geometry has the product proven?**

## 2) Loop and overlap proof

Show:

- whether the target is a subdirectory of the source
- whether the target is a parent of the source
- whether any path aliases or mount rewrites could hide overlap
- whether recursive visibility or echo-back risk exists
- topology verdict: `loop-safe`, `blocked-loop`, `blocked-overlap`, `needs-manual-proof`, `unknown`

The operator must be able to answer: **can bytes from this source re-enter the same managed world through the proposed target?**

## 3) Fanout boundary

Show:

- count of existing derivatives from the source
- whether the proposed target is the first, another sibling derivative, or an attempt to derive from a derivative
- whether fanout is allowed from the source but forbidden from a local derivative
- projected resulting set after apply

The operator must be able to answer: **am I creating allowed fanout from the source, or an impermissible derivative-of-derivative chain?**

## 4) Blocked shapes and safer alternatives

When blocked, render concrete alternatives:

- `Choose disjoint sibling target`
- `Detach as ordinary copy`
- `Use source fanout instead of derivative-of-derivative`
- `Inspect mount alias / path rewrite`

Do not merely say `invalid path`.
The block must publish the exact topology class that caused the refusal.

## 5) Topology receipt promise

The resulting receipt should preserve:

- source path
- target path
- relationship class
- loop verdict
- fanout count before and after
- stronger sentence blocked or allowed

## What this page must never imply

It must never imply that these are equivalent:

- path chosen and path admitted
- disjoint sibling and parent/child adjacency
- allowed source fanout and derivative-of-derivative chain
- removable/network target and identical topology confidence
- same-host convenience and loop safety

## Primary actions

- `Approve loop-safe derivative`
- `Reject child/parent loop`
- `Reject derivative-of-derivative chain`
- `Pick safer disjoint target`
- `Hold for topology proof`

## Text-mode expectations

A CLI or WebUI projection must state the exact relationship class in plain text.
`blocked` alone is not enough.
It must say `blocked because target is a parent of source`, `blocked because target is inside source`, or `blocked because target is already a derivative target`.
