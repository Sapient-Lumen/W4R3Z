# 486 — Official voter-information browser-integrated page summaries, page-context AI sidebars, and authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters may encounter through browser-integrated page-summary features, page-context AI sidebars, or selected-text “summarize/explain/ask” actions while the official page is already open**:
Safari webpage summaries,
Firefox AI-chatbot page summaries or selected-text prompts,
Edge Copilot Chat webpage/PDF summarization,
and similar browser- or app-integrated features that compress, restate, or answer from the currently open official page rather than merely linking to it from elsewhere.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the controlling office/help lane,
- `307`, which governs source labels, answer verifiability, and escalation when a compact public surface is not enough,
- `363`, which governs **official** automated assistants exposed by an election office,
- `386`, which governs **off-platform** AI answer surfaces before the voter reaches the official page,
- `440`, which governs reader mode / simplified view / main-content extraction that reduces clutter without necessarily generating a new answer,
- `487`, which governs browser-integrated page translation and selected-text translation of the already-open official page,
- `488`, which governs browser-integrated OCR, image text extraction, and scanned-PDF text layers that can become the upstream text surface before later summary actions,
- `489`, which governs browser-integrated read aloud, listen-to-page, and page-audio narration of the already-open official page,
- `499`, which governs player- or platform-native AI summaries and question-answer modules over already-open official recordings rather than webpages,
- `473`, which governs quoted-text highlight / text-fragment deep links,
- or `474`, which governs browser find-in-page and first-match truthfulness.

It adds one narrow rule:
**if an official voter-information route may be consumed through browser-integrated page summaries or page-context AI sidebars, the office should keep the controlling current-state/scope/help cues extractable from the current official page itself, should not let a same-page summary quietly become a second hidden authority above that page, and should stay honest that these features are optional, browser-specific, and sometimes blocked or unavailable.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats online voter-information materials as core public communications whose clarity, structure, and usability matter operationally. Digital.gov’s current digital-first public-experience requirements likewise treat authoritative, understandable public digital delivery as an operational requirement rather than a presentation preference. Apple’s current Safari guidance says Safari can generate summaries of webpages with Apple Intelligence. Mozilla’s current Firefox support guidance says users can summarize a page from the AI-chatbot sidebar or by asking a chatbot to summarize the current page, and Mozilla’s current AI-controls guidance says Firefox users can block all or selected AI features. Microsoft’s current Copilot Chat in Edge guidance says Copilot Chat in Edge can summarize website and document content shown in Edge, while Microsoft’s current management guidance says admins can allow or block Copilot Chat in Edge from using webpage or PDF context when it formulates responses. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `apple_support_mac_use_apple_intelligence_in_safari_page`; xref: `mozilla_support_access_ai_chatbots_in_firefox_page`; xref: `mozilla_support_firefox_ai_controls_page`; xref: `microsoft_copilot_chat_in_edge_page`; xref: `microsoft_manage_copilot_chat_in_edge_page`)

That is enough to justify a compact control here.
A route may pass ordinary page quality, reader-mode review, and even off-platform citation hygiene yet still fail first contact because:
- the page summary compresses away election/date/jurisdiction qualifiers that lived too far from the decisive sentence,
- a selected-text summarize/explain action captures only a phrase fragment that no longer carries the controlling exception or help route,
- a browser sidebar answer looks more actionable than the current page even though it is only a browser-generated restatement,
- an enterprise or user setting blocks the feature, but product copy or office assumptions treat page summarization as though it were universal,
- or the browser can summarize the current page/PDF but the page was never written so the operative caution, freshness cue, or escalation path survived compression.

## This is not the same thing as off-platform AI answers or reader mode

`386` asks what happens **before** the voter reaches the official page, when an external AI answer surface retrieves or synthesizes public-web content and hands the voter toward the official source.

`440` asks what happens when the browser or app extracts the page’s main content into a simplified reading view that suppresses clutter but does not necessarily create a new natural-language answer.

`486` asks a different question:
**once the voter already has the official page open, does a browser-integrated summary/AI layer compress that same page in a way that still keeps the current official answer/help lane reconstructible and subordinate to the page itself?**

