# Resilio self-edge local derivation, loop gating, rights ceiling, and license-cliff evaluation

## Why this seam matters now

Current official Resilio docs still make `sync local folders` materially different from ordinary sharing even when the interface language sounds convenient.
They explicitly say:

- local sharing is only for desktop and is a Pro feature.
- the derived target is connected to exactly one peer: self.
- standard peer-discovery routes such as tracker, relay, and LAN discovery are not part of the local-share posture.
- the target may be on USB or network paths, but parent/subdirectory loop shapes are forbidden.
- local derivatives inherit source permissions, cannot receive `Owner`, and can require remove-and-re-share ritual to change access in Advanced shares.
- source-right downgrades cascade down to the local derivative.
- removing or disconnecting the source also removes the local derivative, while restoring the source later does not automatically restore the derivative.
- a local derivative is not propagated across linked same-identity devices.
- a local derivative cannot itself be shared locally again, though the same source may fan out to several local derivatives.
- source and derivative Selective Sync posture can diverge, but the derivative only gets bytes the source actually has.
- if the license expires or is removed, the local derivative becomes unavailable and stops syncing.

That is already enough to reject a clone.
The operator question is not just `do I want another copy on this machine?`.
It is:

> what topology am I creating, what rights ceiling does it carry, what source changes will tear it down, and what hidden entitlement or materialization cliff makes the target weaker than an ordinary peer?

Resilio's documentation preserves the facts, but the feature contract is still convenience-shaped.
The operator still enters through `Sync local folders`, then has to keep the topology, rights, lifecycle, and license consequences in their head.

## The non-clone reason, tightened

AnonSync should borrow Resilio's candor that same-host derivation is real and useful.
AnonSync should refuse the product shape where a self-edge is still presented primarily as a convenience action and the operator has to mentally expand it into:

- a self-only topology,
- a discovery-bypassed lane,
- a rights-ceiling derivative,
- a source-coupled lifecycle,
- a placeholder-limited byte promise,
- and an entitlement-gated continuation.

So the harder stance for this pass becomes explicit:

> **AnonSync is not cloning Resilio because same-host self-edge derivation is a real topology with self-only reachability, inherited-rights ceilings, loop bans, source-coupled deletion/reattach behavior, placeholder-limited byte promises, and license cliffs, but the present contract still compresses that meaning into a convenience-first `sync local folders` action instead of owning it as a stable page family.**

## Product decisions locked by this evaluation

### 1) Same-host self-edge is its own topology class

It is not just `another peer` and not just `another path`.
The reviewed object must name the source, the derived target, the self-edge lane, and the fact that ordinary tracker/relay/LAN discovery semantics do not apply.

### 2) Rights inheritance is a ceiling, not a suggestion

A self-edge derivative may narrow source rights but may not exceed them.
`Owner` does not travel to the derivative, source downgrades can flow down automatically, and some rights changes require a destructive re-share rather than an inline edit.

### 3) Lifecycle coupling must be rendered before commit

If removing or disconnecting the source removes the derivative, that is not an implementation footnote.
If restoring the source later still requires manual derivative reattachment, that must be said before apply.

### 4) Materialization promise is downstream of the source

An independent Selective Sync posture does not create independent bytes.
If the source only has placeholders, the derivative may still lack the file.
The review surface must separate policy independence from byte availability.

### 5) Entitlement cliffs are topology truth

If expiry or license removal suspends the derivative, the entitlement dependency is part of the object contract.
It is not a billing afterthought.

## Required AnonSync page family from this pass

This evaluation requires one stable page family:

1. **Self-edge derivation contract sheet**
2. **Self-edge topology review**
3. **Derived-rights and lifecycle review**
4. **Self-edge materialization and entitlement watch**
5. **Self-edge lineage receipt**

The purpose of the family is to let an operator answer, in one path:

- whether this is truly a self-edge derivative and not an ordinary share,
- whether the target relationship is loop-safe,
- which rights ceiling applies,
- what source events tear the derivative down,
- whether bytes are actually present at the source,
- and what suspension / reattach / re-share boundaries survive later audit.

## What AnonSync should borrow vs refuse

### Borrow from current Resilio

- candor that same-host derivation is a real, supported feature
- candor that the derivative is self-only rather than peer-discovered
- candor that parent/child loop shapes are unsafe
- candor that rights can only flow down and may need re-share ritual to change
- candor that source removal tears down the derivative and source return does not auto-heal it
- candor that placeholder-heavy sources weaken the derivative's byte promise
- candor that entitlement removal can suspend the derivative entirely

### Refuse from current Resilio

- convenience-first entry language that hides topology class
- path picking that does not foreground self-edge / loop / lifecycle semantics
- permission editing that sounds inline when the safe reality is re-share
- policy language that sounds independent while byte availability still depends on the source
- entitlement failure treated as a separate licensing surprise instead of part of the object's continuity contract
- missing durable receipt for why the derivative existed, why it stopped, and what would be required to restore it

## Interface consequence

Every serious same-host derivative action in AnonSync now needs to answer five public questions before commit:

1. **Is this a self-edge derivative or a different object class?**
2. **Is the target topology loop-safe and fanout-safe?**
3. **What rights ceiling and change ritual apply?**
4. **What source events remove, downgrade, or strand the derivative?**
5. **What byte and entitlement promise survives after apply?**

If the interface cannot answer all five without support-lore, it still fails the non-clone bar.
