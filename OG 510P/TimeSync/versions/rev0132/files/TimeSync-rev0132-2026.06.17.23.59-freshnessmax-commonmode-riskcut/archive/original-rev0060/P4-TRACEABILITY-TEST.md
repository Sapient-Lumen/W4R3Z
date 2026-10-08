# P4-TRACEABILITY-TEST

This note tests whether the reduced `traceability_posture` model survives P4 telecom / precision-network pressure.

## Question

Does P4 force the archive to add a third semantic beyond:
- `reference_anchor`
- `evidence_posture`

or does the thin model survive if telecom control semantics remain adjacent rather than absorbed?

## Current result

**The thin model survives P4 provisionally.**

The telecom material is real pressure,
but it mostly confirms the archive's separation:
- traceability state belongs in the hook
- holdover / BMCA / path-switch behavior belongs adjacent to it

## Why P4 looked dangerous

P4 does not merely care about static traceability claims.
It cares about:
- reference-chain quality
- UTC-traceable network sync quality
- clock class / status messages
- loss of traceability in live rearrangement scenarios
- downstream holdover transitions

That could have forced the hook to grow.

## What the source pattern suggests instead

### 1. `reference_anchor` still works
P4 materials still talk in recognizable reference terms:
- UTC-traceable network quality
- PRTC-traceable reference state
- not-traceable-anymore transitions

That still fits the anchor axis.

### 2. `evidence_posture` still works
The practical question is whether receivers should trust the current tie to the anchor.
That still fits the evidence axis.
The boundary can say, in effect:
- this reference is PRTC-traceable
- this reference is no longer PRTC-traceable

### 3. The rest is adjacent control state
When downstream clocks switch to holdover,
when BMCA selects a backup path,
or when path rearrangement occurs,
those are important semantics.
But they are not traceability semantics themselves.
They belong with:
- `regime`
- `holdover_class`
- profile-local control logic

## Archive judgment

P4 does **not** currently force a third traceability semantic.

Instead it strengthens a cleaner distinction:
- **traceability hook** = what reference the claim is tied to, and how seriously that tie should be treated
- **adjacent control semantics** = what the system does when that tie is lost or degraded

## Why this matters

This is a good result for archive discipline.
The hook becomes more credible by surviving a hard profile without getting bigger.

## New pressure point

The strongest remaining uncertainty is not P4.
It is whether `verified` deserves to remain a distinct evidence posture,
or whether that level is really an external process that should stay outside the hook.
