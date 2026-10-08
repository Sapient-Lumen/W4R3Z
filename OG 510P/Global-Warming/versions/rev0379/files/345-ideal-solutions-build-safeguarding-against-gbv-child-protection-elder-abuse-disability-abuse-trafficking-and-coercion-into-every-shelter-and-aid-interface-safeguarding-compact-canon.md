---
id: '345'
revision_added: rev0274
status: canon
object_type: integrity_gate
domain_tags:
- safeguarding
- GBV
- child_protection
- elder_abuse
- disability_abuse
- trafficking
- shelter
- aid_interfaces
service_floor:
- safe_access_to_aid
- safeguarding_and_referral
- confidential_complaint_and_response
hazard_tags:
- evacuation
- displacement
- shelter
- flood
- wildfire
- storm
- heat
- conflict_fragility
- outage
clock_tags:
- emergency_clock
- recovery_clock
- learning_clock
actor_tags:
- shelter_operator
- protection_lead
- GBV_service_provider
- child_protection_agency
- adult_safeguarding_agency
- law_enforcement
- community_organization
- aid_provider
instrument_tags:
- screen
- prevent
- refer
- separate
- protect
- train
- complain
- monitor
- audit
routes_to:
- '282'
- '283'
- '284'
- '287'
- '291'
- '292'
- '313'
- '314'
- '319'
- '328'
- '335'
- '337'
- '339'
- '342'
source_ids:
- S605
- S606
upstream_dependencies:
- trained_staff
- private_space
- lighting
- separate_sleeping_options
- referral_services
- transport
- confidential_records
- community_trust
- legal_and_health_services
downstream_consequences:
- violence
- exploitation
- family_separation
- aid_avoidance
- trauma
- retaliation
- rights_violation
- unreported_harm
equity_lenses:
- women_and_girls
- children
- LGBTQ_people
- disabled_people
- older_adults
- unaccompanied_minors
- survivors_of_violence
- migrants
- people_in_custody_or_institutions
- sex_workers
degraded_modes:
- private_intake_option
- women_child_safe_space
- confidential_referral_card
- community_protection_monitor
- buddy_system
- mobile_protection_team
- low_literacy_complaint_path
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- overcrowding
- privacy_absent
- staff_untrained
- unsafe_lighting_and_toilets
- aid_queue_coercion
- confidentiality_gap
- referral_capacity
- retaliation_fear
failure_modes:
- aid_access_creates_abuse_risk
- shelter_layout_enables_violence
- child_separation_untracked
- survivor_forced_to_report_to_police
- caregiver_abuse_hidden
- trafficking_risk_after_displacement
- complaint_path_not_confidential
proof_ledgers:
- safeguarding_risk_assessment
- staff_training_log
- safe_layout_and_lighting_check
- confidential_complaint_log
- referral_path_log
- child_separation_and_reunification_log
- incident_response_log
- survivor_feedback_log
restoration_conflicts:
- visibility_vs_confidentiality
- security_presence_vs_survivor_trust
- family_unity_vs_safety
- rapid_intake_vs_private_disclosure
- mandatory_reporting_vs_survivor_autonomy
assurance_tests:
- shelter_GBV_safety_walkthrough
- child_separation_drill
- confidential_complaint_test
- aid_queue_coercion_red_team
- accessible_toilet_and_lighting_audit
protection_risk: must_be_assessed_at_shelter_aid_queue_transport_casework_payment_and_reentry_interfaces
---

# 345 — Ideal Solutions: Build safeguarding against GBV, child protection, elder abuse, disability abuse, trafficking, and coercion into every shelter and aid interface

## Claim

Aid interfaces can become harm interfaces. **Shelters, aid queues, transport, registration desks, payment points, reentry checkpoints, repair programmes, and temporary housing must be designed to prevent abuse, coercion, exploitation, and retaliation.**

IASC GBV guidance is explicit that GBV risk mitigation belongs across humanitarian action, not only inside specialist services [S606]. Sphere's protection principles and minimum standards add the broader standard: dignity, protection, security, participation, WASH, shelter, food, and health must be planned together [S605].

## Compact rule

**Every service floor that brings people into a queue, shelter, vehicle, office, portal, checkpoint, or distribution site needs a safeguarding test.**

This includes gender-based violence, child protection, elder abuse, disability abuse, trafficking, family separation, sexual exploitation and abuse, harassment, retaliation, coercive aid access, unsafe toilets, unsafe lighting, privacy failure, and abusive gatekeeping.

## Minimum packet

A safeguarding packet includes:

1. sector-specific risk assessment before sites open;
2. safe layout, lighting, WASH, sleeping, charging, and private intake spaces;
3. trained staff and codes of conduct;
4. confidential complaints and survivor-centered referral;
5. child-separation and reunification protocol;
6. adult-safeguarding and disability-support protocol;
7. community feedback without retaliation;
8. incident logs that protect confidentiality but trigger correction.

## Failure modes

The bad version says protection is handled by police or a hotline. In reality, harm happens because toilets are unsafe, sleeping space is mixed without options, aid is controlled by an abuser, a child is separated during evacuation, a caregiver is abusive, transport is coercive, or a complaint path exposes the survivor.

The archive's rule: **no service floor is complete if using it increases violence or coercion risk.**

## Cube routing

Route this file whenever a packet includes shelter, distribution, aid queue, evacuation, transport, registration, casework, payments, reentry, temporary housing, repairs, legal help, schools, childcare, care homes, custody, or displacement. Pair with `282`, `283`, `291`, `313`, `314`, `319`, `328`, `335`, `337`, `339`, and `342`.

---
Citations point to `sources/register.md`.
