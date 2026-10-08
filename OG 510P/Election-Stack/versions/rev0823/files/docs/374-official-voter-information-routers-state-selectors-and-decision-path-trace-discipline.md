# 374. Official voter-information routers, state selectors, and decision-path trace discipline

**Track:** Shared / Public surfaces

This document treats one bounded public-risk seam as an evidence surface:
**what to require when an election office or official voting-information service exposes an interactive router, state selector, map-backed chooser, dropdown-driven wizard, or decision-tree tool that asks the public a few questions and then tells them what to do next.**

It composes with:
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/219-uncertainty-safe-public-updates.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`
- `docs/363-automated-voter-information-assistants-no-authority-lift-and-answer-trace-discipline.md`
- `docs/365-official-voter-faqs-knowledge-base-articles-and-answer-edition-discipline.md`
- `docs/373-official-voter-information-forms-applications-affidavits-and-version-acceptance-discipline.md`
- `artifacts/checklists/official-voter-information-router-surface-checklist.md`
- `artifacts/templates/official-voter-information-router-surface-payload.json`

## Why this exists (bounded)

The archive already has controls for directories, FAQ/help pages, hotline scripts, chat assistants, form packets, and the underlying voter-question family in `292–343`. That still leaves a narrow but real failure mode: **interactive official routing tools** often sit between the public and the controlling source. A voter may select a state, answer a few questions, click a map region, or follow a short decision tree and then treat the resulting next step as the answer.

Current official guidance is enough to justify a compact control here. EAC's current voter FAQ says election administration is highly decentralized and that the best practical registration and voting information comes from the local elections office. EAC's current Register and Vote in Your State tool says each state and territory administers elections differently, provides summary information pulled from state websites, and links users to state election offices, local office directories, registration/update/status information, and ballot-casting options. NASS's current Can I Vote service is similarly explicit that it was created by state election officials, helps voters figure out how and where to vote, does not capture information, and instead links directly to state election websites and trusted resources. Vote.gov's current About page says the site is a trusted official source from the U.S. government, managed by the EAC, whose mission is to make it easier for eligible voters to understand how to register and vote—not to replace state-specific authorities. EAC's current FAQ toolkit and 2026 design guidance reinforce the same maintainer posture: online voter-information materials should be clear, understandable, accessible, and structured so people can find the right current answer without confusion. (xref: `eac_voter_faqs_page`; xref: `eac_register_and_vote_in_your_state_page`; xref: `nass_can_i_vote_page`; xref: `vote_gov_about_us_page`; xref: `eac_best_practices_faqs_election_officials_page`; xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)

So the bounded problem is not “build a perfect nationwide voter wizard,” and it is not “log every click forever.”
The bounded problem is simpler:
**if an official voter-information router asks questions and gives a next-step result, how does it stay subordinate to the current official sources that control the answer, and how can the jurisdiction later reconstruct which branch logic produced that result at time `T`?**

## What this adds (and what it does not)

This document adds a compact **decision-path trace discipline** for official interactive voter-information routers.

It does **not** require every election office to build such a tool.
It does **not** replace:
- the underlying voter-question family in `292–343`,
- office/help routing in `305`,
- rights/safety escalation in `307`,
- router provenance in `362`,
- automated-assistant controls in `363`, or
- FAQ/help article editioning in `365`.

It only adds one narrow rule set:
**if the public is expected to rely on an interactive router, the tool should make its scope visible, keep its result anchored to current official sources, stop on unresolved conflict, and preserve a bounded trace of the decision path that produced the public result.**

## No hidden authority lift

An interactive router MAY help a voter discover the right office, form, site, deadline page, accommodation lane, or special-case path.
It MUST NOT behave like an unchallengeable source of jurisdiction-specific law.

The controlling artifact remains the current official page, signed notice, office directory, or direct office confirmation that actually governs the result.
In practice that means the tool should make four things plain:
- what the router is and is not deciding,
- which jurisdiction or election scope it is currently routing for,
- which official source anchors the result depends on, and
- where the voter should go when the router cannot answer safely.

A clean dropdown or map pin does not earn authority by itself.
The current official destination still controls.

## Visible scope and input discipline

A public router should say enough about its own question flow that the public is not tricked into over-trusting it.

At minimum, the router should make visible:
- the question class it is helping with,
- the key inputs or assumptions that affect the result,
- whether the result is statewide, local, office-specific, election-specific, or only a general starting point,
- and whether the user still needs to confirm the result with a current official office/page.

Do not hide critical branch assumptions such as:
- whether the voter is military or overseas,
- whether the question depends on a specific address,
- whether the path is only a state-level router that still requires a county/local lookup,
- whether the tool is only a “where to start” selector rather than a final status checker,
- or whether special-case eligibility facts require direct office review.

## Decision-path trace minimum

The archive does not need full clickstream telemetry or indefinite behavioral logging.
But for action-changing results, the router should preserve a compact **decision-path trace** sufficient to reconstruct what happened.

At minimum, that trace should make it possible to answer:
- which router version or content version was in force,
- what bounded input class or branch choices the user followed,
- which branch IDs / route states / selector values produced the result,
- which official anchors the result depended on,
- whether the result was conclusive, partial, routed onward, or stopped on conflict,
- when the result was produced,
- and which office/help path or current official page the user was sent to next.

Prefer bounded route-state identifiers, anchor IDs, timestamps, and router-version digests over raw personal data or indefinite session logs.
If address-level or record-level inputs are necessary, they should be minimized and retained only as long as the public-evidence or operational policy actually requires.

## Result-state classes

A public router should not flatten every output into the same tone of certainty.
A small result-state taxonomy is enough:

1. **Direct route** — the tool found a current official destination for the requested question.
2. **Scoped route** — the tool found a likely destination, but the result still requires address/jurisdiction/office confirmation.
3. **Conflict stop** — current official sources appear inconsistent, incomplete, or stale, so the tool routes the user to human help instead of synthesizing.
4. **Unsupported path** — the tool's question flow does not safely cover the case, so it names the official help path rather than guessing.

That small taxonomy prevents polished UI from disguising uncertainty as certainty.

## Conflict and freshness discipline

Interactive routers should inherit the archive's existing stop-on-conflict posture instead of silently improvising through stale branches.

If the current official source set is incomplete, superseded, or materially conflicting, the safe output is not a neat synthesized result card.
The safe output is to:
- say the current official materials appear inconsistent or incomplete,
- link to the current official help/office path,
- preserve that the result stopped on conflict,
- and update the router logic after the governing source state is clarified.

This matters especially for emergency polling-place moves, court-order changes, late calendar changes, special-case voter paths, and any question where the router's branch logic can drift faster than maintainers notice.

## Privacy and minimization floor

Because these tools may ask for addresses, ZIP codes, language/accessibility needs, move timing, military/overseas status, facility status, or other sensitive routing facts, the router should default to minimization.

That means:
- do not collect more than the route actually requires,
- do not retain raw inputs longer than the policy requires,
- do not turn a public router into a shadow case-management system,
- and route users to official secure channels when record-specific evidence or protected facts are required.

For many public-evidence needs, bounded route-state identifiers and source-anchor traces are enough.

## Minimal claim-set

A jurisdiction can publish a compact, inspectable claim-set:

1. **Router scope claim:** the router identifies which voter-question class and jurisdiction/election scope it is designed to help with.
2. **Authority-boundary claim:** the router is subordinate to current official pages, signed notices, directories, and responsible offices.
3. **Input/assumption claim:** branch-affecting inputs and limitations are visible enough that the public is not misled about what the tool decided.
4. **Decision-trace claim:** action-changing results are reconstructible through bounded route-state, version, anchor, and timestamp evidence.
5. **Conflict-stop claim:** unresolved official conflict produces a visible stop/handoff instead of synthetic certainty.
6. **Privacy-minimization claim:** the router avoids unnecessary retention of addresses or other sensitive voter details.
7. **Superseding claim:** material route-logic changes or source-anchor changes produce explicit updates rather than silent drift.

## Canonical digest artifacts

Publish **digests of the router surface and its route logic**, not full per-user behavioral logs.

- **Voter Router Surface Digest (VRSD):** digest of the bounded public router payload for a scope.
- **Decision-Path Logic Digest (DPLD):** digest of the current route graph / branch set / selector logic that produces public results.
- **Router Change Notice Digest (RCND):** per-event digest when route logic or governing source anchors change materially.
- **Router Result-State Snapshot (RRSS):** optional digest for a bounded public result state when the jurisdiction needs to prove what the router would have displayed for a documented branch path at time `T`.

## What belongs in the public router payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `router_surface_label`
- `router_entrypoints[]`
- `router_modalities[]`
- `question_scope_note`
- `covered_question_classes[]`
- `underlying_surface_refs[]`
- `required_inputs[]`
- `decision_trace_policy`
- `official_source_anchors[]`
- `result_state_classes[]`
- `conflict_stop_behavior`
- `human_help_fallback_uri` / `human_help_fallback_phone`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw user addresses,
- record-specific status results,
- indefinite clickstream telemetry,
- internal analytics identifiers,
- per-user debugging notes,
- or staff-only route-logic commentary that does not affect the public result.

## Relationship to the voter-facing answer-surface family

An interactive router is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing public-answer surfaces.

So the family question remains:
- `292` asks where the polling place is,
- `294` asks registration status,
- `304` asks how to request a mail ballot,
- `305` asks which office/help path is authoritative,
- `307` asks where to escalate,
- and `323–343` capture narrow special-case paths.

This document only says that, if a public router sits in front of those questions, the route logic should stay visibly bounded, anchored, and later reconstructible.

## What this is meant to catch

This rule is intentionally narrow. It is meant to catch failures such as:

- a state-selector or dropdown wizard presenting summary text as if it were the final controlling rule,
- an address- or category-based router quietly following stale branch logic after a signed change notice,
- a map-backed lookup that routes users to a state office but hides that a local office lookup is still required,
- a special-case wizard that produces confident results without exposing that the path is unsupported or needs human review,
- or a public router that cannot later show which versioned route logic or official anchors produced its action-changing result.

## Why this stays narrow

This is not a full civic-design chapter.
It is not a product-analytics program.
It is not a replacement for the underlying voter-question family.

It is a small evidence-discipline patch:
**if a public router helps voters answer “where do I start?” or “which path applies to me?”, make the branch logic bounded, keep the current official destination primary, stop on unresolved conflict, and preserve a compact decision-path trace.**

## Sources (pinned IDs / lockfile IDs)

- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Register and Vote in Your State (xref: `eac_register_and_vote_in_your_state_page`)
- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- NASS: Can I Vote (xref: `nass_can_i_vote_page`)
- Vote.gov: About vote.gov (xref: `vote_gov_about_us_page`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
