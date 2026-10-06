# GPU replay reopened-residue drift governance-retirement portability-drift conflict-arbitration retirement governance-retirement portability-drift witnesses, current carry, stale template, carrier conflict, revoked lesson, expired exit proof, successor-required, and mixed drift

This is the compact successor surface for `OQ-0200`. It answers the narrow question of when a carried post-arbitration-governance-retirement lesson is still current, stale, carrier-conflicted, revoked, expired, successor-required, or mixed after portability was already admitted.

The surface is intentionally smaller than a portability-drift court. It lets a later packet spend a retired scoped-governance lesson only after checking current carrier or audit basis, template staleness, carrier conflict, revocation, exit-proof expiry, successor-packet need, or an explicit mixed case. It does not create a carrier-revalidation board, exit-proof freshness registry, or standing post-retirement drift authority.

## Practice / observation

`rev0305` made retired post-arbitration governance lessons portable in bounded ways: nonportable history, audit reference, carrier template, exit-proof reference, counterexample, successor-packet requirement, or mixed carry. That solved whether a retired lesson may travel at all. It did not by itself say whether a traveled lesson remains current when a carrier changes, a template ages, an exit proof expires, a revocation appears, or a later packet asks the old lesson to do live work.

Use this surface only when all four facts are public:

1. prior governance-threshold, governance-scope, governance-retirement, and governance-retirement-portability tokens are named;
2. a retired post-arbitration governance lesson has actually traveled or is being asked to act in a later packet;
3. the later packet can name the current carrier, audit trail, template basis, exit proof, revocation evidence, expiry window, or successor-packet boundary; and
4. the receipt can state the smallest surviving use and the explicit authorities that do not survive.

## External pressure from audit currentness, finalizer release, tombstone staleness, trace-carrier rebinding, transparency revocation, and policy revalidation windows

Kubernetes audit, admission, owner reference, and finalizer surfaces show that a retained cleanup record and current admission authority are separate lanes. Prometheus staleness, tombstone, rule, and alert-window surfaces show that an old signal can stay visible while losing current force. OpenTelemetry carrier and sampling horizons show that trace context can be carrier-specific and time-bounded. Transparency checkpoints and revocation-style records show that an inclusion or exit proof can persist while its current use must be rechecked.

Those analogies support a compact portability-drift witness: mark the carry current, stale, carrier-conflicted, revoked, expired, successor-required, or mixed. They do not import admission controllers, metrics stores, trace processors, transparency logs, carrier-revalidation boards, or freshness courts into DelayBasin.

## Working synthesis

The witness family is `gpu_replay_cross_observer_custody_exit_appeal_precedent_tiebreak_registry_reopened_residue_post_closeout_portability_drift_conflict_arbitration_retirement_governance_retirement_portability_drift_conflict_arbitration_retirement_governance_retirement_portability_drift_state`. It is exact-token only:

- `current-post-arbitration-governance-retirement-carry` — the carried retired-governance lesson still has a named current carrier or audit basis and may be used only in its bounded nonbinding role.
- `stale-post-arbitration-governance-retirement-template` — the old template remains inspectable, but its carrier, owner, policy window, or review basis has aged out.
- `carrier-conflicted-post-arbitration-governance-retirement-carry` — two or more carriers, owners, trace contexts, or audit lanes disagree about whether the retired lesson can travel.
- `revoked-post-arbitration-governance-retirement-lesson` — a later receipt, revocation note, counterexample, or policy update cancels the carry without erasing the old record.
- `expired-post-arbitration-governance-retirement-exit-proof` — the proof that governance exited remains historical, but its freshness window or reuse authority has expired.
- `successor-required-post-arbitration-governance-retirement-drift` — the later packet wants live force, a broader carrier, or a new authority effect and must open a fresh successor route.
- `mixed-post-arbitration-governance-retirement-drift` — two or more drift branches are material and must be stated separately.

## Current carry vs stale template vs carrier conflict vs revoked lesson vs expired exit proof vs successor-required vs mixed drift

Select `current-post-arbitration-governance-retirement-carry` when the carried lesson is still bound to a named current carrier or audit lane. Select `stale-post-arbitration-governance-retirement-template` when only an old shape remains. Select `carrier-conflicted-post-arbitration-governance-retirement-carry` when currentness differs across carriers or owners. Select `revoked-post-arbitration-governance-retirement-lesson` when later public evidence cancels the carry. Select `expired-post-arbitration-governance-retirement-exit-proof` when the exit proof exists but its freshness/reuse window is over. Select `successor-required-post-arbitration-governance-retirement-drift` when a new live effect is being requested. Select `mixed-post-arbitration-governance-retirement-drift` only when the receipt names each subcase.

## Countermodels / probes

- A retired lesson was portable once. Portability is not currentness; check carrier, audit, exit-proof, revocation, and expiry again.
- An exit proof still exists. Existing proof is not fresh authority if its reuse window, carrier lease, or policy horizon expired.
- A carrier template looks similar. Similar shape is not a current carrier match unless the later packet names the same carrier, owner, or validation basis.
- A revocation note exists. Revocation does not erase history; classify the carry as `revoked-post-arbitration-governance-retirement-lesson` unless new current evidence re-admits it.
- The later packet wants the retired lesson to govern. Use `successor-required-post-arbitration-governance-retirement-drift`, not a hidden portability-drift court.
- The excluded synonyms `post-arbitration-governance-retirement-drift-court`, `carrier-revalidation-board-by-default`, `exit-proof-freshness-registry`, `revoked-retired-governance-history-erased`, and `post-arbitration-governance-retirement-drift-ish` remain outside the allowed vocabulary.

## Design consequences

Receipts that use this family must name the prior governance-threshold, governance-scope, governance-retirement, and governance-retirement-portability tokens; the retired packet; the later packet; the current carrier or audit basis; the exit-proof, expiry, or revocation evidence if any; the selected drift token; the smallest surviving use; explicit excluded live authorities; any successor-packet route; and the fail-closed repair. The witness is a drift/revocation classifier, not a machinery grant.

## Overflow test

Promote a stronger surface only if repeated future revisions show that `current-post-arbitration-governance-retirement-carry, stale-post-arbitration-governance-retirement-template, carrier-conflicted-post-arbitration-governance-retirement-carry, revoked-post-arbitration-governance-retirement-lesson, expired-post-arbitration-governance-retirement-exit-proof, successor-required-post-arbitration-governance-retirement-drift, or mixed-post-arbitration-governance-retirement-drift` cannot keep carried retired post-arbitration governance lessons current without either losing necessary revocation/currentness evidence or reviving live governance. Until then, post-arbitration-governance-retirement drift-arbitration courts, exit-proof priority ladders, carrier-freshness tribunals, and equivalent standing machinery stay quarantined under `QWS-0283`.

## Transformer-facing implication

For a transformer reopening DelayBasin, the important move is to separate portable retired-governance history from current authority. The model should ask: is the carried post-arbitration-governance-retirement lesson still current, stale, carrier-conflicted, revoked, expired, successor-required, or mixed? It should emit one exact token from `gpu_replay_cross_observer_custody_exit_appeal_precedent_tiebreak_registry_reopened_residue_post_closeout_portability_drift_conflict_arbitration_retirement_governance_retirement_portability_drift_conflict_arbitration_retirement_governance_retirement_portability_drift_state` and refuse to infer a live portability-drift court from a useful retired governance lesson.
