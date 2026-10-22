# Minimum Steward proof slice v0

## Purpose
This proof slice gives Steward one small executable center of gravity. It does not attempt to implement Steward, SlopOS, a service manager, a scheduler, a broker, a workflow engine, a remote admin bus, a UI framework, or a shell product. It checks the dangerous collapses that would make the archive's posture language unfalsifiable.

The executable surface now has twenty narrow corpora:

1. the component-lifecycle activation corpus;
2. the control-operation request/receipt corpus;
3. the coordination-gate corpus;
4. the pressure/admission corpus;
5. the activity-accounting corpus;
6. the dependency-gate corpus;
7. the route/channel binding corpus;
8. the demand/custody/effect corpus;
9. the currentness/control corpus;
10. the rollout-generation corpus;
11. the lineage/resume corpus;
12. the retry/hedge settlement corpus;
13. the shutdown settlement corpus;
14. the governance authorization corpus;
15. the receipt transport corpus;
16. the import reconciliation corpus;
17. the local-observation provenance corpus;
18. the witness-surface corpus;
19. the status-channel corpus;
20. the attention-notification corpus.

## Component-lifecycle activation slice
The lifecycle slice covers:

1. CH-COMP v0 component manifests;
2. CH-ACTSET v0 activation-set manifests;
3. canonical digest formation for those two objects;
4. activation receipt before readiness;
5. restart replay without authority widening;
6. runtime-cycle stale-action fences;
7. stop, quiesce, readiness, serving, traffic, material freshness, and retry/effect boundaries remaining separate;
8. adapter observations staying weak unless a Steward witness promotes them through a reviewed path.

## Control-operation slice
The operation slice covers:

1. ST-OPREQ v0 reviewed control-operation requests;
2. ST-OPRECEIPT v0 operation receipts;
3. raw host target refusal for PID, cgroup, host unit, pod/container, terminal, and shell-job selectors;
4. start requests requiring manifest fences;
5. stop/restart/quiesce/refresh requests requiring runtime-cycle fences;
6. idempotency keys refusing different canonical operation intents;
7. receipts binding to exact request digests;
8. operation results refusing readiness, serving, stopped-state, effect-success, and recovery-currentness implications.

## Coordination-gate slice
The coordination-gate slice covers:

1. ST-PRECOND v0 exact precondition witnesses;
2. ST-OPARBIT v0 operation-arbitration witnesses;
3. ST-HOLD v0 deliberate hold-state witnesses;
4. ST-PROGRESS v0 progress-window witnesses;
5. preconditions refusing to become authorization, approval, reservations, locks, execution, currentness, readiness, serving, or effect success;
6. queued, rejected, replaced, flushed, irreversible, and accepted arbitration refusing to become operation result or execution truth;
7. active holds refusing to become failure, stopped/off state, drain completion, readiness, serving, authorization, or execution;
8. progress windows refusing to become readiness, stability, serving, work completion, currentness, execution, or effect success;
9. active holds blocking accepted mutating arbitration unless the request is explicitly rejected or queued;
10. stale preconditions, expired progress windows, duplicate arbitration ids, and ambient/current targets being rejected.

## Pressure/admission slice
The pressure/admission slice covers:

1. ST-PRESSURE v0 pressure witnesses;
2. ST-HEADROOM v0 headroom/spendability witnesses;
3. ST-BACKPRESS v0 backpressure/new-work pacing witnesses;
4. ST-ADMGATE v0 admission-gate decision witnesses;
5. pressure refusing to become failure, readiness, serving, admission, repair, autoscale, execution, or effect success;
6. headroom refusing to become authority, approval, reservation, admission, retry grant, execution, readiness, serving, or effect success;
7. backpressure refusing to become demand acceptance, custody, retry reservation, readiness, serving, work completion, or effect success;
8. admission gates refusing to become authorization, approval, demand acceptance, custody, work completion, execution, readiness, serving, or external effect truth;
9. stale pressure, meter math drift, defer-without-retry-after, allow-with-exhausted-headroom, contradictory backpressure, and duplicate gate id drift being rejected.


## Activity-accounting slice
The activity-accounting slice covers:

