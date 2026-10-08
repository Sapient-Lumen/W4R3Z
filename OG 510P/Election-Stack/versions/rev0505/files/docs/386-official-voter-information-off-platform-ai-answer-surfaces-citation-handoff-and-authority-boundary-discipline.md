# 386 — Official voter-information off-platform AI answer surfaces, citation handoff, and authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **off-platform AI answer surfaces that may summarize, cite, or restate official voter information before a voter reaches the official site**: AI overviews, cited answer cards, assistant/search hybrids, and similar public-web answer layers.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `363`, which governs **official** automated assistants exposed by an election office,
- `365`, which governs official FAQ/help article editions,
- `382`, which governs ordinary search-result presentation before synthesis,
- `383`, which governs official social-profile shells and pinned recovery,
- `385`, which governs office-listing / place-card identity and hours/contact state,
- or `379`, which governs stale-link and expired-page recovery once the voter lands on an older URL.

It adds one narrow rule:
**if voters may encounter off-platform AI answer surfaces that summarize official election content, the jurisdiction should keep the cited official pages scope-legible, current-state legible, and recovery-rich so the AI answer layer does not quietly become a hidden authority above the current official source.**

## Why this is a distinct surface

Current official and primary technical guidance is enough to justify a bounded control here.

EAC's current AI and election-administration guidance says AI-powered tools can help election offices but can also accelerate false or biased information, and it warns that AI-generated voting information may look plausible while still being inaccurate, especially for dates, hours, and locations. NASS's current `#TrustedInfo2026` posture still directs voters to election officials' websites, social media pages, and materials as the trusted sources of election information. Vote.gov's current trust posture likewise emphasizes official `.gov` / HTTPS routing for official information.

On the technical side, Google Search Central's current **AI features and your website** guidance says AI Overviews and AI Mode are part of the search experience from a site owner's perspective, while its current title-link, site-name, and snippet guidance still shows that the underlying cited page cues shape what users see and click. Microsoft's current Copilot Studio guidance for **public websites** says generative answers can retrieve from public web results, perform grounding/provenance checks, and summarize those results into plain language, while Microsoft's current documentation on public web access for Microsoft 365 Copilot says generated search queries are sent to Bing to ground responses in web data.

That is enough to treat off-platform AI answers as a real first-contact voter-information surface rather than an abstract future concern. The problem is not that an election office controls every vendor answer card. The problem is that a voter may trust the answer layer anyway, so the underlying official pages must be shaped for safe citation, fast recovery, and clear authority boundaries. (xref: `eac_ai_and_election_administration_page`; xref: `nass_trustedinfo_2026_page`; xref: `vote_gov_home_page`; xref: `google_search_central_ai_features_page`; xref: `google_search_central_title_links_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_meta_descriptions_snippets_page`; xref: `microsoft_copilot_studio_public_websites_generative_answers_page`; xref: `microsoft_365_copilot_public_web_access_page`)

## AI answer surfaces are routing/summarization layers, not rule sources

An off-platform AI answer MAY help a voter reach the right official source faster.
It MUST NOT be treated as the controlling authority for jurisdiction-specific election rules.

The controlling artifact remains the current official page, signed notice, office/help directory entry, or direct office confirmation that the jurisdiction itself stands behind.
The AI answer layer should therefore do only enough to:
- expose or lead to the current official source,
- preserve the jurisdiction/office/election scope cues the voter needs,
- avoid turning a partial or stale summary into the whole practical answer,
- and recover quickly when the answer card is generic, outdated, ambiguous, or uncited.

This is the same basic no-authority-lift principle as `363`, but applied to an answer surface the office may not directly control.

## Citation handoff is the key bounded control

Google's current AI-features guidance and Microsoft's current public-website generative-answer guidance both make the practical point that AI answer surfaces are grounded in public-web retrieval and may surface links or citations in multiple ways. (xref: `google_search_central_ai_features_page`; xref: `microsoft_copilot_studio_public_websites_generative_answers_page`; xref: `microsoft_365_copilot_public_web_access_page`)

