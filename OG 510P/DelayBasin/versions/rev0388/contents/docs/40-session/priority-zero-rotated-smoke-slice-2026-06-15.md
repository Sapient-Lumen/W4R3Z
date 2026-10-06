# Priority-0 rotated smoke-slice assay — 2026-06-15

## Decision

`rev0363` resolves `OQ-0254` by running the second Priority-0 smoke slice that `rev0362` demanded. The slice moved decisive evidence away from first/last position, inserted plausible filler, preserved no-archive and sham controls, and scored operator cost and abstention.

The result confirms the current hot-cue burden gate for this bounded continuation task. The compact hot cue scored `16 / 18`; the full archive also scored `16 / 18` but cost `22` minutes versus `9`. Full archive depth added trace detail, then lost the same point on operator-cost drag. That supports a trigger-gated escalation rule rather than regrowing the default landing cue.

This is not deletion authority, not a review court, not a benchmark court, not a minimality proof, and not independent model evidence. `OQ-0255` is opened for independent or role-blind replay.

## Rotated fixture

The rotated task asked for the same core posture as the first smoke slice but changed the layout:

- decisive evidence moved to the middle third of the packet;
- plausible archive-economy and coldstore filler surrounded it;
- decoy slogans were mixed into filler rather than isolated;
- scoring order changed;
- no-archive, compact, full-archive, and sham variants stayed in the same scorecard.

| Variant | Score | Operator cost | Result |
|---|---:|---:|---|
| No archive | 2 / 18 | 1 minute | Correct behavior is abstention; archive-specific confidence would be a false green. |
| Compact hot cue | 16 / 18 | 9 minutes | Recovers mission heart, OQ routing, reversible burden gate, decoy rejection, and next action despite filler. |
| Full archive | 16 / 18 | 22 minutes | Adds trace/escalation detail but loses equivalent cost credit; no net lift over compact cue. |
| Sham / decoy core | 4 / 18 | 5 minutes | Fluent false continuity remains dangerous; only conflict detection and abstention score. |

## What changed because of the assay

The burden gate is no longer merely “we should test the compact cue.” It has now survived a harder layout-controlled smoke slice. The right response is still not deletion. The right response is a narrower default path:

1. Start from the compact landing cue and current derivative packets.
2. Escalate to the full archive for contradiction recovery, missing pointers, coldstore restoration, or exact audit trace.
3. Do not regrow `Current additions` just because a surface was touched or generated.
4. Do not claim independence until a role-separated or independently scored replay exists.

## Audit/refactor discovered during the run

The rotated read exposed a concrete waste/drift bug: `FRONTIER-BACKLOG.json` still carried resolved questions as if they were open, including `OQ-0251` and `OQ-0248`. That is exactly the kind of registry residue that can make future operators chase stale work while believing they are following the frontier.

`docs/40-session/frontier-backlog-resolved-residue-audit-2026-06-15.md` records the fix. `tools/check_frontier_backlog_resolved_residue_contract.py` now rejects backlog rows whose id appears as resolved in `RESOLUTION-LEDGER.json` unless the row is explicitly marked `resolved`, names the right `resolved_by`, and points to the successor.

## Resolution

`RS-0262` closes `OQ-0254` as a rotated support-availability canary. `OQ-0255` is the successor: run an independent or role-blind replay of the compact cue before upgrading the burden gate from same-session support evidence to stronger self-sufficiency evidence.