1. ST-ACTBRACKET v0 activity-bracket witnesses;
2. ST-IDLEHINT v0 idle/busy/draining hint witnesses;
3. ST-STOPDEFER v0 bounded stop-deferral witnesses;
4. ST-ACTACCT v0 descriptive activity-accounting witnesses;
5. activity brackets refusing to become demand, custody, drain, readiness, serving, keepalive leases, work completion, lossless continuity, or effect success;
6. busy/idle/draining hints refusing stopped state, stop authority, quiescence, drain completion, currentness, readiness, serving, work completion, or effect truth;
7. stop deferral refusing approval, stopped state, clean exit, drain completion, effect success, or immortal keepalive semantics;
8. activity accounting refusing billing, quota debit, pressure, headroom, admission, demand, work completion, or external effect truth;
9. idle-while-open-bracket, deferral-over-closed-bracket, deferral-past-freshness, closed-accounting-over-open-bracket, and duplicate bracket-id drift being rejected.

## Dependency-gate slice
The dependency-gate slice covers:

1. ST-DEPSPEC v0 dependency declaration witnesses;
2. ST-DEPCHECK v0 dependency condition-check witnesses;
3. ST-DEPGATE v0 dependency-informed lifecycle request gate witnesses;
4. ST-DEPFALLBACK v0 fallback or degraded-mode witnesses;
5. dependency declarations refusing topology authority, start-order authority, readiness, serving, admission, work completion, or effect success;
6. dependency checks refusing subject readiness, subject serving, currentness, material freshness, failure, work completion, or effect success;
7. dependency gates refusing authorization, approval, execution, start success, demand, custody, readiness, serving, failure, work completion, or effect success;
8. fallbacks refusing repair, rollback success, readiness, serving, currentness, work completion, or effect success;
9. stale checks, allow-with-unavailable-hard-dependency, degrade-without-fallback, spec/check mismatch, and duplicate gate id drift being rejected.

## Route/channel slice
The route/channel slice covers:

1. ST-TBIND v0 traffic-binding witnesses;
2. ST-LIVECHAN v0 live-channel witnesses;
3. route facts refusing readiness, serving, admission, custody, work completion, and effect success;
4. route drain refusing to prove no live channels;
5. live-channel observations refusing route authority and effect success;
6. resume hints refusing lossless continuity;
7. endpoint redaction and drain-deadline truth staying bounded.

## Demand/custody/effect slice
The work-path slice covers:

1. ST-DEMAND v0 demand-episode witnesses;
2. ST-CUSTODY v0 custody witnesses;
3. ST-WORKDISP v0 work-disposition witnesses;
4. ST-EFFECT v0 effect-boundary witnesses;
5. accepted demand refusing to become local completion;
6. custody refusing to become external effect success;
7. local completion refusing to become external confirmation;
8. effect boundaries requiring ordered work basis;
9. same effect key with different canonical intent being rejected;
10. retention inversion, secret leakage, and exactly-once flattery being rejected.

## Currentness/control slice
The currentness/control slice covers:

1. ST-STATEATT v0 state-attachment witnesses;
2. ST-MATFRESH v0 material-freshness witnesses;
3. ST-PROBE v0 probe-vantage witnesses;
4. ST-CTRLVERDICT v0 control-verdict witnesses;
5. attachment facts refusing to become material freshness;
6. freshness facts refusing to become reload/use truth;
7. probe observations refusing to become serving or policy action;
8. verdict facts refusing route authority, repair clearance, and global truth;
9. stale/degraded material blocking eligible traffic verdicts unless explicitly withheld;
10. raw paths, secret material, hidden repair actions, missing non-implications, and duplicate keys being rejected.

## Rollout-generation slice
The rollout-generation slice covers:

1. ST-GENPLAN v0 generation-plan witnesses;
2. ST-RECONFAPPLY v0 runtime-cycle-bound reconfiguration-apply witnesses;
3. ST-GENREADY v0 scoped generation-readiness witnesses;
4. ST-PROMOTION v0 promotion/rollback witnesses;
5. generation plans refusing to become material freshness, reload, readiness, promotion, serving, or effect success;
6. applied reconfiguration refusing readiness, promotion, all-worker update, serving, or effect success;
7. scoped generation readiness refusing traffic binding, global readiness, stability, serving, or effect success;
8. promotion refusing serving, drain, lossless transition, work completion, rollback compensation, or effect success;
9. stale readiness, abandoned plans, unknown plans, rollback-without-origin, full-promotion weight mismatch, and duplicate generation drift being rejected.

