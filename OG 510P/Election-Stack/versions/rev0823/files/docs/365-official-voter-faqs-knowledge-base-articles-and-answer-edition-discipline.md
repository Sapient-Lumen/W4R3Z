# 365 — Official voter FAQs, knowledge-base articles, and answer-edition discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter FAQ pages, help articles, and knowledge-base entries** that election offices publish on their websites.

It does **not** require a large CMS or a giant searchable help center.
It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which routes the public to the right office/help path,
- `307`, which governs rights/safety escalation,
- `363`, which governs automated assistants that may quote or summarize FAQ content, or
- `364`, which governs hotline/call-center script packets and live-answer phone lanes.

It adds one narrow rule:
**if an election office expects the public to rely on FAQ/help articles for recurring action-changing voting answers, those articles should be treated as a bounded, reviewable public-answer layer with identifiable answer editions, current official anchors, and explicit superseding/correction behavior.**

## Why this is a distinct surface

Current official guidance is enough to justify a narrow control here.
EAC's current **Best Practices: FAQs for Election Officials** page says election administration is highly decentralized, local election officials are the best source of trusted information, and the FAQ toolkit is specifically designed to help election officials create or improve FAQs for their websites; it also includes social-media guides to promote those FAQs as a trusted source of information.
EAC's current communications clearinghouse keeps FAQ-writing, effective-design guidance, incident-communications guidance, accessibility guidance, and broader communications resources in one current maintainer lane rather than treating website FAQs as throwaway prose.
EAC's current **Effective Design for the Administration of Federal Elections** page says online voter-information materials should be clear, understandable, accessible, and usable, and emphasizes hierarchy, structure, and plain language.
EAC's current voter FAQ page itself shows that FAQs are not a purely internal format: the page is a public voter-information surface, it routes users to current state/local election offices for practical answers, and it publishes translated printable versions.
NASS's current `#TrustedInfo2026` initiative makes the legitimacy baseline even simpler by urging voters toward election officials' websites, social-media pages, and materials for timely election information.

That means an official FAQ/help article is not merely “website copy.”
It is often the **actual public answer surface** a voter, journalist, volunteer, helper, or call-taker will quote, screenshot, deep-link, translate, print, or feed into another delivery layer.

## Answer-edition floor

If an office relies on FAQ/help articles for action-changing voting information, each maintained article or bounded FAQ cluster should have an identifiable **answer edition**.

That edition does not need a heavyweight publishing system.
A date/version label, stable digest, or equivalent bounded edition marker is enough if it lets the office later answer:
- which article or FAQ card controlled at time `T`,
- which official anchors the answer depended on,
- when it was last reviewed,
- and whether a later notice or article superseded it.

The point is not archival maximalism.
The point is to prevent high-impact public answers from living only in silently edited pages, stale screenshots, copied snippets, or search-result fragments.

## Official-anchor rule

An action-changing FAQ/help article should name or link the current official sources it depends on.

That matters especially for:
- registration and update deadlines,
- polling-place, vote-center, early-voting, or drop-box locations/hours,
- voter-ID requirements and alternatives,
- absentee request/return rules,
- office closures or reroutes,
- special-case voter paths,
- and any question where the next safe step depends on the currently responsible office.

The article does not need to reproduce every rule in full.
But it should make the current controlling office/page/notice legible enough that the reader can verify the answer or continue safely to the next official step.

## Conflict and escalation discipline

A FAQ/help article should inherit the archive's existing conflict posture instead of trying to smooth over ambiguity.

If current official materials materially conflict, are stale, or do not safely resolve the question, the article should:
- stop on the unresolved conflict,
- route the reader to `305` for the controlling office/help path,
- route the reader to `307` when the problem has become intimidation, discrimination, rights denial, or another escalation case,
- and stop short of synthetic certainty.

A generic “contact your election office” footer is not enough when the answer is action-changing.
The reader should be able to tell which office/path currently owns the question and what to do next if the article is not safely dispositive.

## Superseding and stale-copy discipline

Because FAQ/help articles are routinely bookmarked, screenshotted, copied into newsletters, quoted by staff, and surfaced by site search or external search, a later correction should be explicit.

So when a material public answer changes, the office should publish a superseding article state, linked notice, or equivalent bounded correction trail rather than silently replacing the text and leaving the public to guess whether an older screenshot or cached article was ever authoritative.

