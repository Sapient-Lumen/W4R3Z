# REASON-PLACEMENT-TEST

This note tests where the archive's tiny optional reason layer should live.

The archive already has:
- four relay verbs
- a tiny optional reason vocabulary
- and a narrow downstream consequence rule for `unknown`

The remaining question is placement.

## Question

Should the tiny optional reason layer live:
- on the wire
- in boundary metadata
- or only in local assessed state?

## Source pattern

The source base does not point to one uniform answer,
but it does show a strong asymmetry.

- Some ecosystems do carry compact source-originated reasons on the wire, such as NTP kiss-o'-death signaling.
- Telecom timing also uses compact failure distinctions, but many of their operational consequences are exercised inside selection, protection, and holdover behavior at the boundary rather than as a universal client-facing wire taxonomy.
- NTPv5 continues to narrow its scope to the on-wire protocol and explicitly leaves many algorithms and local judgments out of scope.
- Roughtime shows that compact wire evidence can be useful, but it does not imply that every local or relay-generated reason belongs in a universal wire object.

This points away from a wire-first design.

## Smallest placement rule that survives the pressure

The current best placement rule is:

> The reason layer is **boundary-first** and **wire-admissible**, not wire-primary.

That means:
- the archive should assume reasons are most naturally attached where state is relayed, downgraded, restated, or marked unknown
- direct-source reasons may also appear on the wire when the profile already has a compact source-originated status path
- local assessed state may retain or summarize those reasons for downstream consequence mapping

## Why boundary-first fits better than wire-first

### 1. Many reasons are created at the boundary
`loss`, `recovery`, `conflict`, and `reconfiguration` often arise when:
- a relay compares sources
- a boundary changes protection path
- a local system enters holdover
- or an aggregator decides that stronger inherited semantics no longer survive

Those are not purely upstream source facts.
A wire-first design would therefore either:
- force boundaries to impersonate sources,
- or force the wire to carry too much local process detail.

### 2. Wire-admissible is still useful
The archive does not need to ban reasons from the wire.
Direct-source conditions can still justify compact wire-carried reasons,
especially where existing systems already use them.

Examples in spirit:
- source refusal / no-sync style responses
- explicit direct-source failure or unusable status
- compact incompatibility or conflict indications

The archive just should not make that the primary home of the whole reason layer.

### 3. Local assessed state still needs access to the result
Even when a reason originated on the wire,
its real value often appears in local assessed state:
- why a hook was downgraded
- why `unknown` blocked a stronger applicability claim
- why a local system entered a different regime

That again pushes the center of gravity away from pure wire placement.

## Hook comparison

### `traceability_posture`
This hook often acquires reasons at the boundary:
- stronger traceability lost during failover
- anchor/evidence no longer preserved through regeneration
- local restatement after recovery

That makes boundary-first placement especially natural.

### `sync_dimension`
This hook is profile-declared first,
so most interesting reasons around it are also profile or boundary shaped:
- reconfiguration into a different operating lane
- loss of the conditions required to keep claiming a dimension-sensitive mode
- conflict between upstream dimension assumptions and local operating mode

Again,
this does not look like a wire-primary reason family.

## Current archive judgment

The tiny optional reason layer should live:
- **primarily in boundary metadata**
- **secondarily in local assessed state**
- and **optionally on the wire** when the profile has a compact source-originated status path that justifies it

This keeps the wire thin without making reasons unusable.

## What this still does **not** settle

This note still does not decide:
- whether boundary metadata needs a named tiny object of its own
- whether all wire-carried reasons should be discoverable/requestable
- how long a retained reason should survive in local assessed state

## Next useful move

Decide whether boundary metadata needs a named tiny surface,
or whether the archive can keep it implicit inside local assessed state plus relay rules.
