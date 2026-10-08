# 362. Election-office discovery ladders, national routers, and routing-divergence discipline

**Track:** Shared / Public surfaces

This document tightens one bounded seam in the voter-information layer:
**how a jurisdiction proves that the office named on its public contact surface is actually the right office, and what it does when discovery paths disagree.**

It composes with:
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/348-special-case-voter-facing-surface-direct-jurisdiction-anchor-floor-and-national-routing-nonsubstitution.md`
- `docs/349-special-case-voter-facing-surface-direct-help-route-and-contactability-floor.md`
- `docs/350-special-case-voter-facing-surface-responsible-office-specificity-and-jurisdiction-match-floor.md`
- `docs/351-special-case-voter-facing-surface-official-secure-channel-and-minimum-disclosure-floor.md`
- `artifacts/checklists/election-office-contact-directory-surface-checklist.md`
- `artifacts/templates/election-office-contact-directory-surface-payload.json`

## Why this exists (bounded)

The archive already treats official channels (`203`) and election-office contact directories (`305`) as evidence surfaces. That still leaves one quiet failure mode: a voter-facing contact page can look clean and current while the **discovery paths leading to it** have drifted.

That matters because current official guidance is routing-first and decentralized. EAC’s voter FAQs tell readers that each state makes its own voting rules, that practical answers often require the local elections office, and that `eac.gov/vote` is the route to current state and local sources. EAC’s current state-routing page says each state and territory administers elections differently, lists state election office links and local election office directories, and explicitly tells voters to verify summary information through linked state and local sources. EAC’s “Who is in charge of elections in my state?” page adds that each state has a chief election official but elections are usually administered at the county level, with real variation inside states. NASS’s current Can I Vote page says it links directly to state election websites and trusted resources rather than acting as the final rule source. Vote.gov likewise presents itself as an official government routing surface, tells users to select a state or territory for action, and emphasizes `.gov` plus HTTPS when sharing sensitive information. EAC’s FAQ toolkit for election officials reinforces the same posture by saying local election officials are the best trusted source of practical voter information and encouraging website FAQs that point readers to the right official office. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `eac_who_is_in_charge_of_elections_in_my_state_page`; xref: `nass_can_i_vote_page`; xref: `vote_gov_home_page`; xref: `vote_gov_register_page`; xref: `eac_best_practices_faqs_election_officials_page`)

So the bounded problem is not “build a better national directory.” The bounded problem is: **when a jurisdiction publishes a contact surface, can an outside reader later show how that office was discovered, whether the discovery ladder agreed, and whether any routing disagreement was surfaced instead of silently papered over?**

## What this adds (and what it does not)

This document adds a compact **discovery-ladder / router-divergence discipline** for office-contact surfaces and the voter-facing public-answer family that routes through them.

It does **not** require mirroring national directories inside this archive.
It does **not** say EAC, NASS, or Vote.gov are controlling rule sources for jurisdiction-specific questions.
It does **not** replace:
- the official-channel root in `203`,
- the office-contact surface in `305`,
- the rights/safety escalation lane in `307`, or
- the high-risk special-case controls in `345`, `348`, `349`, `350`, and `351`.

It only adds one narrow discipline: **record the discovery anchors that led to the named office, and surface material routing disagreement as evidence rather than silently choosing one path.**

## Discovery ladder floor

For an `election_office_contact_directory` surface and for other voter-facing surfaces that rely on it, maintainers should preserve a bounded discovery ladder with the following semantics:

1. **Direct jurisdiction anchor first.** Prefer the current office’s own public page, signed notice, or official state/local directory entry that directly names the responsible office.
2. **State or territory directory second, when available.** Use the official state election-office page or local-office directory as the main corroborator for office identity, scope, and current contact path.
3. **National router third, when useful.** EAC, NASS, and Vote.gov can be recorded as discovery aids or corroborators, but not as substitutes for the governing jurisdiction-specific source.
4. **Public notice beats stale directories.** If a signed current notice reroutes voters because of a closure, relocation, outage, or emergency staffing change, that notice is the current controlling routing artifact until superseded.
5. **Sensitive contact still requires secure-channel discipline.** Even if the right office is discovered, `351` still controls how sensitive records should be sent.

The ladder can be small. One direct jurisdiction anchor plus one corroborating directory/router is enough for most publishable artifacts.

## Material routing disagreement

A routing disagreement is **material** when discovery paths disagree on something that changes what the voter should do next, including:

- which office is responsible,
- whether the state office or local office owns the case,
- which phone, address, webform, or office page is current,
- whether the office is open now or temporarily rerouted,
- whether the voter should appear in person, call a hotline, use a secure webform, or move to another official help path, or
- whether a national router still points to an older directory or stale county page.

Small wording differences are not the point. Action-changing routing drift is.

## Bounded rule

For office-contact evidence surfaces and closely related voter-help surfaces:

- record at least one **direct jurisdiction anchor**,
- record any state-directory or national-router corroborators you actually relied on,
- record a bounded **routing consistency state** such as `consistent`, `minor_drift`, or `material_conflict`, and
- if routing disagreement is material, publish an explicit notice or note that names the currently controlling office/path and points to the superseding artifact.

Do **not** silently collapse disagreeing discovery paths into one “clean” answer. The disagreement itself is evidence and often explains why a voter or journalist reached the wrong office.

## Minimal payload effect

The compact payload effects belong in the existing office-contact surface shape rather than in a new artifact family. The linked example payload should therefore preserve fields for:

- `discovery_anchors[]` — the small set of public discovery artifacts actually used,
- `routing_consistency_state` — whether those anchors agreed in an action-relevant way,
- `routing_consistency_note` — a short plain-language summary of agreement or drift,
- `routing_disagreement_notice_uri` — pointer to the current superseding notice if material conflict exists, and
- `responsible_office_last_confirmed_at` — when the named office/path was last directly confirmed.

This keeps the evidence bounded: the archive records **how the office was found and whether discovery paths drifted**, without turning the payload into a crawler dump.

## Interaction with the voter-facing family

This document is especially relevant when another voter-facing surface routes readers into `305`.

Examples:
- `292`, `297`, `298`, and `299` when a polling-place or schedule surface falls back to office confirmation,
- `304`, `306`, `317`, and `322` when time-sensitive absentee or replacement paths turn into office-routing problems,
- `323` through `343` when a high-risk special-case surface needs to identify the actually responsible office without pretending that a national explainer controls the case.

For those cases, this document helps maintainers preserve the difference between:
- a **helpful router**, and
- a **governing jurisdiction-specific instruction**.

## What this is meant to catch

This rule is intentionally narrow. It is meant to catch failures such as:

- an office-contact page that names a county board while the current state directory or signed closure notice now routes the voter elsewhere,
- a special-case voter-help page that correctly says “contact your local office” but never records which discovery anchor identified that office,
- a situation where a national router still points to an older county page and the public artifact silently rewrites history by pretending the path was always clean, or
- a situation where office identity was stable but a hotline, secure webform, or physical intake address changed and the contact surface never surfaced the routing disagreement.

## Why this stays narrow

This is not a national meta-directory project.
It is not a scraper framework.
It is not a fifty-state contact-law digest.

It is a small evidence-discipline patch: **make router provenance visible, keep the direct jurisdiction source primary, and treat material routing disagreement as publishable evidence rather than cleanup residue.**

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Who is in charge of elections in my state? (xref: `eac_who_is_in_charge_of_elections_in_my_state_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- Vote.gov: Home / official secure-site marker (xref: `vote_gov_home_page`)
- Vote.gov: Register to vote / update registration (xref: `vote_gov_register_page`)
