---
id: '367'
revision_added: rev0277
status: canon
object_type: service_continuity
domain_tags:
- public_information
- rumor_control
- misinformation
- trusted_messengers
- warnings
- community_outreach
service_floor:
- trusted_public_information
- rumor_response_and_correction
hazard_tags:
- storm
- wildfire
- flood
- heat
- outage
- cyber_disruption
- displacement
- misinformation
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- public_information_officer
- emergency_manager
- community_organization
- media
- platform_operator
- call_center
- trusted_messenger
instrument_tags:
- monitor
- correct
- translate
- route
- verify
- publish
- listen
- protect_workers
routes_to:
- '293'
- '294'
- '328'
- '339'
- '365'
source_ids:
- S293
- S294
- S655
upstream_dependencies:
- trusted_channels
- call_center
- language_access
- field_status_feed
- dashboard
- community_partners
- worker_safety
downstream_consequences:
- people_avoid_aid
- responders_threatened
- unsafe_shelter_choice
- fraud_spread
- legitimacy_loss
- delayed_recovery
equity_lenses:
- limited_English_users
- older_adults
- immigrants
- rural_users
- people_without_internet
- politically_targeted_groups
- disaster_survivors_with_low_trust
degraded_modes:
- radio_corrections
- door_to_door_messenger
- printed_rumor_response
- call_center_live_update
- community_anchor_notice
evidence_grade: synthesis
speculation_level: medium
bottlenecks:
- information_vacuum
- slow_official_update
- language_gap
- low_trust_channel
- platform_amplification
- staff_threats
failure_modes:
- rumor_blocks_aid_application
- false_shelter_or_benefit_claim_spreads
- hostile_narrative_threatens_responders
- official_message_arrives_after_bad_information
- correction_lacks_local_messenger
proof_ledgers:
- rumor_log
- correction_response_time
- trusted_messenger_roster
- language_access_log
- call_center_question_log
- threat_to_worker_log
restoration_conflicts:
- speed_vs_verification
- correction_vs_amplification
- transparency_vs_security
- national_message_vs_local_context
assurance_tests:
- rumor_injection_drill
- multilingual_correction_test
- community_messenger_relay_test
- call_center_script_test
rumor_control_posture: rumor_log_correction_clock_trusted_messenger_route_and_worker_safety_check_required
---

# 367 — Ideal Solutions: Treat rumor, misinformation, and trusted public information as climate operational hazards

## Claim

Rumor is not just a communications problem. In disasters it can block aid applications, direct people to unsafe places, spread fraud, delegitimize responders, threaten workers, and fracture recovery coalitions.

FEMA's disaster rumor-response page says rumors and misleading information can spread quickly after any disaster and provides corrections for common disaster-related claims [S655]. The archive already treats warnings, connectivity, rumor, language, accessibility, and shutdowns as critical communication service floors [S293][S294].

House rule: **rumor control is a service floor only when it is fast, local, multilingual, evidence-linked, and paired with visible service delivery.**

## Fast rule

Every major service floor should maintain a rumor log: claim, population affected, likely harm, correction owner, evidence link, trusted messenger, language set, response time, and whether the underlying service problem is real.

## The compact canon

### 1. Information vacuums invite hostile routing

If the public cannot tell which shelters are open, how benefits work, whether water is safe, where fuel exists, or when power will return, unofficial channels will fill the gap. Some will help. Some will mislead. Some will exploit fear.

### 2. Corrections must be operational, not scolding

A correction should say: what is true, what action to take, what proof supports it, who to call, what alternative exists, and when the next update comes. It should not merely say that the rumor is false.

### 3. Trusted messengers are infrastructure

Community organizations, faith leaders, local media, mutual-aid groups, schools, health workers, disability networks, worker organizations, and small businesses often carry facts farther than official accounts. They need current scripts, not occasional press releases.

### 4. Rumor can reveal real service failure

A false claim may spread because an adjacent problem is true: the portal is broken, the call center is overloaded, a shelter turned someone away, a contractor scammed a neighbor, or officials have not explained eligibility. Rumor logs should route to service correction.

### 5. Worker safety belongs in information governance

Misinformation can produce harassment or threats against inspectors, utility crews, shelter workers, aid staff, public-health teams, and volunteers. Rumor response should include worker-safety monitoring and escalation.

## Minimum packet

A rumor-control packet includes: real-time listening; rumor triage; correction template; evidence link; dashboard route; multilingual and accessible distribution; trusted-messenger roster; call-center script; worker-threat log; fraud referral; and after-action review.

## Bottom line

The climate service floor is not “information exists.” It is that people can identify trustworthy, actionable, current information under stress, and that false claims are corrected before they cause preventable harm.

---
Citations point to `sources/register.md`.
