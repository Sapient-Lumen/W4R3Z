# 294. Voter-registration-status lookups and correction notices as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public voter-registration-status lookup** as an **evidence surface**.
The goal is not to publish voter files or expose sensitive matching logic. The goal is to make four things hard to fake after the fact:

1. **What the jurisdiction told a voter** about their registration state at time `T`,
2. **Which public workflow was authoritative** for checking, updating, or escalating that status,
3. **When the public answer surface changed** because of corrections, maintenance, outages, or policy updates, and
4. **Whether the status-check path stayed accessible, language-appropriate, and consistent across declared official channels.**

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/262-jurisdictional-policy-surface-registry.md`
- `docs/269-voter-registration-and-list-maintenance-as-evidence-surfaces.md`
- `docs/290-public-incident-bulletin-with-digest-references.md`
- `docs/292-polling-place-directory-and-change-notices-as-evidence-surfaces.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`

## Why this exists (bounded)

For many voters, the first operational question is not “how do I vote?” but **“am I registered correctly, and what should I do next?”** EAC’s voter-information materials explicitly point voters to official state/local sources for **registering, updating registration, and checking registration status**, and the EAC’s state-information pages summarize those links as a core public-service function. NASS’s nonpartisan **Can I Vote** project likewise treats registration-status lookup as a top-level official voter-information task, routing people directly to state election websites. (source: `eac_election_management_guidelines_2023_pdf`, `eac_register_and_vote_in_your_state_page`, `eac_check_voter_registration_information_page`, `nass_voter_registration_status_page`)

That makes the registration-status lookup part of the legitimacy boundary. If a person later says “the website told me I was inactive,” “the portal showed the wrong address,” or “the status page was unavailable in the crucial window,” the jurisdiction should be able to reconstruct the **public answer surface** without publishing the underlying voter file.

This surface also needs tight privacy discipline. NASS notes that state voter-registration systems often contain sensitive identifiers such as full or partial Social Security, driver’s-license, or state-ID numbers, along with other personal information. Public evidence should therefore focus on the **lookup contract, effective states, correction history, and help paths** — not on publishing raw registration data. (source: `nass_public_vr_info_security_2024_pdf`)

Accessibility and language access are not optional extras. EAC’s accessible voter-registration guidance treats registration as part of the voting process that must be accessible to voters with a wide range of disabilities, and DOJ’s Section 203 guidance requires covered jurisdictions to provide election-related information and materials in the covered minority language as well as English. (source: `eac_accessible_voter_registration_page`, `justice_language_minority_citizens_page`)

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative lookup claim:** for election scope `E`, the jurisdiction identified one authoritative public path for checking registration status and updating or escalating problems.
2. **Effective-state claim:** the public surface declared the status vocabulary in use and the time window for which the answer was intended to be valid.
3. **Correction/maintenance claim:** outages, policy changes, corrected statuses, and major lookup-surface edits were published as explicit superseding events rather than silent replacement.
4. **Help-path claim:** when the portal could not resolve a voter or the answer required action, the voter-facing next step was published clearly (local office, hotline, in-person fail-safe path where applicable, deadline pointer).
5. **Accessibility/language claim:** the public lookup path and fallback materials were published in accessible formats and, where legally required, in the applicable minority language(s).
6. **Channel-parity claim:** website, state portal, mirrored information pages, hotline/help scripts, and signed notice feeds converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public lookup surface**, not the voter file by default.

- **Registration Status Surface Digest (RSSD):** digest of the authoritative public lookup contract, status vocabulary, help paths, and effective window for a jurisdiction/scope.
- **Registration Status Correction Digest (RSCD):** per-event digest for corrections affecting voter actionability: status-label changes, portal logic corrections, stale-address display fixes, outage notices, or policy/help-path updates.
- **Registration Help Path Digest (RHPD):** optional digest of the current voter-help flow used when a lookup fails, returns an ambiguous result, or directs the voter to contact an election office.
- **Registration Surface Parity Snapshot (RSPS):** optional snapshot binding the effective registration-status guidance across declared official channels.
- **Registration Status Availability Snapshot (RSAS):** optional digest for bounded uptime/degradation facts when the lookup service is unavailable or operating in a degraded mode.

Where a correction materially changes voter actionability, pair it with a signed `PublicNotice` or digest-first public bulletin (`docs/186`, `docs/290`).

## What belongs in the public registration-status payload

Keep the payload **small, decision-relevant, and privacy-first**.

Recommended fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `authoritative_lookup_uri`
- `lookup_modes` (for example `portal`, `state-info-page`, `local-office-contact`)
- public `status_terms` with plain-language explanations
- `effective_from` and optional `effective_until`
- public `help_path` / escalation pointer
- accessibility-format indicators
- `language_set`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the most recent signed correction or maintenance notice

Optional but useful:
- coarse update cadence / data freshness note
- plain-language “what to do if this looks wrong” text
- a bounded declaration of the identifiers the voter may need to provide (without revealing matching thresholds or security answers)

Do **not** publish by default:
- voter-registration records or searchable exports
- matching heuristics, fraud-detection logic, or challenge thresholds
- full or partial SSNs, driver’s-license numbers, DOBs, signatures, or other sensitive identifiers
- tiny-cell analytics that could enable intimidation, targeting, or voter-list reconstruction
- internal case notes or adjudication work queues unless moved into controlled disclosure

## Status vocabulary discipline

Jurisdictions use different legal and operational vocabularies, so this archive does **not** attempt to standardize state law. But the public surface should still make its own vocabulary legible.

Recommended discipline:
- publish the exact public status labels the voter may see,
- attach a plain-language explanation of what each label means,
- distinguish **“we cannot find you”** from **“you may need to update information”** from **“your status requires election-office review,”**
- preserve a superseding trail when labels or explanations change.

The point is not uniform law. The point is that a later dispute should be about an explicit, timestamped public vocabulary — not about a silently changing website.

## Corrections, outages, and anti-retcon rules

This evidence surface should fail **loudly** when the public answer path changes.

Rules:
- A change that affects voter actionability SHOULD produce a new **Registration Status Correction Digest**.
- Silent mutation of the public lookup explanation, help path, or status vocabulary SHOULD be treated as a governance failure.
- If the portal is unavailable in a time-sensitive period, publish an outage or degraded-service notice with the alternate official path.
- If the public answer differed across official channels, publish a parity snapshot or explicit correction note.
- Every superseding event SHOULD identify the replaced surface/version and the replacement effective state.

## Accessibility, language access, and fallback paths

A registration-status surface is only real if the affected voter can actually use it.

Minimum publishable facts:
- which languages are provided for the lookup/help path,
- which accessible formats or assistive paths are supported,
- the fallback contact or in-person path when the primary portal fails,
- the effective date/time for the current public answer surface.

This is not a full compliance dossier. It is the **minimum operational truth surface** needed so accessibility or language-access failures do not disappear into rumor or blame-shifting. Pair it with the tighter control set in `docs/248-accessibility-usability-and-language-access-as-integrity.md`. (source: `eac_accessible_voter_registration_page`, `justice_language_minority_citizens_page`)

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public registration-status lookup path for the scope?
- Can we reconstruct what a voter would have been told at time `T`?
- Were outages and corrections explicit, or silently edited away?
- Did official channels converge on the same effective public state?
- Did the lookup surface preserve privacy while still giving a clear next-action path?

These are modest claims. But they are exactly the claims that determine whether a future dispute is about **facts** or about a missing public record.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/voter-registration-status-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/voter-registration-status-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Election Management Guidelines (official voter-information websites) (source: `eac_election_management_guidelines_2023_pdf`)
- EAC: Register and Vote in Your State (state election office + registration/status/update links) (source: `eac_register_and_vote_in_your_state_page`)
- EAC: How do I check my voter registration information? (source: `eac_check_voter_registration_information_page`)
- EAC: Best Practices: Accessible Voter Registration (source: `eac_accessible_voter_registration_page`)
- NASS: Can I Vote — Voter Registration Status (source: `nass_voter_registration_status_page`)
- NASS: Public voter registration information and security of state voter registration databases (source: `nass_public_vr_info_security_2024_pdf`)
- DOJ: Language Minority Citizens / Section 203 overview (source: `justice_language_minority_citizens_page`)
