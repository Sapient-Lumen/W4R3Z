# Control saturation and no-new-control rule

## Purpose

This surface prevents the archive from treating every remaining uncertainty as a reason to add another validator, schema, or release artifact. After rev0222 the `FT-0181` gate is already surrounded by import readiness, source dictionaries, acceptance calibration, negative fixtures, redaction profiles, sector adapters, release candidates, audit manifests, assurance cases, control coverage, evidence refresh, signoff quorum, invariants, dependency graphs, delta manifests, recovery drills, and a closure checklist.

The next material change should normally be a real `SRC2+` pilot packet, not another pre-import control. New controls are allowed only when a review finds a risk that is not already blocked by an existing validator, human artifact, failure fixture, recovery drill, or invariant.

## Saturation states

| State | Meaning | Default action |
|---|---|---|
| `SAT0` | pre-control: basic lint only | add foundational controls |
| `SAT1` | partial: some validators but weak human artifacts | complete missing controls |
| `SAT2` | covered: known false-closure risks have validators and artifacts | add only targeted patches |
| `SAT3` | audit-ready: coverage, invariants, drills, audit, and checklist exist | prefer real evidence over new controls |
| `SAT4` | maintenance mode: no new control without uncovered material risk | freeze control growth |
| `SATX` | saturated but unreliable: controls conflict or produce false confidence | downgrade release candidate |

rev0223 sets the `FT-0181` control plane to `SAT4`. This does not close the gate; it says the pre-import control layer is sufficiently complete that further work should not masquerade as progress unless it removes a newly identified uncovered risk.

## New-control admission test

A proposed new control must answer all six questions:

1. What concrete false-closure, protected-leakage, hidden-authority, public-overclaim, stale-evidence, waiver-bypass, or burden-creep failure does it catch?
2. Which existing validator, negative fixture, human artifact, invariant, drill, or checklist fails to catch it?
3. What is the smallest artifact that catches the failure without increasing public claims?
4. Does the control reduce the chance of real pilot import, by adding friction, more than it reduces the chance of harm?
5. Is the proposed control a general rule, or is it merely another serial shell around `FT-0181`?
6. Can the control be retired or merged after the first real import?

If any answer is missing, the proposed control stays in notes and does not become a new surface, schema, or validator.

## Hard limits

- Do not close `FT-0181` through saturation, audit consistency, or release-candidate cleanliness.
- Do not add a new validator that checks only that another validator exists.
- Do not add another release artifact unless it changes a decision, prevents a defined harm, or shrinks existing process.
- Do not cite a synthetic example as evidence that the service works.
- Do not let a policy exception waive source truth, protected-route separation, public-claim limits, or action-authority ceilings.

## Relationship to compression

This is the release-control analogue of the serial-repair compression rule. Repeated pre-import hardening should eventually generalize, freeze, or wait for real evidence rather than spawning an endless chain of protective shells.

Related: [`release-invariants-and-claim-boundaries.md`](release-invariants-and-claim-boundaries.md), [`artifact-dependency-graph-and-control-plane.md`](artifact-dependency-graph-and-control-plane.md), [`ft0181-closure-evidence-checklist.md`](ft0181-closure-evidence-checklist.md), [`../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md).