For voter information, that makes **citation handoff** the key bounded control.
The question is not “did the AI summarize beautifully?”
The question is:
**when a voter sees a synthesized answer, does the citation/link handoff carry them into a page that is clearly official, clearly scoped, clearly current enough for action, and clearly able to recover if the summary was partial?**

That means cited pages for action-changing topics should usually make at least some combination of these legible without requiring deep scrolling or guesswork:
- jurisdiction or office identity,
- election/date scope when material,
- page purpose,
- whether the page is a directory, FAQ/help answer, form, notice, or status explainer,
- and the next official office/help route when self-service is not enough.

## Current-state cues matter more when the answer layer synthesizes

EAC's current AI guidance is explicit that plausible-looking AI output can still be wrong on operationally critical facts like dates, hours, and locations. (xref: `eac_ai_and_election_administration_page`)

That means pages likely to be cited by off-platform AI should not rely on vague timeless prose when the fact is materially time-sensitive.
For action-changing topics, pages should prefer visible cues such as:
- current election or cycle labeling,
- “last updated” or “as of” state when that helps users judge volatility,
- explicit superseding-notice or current-cycle routing when older materials still circulate,
- and visible office/help recovery when the answer depends on address, district, disability accommodation, language path, facility status, or another record-specific fact.

The goal is not to decorate every page with timestamps.
The goal is to reduce the chance that an off-platform synthesis extracts one sentence from a page that no longer tells the whole practical story.

## Vendor-specific optimization is optional; authority-boundary clarity is not

This archive does **not** need a per-vendor ranking or prompt-hacking playbook.
Google's current AI-features guidance still routes site owners toward the same general content principles used across Search, and Microsoft's current public-web generative-answer guidance describes retrieval, grounding, and summarization rather than a magic election-specific markup channel. (xref: `google_search_central_ai_features_page`; xref: `microsoft_copilot_studio_public_websites_generative_answers_page`)

So the bounded maintenance rule is:
- do not chase every opaque vendor behavior,
- do keep official pages citation-ready and recovery-rich,
- do make current-state and jurisdiction scope easy to read,
- and do preserve a small policy trace describing how the office intends important pages to hand voters from AI summaries into the official answer path.

## Ambiguous-answer recovery and high-risk routing

Off-platform AI answers are especially risky when they compress questions that are really address-specific, district-specific, election-phase-specific, or rights-sensitive.
So for high-risk topics, the cited official page should make the safe next step obvious rather than trying to look universally self-sufficient.

Examples include:
- polling-place / early-voting / drop-box lookup,
- office hours and temporary closures,
- registration status or reactivation,
- absentee request and return deadlines,
- ID alternatives,
- disability or language accommodation,
- facility/jail/tribal/disaster/new-citizen edge cases,
- and any path that can pivot into `305` or `307`.

If the answer genuinely depends on local facts the AI layer cannot safely compress, the official landing page should say so clearly and hand the voter to the current office/help route rather than pretending the synthesized summary already resolved the case.

## Minimal AI-answer state taxonomy

A small taxonomy is enough:

1. **cited_current_answer_with_clear_scope**
2. **cited_answer_needing_address_or_record_followup**
3. **ambiguous_or_partial_ai_answer_recovered_by_current_official_page**
4. **stale_ai_answer_recovered_by_notice_redirect_or_help_lane**
5. **high_risk_question_routed_to_office_help_or_rights_escalation**

That is usually more useful than pretending every AI answer experience needs a separate theory of operation.

## Bounded trace minimum

The archive does **not** need raw vendor telemetry, individualized clickstreams, or private prompt logs from third-party platforms.
But for accountability and later reconstruction, it is still useful to preserve a bounded **AI answer handoff policy trace** for action-changing official pages.

At minimum, a jurisdiction should be able to reconstruct:
- which official pages were intended as citation-ready anchors for volatile voter-information topics,
- what scope/current-state cues those pages were supposed to expose,
- which office/help fallback should appear when summary alone is unsafe,
- when the handoff policy was last verified,
- and whether a major page/template change should have triggered re-checking of off-platform AI answer recovery.

