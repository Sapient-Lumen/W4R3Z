# Metanorms governing punishment are world contracts, not background culture

Recent work adds a missing layer to Concord's sanction worlds:
not just **who gets punished**, but **what counts as the right response to a violation**.

- `RS-GR-166` argues that societies stabilize and adapt norms through **metanorms** — rules about how norms are interpreted, changed, and enforced.
- `RS-GR-167` shows that people adapt their punishment style through social observation, shifting among inaction, gossip, exclusion, and confrontation after watching what others do.
- `RS-GR-168` shows that once multiple third parties are present, failure to punish and anti-social punishment can themselves become sanction targets, but the resulting discipline is institution- and society-sensitive.

## Why this matters for Concord

A sanction world is under-specified if it only says:

> defectors can be punished.

It also needs to say what observers are *supposed* to do after seeing a violation.
In some worlds, inaction is acceptable.
In others, failing to punish is itself a second-order offense.
In some worlds, gossip is a legitimate response.
In others, only direct confrontation counts.

Those are not minor cultural decorations.
They change who enforces, how costly enforcement is, and whether punishment appears stable because observers are learning a local punishment norm rather than independently endorsing the same sanction logic.

## Minimal implementor handoff

If Concord builds a sanction / exclusion / norm-enforcement lane, publish at least:

1. what responses to violations are admissible (inaction, gossip, exclusion, confrontation, material punishment, or other);
2. whether observers are expected, encouraged, or required to respond;
3. whether failing to punish is itself punishable;
4. whether anti-social or excessive punishment is itself punishable;
5. whether observers can learn enforcement style from others or whether punishment choices are independent and private.

Without that compact contract, future inheritors can mistake local punishment culture for deeper reciprocity or justice effects.
