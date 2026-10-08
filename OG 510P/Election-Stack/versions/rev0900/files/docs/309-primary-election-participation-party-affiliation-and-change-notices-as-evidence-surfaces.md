# 309. Primary-election participation, party affiliation, and change notices as evidence surfaces

**Track:** Shared

This document treats the **public answer surface for “can I participate in this primary, which ballot am I eligible to receive, does party affiliation or declaration matter, when must I act, and what changed?”** as an **evidence surface**.
The goal is not to publish voter rolls, party-registration files, or the full body of state election law. The goal is to make six things hard to fake after the fact:

1. **Which public surface the jurisdiction identified as authoritative** for primary-participation rules for election scope `E`,
2. **Which primary model the public said applied** to the contest or ballot path in question,
3. **Whether party affiliation, party declaration, or no party relationship at all controlled ballot eligibility**,
4. **Whether any affiliation-change, registration-update, or declaration timing rule materially changed voter actionability**,
5. **Whether mixed ballots, nonpartisan contests, or presidential-primary specifics were explained clearly enough to avoid misleading answers**, and
6. **When eligibility semantics, deadlines, or participation instructions changed across official channels.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/294-voter-registration-status-lookups-and-correction-notices-as-evidence-surfaces.md`
- `docs/300-voter-identification-requirements-alternatives-and-change-notices-as-evidence-surfaces.md`
- `docs/303-same-day-registration-locations-proof-requirements-and-change-notices-as-evidence-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

A voter can know **where** to vote and still lose the race if the public answer surface is muddy about **which primary they may participate in**. In one jurisdiction the decisive fact is prior party affiliation; in another it is a ballot choice made at the polling place; in another it may be a top-two or top-four style primary where party affiliation works differently or does not gate participation in the same way. If those semantics are stale, oversimplified, or silently edited, disputes later become arguments about memory instead of evidence.

Current official guidance makes that problem concrete. EAC’s current **Primary Election Types** page explains that partisan primaries choose which candidates represent a political party in the general election, that nonpartisan primaries narrow the field of candidates, and that states use materially different primary models such as closed, open, partially closed, and partially open primaries. EAC’s current **How do I change my political party affiliation?** FAQ adds the operational consequence: some states require party affiliation to be declared when registering, some do not track party affiliation, and some require party affiliation to vote in primary elections. EAC’s current **Register and Vote in Your State** page and NASS’s current **Can I Vote** service both route voters to state-specific official election resources rather than pretending one national primary rulebook exists. (xref: `eac_primary_election_types_page`; xref: `eac_change_political_party_affiliation_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_can_i_vote_page`)

That is exactly why this surface should stay compact. The archive should not become a fifty-state treatise on primary law. It should instead preserve the bounded public facts that controlled actionability at time `T`: what kind of primary the voter-facing surface said this was, whether party affiliation or same-day declaration mattered, whether a deadline to update affiliation mattered, and where the official detailed help path lived.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative primary-rules claim:** for election scope `E`, the jurisdiction identified one authoritative public path for primary-participation rules and one authoritative help path.
2. **Primary-model claim:** the public surface stated which participation model applied (for example `closed_partisan`, `open_partisan`, `partially_closed_partisan`, `partially_open_partisan`, `nonpartisan_primary`, `top_two`, `top_four`, or other locally-described model).
3. **Ballot-eligibility claim:** the public surface stated whether ballot choice depended on prior affiliation, declaration at voting time, no party affiliation, or another clearly described rule.
4. **Timing claim:** if changing affiliation, updating registration, or making a party choice had a time-sensitive consequence, the public surface stated that timing and pointed to the authoritative detailed rule.
5. **Mixed-ballot claim:** if the ballot combined party-specific contests with nonpartisan contests, ballot questions, or presidential delegate rules, the public surface explained that clearly enough to avoid false assumptions.
6. **Change-log/parity claim:** corrections to model type, affiliation semantics, declaration rules, or timing were published as explicit superseding events rather than silent edits, and official channels converged on the same effective public answer.

## Canonical digest artifacts

Publish **digests of the public primary-participation surface**, not voter histories or party files.

