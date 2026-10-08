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

Current official guidance is explicit enough to justify a bounded control here. EAC's current AI and election-administration guidance says AI-powered tools can help election offices but can also accelerate false or biased information, and it adds that AI-generated voting information may look plausible while still being inaccurate, which is especially harmful for voting dates, hours, and locations. EAC's AI toolkit likewise frames the problem as one of communications and directs election officials toward proactive routing to verifiable official sources of accurate information. EAC's current blog guidance for election officials adds three operational themes that matter directly here: have a content-review/public-communications plan for AI misuse, test that plan in tabletop exercises, and build public trust in election officials ahead of time. NASS's current `#TrustedInfo2026` posture still points the public toward state and local election officials as the reliable source of election information, and Vote.gov says it is a trusted source that routes voters to state election websites for state-specific rules rather than acting as the registration authority itself. (xref: `eac_ai_and_election_administration_page`; xref: `eac_ai_toolkit_2023_pdf`; xref: `eac_emerging_technology_ai_and_elections_blog_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_about_us_page`)

So the bounded problem is not "ban AI" and it is not "certify a perfect chatbot." The bounded problem is simpler:
**if an election office deploys an automated answer surface, how does it prevent that surface from silently becoming a new authority layer above the official pages, notices, and office contacts that actually control the answer?**

## What this adds (and what it does not)

This document adds a compact **no-authority-lift + answer-trace discipline** for automated voter-information assistants.

It does **not** require election offices to deploy such assistants.
It does **not** claim LLMs are safe for unsupervised legal interpretation.
It does **not** replace:
- the underlying voter-facing answer surfaces in `292–343`,
- the office-routing fallback in `305`,
- the rights/safety escalation lane in `307`,
- the current-official hierarchy rules in `345`, or
- the unresolved-conflict stop rule in `347`.

It only adds one narrow control set:
**if an automated assistant is exposed to the public, keep it anchored to current official sources, make action-changing answers traceable, and stop it from inventing or silently synthesizing governing instructions.**

## No-authority-lift rule

An automated assistant MAY help users discover, summarize, translate, or navigate official election information.
It MUST NOT present itself as an independent authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, official directory entry, or responsible office identified through the normal routing hierarchy.

In practice that means the assistant surface should say, in plain language, that it is:
- a helper for finding and restating official information,
- not a substitute for the current controlling jurisdiction-specific instruction, and
- not permitted to outrank a later signed notice, current state/local page, or direct office confirmation.

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

## Conflict and ambiguity stop rule

An automated assistant MUST inherit the archive's existing conflict discipline rather than papering it over.

If the assistant sees materially conflicting or incomplete official materials, it should not combine fragments into a confident jurisdiction-specific instruction.
Instead it should:
- state that the current official materials appear inconsistent or incomplete,
- identify the office/path that can resolve the question now,
- point to the latest visible signed notice or official directory entry when one exists, and
- preserve a bounded record that the answer stopped on conflict rather than inventing a synthesis.

That keeps `347` and `362` meaningful even when the first user contact point is a generated answer surface.

## Answer-trace minimum

The archive does **not** need full raw chat logs for every deployment.
But for accountability, reproducibility, dispute resolution, and operator QA, an automated assistant should preserve a bounded **answer trace** for action-changing answers.

At minimum, that trace should make it possible to reconstruct:
- what class of question was asked,
- which official anchors the answer relied on,
- which policy/prompt/version rules were in force,
- when the answer was produced,
- whether the answer was conclusive, routed, or stopped on conflict,
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

Where an election office exposes an automated assistant publicly, it should also keep four visible operator commitments:

1. **current-source discipline** — action-changing answers are anchored to current official-public sources,
2. **clear escalation** — ordinary-help, rights/safety, and emergency lanes remain visible,
3. **change discipline** — source, model, or policy changes that materially affect answers are treated as change-controlled public-surface updates rather than invisible product tweaks, and
4. **exercise discipline** — AI-misuse and AI-answer-failure scenarios belong in tabletop or rehearsal work, consistent with EAC's current operator guidance.

## Minimal payload effect

This control does not need a heavyweight new schema family.
A compact publishable payload can stay bounded around the following fields:

- `assistant_surface_uri` — where the public assistant lives,
- `authority_statement` — plain-language no-authority-lift notice,
- `official_source_anchors[]` — the current official sources the assistant is allowed to rely on,
- `action_sensitive_topics[]` — the question classes that require explicit official anchors or abstention,
- `uncertainty_and_conflict_behavior` — how the assistant responds when sources are incomplete, stale, or conflicting,
- `routing_fallback_uri` / `routing_fallback_phone` — official human-help path,
- `rights_escalation_uri` — when `307` style escalation is needed,
- `answer_trace_policy` — what bounded evidence the system preserves for action-changing answers,
- `pii_minimization_note` — what personal data is avoided or redacted,
- `last_verified_at` — when the surface and its anchor policy were last checked.

This keeps the artifact small while still making the assistant's authority boundary and evidence posture inspectable.

## Relationship to the voter-facing answer-surface family

The assistant itself is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing public-answer surfaces.

So the family question remains:
- `292` asks where the polling place is,
- `304` asks how to request a mail ballot,
- `305` asks which office is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- and `323–343` ask the narrow high-risk special-case questions.

This document only says that, if an automated assistant helps answer those questions, it must stay visibly subordinate to the governing source surface and preserve a bounded evidence trail for what it told the public.

## What this is meant to catch

This rule is intentionally narrow. It is meant to catch failures such as:

- a chatbot confidently stating a voting deadline without naming the current official page or notice it used,
- an assistant summarizing stale office hours after a signed closure or reroute notice was posted,
- an LLM answer collapsing conflicting county/state instructions into one confident rule,
- a public FAQ bot that routes ordinary help correctly but gives no evidence about what source or version produced the answer,
- or a deployment that quietly retains sensitive voter conversation text even though digests and source-anchor references would have been enough.

## Why this stays narrow

This is not a general AI governance chapter.
It is not a model-evaluation benchmark.
It is not a content-moderation manifesto.
It is not a replacement for the archive's existing voter-surface family.

It is a small evidence-discipline patch:
**if an automated voter-information assistant is in the path, keep official sources primary, keep action-changing answers traceable, stop on unresolved conflict, and preserve a bounded human-help handoff.**

## Sources (pinned IDs / lockfile IDs)

- EAC: Artificial Intelligence (AI) and Election Administration (xref: `eac_ai_and_election_administration_page`)
- EAC: AI Toolkit for Election Officials (xref: `eac_ai_toolkit_2023_pdf`)
- EAC: Emerging Technology, AI, and Elections (xref: `eac_emerging_technology_ai_and_elections_blog_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: About vote.gov (xref: `vote_gov_about_us_page`)
