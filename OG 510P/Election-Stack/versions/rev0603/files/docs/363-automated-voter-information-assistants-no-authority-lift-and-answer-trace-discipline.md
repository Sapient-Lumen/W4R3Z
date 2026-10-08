# 363. Automated voter-information assistants, no-authority-lift, and answer-trace discipline

**Track:** Shared / Public surfaces

This document tightens one bounded seam in the archive's voter-information layer:
**what to require when an election office exposes an automated search assistant, chatbot, FAQ bot, or LLM-backed answer surface to the public.**

It composes with:
- `docs/194-synthetic-media-and-comms-authenticity-minimum-controls.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/219-uncertainty-safe-public-updates.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/305-election-office-contact-directories-office-hours-and-change-notices-as-evidence-surfaces.md`
- `docs/307-voting-issue-reporting-civil-rights-escalation-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/345-special-case-voter-facing-surface-authority-hierarchy-and-official-routing-precedence.md`
- `docs/347-special-case-voter-facing-surface-unresolved-conflict-stop-and-no-synthesis-rule.md`
- `docs/362-election-office-discovery-ladders-national-routers-and-routing-divergence-discipline.md`
- `artifacts/checklists/automated-voter-information-assistant-surface-checklist.md`
- `artifacts/templates/automated-voter-information-assistant-surface-payload.json`

## Why this exists (bounded)

The archive already has strong controls for official pages, directories, signed notices, rumor-control surfaces, and special-case voter-help pages. That still leaves a narrow but now important failure mode: **the public may increasingly encounter automated answer surfaces before they reach the underlying official page.**

Current official guidance is explicit enough to justify a bounded control here. EAC's current AI and election-administration guidance says AI-powered tools can help election offices but can also accelerate false or biased information, and it adds that AI-generated voting information may look plausible while still being inaccurate, which is especially harmful for voting dates, hours, and locations. EAC's AI toolkit likewise frames the problem as one of communications and directs election officials toward proactive routing to verifiable official sources of accurate information. EAC's current blog guidance for election officials adds three operational themes that matter directly here: have a content-review/public-communications plan for AI misuse, test that plan in tabletop exercises, and build public trust in election officials ahead of time. NASS's current `#TrustedInfo2026` posture still points the public toward state and local election officials as the reliable source of election information, and Vote.gov says it is a trusted source that routes voters to state election websites for state-specific rules rather than acting as the registration authority itself. NIST's AI RMF separately treats transparency, explainability, documentation, and post-deployment monitoring as core trustworthiness and governance work rather than optional UX polish. That is enough to justify not only source anchoring, but also visible notice, operating-bound disclosure, and feedback-fed review for official election assistants. (xref: `eac_ai_and_election_administration_page`; xref: `eac_ai_toolkit_2023_pdf`; xref: `eac_emerging_technology_ai_and_elections_blog_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_about_us_page`; xref: `nist_ai_rmf_100_1_pdf`)

So the bounded problem is not "ban AI" and it is not "certify a perfect chatbot." The bounded problem is simpler:
**if an election office deploys an automated answer surface, how does it prevent that surface from silently becoming a new authority layer above the official pages, notices, and office contacts that actually control the answer?**

## What this adds (and what it does not)

This document adds a compact **no-authority-lift + answer-trace discipline** for automated voter-information assistants, plus a small public notice / source-hierarchy / operating-bounds layer that keeps the assistant's limits inspectable at first contact.

It also adds a small **lifecycle-state honesty rule**: if the public assistant is only a pilot, temporarily paused, or already retired, the public surface should say so explicitly instead of drifting between internal phases while the voter keeps treating it like a stable production help lane.

It does **not** require election offices to deploy such assistants.
It does **not** claim LLMs are safe for unsupervised legal interpretation.
It does **not** replace:
- the underlying voter-facing answer surfaces in `292–343`,
- the office-routing fallback in `305`,
- the rights/safety escalation lane in `307`,
- the current-official hierarchy rules in `345`, or
- the unresolved-conflict stop rule in `347`.

