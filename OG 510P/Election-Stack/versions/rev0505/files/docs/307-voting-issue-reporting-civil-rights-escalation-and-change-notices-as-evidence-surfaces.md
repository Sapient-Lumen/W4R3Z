# 307. Voting-issue reporting, civil-rights escalation, and change notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “I have a voting problem right now; which official help or escalation path applies, what is an emergency, what is a formal complaint path, and what changed?”** as an **evidence surface**.
The goal is not to publish allegation databases, investigative files, doxxable staff rosters, or unverified complaint narratives. The goal is to make six things hard to fake after the fact:

1. **Which official help and escalation paths the jurisdiction identified as authoritative** for election scope `E`,
2. **Which issue classes the public surface said each path handled**,
3. **Whether emergency, civil-rights, administrative-complaint, and ordinary-help routing were clearly distinguished**,
4. **Which fallback path applied when the primary office, hotline, or complaint form was unavailable**,
5. **When reporting or escalation instructions changed**, and
6. **Whether official channels stayed consistent, accessible, and explicit about the change**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/259-incident-reporting-and-coordinated-disclosure-as-evidence-surfaces.md`
- `docs/296-provisional-ballot-status-lookups-and-reason-notices-as-evidence-surfaces.md`
- `docs/301-accessible-voting-accommodations-curbside-and-change-notices-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/306-military-and-overseas-voting-paths-fpca-fwab-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter-facing help path is not the same thing as an office directory. When something goes wrong, the practical question becomes **“who should I contact now, for this kind of problem, through which official route, and what if the situation is urgent or rights-related?”** Current official guidance makes that a distinct public-information surface rather than a generic footer link.

EAC’s current voter-facing materials keep the baseline routing simple: election administration is highly decentralized, the best source of practical registration and voting information is the local elections office, and voters should use `eac.gov/vote` to reach state and local sources. NASS’s current `#TrustedInfo2026` materials make the same public-trust point in a different way: drive voters directly to election officials’ websites, social media pages, and materials for timely election information. That means the public reporting surface should start with the authoritative state/local election path, not with rumor, screenshots, or ad hoc hotline lore. (source: `eac_voter_faqs_page`; source: `eac_register_and_vote_in_your_state_page`; source: `nass_trustedinfo_2026_page`)

But the same official sources also show that **not every voting problem belongs in the same lane**. EAC’s current “Other National Contact Information” page tells the public to report misinformation/disinformation, voter intimidation, or voter fraud to the state or local election office **in addition to** using listed federal contacts. DOJ’s current voting-resources page separates ordinary state-law questions from civil-rights complaints, federal criminal civil-rights violations, and emergency violence or intimidation; it explicitly says violence, threats of violence, or intimidation at a polling place should be reported first to local police by calling 911, then to DOJ, while election-crime complaints should go to the local U.S. Attorney’s Office or FBI office. That is not incidental wording — it is an operational routing map. (source: `eac_other_national_contact_information_page`; source: `justice_voting_resources_page`; source: `justice_voter_intimidation_guide_2024_pdf`)

There is also a distinct **formal complaint** lane that should not disappear behind generic help copy. EAC’s current State Administrative Complaints page says HAVA requires states receiving funds to establish complaint procedures for violations of Title III, and says voters who want to file a complaint should contact the state directly or consult the state’s HAVA plan. That means a trustworthy public reporting surface should name when the path is “ask the local office for help,” when the path is “use the state administrative complaint procedure,” and when the path is a federal civil-rights or emergency escalation route. (source: `eac_state_administrative_complaints_page`)