- **Primary Participation Surface Digest (PPSD):** digest of the authoritative public primary-rules payload for a scope.
- **Primary Participation Change Notice Digest (PPCND):** per-event digest for changed participation semantics, party-affiliation rules, declaration rules, or timing.
- **Primary Participation Advisory Digest (PPAD):** optional digest for bounded court-order, emergency, or late-breaking ballot-eligibility advisories.
- **Primary Participation Parity Snapshot (PPPS):** optional snapshot binding the effective primary-participation answer surface across declared official channels.
- **Primary Participation Help Path Digest (PPHPD):** optional digest of the current official escalation path when a voter cannot determine which primary ballot, if any, they may receive.

## What belongs in the public primary-participation payload

Keep the payload **small, action-relevant, and explicit about semantics**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_primary_rules_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `primary_model`
- `effective_from` and optional `effective_until`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or advisory notice

Recommended rule fields:
- stable `rule_id`
- `contest_scope` or `ballot_scope`
- `ballot_eligibility_basis` (for example `party_affiliation_on_record`, `party_choice_at_voting_time`, `no_party_affiliation_required`, `mixed_model`, `see_detailed_rule`)
- `party_affiliation_required`
- optional `affiliation_change_deadline`
- optional `same_day_affiliation_change_allowed`
- optional `declaration_required_at_voting_time`
- `detail_surface_uri` or `detail_surface_ref`
- bounded `plain_language`
- optional `mixed_ballot_note`
- optional `notice_uri`

Suggested `primary_model` values:
- `closed_partisan`
- `open_partisan`
- `partially_closed_partisan`
- `partially_open_partisan`
- `nonpartisan_primary`
- `top_two`
- `top_four`
- `presidential_delegate_variant`
- `other_local_model`

Do **not** publish by default:
- searchable voter party-registration rolls
- individualized participation histories or prior primary choices
- exact party-selection telemetry from polling places or portals
- copied state statutes or party rules when a bounded summary plus pointer will do
- internal dispute notes or challenge queues unless moved into controlled disclosure

## Semantics and anti-retcon rules

This surface should fail **loudly** when eligibility semantics change.

Rules:
- A change that affects which voters may participate in a primary ballot SHOULD produce a new change notice digest.
- A change that affects party-affiliation timing or declaration semantics SHOULD produce a new change notice digest.
- The surface SHOULD distinguish **party affiliation on record** from **party declaration at voting time** from **no party linkage required**.
- If same-day registration, same-day affiliation change, or presidential-primary exceptions apply only in certain cases, the surface SHOULD say so and point to the detailed official rule.
- If the ballot includes nonpartisan contests or ballot questions alongside party-specific contests, the surface SHOULD say so clearly enough to avoid the false impression that the whole ballot is party-gated.
- Silent mutation of primary model labels, affiliation deadlines, or ballot-eligibility instructions without a superseding event SHOULD be treated as a governance failure.
- If different audiences are sent to different participation rules, publish a parity snapshot (`201`) and follow it with a signed correction notice.

## Accessibility, language access, and clarity of choice

Primary-election rules are unusually easy to misstate in ways that change behavior.

Minimum publishable facts:
- which contests or ballots the rule applies to,
- whether party affiliation on record matters,
- whether a party declaration at voting time matters,
- whether a deadline to change affiliation or update registration matters,
- where the detailed official help path lives,
- which signed notice superseded the prior answer,
- which languages and accessible formats cover the answer surface.

If the jurisdiction publishes one simplified graphic saying “anyone can vote in the primary” while the detailed official page quietly limits who may receive which ballot, the public answer surface is not trustworthy. Treat plain-language precision and channel parity as integrity controls, not design polish.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public primary-rules surface at time `T`?
- Can we reconstruct which participation model the public was told applied?
- Did the public surface say whether prior affiliation, declaration at voting time, or no party linkage controlled ballot eligibility?
- Were affiliation-change deadlines or update timing semantics stated clearly enough to matter in practice?
- Were mixed ballots, nonpartisan contests, or presidential-primary exceptions made explicit?
- Did official channels converge on the same effective public rule set, or were changes silently edited into mutable pages?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/primary-election-participation-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/primary-election-participation-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Primary Election Types (xref: `eac_primary_election_types_page`)
- EAC: How do I change my political party affiliation? (xref: `eac_change_political_party_affiliation_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_2024_pdf`)