It only adds one narrow control set:
**if an automated assistant is exposed to the public, keep it anchored to current official sources, make its role and limits visible at first contact, make action-changing answers traceable, and stop it from inventing or silently synthesizing governing instructions.**

## No-authority-lift rule

An automated assistant MAY help users discover, summarize, translate, or navigate official election information.
It MUST NOT present itself as an independent authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, official directory entry, or responsible office identified through the normal routing hierarchy.

In practice that means the assistant surface should say, in plain language, that it is:
- a helper for finding and restating official information,
- not a substitute for the current controlling jurisdiction-specific instruction, and
- not permitted to outrank a later signed notice, current state/local page, or direct office confirmation.

## Point-of-interaction notice and short warning label

The assistant should not make the user infer, after the fact, that they were interacting with an automated system.
At the point where the public meets the assistant, the surface should keep a short, plain-language notice that says:
- this is an automated assistant,
- it helps find or restate current official election information,
- it may be incomplete or mistaken, especially on action-changing topics, and
- the user can reach an official human-help or escalation lane if needed.

That short warning label does not replace the fuller authority statement.
It complements it by interrupting false certainty at the moment the generated answer is most persuasive.
The notice should stay visible enough that a user does not have to open a buried legal footer to learn that the surface is automated or to find the human-help fallback.

## Lifecycle phase labels and state honesty

An official automated voter-information assistant should not drift through hidden phases while the public keeps treating it like a stable production channel.
So the assistant surface or its public operating-bounds card should expose a small **lifecycle phase label** chosen from a bounded state set such as:
- `pre_deployment_not_live`
- `pilot_or_beta_limited_live`
- `production`
- `paused`
- `retired`

The point is not product marketing.
The point is to keep the public record honest about whether the office is still learning on a bounded live scope, relying on the assistant in normal operations, temporarily suspending it while issues are investigated, or preserving only a historical/tombstoned record after retirement.

At minimum the public-facing state disclosure should make it possible to tell:
- the current phase,
- when the phase last changed,
- whether the assistant is limited to a bounded topic/jurisdiction/live-user cohort,
- what evidence or review is expected before the next phase transition when the assistant is not yet full production,
- and where the voter should go instead if the assistant is paused or retired.

A pilot or beta should not silently masquerade as production.
A paused assistant should not continue to look available while routing or citation quality is under investigation.
A retired assistant should not persist as a zombie public-help lane without a clear tombstone, redirect, or successor path.


## Action-changing answer floor

For answers that change what the voter should do next, the assistant should either:

1. **name the current official anchor(s) it is using**, or
2. **decline to answer conclusively and route the user to the official office/path.**

This floor is especially important for:
- dates and deadline semantics,
- polling-place / early-voting / drop-box locations and hours,
- ID requirements and alternatives,
- registration status / update / same-day-registration paths,
- absentee or replacement-ballot deadlines,
- special-case eligibility or accommodation questions,
- any issue where the next step depends on the responsible office or a current superseding notice.

If the assistant cannot point to a current official anchor for one of those questions, the safe answer is not a synthetic guess. The safe answer is a bounded handoff.

## Approved source hierarchy and citation gate

For action-changing topics, the assistant should operate under an explicit **approved source hierarchy** rather than a vague promise to be generally helpful.
A compact hierarchy normally prefers, in order:
- current canonical service pages,
- current signed notices or current-cycle status pages,
- official office directories and office-specific help/contact routes,
- official forms, wizards, or transactional flows when one already exists,
- and only then narrowly approved explanatory materials.

This has one practical consequence: **no current source, no authoritative-sounding answer.**
If the assistant cannot name a current official anchor close to the answer, it should abstain, ask for narrowing information that would make grounding possible, or route the user to the official wizard, form, office, or escalation path that actually governs the case.

Where a maintained official wizard, lookup, or form already exists, the assistant should prefer routing the voter there instead of reconstructing branching eligibility logic in free text.
That keeps the assistant from becoming a shadow copy of a faster-changing official transaction surface.


