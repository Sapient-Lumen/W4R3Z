# P4-COHESION

This note asks whether the P4 lane split should become a profile split.

## Current judgment

**Not yet.**

P4 should stay one profile with two lanes for now.
The lane split buys clarity.
A profile split does not yet buy enough additional clarity to justify the extra archive structure.

## Why the profile stays together

### 1. The strongest cases still live in the same deployment neighborhood
The source material keeps placing both lanes inside the same telecom / precision-network family.
The archive is not looking at two unrelated worlds.
It is looking at one world with two recurring timing demands.

### 2. The same small hook family still spans both lanes
Both lanes still mainly pull on:
- `sync_dimension`
- `holdover_class`
- `validity_scope`

That is a sign of real cohesion.
If the hooks had split sharply, a profile split would look more justified.

### 3. The same control surfaces still dominate
Both lanes keep returning to the same minimal control-surface family:
- source policy
- holdover policy
- regime transition

That does not mean the policy contents are identical.
It means the shape of the problem is still shared.

## Minimal case map

### Case A1 — packet-based frequency delivery without network timing support
This is Lane A.
It is frequency-first and can live on packet pathways that do not yet provide stronger time/phase semantics.

### Case A2 — cellular base-station frequency accuracy
This is Lane A.
The pressure is rate discipline and continuity, often stated in ppm-style requirements.

### Case B1 — neighboring base-station time alignment
This is Lane B.
The pressure is explicit relative alignment error between base stations.

### Case B2 — traceable phase/time path with holdover on reference loss
This is Lane B.
The pressure is not only alignment but also holdover and recovery semantics when the traceable path breaks.

## Why the split is still useful

Keeping P4 together does **not** make the lane split cosmetic.
The lane split is useful because it prevents the archive from asking a false binary question about telecom pressure.

## What would justify a later split

The archive should split P4 into two profiles only if one or more of these becomes true:
- the hook families diverge
- the control surfaces diverge
- the scenario sets diverge enough that one profile starts obscuring more than it reveals
- the first-missing-field question needs different surrounding semantics, not just different ranking

## Current archive posture

Keep:
- one P4 profile
- two explicit P4 lanes
- one shared hook family
- one shared control-surface family
