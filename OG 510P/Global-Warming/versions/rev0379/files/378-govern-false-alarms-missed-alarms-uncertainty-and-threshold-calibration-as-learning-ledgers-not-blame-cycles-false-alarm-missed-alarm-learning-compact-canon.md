---
id: '378'
revision_added: rev0278
status: canon
object_type: integrity_gate
domain_tags:
- false_alarms
- missed_alarms
- uncertainty
- threshold_calibration
- after_action_learning
- decision_logs
service_floor:
- calibrated_trigger_learning
- public_uncertainty_accountability
hazard_tags:
- all_hazards
- forecast_error
- model_error
- uncertainty
- public_backlash
clock_tags:
- emergency_clock
- seasonal_clock
- recovery_clock
- learning_clock
actor_tags:
- emergency_manager
- meteorological_service
- public_auditor
- service_owner
- community_organization
- scientist
- ombuds
instrument_tags:
- log
- review
- calibrate
- communicate_uncertainty
- demote
- update_threshold
- publish
routes_to:
- '110'
- '114'
- '322'
- '338'
- '356'
- '364'
- '371'
- '372'
- '373'
- '377'
source_ids:
- S686
upstream_dependencies:
- forecast_archive
- decision_log
- impact_data
- complaint_channel
- public_ledger
- threshold_owner
downstream_consequences:
- threshold_drift
- alert_fatigue
- delayed_action
- hidden_model_error
- loss_of_trust
equity_lenses:
- over_warned_community
- under_warned_community
- low_trust_group
- excluded_user
- small_business
- school_family
degraded_modes:
- low_regrets_activation
- localized_targeting
- graduated_action
- public_explanation
- threshold_review
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- false_alarm_punished
- missed_alarm_blame_without_fix
- uncertainty_hidden
- threshold_never_recalibrated
failure_modes:
- alert_fatigue
- official_delay
- calibration_failure
- public_trust_loss
- avoidable_harm
proof_ledgers:
- hit_false_missed_near_miss_ledger
- uncertainty_brief
- threshold_change_log
- complaint_and_appeal_log
restoration_conflicts:
- public_confidence_vs_uncertainty
- false_alarm_cost_vs_missed_alarm_harm
- expert_model_vs_local_experience
- transparency_vs_panic
assurance_tests:
- false_alarm_after_action
- missed_alarm_root_cause_review
- threshold_replay_test
- uncertainty_message_user_test
false_alarm_learning: hit_false_missed_near_miss_calibration_ledger
forecast_trigger_rule: calibration_required_after_activation_or_nonactivation
---
# 378 — Ideal Solutions: Govern false alarms, missed alarms, uncertainty, and threshold calibration as learning ledgers, not blame cycles

## Core claim

Forecast-to-action systems will sometimes activate before a hazard weakens, misses, shifts, or arrives below threshold. They will also sometimes fail to activate before a harmful event. Both cases are design inputs.

If every false alarm becomes a scandal and every missed alarm becomes a search for one villain, officials will delay action, hide uncertainty, and quietly raise thresholds until early warning loses its protective value. The right unit is a **calibration ledger**: did the threshold match the purpose, was uncertainty communicated, were no-regrets actions proportionate, were excluded users protected, and what changed after the event?

## Required ledgers

The cube should track four classes of event:

- **hit:** trigger activated and hazard/impact occurred;
- **false alarm:** trigger activated and material impact did not occur;
- **missed alarm:** no activation, but impact exceeded threshold;
- **near miss:** credible hazard or exposure almost exceeded threshold, revealing a vulnerability.

For each, record forecast signal, confidence, affected geography, actual impact, action taken, cost, benefit, complaints, exclusion, harm caused by action, harm avoided, media/rumor effects, and recommended threshold change.

## Uncertainty communication

Impact-based decision support requires communicating not only the most likely scenario, but probabilities, confidence, and extreme/historical distinctions [S686]. Trigger rules should therefore be allowed to act on low-probability high-consequence scenarios when the action is low-regrets, reversible, or targeted to people whose exposure would be catastrophic.

## No-regrets hierarchy

False-alarm tolerance depends on action type. Door-knocking, outreach, translation, staff standby, filter checks, fuel staging, and shelter readiness can tolerate more false positives than compulsory evacuation, school closure, or costly shutdown. The archive should encode this hierarchy so the trigger threshold is matched to the burden of action.

## Political rule

Leaders should explain in advance that some early actions will be taken under uncertainty by design. The after-action question is not “was the forecast perfect?” but “was the decision rule reasonable with the information available, and was it updated afterward?”

## Operating test

The file is operational only if a named owner can answer five questions before the event, not while the event is already unfolding:

1. What signal activates the action?
2. Who is authorized to act without waiting for a new meeting?
3. What money, staff, contracts, routes, and public messages are already pre-cleared?
4. Which households, workers, institutions, or places are likely to be missed by the nominal channel?
5. How will the decision be reviewed if the forecast misses, the hazard shifts, or the action causes harm?

A forecast, warning, model, dashboard, or alert is not a service floor by itself. It becomes a service floor only when it releases an owned action bundle with funding, authority, equity checks, degraded modes, public explanation, and after-action learning.

## Cube rule

Every trigger-facing packet should expose `forecast_trigger_rule`, `impact_based_decision_support`, `anticipatory_finance_rule`, `protective_action_authority`, `alert_interoperability_state`, `false_alarm_learning`, and `prepositioning_state` where relevant. Blank fields mean the cube should demote the readiness score, not assume the prose is sufficient.

---
Citations point to `sources/register.md`.
