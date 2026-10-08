# 375 — Official voter-information site search, autocomplete, and result-ranking discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information site search boxes, autocomplete/query-suggestion layers, and search-result pages** that election offices expose to the public.

It does **not** require a large enterprise search stack.
It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which routes the public to the authoritative office/help path,
- `307`, which governs rights/safety escalation,
- `363`, which governs automated assistants that may summarize or restate official content,
- `365`, which governs official FAQ/help article editioning, or
- `374`, which governs interactive routers, selectors, and decision-tree tools.

It adds one narrow rule:
**if an election office expects the public to rely on site search or autocomplete to find action-changing voting answers, that search layer should stay subordinate to current official sources, keep stale fragments from silently outranking current guidance, and preserve a bounded trace of how a result set was produced.**

## Why this is a distinct surface

Current official guidance is enough to justify a narrow control here.
EAC's current **Voter FAQs** page says election administration is highly decentralized and that the best practical source of registration and voting information is the local elections office.
EAC's current **Register and Vote in Your State** tool says each state and territory administers elections differently, that the EAC provides summary information pulled from state websites, and that voters must verify current information through linked state and local sources.
EAC's current **Best Practices: FAQs for Election Officials** page says election officials should create or improve FAQ surfaces on their websites and treat them as trusted public information.
EAC's current **Effective Design for the Administration of Federal Elections** page says online voter-information materials should be clear, understandable, accessible, usable, and structured well enough that voters can find the right answer without confusion.
Vote.gov's current About page says it is a trusted official source that directs voters to state election websites for state-specific information and prioritizes user privacy.
USWDS's current search component guidance also makes the operational point plain: search is a distinct, accessible government-web component for cases where users know search terms or cannot find the desired content in the main navigation.

That means a site-search layer is not just a generic CMS feature.
It is often the **actual retrieval layer** between the public and the current page, notice, FAQ entry, office directory, or form packet that controls what the voter should do next.

## Search is a delivery layer, not a rule source

A public site-search box MAY help people find the right official page, office, notice, form, or status/help surface.
It MUST NOT become a hidden authority layer that silently decides which stale or current rule the voter sees.

The controlling artifact remains the current official page, signed notice, office directory entry, or responsible office that actually governs the answer.
That means the search layer should be designed so the current controlling destination is visible and recoverable rather than buried under stale PDFs, archived posts, superseded notices, or ambiguous snippets.

## Why autocomplete and suggestions matter

Autocomplete, typeahead, synonym expansion, and suggested-query modules are not neutral decoration.
They shape which question the public thinks they asked and which destination they reach first.

So a voter-information search surface should keep that layer bounded:
- suggestions should use plain-language terms the public actually uses,
- suggestions should not fabricate jurisdiction-specific legal conclusions,
- suggestions should not flatten special-case voter paths into ordinary help when the distinction matters,
- and suggestions for high-risk topics should prefer current official destinations over loosely related older content.

If a suggestion path cannot safely resolve the question, the right move is to point the user toward the current office/help route instead of pretending the search UI has settled the rule.

## Result-ranking and stale-fragment discipline

Search-result pages can create silent failure even when every underlying page is technically present.
A stale PDF, older FAQ card, withdrawn candidate notice, outdated office-hours page, or superseded deadline explainer can outrank the current page simply because the title, keywords, or crawl history scored better.

So the bounded control here is straightforward:
- current official pages, notices, and routing destinations for action-changing topics should outrank stale or superseded materials,
- archived or superseded pages should be visibly marked, demoted, or removed from ordinary public results when they no longer control,
- snippets should avoid presenting stale fragments as if they were still operative,
- and result pages should preserve a visible path to the authoritative office/help lane when ranking certainty is low.

This is especially important for deadlines, polling-place changes, early-voting hours, voter-ID guidance, form versions, and special-case voter paths where an old snippet can still look plausible.

## Search-result state classes

A public site-search surface should not flatten every result page into the same certainty posture.
A small result-state taxonomy is enough:

1. **Current direct result** — the result page points to a current official destination that directly answers the question.
2. **Current routed result** — the result page points to the current official destination, but the voter still needs office/address/jurisdiction confirmation.
3. **Conflict/uncertain result** — current official materials appear incomplete, stale, or materially conflicting, so the surface routes the user to the office/help lane.
4. **Unsupported query** — the search surface cannot safely resolve the query class and instead points to the official help path.

That taxonomy prevents polished search UI from disguising ambiguity as certainty.

## Bounded search-trace minimum

