# Selector-freshness witnesses, live provenance, sync lag, and ancestor residue

This is the compact successor surface for `OQ-0127`.

## Practice / observation

Once DelayBasin already distinguishes selector coverage from selector provenance, one further failure mode stays live: a provenance label can still be correct in kind while stale in time.

A row can still honestly say that present coverage comes from inherited bindings or synced membership, yet that phrase can hide whether the inherited path is still the current ancestor, whether the synced feed is still updating, or whether the current governed object is only borrowing authority from a last-known mirror.

The compact repair is one small selector-freshness witness. It does not replace the selector witness or the selector-provenance witness. It only says whether the current provenance evidence is still live enough to count as present authority.

## External pressure from reconciled IdP teams, dynamic-group processing clocks, inherited effective tags, synced-segment status, and ignored-during-execution schedulers

GitHub IdP-linked team membership is reconciled from SCIM updates and a daily reconciliation job, so a mapped team can be legitimately synced in kind while still showing an out-of-sync posture in time.

Microsoft Entra dynamic groups likewise make the freshness question explicit: processing can lag for hours or more than a day, and the processing status exposes whether membership updates have actually run and when they last completed.

Google Cloud effective tags keep inheritance honest but also show why freshness is adjacent: an inherited tag can reappear from an ancestor once a local override is removed, so a selector may still look inherited while the operative ancestor path has changed.

LaunchDarkly synced segments and persistent-store integrations add the same pressure from another angle: synced membership can remain the right provenance class while the environment still needs a most-recent-sync timestamp and a health state before that class counts as live current authority.

GPUstorming sharpens the point. Kubernetes GPU scheduling routinely depends on labels, selectors, affinity, and taints. But `requiredDuringSchedulingIgnoredDuringExecution` explicitly allows pods to keep running after node labels change, and `NoSchedule` taints prevent new placement without evicting current pods. That means a cluster can preserve a plausible selector story for already-bound GPU work even when current selector authority is no longer live at execution time.

## Working synthesis

When a continuity claim depends on inherited or synced selector provenance still being current now, DelayBasin should preserve one compact witness that names:

- the governed row or surface;
- the selector handle / provenance path;
- the prior freshness evidence;
- the current freshness evidence;
- the `selector_freshness_state`;
- the stronger surfaces that still outrank the witness; and
- the fail-closed repair.

Keep exact timestamps, queue-depth narratives, ancestor trees, sync-job ids, audit-log events, and scheduler traces in surrounding prose. The witness stays compact and comparative.

## Live provenance vs sync lag vs ancestor residue vs mixed freshness

Use the controlled family `selector_freshness_state`:

- `live-provenance` when the inherited or synced provenance is still supported by current freshness evidence and can honestly count as present authority now;
- `sync-lag` when the provenance class is still right in kind but the current mirror, reconciliation loop, or processing queue is lagging enough that present authority must be narrowed or delayed;
- `ancestor-residue` when the current claim is borrowing legitimacy from an earlier ancestor path, removed override, or prior inherited source rather than the still-operative current source;
- `mixed-freshness` when multiple freshness conditions coexist and the row cannot honestly collapse them to one token.

## Countermodels / probes

- unchanged selector handle does not prove live authority;
- correct provenance class does not prove current freshness;
- current member inventory does not prove the current upstream path is still the operative source;
- last-known scheduler placement does not prove current execution-time selector authority.

## Design consequences

DelayBasin should keep the selector witness, selector-provenance witness, and selector-freshness witness separate:

1. selector witness: did the same handle still cover the same realized members?
2. selector-provenance witness: did the same mechanism still produce that coverage?
3. selector-freshness witness: is that mechanism still live enough now to count as present authority?

This separation keeps GPUstorming and control-plane reasoning compact. We do not need a standing selector-freshness court just to say that a synced or inherited source is real but stale.

## Overflow test

If later revisions repeatedly need standing governance over reconciliation clocks, scheduler grandfathering, upstream-health adjudication, or ancestor-path arbitration across many rows, then this compact witness is no longer enough and broader machinery may be justified.

## Transformer-facing implication

This strengthens the archive's public-belief-state posture. A model can carry forward the right selector label and even the right provenance class while still smearing time. The compact freshness witness forces current-authority evidence to stay explicit rather than letting last-known-good mechanism tokens silently count as live present truth.
