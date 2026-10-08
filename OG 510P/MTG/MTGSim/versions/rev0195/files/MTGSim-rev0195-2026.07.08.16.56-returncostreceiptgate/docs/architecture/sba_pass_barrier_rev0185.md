# rev0185 — SBA Pass Barrier

rev0185 is a code-bearing state-based-action seam revision. The risky behavior was cleanup that happened inside the action that created an SBA condition, instead of waiting for the next state-based-action check/pass.

## Rule pressure

The online rules check for this pass focused on the current public rules surface for rule 704: state-based actions are checked when a player would receive priority, all applicable actions from that check are performed together, and the check repeats if anything was performed. The observed current public list also keeps Aura cleanup at 704.5m and illegal Equipment/Fortification unattach at 704.5n. Official Magic rules text is not bundled in this datacube; only metadata observations are recorded.

## Engine change

`apply_state_based_actions` now starts each pass by collecting the candidates that exist at that check boundary. It applies only that candidate set, annotating each `StateBasedActionRecord` with:

- `check_index`: one logical SBA invocation/check loop.
- `pass_index`: the repeated pass inside that invocation.
- `pass_candidate_count`: how many candidates existed at the beginning of the pass.

This prevents a newly-created SBA condition from being silently swept into the same pass. In particular, when lethal damage destroys an enchanted creature, the Aura is detached by zone-change cleanup but remains on the battlefield until the repeated SBA check. That repeated check then moves the unattached Aura to its owner's graveyard as its own `AuraGraveyard` SBA record.

## Refactor/audit fix

`clear_attachment_links_for_zone_change` no longer moves Auras directly to graveyard when their attached object leaves. It now only clears attachment metadata and emits a pending-cleanup event note. Aura graveyard movement goes through the normal SBA engine and receives structured `StateBasedActionRecord` and `ZoneChangeRecord` evidence.

The first version of this validator treated `pass_index` as globally monotonic. Broad fuzz immediately exposed that as wrong: pass indexes reset on each later priority/SBA check. The final rev0185 seal adds `check_index` and validates monotonic pass order only within one check.

## Regression

`test_sba_pass_barrier_delays_aura_cleanup_from_creature_death` proves:

- a lethal creature SBA and the Aura cleanup it creates are two separate records;
- both records share one `check_index`;
- the creature death is pass 1 and Aura cleanup is pass 2;
- validator corruption catches missing `check_index`, missing `pass_index`, and pass regression within a check.

## Remaining risk

The engine still performs the collected candidates in a deterministic category order to produce typed records. That is acceptable for the current scaffold, but a fuller SBA batch object is still the better long-term representation for replacement effects that replace multiple simultaneous SBA results or for effects that depend on whole-batch identity.
