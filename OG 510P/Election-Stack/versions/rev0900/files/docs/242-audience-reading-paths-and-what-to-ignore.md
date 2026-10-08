# Audience reading paths and “what to ignore” (size discipline)

**Track:** Shared

This archive is large and will grow. To keep it usable, treat this file plus `docs/START_HERE.md` as the stable map for orientation, not as a duplicate copy of every downstream rule.

## v897 compaction note

This file is now a compact navigation/control surface. The full pre-v897 prose bytes are preserved inside `artifacts/history/rev0897-doctrine-sprawl-preserved-docs.tar.gz` and indexed by `artifacts/reports/rev0897-doctrine-sprawl-compaction.json`.

The compaction intentionally keeps current control pointers executable instead of copying long local summaries that drift. Treat this document as an entrypoint and use the cited tables/checks as the governing source.

## Mission-first reading path

1. Start with `docs/START_HERE.md`, `README.md`, and `ARCHIVE_INDEX.md`.
2. For release integrity, use `docs/162-release-and-ci-evidence-pipeline.md`, `scripts/release_gate.py`, `scripts/release_gate_steps.py`, and `artifacts/reports/release-go-no-go-decision.json`.
3. For the current mission kernel, use `docs/215-election-lifecycle-evidence-map.md`, `docs/927-mission-kernel-closeout-gaps-and-example-county-refactor.md`, `docs/932-mission-heart-authentication-boundary-and-cloudtainer-correction-plan.md`, and `docs/934-ballot-accounting-reconciliation-and-stale-pack-audit.md`.
4. For CDF/results replay, use `tools/cdf_export_replay.py`, `tools/cdf_replay_independent_verifier.py`, `tools/ballot_accounting_reconciler.py`, `scripts/check_cdf_export_replay.py`, `scripts/check_cdf_independent_replay_verifier.py`, and `scripts/check_ballot_accounting_reconciler.py`.
5. For public voter-information surfaces, use the table `artifacts/tables/voter-facing-public-answer-surfaces.csv` and the compact family map `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`.

## What to ignore first

- Ignore historical generated reports unless a release note or current gate references them.
- Ignore superseded doctrine prose preserved in compaction bundles unless you are auditing history.
- Ignore synthetic examples as proof of live jurisdiction evidence; they are fixtures only.
- Ignore any local summary of the special-case control stack that disagrees with `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md` for the current `344–361` perimeter.

## Voter-facing surface entrypoints

The bounded voter-facing surface family is defined by `artifacts/tables/voter-facing-public-answer-surfaces.csv`. Current full-path coverage is kept here because `scripts/check_voter_facing_surface_entrypoint_coverage.py` intentionally uses this file as a user-facing navigation checkpoint.

- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md` — polling_place_directory: Where do I vote?
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md` — ballot_style_and_sample_ballot: What is on my ballot?
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md` — voter_registration_status: Am I registered and what correction path exists?
- `docs/295-mail-ballot-status-lookups-and-cure-notices-as-evidence-surfaces.md` — mail_ballot_status_and_cure: What happened to my mail ballot and what cure/help path exists?
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md` — provisional_ballot_status: What happened to my provisional ballot and why?
- `docs/297-early-voting-site-hours-and-change-notices-as-evidence-surfaces.md` — early_voting_site_hours: Where and when can I vote before Election Day?
- `docs/298-ballot-drop-box-directories-hours-and-change-notices-as-evidence-surfaces.md` — ballot_drop_box_directory: Where can I return my ballot by drop box and until when?
- `docs/299-polling-place-live-status-queue-advisories-and-reroute-notices-as-evidence-surfaces.md` — polling_place_live_status: Is my voting site usable right now and what is the fallback?
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md` — voter_id_requirements: What identification do I need and what counts?
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md` — voting_accessibility_accommodations: What accessible voting accommodations or alternate paths exist?
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md` — language_assistance_and_translated_materials: What language assistance and translated materials exist?
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md` — same_day_registration: Can I still register or update on site and what do I bring?
- `docs/304-mail-ballot-request-methods-deadlines-and-change-notices-as-evidence-surfaces.md` — mail_ballot_request: How do I request a mail ballot and by what deadline?
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md` — election_office_contact_directory: Which election office is authoritative and how do I reach it?
- `docs/306-military-and-overseas-voting-paths-fpca-fwab-and-change-notices-as-evidence-surfaces.md` — uocava_voting_path: If I am military or overseas, which ballot path and fallback apply?
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md` — voting_issue_reporting_and_escalation: Where do I report this problem or escalate it safely?
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md` — election_calendar_and_key_dates: Which dates, windows, and deadline semantics control action right now?
- `docs/309-primary-election-participation-party-affiliation-and-change-notices-as-evidence-surfaces.md` — primary_participation_and_party_affiliation: Can I participate in this primary and which ballot am I eligible to receive?
- `docs/311-mail-ballot-return-instructions-envelope-requirements-and-deadline-semantics-as-evidence-surfaces.md` — mail_ballot_return_instructions: How do I return this ballot correctly and by what deadline semantics?
- `docs/312-runoff-and-special-election-participation-district-scope-and-change-notices-as-evidence-surfaces.md` — runoff_and_special_election_participation: Is there a runoff or special election for my district and do any carry-forward rules control participation?
- `docs/313-ballot-measure-explanatory-texts-official-voter-guides-and-voters-pamphlets-as-evidence-surfaces.md` — ballot_measure_explanatory_guides: What does this measure mean, where is the authoritative guide or pamphlet, and what version controlled that explanation?
- `docs/314-candidate-withdrawal-death-disqualification-and-replacement-notices-as-evidence-surfaces.md` — candidate_field_change_notices: Did the candidate field for this race change, and which official notice now controls?
- `docs/315-precinct-district-and-jurisdiction-lookups-and-assignment-change-notices-as-evidence-surfaces.md` — assignment_scope_and_jurisdiction: Which precinct, districts, and local election jurisdiction apply to me right now?
- `docs/316-voter-history-and-participation-record-lookups-and-correction-notices-as-evidence-surfaces.md` — voter_history_and_participation_record: Does the official record now show that I voted in this election, and what correction/help path exists if it does not?
- `docs/317-mail-ballot-replacement-spoilage-nonreceipt-and-surrender-fallback-as-evidence-surfaces.md` — mail_ballot_replacement_and_surrender_fallback: My mail ballot was lost, spoiled, damaged, or never arrived; how do I get a replacement or lawfully switch to another voting path?
- `docs/318-voter-registration-updates-address-name-party-and-move-close-to-election-notices-as-evidence-surfaces.md` — voter_registration_updates_and_move_close_to_election: I moved or changed my name, address, or party affiliation; how do I update my voter record, by what deadline, and what late-change fallback applies?
- `docs/319-voter-registration-inactive-removed-statuses-and-reactivation-notices-as-evidence-surfaces.md` — inactive_removed_registration_state: My voter record says inactive or removed; can I still vote, and how do I reactivate or restore it?
- `docs/320-vote-center-countywide-voting-and-assigned-location-rules-as-evidence-surfaces.md` — location_eligibility_model_and_vote_center_rules: Can I vote at any site in my county, any assigned center, or only one designated location for this phase?
- `docs/321-provisional-ballot-issuance-reasons-partial-count-rules-and-voter-instructions-as-evidence-surfaces.md` — provisional_ballot_issuance_and_partial_count_rules: Why am I being asked to vote provisionally, what does that mean now, and what part of my ballot may count?
- `docs/322-emergency-absentee-ballots-hospitalized-incapacitated-and-late-emergency-delivery-paths-as-evidence-surfaces.md` — emergency_absentee_and_hospitalized_late_ballot_path: A late emergency or hospitalization now prevents ordinary voting; what emergency ballot path, representative-delivery rule, and deadlines control?
- `docs/323-felony-conviction-voting-eligibility-restoration-and-reregistration-help-as-evidence-surfaces.md` — conviction_voting_eligibility_and_restoration: Can I vote with this conviction right now, and if not, what restoration or re-registration path controls?
- `docs/324-no-fixed-address-homelessness-residence-and-ballot-delivery-as-evidence-surfaces.md` — no_fixed_address_and_homelessness_voting: I do not have a fixed address; can I still register or vote, what residence rule applies, and what fallback exists if mail delivery fails?
- `docs/325-confidential-voter-registration-address-confidentiality-and-protected-ballot-paths-as-evidence-surfaces.md` — confidential_voter_registration_and_protected_address: I need to vote without exposing my address; what confidential-registration, substitute-address, or protected ballot path applies?
- `docs/326-in-custody-eligible-voting-jail-detention-and-civil-commitment-ballot-access-as-evidence-surfaces.md` — in_custody_eligible_voting_and_ballot_access: I am in jail, detention, or civil commitment but may still be eligible; what address, ballot-request path, and facility handoff control how I vote?
- `docs/327-long-term-care-assisted-living-residential-facility-and-facility-assisted-voting-as-evidence-surfaces.md` — long_term_care_and_facility_assisted_voting: I live in a nursing home, assisted-living facility, treatment center, veterans home, group home, shelter, or similar residential facility; what proof, assistance team, or supervised/agent ballot path applies?
- `docs/328-college-student-voting-campus-residence-and-home-address-choice-as-evidence-surfaces.md` — college_student_voting_campus_residence_and_home_address_choice: I am a college student; should I vote from campus or home, what residence/proof rules apply, and when should I use absentee voting from the other address?
- `docs/335-guardianship-conservatorship-and-court-determined-voting-capacity-as-evidence-surfaces.md` — guardianship_conservatorship_and_voting_capacity: I am under guardianship or conservatorship, or someone says a court found me unable to vote; can I still register or vote, who decides, and what help path applies?
- `docs/336-tribal-community-voting-tribal-ids-reservation-addresses-and-tribal-government-ballot-access-paths-as-evidence-surfaces.md` — tribal_community_voting_and_reservation_access: I vote as a tribal member or from tribal land; do tribal IDs, reservation or nontraditional addresses, tribal-government buildings, or reservation voting sites change which official voting path controls?
- `docs/337-disaster-displacement-evacuation-and-temporary-relocation-voting-paths-as-evidence-surfaces.md` — disaster_displacement_and_temporary_relocation_voting: I have been evacuated or temporarily displaced by a disaster; should I keep my home address, use a temporary mailing address, and what ballot fallback controls if delivery or site access is disrupted?
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md` — new_citizen_and_newly_naturalized_voter_registration: I just became a U.S. citizen or will naturalize close to the election; when may I register, what proof or in-person rule applies, and what fallback exists if the ordinary online or deadline path does not fit?
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md` — signature_alternatives_mark_witness_stamp_and_cure: I cannot provide an ordinary handwritten signature; what mark, witness, stamp, typed/digital, or cure/update path applies so my registration or ballot still counts?
- `docs/340-youth-voter-preregistration-activation-timing-and-primary-before-general-eligibility-as-evidence-surfaces.md` — youth_voter_preregistration_activation_and_primary_before_general: I am 16 or 17, or I turn 18 near the election; may I pre-register or register now, when does it become active, and may I vote in a primary if I will be 18 by the general election?
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md` — voter_assistance_person_of_choice_interpreter_and_restricted_helpers: I need another person to help me vote or translate; who may assist me, what oath or form applies, and who is not allowed to help?
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md` — ballot_return_by_another_person_and_agent_bearer_rules: May someone else pick up, carry, drop off, or return my ballot materials for me, and what authorization, helper, bearer, or agent rules control?
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md` — challenged_voter_oaths_affidavits_witnesses_and_fail_safe_ballot_rights: Someone is challenging my right to vote right now; what oath, affidavit, witness, or fail-safe ballot path controls?