A route may pass `386` and `440` and still fail `486` if:
- off-platform search results hand the voter to the right page, but the in-browser summary hides the decisive qualifier,
- reader mode keeps the main article readable, but the AI summary invents a too-universal short answer from only part of the page,
- or the official page is correct in full context, yet a same-page summarize/explain action makes a partial excerpt look like the complete official instruction.

## Same-page summaries compress from the current page boundary

The important fact here is not generic “AI exists.”
It is that the browser-integrated layer often works from the page the voter is already viewing, or from a text selection inside it.
That makes the **current page boundary** load-bearing.
If the office wants the official page to remain the controlling artifact, the page itself should carry enough nearby context that a same-page summary cannot easily detach the answer from:
- jurisdiction and office identity,
- election/date scope when material,
- whether the answer is universal or depends on address, district, record status, or facility-specific facts,
- freshness or superseding-notice posture when the fact can change,
- and the next official help route when a short answer is unsafe.

This archive does **not** require offices to optimize for every browser prompt string.
It does require them to notice that “summarize this page” is now a real public reading path.

## Feature availability varies; do not build policy on its presence

Apple’s current Safari guidance says Apple Intelligence is not available on all Mac models or in all languages or regions. Mozilla’s current AI-controls guidance says Firefox users can block all AI enhancements or individual AI features. Microsoft’s current Edge/Copilot management guidance says page-context use can be allowed or blocked by policy. (xref: `apple_support_mac_use_apple_intelligence_in_safari_page`; xref: `mozilla_support_firefox_ai_controls_page`; xref: `microsoft_manage_copilot_chat_in_edge_page`)

So the public-safe posture is:
- the authoritative answer still lives on the page/help lane itself,
- browser summary features are convenience surfaces rather than required delivery channels,
- office copy should not assume every voter can or will use them,
- and failure or absence of a page-summary feature should degrade to the ordinary page, not to a broken or context-poor route.

## Selected-text summarization is especially prone to qualifier loss

Browser-integrated AI layers do not always summarize the whole page.
Some also act on selected text or page-local prompts.
That is where qualifier loss becomes acute.
A voter can select only:
- a deadline sentence without the exception beneath it,
- an ID rule without the alternatives or cure path,
- a polling-place note without the address-specific lookup qualifier,
- or a “bring this document” phrase without the surrounding scope and help context.

For `486`, that means the page should avoid writing decisive text so that the controlling exception or routing note lives only in distant UI chrome, an unrelated accordion, or another panel the summary/selection path is unlikely to carry.
If the answer is not safely compressible, the page should say so plainly and point the voter toward the current official office/help route instead of pretending the short excerpt settles the case.

## High-risk topics should bias toward routing, not universal compression

The most dangerous failures are questions whose correct answer depends on local facts or rapidly changing state.
Examples include:
- polling-place / drop-box / early-voting locations and hours,
- registration status or reactivation,
- absentee deadlines and receipt rules,
- ID alternatives and cure paths,
- disability, language, jail/facility, disaster, or new-citizen edge cases,
- and any answer that should really move the voter into `305` ordinary help or `307` rights/safety escalation.

For those topics, `486` does not ask the page to become summary-proof in an impossible sense.
It asks the page to make the safe routing answer visible enough that a browser summary remains subordinate to the same official next step.

## The browser-generated answer is still not the controlling authority

A browser-generated same-page summary may feel more intimate than an off-platform AI card because it appears beside the live official page.
That does **not** make it the controlling authority.
The controlling artifact remains the current official page and, when needed, the office/help route the page names.

So this surface especially cares about:
- visible “current official page” cues,
- headings and nearby prose that survive compression coherently,
- fast recovery from ambiguous short answers,
- and avoiding page designs where the summary looks like the real answer while the page looks like decorative backing.

## Claims this control should support