Prefer digests, page-class identifiers, policy versions, timestamps, and destination refs over expansive individualized telemetry.

## Claims this supports

1. **Authority-boundary claim:** off-platform AI answers do not outrank the current official page, notice, or office/help route.
2. **Citation-handoff claim:** important official pages are maintained so cited answer handoff leads into a clearly official, clearly scoped, and recoverable destination.
3. **Current-state-cue claim:** volatile topics expose enough current-state cues to reduce plausible-but-stale summary drift.
4. **High-risk-routing claim:** questions that depend on local facts or rights-sensitive conditions retain visible office/help or escalation handoff instead of being flattened into one synthetic universal answer.
5. **Vendor-independence claim:** the archive requires bounded readiness for AI citation/recovery without depending on proprietary optimization tricks.
6. **Trace-minimization claim:** bounded reconstruction is possible without collecting individualized third-party AI usage telemetry.

## Canonical digest artifacts

Publish **digests of handoff policy and page-class state**, not vendor dashboards.

- **AI Answer Handoff Surface Digest (AAHSD):** digest of the bounded public payload for off-platform AI answer readiness.
- **Citation-Ready Page Class Digest (CRPCD):** digest of the policy describing which page classes are maintained for safe AI-answer citation and recovery.
- **AI Answer Recovery State Digest (AARSD):** optional digest proving what current-state / recovery cues a cited official page class was supposed to expose at time `T`.

## What belongs in the public payload

Keep the payload **small, current-state-aware, and authority-boundary explicit**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `ai_answer_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `authority_boundary_note`
- `citation_handoff_policy_note`
- `current_state_cue_policy_note`
- `scope_legibility_policy_note`
- `high_risk_topic_routing_note`
- `vendor_independence_note`
- `ai_answer_state_classes[]`
- `ai_answer_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw third-party AI telemetry,
- individualized prompt/click logs,
- private experimentation notes for vendor-specific ranking hacks,
- or any synthetic “model score” that is not needed to reconstruct the bounded public handoff policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official pages were intended to be safe citation anchors for off-platform AI answer surfaces at time `T`?
- Did those pages make jurisdiction, purpose, and current-state cues legible?
- Was the voter given a visible recovery path when the answer depended on address, district, office status, or other local facts?
- Could a stale or ambiguous AI summary be recovered by the cited official page, a current notice, or the office/help lane?
- Did the jurisdiction preserve a bounded handoff-policy trace without relying on individualized third-party telemetry?

## How this fits the family map

Off-platform AI answer surfaces are **not** a new canonical voter-question family bucket.
They are a first-contact delivery layer that sits outside the official site and may synthesize across public-web content before the voter clicks through.

So the underlying question remains:
- where to vote,
- which office is authoritative,
- which deadline or hours page controls,
- which FAQ, form, or notice is current,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if voters may meet an off-platform AI answer surface first, the cited official pages should stay current-state-aware, scope-legible, authority-bounded, and recovery-rich instead of letting the synthesis layer silently become the trusted answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-ai-answer-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-ai-answer-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Artificial Intelligence (AI) and Election Administration (xref: `eac_ai_and_election_administration_page`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
- Vote.gov: Home / trust marker (xref: `vote_gov_home_page`)
- Google Search Central: AI features and your website (xref: `google_search_central_ai_features_page`)
- Google Search Central: Influencing your title links in search results (xref: `google_search_central_title_links_page`)
- Google Search Central: Site names in Google Search (xref: `google_search_central_site_names_page`)
- Google Search Central: Meta descriptions / snippets (xref: `google_search_central_meta_descriptions_snippets_page`)
- Microsoft Copilot Studio: Use public websites to improve generative answers (xref: `microsoft_copilot_studio_public_websites_generative_answers_page`)
- Microsoft 365 Copilot: Data, privacy, and security for web search in Microsoft 365 Copilot and Microsoft 365 Copilot Chat (xref: `microsoft_365_copilot_public_web_access_page`)