## Lineage/resume slice
The lineage/resume slice covers:

1. ST-RTCYCLE v0 runtime-cycle witnesses;
2. ST-INCARN v0 incarnation-lineage witnesses;
3. ST-RESIDENCY v0 residency witnesses;
4. ST-RESUME v0 resume/reconciliation witnesses;
5. cycle reuse after termination being rejected;
6. stale-cycle and stale-incarnation operations being fenced;
7. residency refusing to become readiness or serving;
8. resume refusing to claim same-cycle identity, lossless continuity, or predecessor effect settlement.

## Retry/hedge settlement slice
The retry/hedge slice covers:

1. ST-RETRYADVICE v0 retry-advice witnesses;
2. ST-RETRYBUDGET v0 retry-budget witnesses;
3. ST-RETRYATTEMPT v0 retry-attempt witnesses;
4. ST-HEDGEFATE v0 hedge-fate witnesses;
5. retry advice refusing to become a reservation, grant, admission, readiness, serving, effect success, or retry success;
6. zero/exhausted budgets refusing to allow automatic retry;
7. same idempotency or effect key with different canonical intent being rejected;
8. transparent retry after commitment boundary being rejected;
9. unsafe early-data replay and retry-after-425-in-early-data being rejected;
10. effect-confirmed attempts requiring adjacent effect witness refs;
11. hedge loser cancellation refusing to prove no side effect or exactly-once truth.

## Shutdown settlement slice
The shutdown slice covers:

1. ST-QUIESCE v0 quiesce/no-new-work gate witnesses;
2. ST-DRAIN v0 drain-boundary witnesses;
3. ST-ESCALATE v0 stop-escalation / stronger-intervention witnesses;
4. ST-TERMCAUSE v0 termination-cause witnesses;
5. quiesce refusing to become stopped, drained, force-kill, no-live-channel, no-inflight-work, readiness, serving, or effect-success truth;
6. drain refusing to hide pending work or become lossless, no-side-effect, stopped, readiness, or effect-success truth;
7. escalation refusing to become final stopped, clean-exit, graceful-exit, lossless, or effect-success truth;
8. termination refusing to become drain completion, restart success, successor readiness, custody, lossless continuity, or effect-success truth;
9. clean termination after applied kill-level escalation being rejected;
10. duplicate packet ids reused for different canonical bytes being rejected.

## Governance authorization slice
The governance authorization slice covers:

1. ST-DELEGATE v0 delegation-warrant witnesses;
2. ST-REVIEW v0 operator-review witnesses;
3. ST-APPROVAL v0 approval-decision witnesses;
4. ST-AUTHCHECK v0 authorization-check witnesses;
5. owner-label-as-approval rejection;
6. expired or revoked delegation rejection;
7. review-pass-as-authorization rejection;
8. approval-as-execution rejection;
9. allowed authorization requiring delegation, review, and approval refs;
10. subject digest, delegatee, verb, component, runtime-cycle, freshness, and approval-state binding across the flow.

## Receipt transport slice
The receipt transport slice covers:

1. ST-RECEIPTCHAIN v0 receipt-chain witnesses;
2. ST-REDACTION v0 redaction witnesses;
3. ST-EXPORTBUNDLE v0 evidence-export bundle witnesses;
4. ST-REPLAYOBS v0 replay/import observation witnesses;
5. receipt chains refusing authority, current-state, effect-success, and complete-history claims;
6. redaction refusing full-fidelity, source-truth, authority, and secret-free-by-assertion claims;
7. export bundles requiring redaction evidence and refusing authority or live-state claims;
8. replay observations binding exact export digests while refusing freshness/currentness and requiring explicit gap downgrade for partial replay.

## Import reconciliation slice
The import reconciliation slice covers:

1. ST-IMPORT v0 import-observation witnesses;
2. ST-SRCAPPRAISE v0 source-appraisal witnesses;
3. ST-RECONPLAN v0 reconciliation-plan witnesses;
4. ST-RECONDECISION v0 reconciliation-decision witnesses;
5. imported receipt digest sorting and redaction gates;
6. accepted imports refusing authority, currentness, freshness, live state, and effect success;
7. source appraisal refusing current-state or mutation-authority use;
8. ready reconciliation plans requiring local witnesses and recheck horizons;
9. quarantined imports preventing weak-basis adoption;
10. reconciliation decisions refusing to execute lifecycle operations.

## Local observation provenance slice
The local observation slice covers:

1. ST-LOCALOBS v0 local observation witnesses;
2. ST-OBSAPPRAISE v0 observation appraisal witnesses;
3. ST-OBSCURSOR v0 observation cursor/gap witnesses;
4. ST-OBSATTACH v0 observation attachment/recheck witnesses;
5. host-manager, orchestrator, adapter, shell, file watcher, and cursor observations refusing native currentness, readiness, serving, freshness, authority, lifecycle mutation, demand drain, and effect success;
6. raw host identifiers and raw observation material being rejected;
7. expired appraisals and cursor gaps requiring downgrade or recheck paths.

## Witness surface slice
The witness-surface slice covers:

1. ST-WITCARD v0 witness-card surface packets;
2. ST-ACTIONAFFORD v0 action-affordance packets;
3. ST-STATUSBARRIER v0 status-barrier packets;
4. ST-SURFAUDIT v0 surface audit/refactor packets;
5. weak evidence cards refusing settled headlines and readiness/currentness promotion;
6. mutating affordances requiring exact request digest, authorization-check ref, stale fences, and review before enablement;
7. active barriers blocking enabled actions that would ignore stale or missing evidence;
8. audit/refactor records refusing to become fixes, releases, authority, or proof of correctness.

## Status channel slice
The status-channel slice covers:

1. ST-OBSSUB v0 observation-subscription packets;
2. ST-OBSDELIV v0 observation-delivery packets;
3. ST-OBSSYNC v0 observation-sync marker packets;
4. ST-OBSGAP v0 observation-gap/resync barrier packets;
5. subscriptions requiring explicit subjects and bounded views instead of ambient current-pane folklore;
6. delivered batches requiring sorted refs and refusing current-state or lossless-delivery claims;
7. sync markers refusing known gaps, future `as_of` times, global currentness, readiness, serving, quiescence, and effect success;
8. open gaps blocking risky lifecycle verbs until refresh and refusing drain/lossless flattery;
9. flow checks requiring subscription-before-delivery and rejecting synced-through markers over open gaps.

## Attention notification slice
The attention-notification slice covers:

1. ST-ATTNHINT v0 attention-hint packets;
2. ST-ATTNWATCH v0 attention-watch packets;
3. ST-NOTICE v0 notification-delivery packets;
4. ST-ATTNACK v0 attention-acknowledgement packets;
5. hints requiring exact anchors and future stale boundaries instead of current-pane folklore;
6. watches refusing automation, approval, authorization, execution, currentness, readiness, serving, and effect success;
7. notification delivery allowing reveal/focus/open/dismiss actions only;
8. delivered notices refusing user-seen, user-read, resolution, mutation, execution, and current lifecycle truth;
9. acknowledgements refusing resolution, work completion, authorization, execution, readiness, serving, and effect success;
10. flow checks requiring watch and hint before notice, notice before acknowledgement, and stable packet identity.

## Why this is enough for now
Steward has many valuable posture docs. The missing discipline was not another large surface, but repeatable checks that reject the most tempting lies:

