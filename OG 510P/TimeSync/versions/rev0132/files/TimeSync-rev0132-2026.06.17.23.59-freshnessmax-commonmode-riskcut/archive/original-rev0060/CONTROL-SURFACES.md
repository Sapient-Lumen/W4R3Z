# CONTROL-SURFACES

This note drafts the first minimal control-surface family for TimeSync.

These are not full operator workflows.
They are the smallest current set of surfaces that seem to matter repeatedly across scenarios.

## 1. Source policy

A way to declare what kinds of sources may influence TimeState.

This includes questions such as:
- authentication required or preferred?
- how many agreeing sources are needed?
- when may unauthenticated sources contribute only conditionally?
- when is a source visible but not selectable?

This surface is inspired by current source-selection and authentication policy knobs in real systems.

## 2. Error / acceptability policy

A way to declare what maximum error or distance is still acceptable for synchronization or for downstream use.

The archive treats this as load-bearing because current timing systems already make accept/reject decisions based on bounded-error style quantities.

## 3. Regime transition surface

A way to declare or detect when the system moves among regimes such as:
- normal
- degraded
- holdover
- partition-local
- recovery

This surface matters because a system can remain "working" while no longer deserving the same trust.

## 4. Holdover policy

A way to define:
- when holdover begins,
- how long it remains acceptable,
- what evidence or thresholds force degradation,
- and what conditions allow exit from holdover.

This is separate from regime in order to keep holdover a first-class operational concern.

## 5. Downstream applicability policy

A way to bind TimeState to consequences.

Examples:
- still acceptable for ordinary auth/logging
- no longer acceptable for high-integrity sequencing
- only acceptable for local continuity
- requires operator review

The archive treats this as essential because timing state exists for consumers, not for ornament.

## Profile boundary note

rev0006 makes the following boundary explicit:

The core control surfaces should expose that policy exists.
Profiles should carry most of the dense policy content, such as:
- sector-specific error thresholds
- traceability requirements
- phase / frequency performance targets
- topology assumptions
- operator and audit workflow detail

This keeps the core from becoming a disguised compliance matrix.

## Minimal list

The current best minimal control-surface family is:
- source policy
- error / acceptability policy
- regime transition
- holdover policy
- downstream applicability policy

## What is intentionally not yet core

Not every core control surface should include:
- full sector-specific compliance logic
- incident review workflow
- court / appeal process
- detailed topology management
- large operator UI surface
- full phase / frequency control logic by default

Those may matter later, but they do not yet look invariant.