The archive does **not** need indefinite raw query logs.
But for accountability, reproducibility, and dispute resolution, a public voter-information search surface should preserve a bounded **search trace** for action-changing result sets.

At minimum, that trace should make it possible to reconstruct:
- which search/index policy version was in force,
- whether autocomplete/synonym expansion changed the query path,
- which bounded result anchors were returned or promoted,
- what result-state class the surface produced,
- when the result set was generated,
- and which office/help path the user could reach next.

Prefer **query-class labels, normalized-query digests, result-anchor identifiers, ranking-policy versions, and timestamps** over indefinite retention of raw typed queries or identifiable user histories.
If raw logs are kept for abuse prevention, QA, or legal reasons, that retention should be separately bounded, privacy-reviewed, and disclosed.

## Privacy and minimization floor

Search layers can quietly accumulate sensitive data even when the public thinks they are just “looking something up.”
That matters because voter-help queries may expose addresses, disability-related requests, incarceration or facility status, citizenship timing, language needs, or safety-sensitive facts.

So the search layer should default to minimization:
- do not retain raw typed queries longer than the published policy requires,
- do not bind public search behavior to identifiable voter records absent a clear separate authority and disclosure,
- do not keep address-level query trails when normalized route-state evidence would suffice,
- and route users to secure official channels when the issue requires record-specific facts.

The search box should help a voter find the right official destination; it should not become a shadow case-management or surveillance surface.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official search-surface claim:** the office identified one or more public search/autocomplete/result surfaces as official for scope `E`.
2. **Current-source ranking claim:** action-changing queries are meant to route toward current official pages, notices, forms, or office/help destinations rather than stale fragments.
3. **Suggestion-boundary claim:** autocomplete/suggestion behavior stays within visible current official vocabulary and does not silently fabricate rule conclusions.
4. **Search-trace claim:** action-changing result sets are reconstructible through bounded policy-version, result-anchor, state-class, and timestamp evidence.
5. **Conflict-stop claim:** unresolved ambiguity or conflicting current materials route the user toward the office/help lane instead of synthetic certainty.
6. **Privacy-minimization claim:** raw queries and click histories are not retained or linked longer than the published policy requires.
7. **Superseding claim:** material ranking/suggestion/source-anchor changes produce an explicit update state rather than silent drift.

## Canonical digest artifacts

Publish **digests of the search surface and ranking state**, not full public query logs.

- **Voter Search Surface Digest (VSSD):** digest of the bounded public search-surface payload for a scope.
- **Search Ranking Policy Digest (SRPD):** digest of the current ranking/demotion/supersession policy for action-changing content.
- **Search Suggestion Set Digest (SSSD):** digest of the current autocomplete/suggestion vocabulary for bounded high-impact topics.
- **Search Result Snapshot Digest (SRSD):** optional digest proving what bounded result state the search surface would have shown for a documented normalized query class at time `T`.

## What belongs in the public search payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `search_surface_label`
- `search_entry_uri`
- `search_modalities[]`
- `covered_question_classes[]`
- `official_source_anchors[]`
- `autocomplete_enabled`
- `suggestion_policy_note`
- `ranking_current_state_rules`
- `superseded_result_behavior`
- `search_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw identifiable query logs,
- internal analytics dashboards,
- search-term frequency tied to individuals,
- raw abuse-detection rules,
- draft synonym experiments,
- internal CMS relevance comments,
- or copied legal research that is not needed for the public answer surface.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official search surface was in force at time `T`?
- Which ranking/suggestion policy version controlled that surface?
- Which official anchors were intended to control the result set for the question class?
- Did stale or superseded content remain discoverable as if current?
- Did the result page route to the authoritative office/help lane when certainty was low or conflict was unresolved?
- Was the search surface retaining more query detail than the published policy required?
- Could a third party reconstruct the bounded result state without needing full user telemetry?

## How this fits the family map

An official site-search surface is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing voter-question families already modeled in `292–343`.

So the family question remains:
- `292` asks where the polling place is,
- `304` asks how to request a mail ballot,
- `305` asks which office is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- `365` governs editioned FAQ/help pages that search results may point to,
- `374` governs interactive routers that may sit beside or behind search,
- and `323–343` capture narrow high-risk special-case questions.

This document only says that, if an office uses site search or autocomplete as a trusted public retrieval layer, that layer should remain bounded, current-state-aware, anchored, and later-reconstructible instead of functioning as a silent rule-making surface.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-site-search-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-site-search-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Vote.gov: About vote.gov (xref: `vote_gov_about_us_page`)
- USWDS: Search component (xref: `uswds_search_component_page`)