## Conflict and ambiguity stop rule

An automated assistant MUST inherit the archive's existing conflict discipline rather than papering it over.

If the assistant sees materially conflicting or incomplete official materials, it should not combine fragments into a confident jurisdiction-specific instruction.
Instead it should:
- state that the current official materials appear inconsistent or incomplete,
- identify the office/path that can resolve the question now,
- point to the latest visible signed notice or official directory entry when one exists, and
- preserve a bounded record that the answer stopped on conflict rather than inventing a synthesis.

That keeps `347` and `362` meaningful even when the first user contact point is a generated answer surface.

## Official discoverability and dependency honesty

If an election office is willing to expose a public assistant as an **official** voter-help surface, the public should be able to rediscover that fact without relying on screenshots, vendor chrome, or app-store memory.
So the assistant should appear in the office's **official channel directory** (`203`) or equivalent domain-first discovery route (`204`) with a stable assistant/help channel identifier and a canonical landing URI.
That directory entry can stay small, but it should not leave a voter guessing whether the chat surface is official, experimental, migrated, or already withdrawn.

The same honesty applies to material external dependencies.
A voter does not need a procurement dossier, but the operating-bounds card should say enough to avoid false impressions of sovereign control, including:
- whether the assistant's inference and retrieval path is primarily **in-house**, **vendor-hosted**, or **mixed**,
- whether voter questions leave the office's direct hosting boundary for processing,
- and which material external suppliers, model families, managed AI services, moderation layers, or hosted retrieval components sit in the action-changing answer path when those dependencies are stable enough to name publicly.

A switch in model provider, managed inference host, moderation layer, retrieval service, or data-processing boundary is not merely a quiet engineering tweak if it can materially change answer quality, evidence access, continuity, or public risk.
For this control, those changes should trigger a **governance refresh**: update the operating-bounds card, refresh the assistant payload, re-check directory discovery, and decide whether the phase label, scope note, or `last_verified_at` posture must change.

This stays bounded because it does **not** require disclosing sensitive internals or secrets.
It only requires enough public truthfulness that an official assistant cannot quietly become a shadow vendor surface whose authority, hosting boundary, or dependency churn is invisible to the voter.

## Public operating-bounds card

A public election assistant should also keep a small, stable **operating-bounds card** or similarly compact public description that a voter, reporter, observer, or partner can re-find later.
That card does not need vendor internals or model-marketing prose.
It should say, in bounded terms:
- what the assistant is for,
- what lifecycle phase it is currently in,
- when that phase last changed,
- what it is not for,
- which topics require current citations or abstention,
- which human-help / office / rights-escalation lanes remain primary,
- whether outputs are directly human-reviewed before the public sees them,
- which languages and accessibility modes are intended to work,
- the main known failure classes the office expects users to watch for,
- and, when applicable, the bounded live scope or the pause/retirement recovery path,
- whether the critical answer path is in-house, vendor-hosted, or mixed,
- whether user questions leave the office boundary for processing,
- and which material external suppliers or model/service families are in the public-answer path when the office can name them safely.

This keeps the public-facing disclosure surface smaller than a full technical system report while still making the assistant's real envelope challengeable.


## Answer-trace minimum

The archive does **not** need full raw chat logs for every deployment.
But for accountability, reproducibility, dispute resolution, and operator QA, an automated assistant should preserve a bounded **answer trace** for action-changing answers.

At minimum, that trace should make it possible to reconstruct:
- what class of question was asked,
- which official anchors the answer relied on,
- which approved-source-hierarchy or routing rule applied,
- which policy/prompt/version rules were in force,
- which operating-bounds-card or warning-label version was in force,
- when the answer was produced,
- whether the answer was conclusive, routed, abstained, or stopped on conflict,
- and which office/help path the user was told to use next.

Prefer **digests, source-anchor identifiers, timestamps, and policy versions** over indefinite storage of raw free-text conversations.
If a deployment keeps raw transcripts for QA or legal reasons, that retention should be separately bounded, privacy-reviewed, and disclosed.