1. **Same-page authority-boundary claim:** browser-generated summaries remain visibly subordinate to the current official page/help lane.
2. **Context-carrying page claim:** page-local summaries or selected-text prompts can still recover office identity, jurisdiction scope, and action-safe qualifiers from nearby page content.
3. **Blocked/optional feature honesty claim:** the office does not assume browser summary/AI features are universal, enabled, or policy-allowed.
4. **High-risk routing claim:** pages for volatile or local-fact-dependent topics preserve a visible safe next step instead of pretending a short summary is sufficient.
5. **Boundary clarity claim:** failures in this lane stay distinct from off-platform AI retrieval (`386`), reader mode (`440`), text-fragment highlights (`473`), and browser find-in-page (`474`).

## Canonical digest artifacts

Publish **small digests of page-context summary posture**, not prompt logs or screenshots of every vendor surface.

- **Page-Context AI Surface Digest (PCASD):** digest of official routes reviewed for page-summary/selected-text compression safety.
- **Summary-Safe Qualifier Digest (SSQD):** optional digest of pages where decisive qualifiers and routing notes were pulled adjacent to the operative answer.
- **Blocked-or-Optional Feature Note (BOFN):** optional note describing that browser page-summary features vary by browser, settings, account state, language, region, platform, or enterprise policy.

## What belongs in the public page-context-AI payload

Keep the payload **small, route-aware, and explicit about summary-boundary posture**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `page_context_ai_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `supported_summary_contexts[]`
- `authority_boundary_note`
- `selected_text_qualifier_loss_note`
- `blocked_or_optional_feature_note`
- `high_risk_topic_routing_note`
- `current_page_controls_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- user prompts,
- individualized page-summary transcripts,
- browser/account telemetry about which voters invoked AI features,
- or massive vendor-specific screenshot galleries.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which current official pages were reviewed for browser-integrated page-summary / selected-text compression safety?
- If a page is summarized out of context, does the page itself still expose the controlling jurisdiction/scope/current-state cues nearby?
- Are volatile or address-specific topics routed back to the official help lane instead of left to a generic short summary?
- Does the public posture say clearly that these browser features are optional, browser-specific, and sometimes blocked?
- Is the failure being analyzed really about same-page summary compression, rather than off-platform AI answers, reader mode, text fragments, or find-in-page?

## Quarantine boundary: no pseudo-forensics yet

This document does **not** assume standardized summary-provenance hooks, stable browser-generated transcript formats, or reliable cross-browser logging of how a page summary was produced.
If browsers later expose trustworthy, portable summary provenance or reproducible page-context AI audit signals, that may justify a future narrow control.
For now, keep that possibility in quarantine.
The canon here is smaller:
review the official page so the answer remains safe when compressed, and preserve only the bounded public digest needed to prove that posture was considered.

## How this fits the family map

Browser-integrated page summaries are **not** a new underlying voter-question family bucket.
They are a shared public-surface control that can apply to many official routes whenever the browser itself starts compressing or restating the currently open page.

Use `486` when the right official page exists and is already open, but a browser-integrated summary/sidebar/selected-text action can still make the answer look more universal, final, or context-free than the office intended.
Keep using:
- `386` for off-platform AI answer surfaces before arrival,
- `440` for reader mode / simplified view / extracted-main-content presentation,
- `473` for text-fragment highlight anchors,
- `474` for browser find-in-page / first-match truthfulness,
- `305` for the controlling office/help lane,
- and `307` when source labels, verifiability, or escalation need to become explicit because the short answer is not safely self-sufficient.

This document only says that, if modern browsers can summarize or “answer from” the page while the voter is reading it, the page should keep one reconstructible official answer/help story rather than quietly tolerating a second browser-generated authority surface beside it.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Apple Support: Use Apple Intelligence in Safari on Mac (xref: `apple_support_mac_use_apple_intelligence_in_safari_page`)
- Mozilla Support: Access AI chatbots in Firefox (xref: `mozilla_support_access_ai_chatbots_in_firefox_page`)
- Mozilla Support: Block generative AI features with Firefox AI controls (xref: `mozilla_support_firefox_ai_controls_page`)
- Microsoft Learn: Microsoft 365 Copilot Chat in Edge (xref: `microsoft_copilot_chat_in_edge_page`)
- Microsoft Learn: Manage Microsoft 365 Copilot Chat (xref: `microsoft_manage_copilot_chat_in_edge_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-page-context-ai-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-page-context-ai-surface-checklist.md`
