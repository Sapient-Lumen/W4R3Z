# Micro-pilot next-action router audit rev0322

## Finding

Rev0321 made the synthetic completed-packet branch repeatable, but it still left a small but important
manual state-selection burden. The operator had to decide whether the next act was packet preparation,
local completion, dry-run rehearsal, synthetic discard/regeneration, or owner review stop.

That is exactly the kind of friction that lets the cube drift back into registry and doctrine work.

## Correction

Rev0322 adds `tools/decide_teacher_tutor_micro_pilot_next_action.py` and `make micro-pilot-next`. The
router reads packet existence and readiness status, then emits one bounded next action. It can write a
scratch-only next-action brief so the command path survives handoff without becoming archive evidence.

## Substance gained

The first pedagogical path now has five executable operator states:

1. no packet: `PREPARE_PACKET`;
2. fresh blank/incomplete packet: `COMPLETE_LOCAL_PACKET_OR_OPTIONAL_DRY_RUN`;
3. synthetic positive smoke: `DISCARD_SYNTHETIC_AND_REGENERATE`;
4. future fresh completed aggregate packet: `LOCAL_OWNER_REVIEW_STOP`;
5. unexpected state: `STOP_UNKNOWN_STATUS`.

This is still not evidence, but it is forward motion because it reduces the chance that a prepared or
synthetic packet is counted as progress.

## Burden removed

The operator no longer has to open several scratch files and multiple docs to know the next safe
command. The hot path is command-routed; governance-tail retrieval is deferred until a real owner
result, real micro-pilot result, or validator failure makes it decision-bearing.

## Remaining blocker

The highest-risk unfinished work is unchanged: a human must send the bounded `FT-0181` owner request
or record a route block, and a real teacher/tutor owner must run a fresh packet before any local
readout can be considered for an evidence route.