- spawn means ready;
- route means serving;
- active host unit means Steward-ready;
- descriptor redelivery means portable authority;
- retry means safe or exactly once;
- retry advice means reservation;
- hedge winner means losing attempts caused no side effects;
- stop request means stopped;
- quiesce means all old work and live channels disappeared;
- drained means lossless or no-side-effect;
- escalation means stopped;
- termination means effect success or successor readiness;
- operation completed means component stopped;
- owner label means delegated lifecycle authority;
- review pass means approval;
- approval means execution;
- authorization means effect success;
- export means authority or live state;
- replay means currentness or freshness;
- import means authority or live state;
- source appraisal means global trust;
- reconciliation plan means execution;
- reconciliation decision means current readiness, serving, or effect success;
- local observation means native currentness;
- cursor advance means drain or lossless continuity;
- weak card headline means settled truth;
- enabled button means execution or authorization;
- clear-looking surface means no stale barrier exists;
- audit means fixed or released;
- subscribed means current;
- delivered means live truth;
- synced-through means global currentness;
- notification delivered means the user saw or approved it;
- acknowledgement means the condition was resolved;
- watch armed means automation authority;
- cursor advanced means lossless continuity;
- gap cleared means no event was ever missed globally;
- redaction means full fidelity or proof no secret ever existed;
- queued/running before manager recovery remains current after manager recovery;
- path presence means freshness;
- projected material means fresh material;
- reload/apply means readiness;
- generation readiness means traffic binding, serving, or global stability;
- promotion means serving or effect success;
- rollback means compensation for prior effects;
- restart can carry whatever the host happens to provide.

The corpora under `corpora/` are deliberately small and readable. Their purpose is to make future posture changes pay a proof tax before they become archive law.

## Executable contract
`make lint` and `make corpus` must use the shared `tools/harness_registry.py` list. `make corpus` delegates through `tools/run_corpora.py` instead of enumerating harnesses in Makefile:

- `tools/steward_lifecycle_harness.py --check`
- `tools/steward_operation_harness.py --check`
- `tools/steward_channel_binding_harness.py --check`
- `tools/steward_work_effect_harness.py --check`
- `tools/steward_currentness_control_harness.py --check`
- `tools/steward_rollout_generation_harness.py --check`
- `tools/steward_lineage_resume_harness.py --check`
- `tools/steward_retry_settlement_harness.py --check`
- `tools/steward_shutdown_harness.py --check`
- `tools/steward_governance_harness.py --check`
- `tools/steward_receipt_transport_harness.py --check`
- `tools/steward_import_reconciliation_harness.py --check`
- `tools/steward_local_observation_harness.py --check`
- `tools/steward_witness_surface_harness.py --check`
- `tools/steward_status_channel_harness.py --check`
- `tools/steward_attention_notification_harness.py --check`

Each harness verifies:

- corpus determinism: the checked JSONL must match the harness-emitted corpus byte-for-byte;
- closed decode for its authority-bearing objects;
- duplicate-key rejection for raw JSON input;
- canonical digest stability;
- cross-object checks where the schema needs another packet or manifest.

## What this slice does not prove
It does not prove host integration, runtime scheduling, network behavior, durable execution, process containment, UX quality, remote administration, job history, effect correctness, or complete UI correctness. It proves only that a few canonical records, receipts, witness transitions, and rendered witness surfaces preserve separation-of-truth rules.

## Promotion rule
A new lifecycle, operation, observation, or surface posture should not become central unless it either:

1. adds a case to one of these corpora;
2. explicitly declares why it is outside the current proof slice; or
3. belongs to a sibling cube and is referenced only as pressure.