This is especially important for deadline shifts, site changes, emergency closures, corrected ID guidance, and niche special-case paths where a stale answer can cost the voter the remaining lawful route.

## Accessibility, language access, and printable parity

An FAQ/help article is only operationally real if it remains accessible and usable in the modes the public actually encounters.

Minimum expectations include:
- plain-language structure that ordinary readers can parse,
- accessible online presentation,
- parity with translated or alternate-language materials where required,
- parity with printable/downloadable FAQ forms where the jurisdiction offers them,
- and a visible official help path when the written article is not enough.

Do not let the accessible PDF, printable handout, translated FAQ card, and web article drift into different effective answers.
If the article is part of the public answer surface, those modes should converge on the same current state.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official FAQ/help claim:** the office identified one or more FAQ/help pages or article clusters as official for scope `E`.
2. **Answer-edition claim:** each maintained action-changing article or bounded FAQ cluster carried an identifiable edition/version/digest and review timestamp.
3. **Anchor claim:** the article or FAQ cluster identified the current official pages, notices, or office-routing artifacts it relied on.
4. **Escalation claim:** the article distinguished direct-answer cases from cases that require office routing or `307`-style escalation.
5. **Superseding claim:** material answer changes produced an explicit newer article state, notice, or equivalent correction trail rather than only a silent overwrite.
6. **Parity/accessibility claim:** web article, printable/downloadable version where offered, translated/public-help variants where applicable, hotline packet, and signed notices converged on the same effective public state.

## Canonical digest artifacts

Publish **digests of the FAQ/help surface**, not entire CMS exports.

- **Voter FAQ Surface Digest (VFSD):** digest of the bounded official FAQ/help payload for a scope.
- **FAQ Answer Edition Digest (FAED):** digest of the current approved article/answer edition for a bounded question or article cluster.
- **FAQ Superseding Notice Digest (FSND):** per-event digest when a material FAQ/public answer changed.
- **FAQ Parity Snapshot (FQPS):** optional digest that binds FAQ/help guidance to the current website / hotline / notice state.

## What belongs in the public FAQ/help payload

Keep the payload **small, action-relevant, and current-state oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `faq_collection_label`
- `faq_entry_id`
- `faq_entry_uri`
- `question_family_refs[]`
- `official_source_anchors[]`
- `answer_edition`
- `plain_language_summary`
- `action_sensitive`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `unresolved_conflict_behavior`
- `printable_or_downloadable_variant_uri`
- `translated_variants[]`
- `latest_notice_uri`
- `last_reviewed_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- full CMS revision history,
- internal draft comments,
- search analytics,
- staff-edit rosters,
- raw ticket data,
- per-user personalization traces,
- or copied legal research that is not needed for the public answer.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official FAQ/help article or bounded FAQ cluster was in force at time `T`?
- Which answer edition or digest controlled the article at time `T`?
- Which official pages, notices, or routing artifacts did it rely on?
- Did the article stay inside the correct underlying voter-question family instead of drifting into adjacent rule pages?
- Did the FAQ/help article match the current hotline packet, office-routing page, and signed notice state?
- Was a later correction explicit, or was the answer silently replaced?
- Could a reader who hit uncertainty safely find the controlling office or escalation path?

## How this fits the family map

An official FAQ/help article is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the existing voter-question families already modeled in `292–343`.

So the family question remains:
- `292` asks where the polling place is,
- `304` asks how to request a mail ballot,
- `305` asks which office is authoritative and reachable,
- `307` asks where to escalate when ordinary help fails,
- `323–343` ask narrow special-case questions,
- `363` governs automated assistants that may summarize or quote FAQ content,
- and `364` governs live phone/help lanes that may read from or parallel those same FAQ answers.

This document only says that, if an office uses FAQ/help pages as a trusted public-answer surface, those pages should be editioned, anchored, synchronized, and later-reconstructible rather than living only as mutable copy.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-faq-answer-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-faq-answer-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Best Practices: FAQs for Election Officials (xref: `eac_best_practices_faqs_election_officials_page`)
- EAC: Clearinghouse Resources on Communications (xref: `eac_clearinghouse_resources_communications_page`)
- EAC: Communications 101 (xref: `eac_communications_101_page`)
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- EAC: Accessibility Checklist: Accessible Communications (xref: `eac_accessibility_checklist_accessible_communications_2024_pdf`)
- NASS: #TrustedInfo2026 (xref: `nass_trustedinfo_2026_page`)
