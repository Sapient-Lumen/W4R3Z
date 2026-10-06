# GPU replay reopened-residue drift governance-retirement witnesses, discharge, sunset, return, freeze, quarantine, handoff, and mixed closeout

This is the compact successor surface for `OQ-0191`. It answers the narrow question of how scoped standing residue-drift retirement governance closes, shrinks, or hands off after the local threshold overflow that justified it has been discharged.

## Practice / observation

`rev0296` bounded any promoted residue-drift retirement governance to packet-local, carrier-bound, authority-limited, nonbinding-history, retirement-window, or mixed scope. That was necessary but not quite enough: a scoped governance surface can still outlive the reason it was opened. The new witness therefore records the exit state, not a new court.

Use this surface only when all three facts are public:

1. a compact governance-threshold surface overflowed into scoped standing governance;
2. the governance surface has a named packet, carrier, authority, history lane, and retirement window from the prior scope witness; and
3. the immediate overflow has either discharged, failed to discharge cleanly, or needs one bounded successor handoff.

## External pressure from finalizer removal, tombstone expiry, audit retention, rule silence, sampling horizon, and transparency checkpoint closures

Kubernetes-style cleanup teaches that finalizers and owner references should eventually release objects rather than become permanent owners. Prometheus-style tombstones, recording windows, and alert silence windows teach that old metric facts can remain inspectable while losing live force. OpenTelemetry sampling and trace horizons teach that a retained trace can be carried forward without binding every later packet. Transparency logs teach that durable monitorability is not the same thing as ongoing governance authority.

Those analogies support a compact governance-retirement witness: close the surface when discharged, sunset its scope when the window ends, return named authority to the ordinary owner, freeze history as nonbinding audit material, quarantine leftover residue, hand off a genuinely new successor pressure, or mark an honest mixed case. They do not import platform controllers, observability stores, or transparency logs as DelayBasin governance machinery.

## Working synthesis

The witness family is `gpu_replay_cross_observer_custody_exit_appeal_precedent_tiebreak_registry_reopened_residue_post_closeout_portability_drift_conflict_arbitration_retirement_governance_retirement_state`. It is exact-token only:

- `discharged-reopen-drift-governance-retirement` — the local overflow is discharged; retire the governance surface and return to ordinary compact witnesses.
- `scope-sunset-reopen-drift-governance-retirement` — the named packet/carrier/window expires; keep history visible but sunset the governance scope.
- `authority-return-reopen-drift-governance-retirement` — the exceptional surface has done its job; return authority to the ordinary owner, policy, or appeal lane.
- `history-freeze-reopen-drift-governance-retirement` — retained history remains citable audit material but loses live priority over future packets.
- `residue-quarantine-reopen-drift-governance-retirement` — residue remains after discharge, but it is quarantined rather than used to keep governance live.
- `successor-handoff-reopen-drift-governance-retirement` — the closeout discovered a distinct successor pressure; hand off to a new open question instead of stretching the old governance surface.
- `mixed-reopen-drift-governance-retirement` — two or more of the above are true and must be stated separately.

## Discharged vs scope-sunset vs authority-return vs history-freeze vs residue-quarantine vs successor-handoff vs mixed governance retirement

Select `discharged-reopen-drift-governance-retirement` when the scoped governance surface completed the local cleanup and no residue remains. Select `scope-sunset-reopen-drift-governance-retirement` when the window, packet, or carrier expired. Select `authority-return-reopen-drift-governance-retirement` when the important event is the handback to ordinary owner authority. Select `history-freeze-reopen-drift-governance-retirement` when the history remains visible but nonbinding. Select `residue-quarantine-reopen-drift-governance-retirement` when unresolved residue exists but should stay out of canon. Select `successor-handoff-reopen-drift-governance-retirement` when the pressure is no longer governance retirement but a different successor issue. Select `mixed-reopen-drift-governance-retirement` only when the receipt names which subcases are mixed.

## Countermodels / probes

- If a packet is simply still active, this witness is premature; keep the prior governance-scope surface live.
- If an old trace or audit entry is merely useful as evidence, use `history-freeze-reopen-drift-governance-retirement`, not permanent governance.
- If an operator wants to preserve the governance surface because it was convenient, classify that as `residue-quarantine-reopen-drift-governance-retirement` unless a new public successor pressure is explicit.
- If a later packet needs to carry a retired governance lesson into another carrier, use `successor-handoff-reopen-drift-governance-retirement` and open the successor question rather than inventing a standing portability court.
- The excluded synonyms `permanent-governance-by-scope`, `immortal-revival-history-ledger`, `operator-court-after-closeout`, `retired-governance-remains-live`, and `governance-retirement-ish` remain outside the allowed vocabulary.

## Design consequences

Receipts that use this family must name the prior governance-scope token, the discharge event or failed discharge, the authority returned or frozen, any residue quarantined, and the successor surface if one is being opened. The witness is intentionally one step smaller than a governance-retirement board: it is a closeout receipt and a fail-closed handoff path.

## Overflow test

Promote a stronger surface only if repeated future revisions show that `discharged-reopen-drift-governance-retirement, scope-sunset-reopen-drift-governance-retirement, authority-return-reopen-drift-governance-retirement, history-freeze-reopen-drift-governance-retirement, residue-quarantine-reopen-drift-governance-retirement, successor-handoff-reopen-drift-governance-retirement, or mixed-reopen-drift-governance-retirement` cannot retire scoped governance without losing portability-critical evidence, creating conflicting handoffs, or reopening the same authority dispute. Until then, post-governance-retirement portability courts, retired-governance carrier exchanges, exit-proof registries, and equivalent standing machinery stay quarantined under `QWS-0274`.

## Transformer-facing implication

For a transformer reopening DelayBasin, the important move is to stop treating scoped governance as sticky state. The model should ask: did the local overflow discharge, sunset, return authority, freeze history, leave residue for quarantine, or require a successor handoff? It should emit one exact token from `gpu_replay_cross_observer_custody_exit_appeal_precedent_tiebreak_registry_reopened_residue_post_closeout_portability_drift_conflict_arbitration_retirement_governance_retirement_state` and refuse to infer a live governance court from a useful history trail.