Accessibility and language access remain load-bearing. DOJ’s current voting-resources page exposes multilingual access to the page itself and explicitly includes lack of accessibility while voting, voter-registration issues, and absentee-voting issues for uniformed services or overseas voters as examples of reportable civil-rights problems. The archive should therefore treat accessibility and language coverage as part of the reporting surface, not a side note. Pair this document with `docs/301`, `docs/302`, and `docs/306` instead of assuming one generic contact method is enough for every issue class. (source: `justice_voting_resources_page`; source: `eac_accessibility_resources_page`; source: `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative reporting-path claim:** for election scope `E`, the jurisdiction identified one authoritative public path for voting-problem reporting and help.
2. **Issue-class routing claim:** the public surface stated which official path applies to each problem class (for example location confusion, registration problem, accessibility barrier, language-assistance problem, intimidation/threat, misinformation, suspected fraud, UOCAVA problem, or HAVA administrative complaint).
3. **Emergency-escalation claim:** the public surface distinguished urgent safety issues from non-emergency voting questions.
4. **Formal-complaint claim:** the public surface stated whether and where a formal state administrative complaint path exists, rather than collapsing everything into one generic contact form.
5. **Change-log claim:** changes to numbers, forms, office availability, emergency-routing instructions, or complaint procedures were published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, hotline scripts, PDFs, and signed notices converged on the same effective reporting state in accessible and, where required, language-appropriate forms.

## Canonical digest artifacts

Publish **digests of the public reporting and escalation surface**, not complaint contents or investigative records.

- **Voting Issue Reporting Surface Digest (VIRSD):** digest of the authoritative public reporting/escalation payload for a scope.
- **Voting Issue Reporting Change Notice Digest (VIRCND):** per-event digest for changed hotlines, forms, office routing, complaint paths, or escalation instructions.
- **Emergency Voting Escalation Advisory Digest (EVEAD):** optional digest for urgent public guidance about threats, intimidation, safety events, or immediate rerouting.
- **State Administrative Complaint Path Digest (SACPD):** optional digest when the jurisdiction updates its formal HAVA complaint path or filing instructions.
- **Voting Issue Reporting Surface Parity Snapshot (VIRSPS):** optional snapshot binding the effective reporting/escalation surface across declared official channels.

## What belongs in the public reporting payload

Keep the payload **small, action-relevant, and issue-class aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_reporting_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `effective_from` and optional `effective_until`
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction, outage, or escalation notice

Recommended reporting-specific fields:
- `issue_classes`
- `reporting_routes`
- `emergency_rule`
- `state_administrative_complaint_path`
- `civil_rights_reporting_path`
- `federal_election_crime_reporting_path`
- `languages_available`
- accessibility / relay indicators
- `fallback_contact_path`

Recommended per-route fields:
- stable `route_id`
- `issue_classes`
- `priority` (`emergency`, `urgent`, `standard`)
- `contact_type` (`phone`, `webform`, `office_directory`, `email`, `in_person`, `law_enforcement`, `state_complaint_portal`)
- `value`
- `plain_language`
- `call_911_first`
- `availability_scope`
- `formal_complaint`
- `after_hours_behavior`

Do **not** publish by default:
- unverified complaint narratives or allegation feeds
- names of complainants, witnesses, or accused private persons
- investigative workflow details, evidentiary thresholds, or law-enforcement notes
- internal case-management IDs or ticket metadata
- direct personal numbers for staff unless intentionally public and role-bound

## Routing semantics and anti-retcon rules

The reporting surface should fail **loudly** when the public escalation path changes.

Rules:
- A change that affects which office, hotline, complaint form, or emergency path the public should use SHOULD produce a new change notice digest.
- The public surface SHOULD distinguish **ordinary election help**, **state administrative complaint**, **civil-rights reporting**, and **emergency/law-enforcement** routing when the action changes.
- If the jurisdiction instructs the public to call 911 first for threats or violence, that rule SHOULD appear explicitly and consistently across all declared official channels.
- If a webform, hotline, or office route is unavailable, publish a degraded-service notice naming the alternate official path.
- Silent mutation of complaint instructions, hotline numbers, or emergency guidance without a superseding event SHOULD be treated as a governance failure.
- If the state administrative complaint process lives off-site or in a state-plan document, the public surface SHOULD still point to that path explicitly rather than assuming the voter will discover it.

## Accessibility, language access, and next-step clarity

A reporting surface only matters if a stressed voter can use it during the decision window that matters.

Minimum publishable facts:
- which public path is authoritative for ordinary election help,
- which path applies to civil-rights or discrimination complaints,
- which path applies to emergency threats or intimidation,
- whether a formal state administrative complaint path exists and where it lives,
- which languages and accessible/relay paths are available,
- which public notice superseded the prior routing state.

This is not a universal voter-rights handbook. It is the **minimum operational truth surface** needed so voters, journalists, observers, and courts can reconstruct what the official public answer actually was when a person needed help or escalation. Pair it with `docs/305` for office-routing facts, `docs/195` for rumor-control/state updates, `docs/301` and `docs/302` for protected-access categories, and `docs/306` for UOCAVA-specific lanes. (source: `eac_other_national_contact_information_page`; source: `justice_voting_resources_page`; source: `eac_state_administrative_complaints_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public path for reporting or escalating a voting problem at time `T`?
- Could a voter tell the difference between ordinary help, formal complaint, and emergency reporting?
- Did the public surface say which problems belonged to which official route?
- Were hotline or complaint-form changes explicit, or silently edited away?
- Did official channels converge on the same effective reporting and escalation state?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voting-issue-reporting-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voting-issue-reporting-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (source: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (source: `eac_register_and_vote_in_your_state_page`)
- EAC: Other National Contact Information (source: `eac_other_national_contact_information_page`)
- EAC: State Administrative Complaints (source: `eac_state_administrative_complaints_page`)
- EAC: Accessibility resources for election officials (source: `eac_accessibility_resources_page`)
- NASS: #TrustedInfo2026 (source: `nass_trustedinfo_2026_page`)
- DOJ: Voting resources / report voting issues (source: `justice_voting_resources_page`)
- DOJ: Voter Intimidation Under Federal Law (source: `justice_voter_intimidation_guide_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