## Adjacent material
- `component-lifecycle-activation-corpus-v0.md`
- `control-operation-corpus-v0.md`
- `channel-binding-corpus-v0.md`
- `demand-custody-effect-corpus-v0.md`
- `currentness-control-corpus-v0.md`
- `rollout-generation-corpus-v0.md`
- `lineage-resume-corpus-v0.md`
- `retry-settlement-corpus-v0.md`
- `shutdown-settlement-corpus-v0.md`
- `governance-authorization-corpus-v0.md`
- `receipt-transport-corpus-v0.md`
- `import-reconciliation-corpus-v0.md`
- `local-observation-provenance-corpus-v0.md`
- `witness-surface-corpus-v0.md`
- `status-channel-corpus-v0.md`
- `attention-notification-corpus-v0.md`
- `../30-architecture/witness-surface-posture-v0.md`
- `../30-architecture/witness-card-schema-v0.md`
- `../30-architecture/action-affordance-witness-schema-v0.md`
- `../30-architecture/status-barrier-witness-schema-v0.md`
- `../30-architecture/surface-audit-witness-schema-v0.md`
- `../30-architecture/status-channel-proof-posture-v0.md`
- `../30-architecture/observation-subscription-witness-schema-v0.md`
- `../30-architecture/observation-delivery-witness-schema-v0.md`
- `../30-architecture/observation-sync-witness-schema-v0.md`
- `../30-architecture/observation-gap-witness-schema-v0.md`
- `../30-architecture/attention-notification-proof-posture-v0.md`
- `../30-architecture/attention-hint-witness-schema-v0.md`
- `../30-architecture/attention-watch-witness-schema-v0.md`
- `../30-architecture/notification-delivery-witness-schema-v0.md`
- `../30-architecture/attention-acknowledgement-witness-schema-v0.md`
- `../30-architecture/local-observation-witness-schema-v0.md`
- `../30-architecture/observation-appraisal-witness-schema-v0.md`
- `../30-architecture/observation-cursor-witness-schema-v0.md`
- `../30-architecture/observation-attachment-witness-schema-v0.md`
- `../30-architecture/traffic-binding-witness-schema-v0.md`
- `../30-architecture/live-channel-witness-schema-v0.md`
- `../30-architecture/demand-episode-witness-schema-v0.md`
- `../30-architecture/custody-witness-schema-v0.md`
- `../30-architecture/work-disposition-witness-schema-v0.md`
- `../30-architecture/effect-boundary-witness-schema-v0.md`
- `../30-architecture/state-attachment-witness-schema-v0.md`
- `../30-architecture/material-freshness-witness-schema-v0.md`
- `../30-architecture/probe-vantage-witness-schema-v0.md`
- `../30-architecture/control-verdict-witness-schema-v0.md`
- `../30-architecture/rollout-generation-proof-posture-v0.md`
- `../30-architecture/generation-plan-witness-schema-v0.md`
- `../30-architecture/reconfiguration-apply-witness-schema-v0.md`
- `../30-architecture/generation-readiness-witness-schema-v0.md`
- `../30-architecture/promotion-witness-schema-v0.md`
- `../30-architecture/runtime-cycle-witness-schema-v0.md`
- `../30-architecture/incarnation-lineage-witness-schema-v0.md`
- `../30-architecture/residency-witness-schema-v0.md`
- `../30-architecture/resume-reconciliation-witness-schema-v0.md`
- `../30-architecture/retry-advice-witness-schema-v0.md`
- `../30-architecture/retry-budget-witness-schema-v0.md`
- `../30-architecture/retry-attempt-witness-schema-v0.md`
- `../30-architecture/hedge-fate-witness-schema-v0.md`
- `../30-architecture/quiesce-witness-schema-v0.md`
- `../30-architecture/drain-witness-schema-v0.md`
- `../30-architecture/escalation-witness-schema-v0.md`
- `../30-architecture/termination-cause-witness-schema-v0.md`
- `../30-architecture/delegation-warrant-witness-schema-v0.md`
- `../30-architecture/operator-review-witness-schema-v0.md`
- `../30-architecture/approval-decision-witness-schema-v0.md`
- `../30-architecture/authorization-check-witness-schema-v0.md`
- `../30-architecture/receipt-chain-witness-schema-v0.md`
- `../30-architecture/redaction-witness-schema-v0.md`
- `../30-architecture/evidence-export-bundle-witness-schema-v0.md`
- `../30-architecture/replay-observation-witness-schema-v0.md`
- `../30-architecture/import-observation-witness-schema-v0.md`
- `../30-architecture/source-appraisal-witness-schema-v0.md`
- `../30-architecture/reconciliation-plan-witness-schema-v0.md`
- `../30-architecture/reconciliation-decision-witness-schema-v0.md`
- `../30-architecture/component-manifest-schema-v0.md`
- `../30-architecture/activation-set-schema-v0.md`
- `../30-architecture/control-operation-request-schema-v0.md`
- `../30-architecture/control-operation-receipt-schema-v0.md`
- `../30-architecture/lifecycle-currentness-lattice-v0.md`
- `../30-architecture/slopos-boundary-crosswalk-v0.md`