## Privacy and minimization floor

Because voter-help interactions may involve names, addresses, dates of birth, contact details, disability-related requests, incarceration/facility status, citizenship timing, or safety-sensitive address facts, the assistant surface should default to minimization.

That means:
- do not require more personal information than the routing task actually needs,
- do not keep raw conversation text longer than the stated retention policy requires,
- do not treat convenience analytics as a reason to retain sensitive voter details,
- and route users toward official secure channels when the issue requires record-specific evidence.

The assistant should help a voter reach the right office; it should not become a shadow case-management system.

## Operational posture for public trust

Where an election office exposes an automated assistant publicly, it should also keep six visible operator commitments:

1. **current-source discipline** — action-changing answers are anchored to current official-public sources,
2. **phase honesty** — the assistant's public lifecycle state is visible, dated, and not quietly flatter than the deployment reality,
3. **clear escalation** — ordinary-help, rights/safety, and emergency lanes remain visible,
4. **change discipline** — source, model, supplier, hosting-boundary, prompt, policy, or lifecycle-state changes that materially affect answers are treated as change-controlled public-surface updates rather than invisible product tweaks,
5. **feedback discipline** — wrong-answer reports, user confusion reports, and operator escalations are treated as monitoring inputs rather than as support noise, and
6. **exercise discipline** — AI-misuse and AI-answer-failure scenarios belong in tabletop or rehearsal work, consistent with EAC's current operator guidance.

## Wrong-answer reports and feedback-fed monitoring

An election office should not monitor a public assistant only through internal uptime, latency, or spot-check QA.
If the assistant gives a wrong deadline, stale office hours, or an overconfident route for a special-case voter, the public's reports of that failure are part of the evidence.

So the assistant surface should keep a bounded public route for reporting wrong, stale, unclear, or unsafe answers, and the office should treat recurring report themes as review signals for:
- source-anchor drift,
- missing citations or stale citation heads,
- poor abstention behavior,
- weak warning-label clarity,
- language/accessibility gaps, or
- topics that should be removed from automated handling and pushed back to human-help lanes.

This does not require a giant complaint database inside the public payload.
It does require enough visible policy that user-reported failures can influence re-check, rollback, narrower scope, or retirement decisions instead of dying in a generic inbox.

## Minimal payload effect

This control does not need a heavyweight new schema family.
A compact publishable payload can stay bounded around the following fields:

- `assistant_surface_uri` — where the public assistant lives,
- `official_directory_channel_id` — canonical assistant/help channel ID from the official channel directory (`203`) when the assistant is claimed as official,
- `directory_listing_verified_at` — when that directory/discovery binding was last checked,
- `point_of_interaction_notice` — short plain-language disclosure that the user is interacting with an automated assistant,
- `warning_label` — short first-contact caution against treating the assistant as standalone authority,
- `authority_statement` — fuller no-authority-lift notice,
- `system_card_uri` — where the compact public operating-bounds card lives,
- `lifecycle_phase` — bounded public lifecycle state for the assistant,
- `phase_changed_at` — when the current lifecycle phase took effect,
- `phase_scope_note` — bounded live-scope note when the assistant is not full production,
- `next_review_or_exit_criteria` — what review or evidence is expected before promotion, restart, narrowing, or retirement,
- `paused_or_retired_notice_uri` — where the voter can re-find the public pause, withdrawal, or retirement notice when applicable,
- `official_source_anchors[]` — the current official sources the assistant is allowed to rely on,
- `approved_source_hierarchy[]` — ranked source classes and routing precedence,
- `wizard_or_form_handoff_rules[]` — cases where the assistant must route to an existing official wizard, lookup, or form,
- `action_sensitive_topics[]` — the question classes that require explicit official anchors or abstention,
- `uncertainty_and_conflict_behavior` — how the assistant responds when sources are incomplete, stale, or conflicting,
- `assistant_operating_bounds` — intended use, no-use cases, and human-review posture,
- `deployment_boundary` — whether the decisive answer path is in-house, vendor-hosted, or mixed,
- `data_boundary_note` — whether user prompts or routing facts leave the office boundary for processing,
- `material_external_dependencies[]` — bounded list of material third-party models, managed AI services, retrieval/moderation layers, or hosted components in the public-answer path,
- `supported_languages[]` — the language paths the office intends to support,
- `known_limitations[]` — concrete failure classes the office wants the public to watch for,
- `routing_fallback_uri` / `routing_fallback_phone` — official human-help path,
- `rights_escalation_uri` — when `307` style escalation is needed,
- `feedback_reporting_uri` / `feedback_reporting_phone` — bounded public route for wrong-answer or unsafe-answer reports,
- `feedback_monitoring_note` — how user/operator reports feed review,
- `answer_trace_policy` — what bounded evidence the system preserves for action-changing answers,
- `pii_minimization_note` — what personal data is avoided or redacted,
- `last_verified_at` — when the surface, its source hierarchy, and its operating-bounds disclosure were last checked.