## Special-case high-risk voter-facing surfaces

The special-case voter-facing public-answer subfamily is intentionally limited to these registered surface docs. They are entrypoints for volatile, jurisdiction-specific voter questions and must not be answered from generic inference.

- `docs/335-guardianship-conservatorship-and-court-determined-voting-capacity-as-evidence-surfaces.md` — guardianship_conservatorship_and_voting_capacity: I am under guardianship or conservatorship, or someone says a court found me unable to vote; can I still register or vote, who decides, and what help path applies?
- `docs/336-tribal-community-voting-tribal-ids-reservation-addresses-and-tribal-government-ballot-access-paths-as-evidence-surfaces.md` — tribal_community_voting_and_reservation_access: I vote as a tribal member or from tribal land; do tribal IDs, reservation or nontraditional addresses, tribal-government buildings, or reservation voting sites change which official voting path controls?
- `docs/337-disaster-displacement-evacuation-and-temporary-relocation-voting-paths-as-evidence-surfaces.md` — disaster_displacement_and_temporary_relocation_voting: I have been evacuated or temporarily displaced by a disaster; should I keep my home address, use a temporary mailing address, and what ballot fallback controls if delivery or site access is disrupted?
- `docs/338-new-citizen-and-newly-naturalized-voter-registration-timing-proof-and-post-ceremony-fallback-paths-as-evidence-surfaces.md` — new_citizen_and_newly_naturalized_voter_registration: I just became a U.S. citizen or will naturalize close to the election; when may I register, what proof or in-person rule applies, and what fallback exists if the ordinary online or deadline path does not fit?
- `docs/339-signature-alternatives-mark-witness-stamp-and-accessible-signature-cure-paths-as-evidence-surfaces.md` — signature_alternatives_mark_witness_stamp_and_cure: I cannot provide an ordinary handwritten signature; what mark, witness, stamp, typed/digital, or cure/update path applies so my registration or ballot still counts?
- `docs/340-youth-voter-preregistration-activation-timing-and-primary-before-general-eligibility-as-evidence-surfaces.md` — youth_voter_preregistration_activation_and_primary_before_general: I am 16 or 17, or I turn 18 near the election; may I pre-register or register now, when does it become active, and may I vote in a primary if I will be 18 by the general election?
- `docs/341-voter-assistance-person-of-choice-interpreter-rules-and-restricted-helper-boundaries-as-evidence-surfaces.md` — voter_assistance_person_of_choice_interpreter_and_restricted_helpers: I need another person to help me vote or translate; who may assist me, what oath or form applies, and who is not allowed to help?
- `docs/342-ballot-return-by-another-person-designated-agent-or-bearer-rules-and-ballot-handoff-boundaries-as-evidence-surfaces.md` — ballot_return_by_another_person_and_agent_bearer_rules: May someone else pick up, carry, drop off, or return my ballot materials for me, and what authorization, helper, bearer, or agent rules control?
- `docs/343-challenged-voter-oaths-affidavits-witnesses-and-fail-safe-ballot-rights-as-evidence-surfaces.md` — challenged_voter_oaths_affidavits_witnesses_and_fail_safe_ballot_rights: Someone is challenging my right to vote right now; what oath, affidavit, witness, or fail-safe ballot path controls?

## Current control-stack inheritance

Do not duplicate the current special-case control-stack tail here. This document inherits it from `docs/355-special-case-voter-facing-surface-control-stack-reference-closure-and-navigation-firewall.md`, which is the canonical pointer for the live `344–361` stack.

## Boundary

This file is navigation only. It is not current voter instruction, legal advice, certification evidence, production signer authority, live-pilot authorization, live custody evidence, or proof of election outcome truth.
