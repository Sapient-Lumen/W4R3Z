# Control change and controller-zone seams

rev0026 adds a deliberately narrow control-changing scaffold. The goal is not to implement every control-changing continuous effect yet; the goal is to protect the owner/controller boundary and create a reusable seam for future layer-2 work.

## Implemented seam

`EffectKind::GainControlPermanent` resolves through the existing one-shot targeted effect pipeline. When the target is a legal battlefield permanent, `gain_control_of_permanent(...)`:

1. keeps the object's owner unchanged;
2. removes the object from the old controller's battlefield container;
3. updates `GameObject::controller`;
4. stamps `controlled_since_turn_start_index` from the new controller;
5. clears combat metadata through the shared combat-cleanup helper;
6. inserts the permanent into the new controller's battlefield container.

That gives us a compact but important audit target: a stolen creature should be controlled by the new controller while it remains on the battlefield, but if it later dies it still moves to its owner's graveyard.

## Why this matters for layers

Rule-ledger row `613.1b` is now represented as a tiny layer-2-style scaffold. It does not implement a full timestamp/dependency engine. It does give future code a single control-change hook and it demonstrates that controller-scoped derived characteristics recompute after control changes. In rev0026 that means a fictional `creatures_you_control` static anthem starts applying to a stolen creature as soon as the permanent's controller changes.

## Summoning sickness and combat cleanup

Changing controller updates the control-start timestamp. Existing summoning sickness checks then treat the permanent as newly controlled by the new controller unless haste or a future continuous effect says otherwise. Control changes also remove the object from combat, clear defending-player and attacked-object metadata, and clear blocked-attacker memory.

## Tests

The C++ cases cover owner/controller graveyard behavior, controller battlefield container movement, combat cleanup, summoning-sickness refresh, static-effect recomputation, legal-action casting of targeted control spells, and validation failures when a battlefield permanent appears in the wrong controller's container.

The scenario fixtures cover a targeted control spell, direct control change plus controller-scoped static effects, and control change after an attacker has been declared.

## Still missing

This is not a complete control-changing effect or layer system. It does not implement durations, timestamps, dependencies, control-changing effects from unusual zones, multiplayer team-control nuance, controller changes for spells on the stack, gaining control of nonpermanents, Aura/Equipment legality fallout from control change, or Oracle-text-derived continuous effects.