This keeps the artifact small while still making the assistant's authority boundary, public warning posture, and evidence discipline inspectable.

## Relationship to the voter-facing answer-surface family

The assistant itself is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing public-answer surfaces.

So the family question remains:
- `292` asks where the polling place is,
- `304` asks how to request a mail ballot,
- `305` asks which office is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- and `323–343` ask the narrow high-risk special-case questions.

This document only says that, if an automated assistant helps answer those questions, it must stay visibly subordinate to the governing source surface, disclose its limits where the public meets it, and preserve a bounded evidence trail for what it told the public.

## What this is meant to catch

This rule is intentionally narrow. It is meant to catch failures such as:

- a chatbot confidently stating a voting deadline without naming the current official page or notice it used,
- an assistant summarizing stale office hours after a signed closure or reroute notice was posted,
- an LLM answer collapsing conflicting county/state instructions into one confident rule,
- a public FAQ bot that routes ordinary help correctly but gives no evidence about what source or version produced the answer,
- a chatbot that has a hidden or missing warning label so the user does not learn it is automated until after trusting the output,
- a deployment that keeps a vague public promise to use official sources but has no inspectable source hierarchy or wizard-handoff rule,
- a public assistant that is missing from the office's official channel directory so voters cannot easily tell whether it is actually an official surface,
- a vendor-hosted assistant that looks like a fully in-house official service even though prompts or critical answer generation leave the office boundary,
- a service that collects wrong-answer reports but never feeds them into scope changes or re-check decisions,
- a pilot that looks indistinguishable from a full production help lane,
- a paused assistant that still appears to be an active authoritative route,
- a retired assistant URL that remains indexable without a clear successor or tombstone,
- or a deployment that quietly retains sensitive voter conversation text even though digests and source-anchor references would have been enough.

## Why this stays narrow

This is not a general AI governance chapter.
It is not a model-evaluation benchmark.
It is not a content-moderation manifesto.
It is not a replacement for the archive's existing voter-surface family.

It is a small evidence-discipline patch:
**if an automated voter-information assistant is in the path, keep official sources primary, make the assistant's limits and hosting/dependency posture visible, bind the surface into official discovery, keep action-changing answers traceable, stop on unresolved conflict, and preserve a bounded human-help handoff.**

## Sources (pinned IDs / lockfile IDs)

- EAC: Artificial Intelligence (AI) and Election Administration (xref: `eac_ai_and_election_administration_page`)
- EAC: AI Toolkit for Election Officials (xref: `eac_ai_toolkit_2023_pdf`)
- EAC: Emerging Technology, AI, and Elections (xref: `eac_emerging_technology_ai_and_elections_blog_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: About vote.gov (xref: `vote_gov_about_us_page`)
- NIST: Artificial Intelligence Risk Management Framework (AI RMF) 1.0 (xref: `nist_ai_rmf_100_1_pdf`)
