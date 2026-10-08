# 487 — Official voter-information browser-integrated page translation, selected-text translation, and authority-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that voters may encounter through browser-integrated webpage translation, selected-text translation, or auto-translate behavior while the official page is already open**:
Chrome page translation and selected-text translation,
Firefox full-page or selected-text translations,
Edge Translator webpage translation,
Safari webpage translation and same-domain tab-continuity translation,
and similar browser- or app-integrated translation layers that rewrite the already-open official page into another language without turning that convenience output into a separately reviewed official publication.

It does **not** replace the underlying language-assistance and translated-materials surface in `302`.
It does **not** replace:
- `305`, which governs the controlling office/help lane,
- `377`, which governs language selectors, multilingual landing paths, locale fallback, and equivalence classes **before** or **while** the voter chooses a language path,
- `397`, which governs multilingual search/discovery and alternate-language declarations,
- `440`, which governs reader mode / simplified view / main-content extraction without translation,
- `486`, which governs browser-integrated summaries or page-context AI answers from the already-open page,
- `488`, which governs browser-integrated OCR, image text extraction, and scanned-PDF text layers that can become the upstream text surface before later translation,
- `492`, which governs generated live captions and translated subtitles over already-open official media rather than translation of already-authored page text,
- or `302`, which governs what translated materials or oral-assistance routes the jurisdiction actually stands behind.

It adds one narrow rule:
**if an official voter-information route may be consumed through browser-integrated translation while the original page is already open, the office should keep the original-language authority and current-state cues recoverable, should not let convenience translation quietly masquerade as a reviewed equivalent official publication, and should keep the current official translated/help lane visible when translation ambiguity matters.**

## Why this is a distinct surface

The archive already treats language access and multilingual public delivery as an operational requirement rather than decorative UX. DOJ’s current Language Minority Citizens page says covered jurisdictions that provide election-related materials or information must provide them in the applicable minority language as well as English. The EAC’s current language-access resources and checklist likewise treat translated materials, proofing, and oral-assistance planning as live election-administration work. Browser vendors now also document built-in webpage translation as an ordinary reading path: Chrome can translate full pages and selected text, Firefox has built-in full-page and selected-text translations, Edge can translate webpages and optionally always translate from a language, and Safari can translate webpages when available. Apple’s current Safari guidance also says that after translating one webpage, other webpages in the same domain visited in the same tab may also be translated automatically. (xref: `justice_language_minority_citizens_page`; xref: `eac_language_access_resources_page`; source: `eac_language_access_program_checklist_pdf`; xref: `google_chrome_help_translate_pages_page`; xref: `mozilla_support_firefox_translations_page`; xref: `microsoft_support_edge_translator_page`; xref: `apple_support_safari_translate_webpage_page`; xref: `apple_support_safari_web_page_translation_auto_same_domain_page`)

That is enough to justify a compact control here.
A route may pass language-selector review, alternate-language discovery review, and even ordinary content review yet still fail first contact because:
- the voter reaches the right official page, but browser translation rewrites a qualifier so it reads more universal than the underlying source,
- office names, form names, or legal labels are translated into more familiar but less exact wording,
- the browser keeps translating later pages in the same tab or language pair and the voter stops noticing which language path they are actually on,
- a selected-text translation detaches one sentence from the official surrounding exception or help lane,
- or the jurisdiction already publishes a reviewed official translation, but the browser-translated original-language page looks equivalent enough that the voter cannot tell which one the office actually stands behind.

## This is not the same thing as selector routing or alternate-language discovery

`377` asks what happens when the voter must move through a language selector, locale fallback, or multilingual landing path and needs explicit visibility into whether the destination is a true equivalent translation, selected multilingual content, or a help/oral-assistance route.

`397` asks whether search and discovery layers can find the right translated official page through stable locale URLs, `hreflang`, `x-default`, and safe multilingual fallback.

`487` asks a different question:
**once the official page is already open, does the browser’s own translation layer rewrite that page in a way that still keeps the original-language authority boundary, current-state cues, and safe official translated/help route reconstructible?**

A route may pass `377` and `397` and still fail `487` if:
- the official translated page exists, but the voter instead opens the original-language page and browser translation makes that convenience rendering look like the office-endorsed equivalent,
- search lands on the right locale page, but the voter later opens a nonlocalized attachment or linked page and browser translation makes mixed-source wording look uniformly official,
- or the language selector is honest, yet a same-page translate action quietly suppresses the difference between “official reviewed translation” and “browser convenience rewrite.”

## Convenience translation is not the same as an official reviewed translation

The important boundary here is not whether translation is helpful.
It often is.
The boundary is whether the translated rendering is the **current official artifact** or a browser convenience layer applied to that artifact.

For `487`, the public-safe posture is:
- the current official translated page, if the jurisdiction publishes one, remains the reviewed/publicly supported language lane,
- browser-integrated translation remains subordinate to the original page plus the current official translated/help lane,
- the page should avoid making the translated convenience layer look like the source of legal authority,
- and unresolved ambiguity should route the voter back to the current official translated page or help/oral-assistance lane rather than pretending the browser’s rewrite settled the matter.

This is especially important where the translation may rewrite:
- election names,
- deadline qualifiers,
- receipt-vs-postmark semantics,
- status/result vocabulary,
- office names and jurisdiction labels,
- ID-document labels,
- cure/review/escalation instructions,
- or “may” / “must” / “only if” distinctions.

## Selected-text translation is especially prone to qualifier loss

Chrome and Firefox both document selected-text translation in addition to full-page translation. That means the voter may not even translate the whole page; they may translate only the sentence they highlighted. (xref: `google_chrome_help_translate_pages_page`; xref: `mozilla_support_firefox_translations_page`)

That is where qualifier loss becomes acute.
A voter can translate only:
- a deadline sentence without the exception beneath it,
- an ID rule without the alternatives or cure path,
- a polling-place note without the address-specific lookup qualifier,
- or a rights-sensitive phrase without the official help/escalation lane that controls the real next step.

For `487`, that means the page should avoid writing decisive text so the controlling exception or help route lives only in distant UI chrome, a different accordion, or another panel the translation/excerpt path is unlikely to carry.
If the answer is not safely portable through isolated translation, the page should say so plainly and point the voter toward the current official translated/help lane.

## Auto-translate persistence and language settings are part of the risk boundary

Chrome lets users manage automatically translated languages and translation suggestions. Firefox says the translation panel can open automatically, can be enabled or blocked per language or site, and can be configured through AI Controls. Edge says users can choose Always translate from a language or never translate it. Apple says Safari may keep translating other webpages in the same domain visited in the same tab after one page has been translated. (xref: `google_chrome_help_translate_pages_page`; xref: `mozilla_support_firefox_translations_page`; xref: `microsoft_support_edge_translator_page`; xref: `apple_support_safari_web_page_translation_auto_same_domain_page`)

So this surface cares about more than one button click.
It also cares about whether a browser may keep the voter inside a translated reading mode across multiple pages without the office explicitly choosing that lane.
If translation persistence is plausible, the page should keep source-language identity, current-state labels, and official help routing visible enough that continued translation does not quietly create a shadow multilingual publication track.

## Original-language recovery should stay legible

Firefox and Edge both document an explicit “Show original” recovery path after translation. Safari and Chrome both keep translation as an optional page action or address-bar affordance rather than a mandatory replacement for the source. (xref: `mozilla_support_firefox_translations_page`; xref: `microsoft_support_edge_translator_page`; xref: `apple_support_safari_translate_webpage_page`; xref: `google_chrome_help_translate_pages_page`)

The archive does **not** require every office to control browser UI.
It does require the official page/help lane to remain reconstructible when a voter moves between translated and original views.
Practical consequences:
- keep source-language office identity and page purpose legible on the page itself,
- do not bury the official translated/help lane only in untranslated footer residue,
- and avoid designs where the browser-translated rendering appears to be the canonical official translated publication while the actual reviewed translated page is hidden or absent.

## High-risk topics should bias toward routing, not translation confidence

The most dangerous failures are the same topics that are already risky under `302`, `305`, `307`, `311`, `317–343`, and related public-answer surfaces:
- polling-place / drop-box / early-voting location and hour changes,
- registration status or reactivation,
- absentee request/return deadlines and receipt rules,
- ID alternatives and cure paths,
- disability, language, jail/facility, disaster, or new-citizen edge cases,
- and any answer that should move the voter into `305` ordinary help or `307` rights/safety escalation.

For those topics, `487` does not ask the page to become translation-perfect in an impossible sense.
It asks the page to keep the safe official routing answer visible enough that browser translation remains a convenience layer rather than a hidden substitute for official multilingual support.

## Minimal state taxonomy

A small taxonomy is enough:

1. **official_equivalent_translation_available_browser_translation_subordinate**
2. **original_language_page_browser_translated_current_help_lane_visible**
3. **selected_text_translation_only_not_safe_to_treat_as_complete_answer**
4. **browser_auto_translate_or_language_persistence_in_effect**
5. **translation_feature_blocked_disabled_or_unavailable**
6. **mixed_language_or_nontranslated_attachment_context_not_equivalent**
7. **translation_conflict_under_review_route_to_official_help_or_reviewed_translation**

## Bounded browser-translation trace minimum

The archive does **not** need translated transcripts, per-user language histories, or browser telemetry.
But a voter-information browser-translation surface should preserve a bounded trace for action-changing outputs.

At minimum, that trace should make it possible to reconstruct:
- which official routes were reviewed for browser translation behavior,
- whether a reviewed official translation existed separately,
- whether the browser behavior reviewed was full-page translation, selected-text translation, or likely auto-translate persistence,
- what original-language recovery or official translated/help route the page exposed,
- what non-equivalence or ambiguity warning controlled,
- and when the review was last performed.

Prefer **route identifiers, translation-context labels, official-translation-availability labels, recovery/help anchors, policy notes, and timestamps** over prompt logs, translated copies of every page state, or individualized browser-language histories.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Browser-translation surface claim:** the office reviewed one or more official voter-information routes for browser-integrated translation behavior.
2. **Subordination claim:** browser translation remains subordinate to the current official page plus any reviewed official translated/help lane.
3. **Equivalence-boundary claim:** the surface distinguishes reviewed official translated pages from browser convenience translation of an original-language page.
4. **Selected-text claim:** isolated translated excerpts are not silently treated as complete official answers when qualifiers or help routing matter.
5. **Recovery claim:** the voter can recover the original-language authority or the official translated/help lane without guesswork.
6. **Persistence-honesty claim:** auto-translate or continued same-tab translation behavior is treated as a bounded risk, not a hidden multilingual publication channel.
7. **Privacy-minimization claim:** the office does not retain individualized translation prompts, translated text captures, or language histories when bounded policy evidence is enough.

## Canonical digest artifacts

Publish **digests of browser-translation review posture**, not translated page dumps or per-user telemetry.

- **Browser Translation Surface Digest (BTSD):** digest of the bounded public browser-translation posture payload for a scope.
- **Translation Context Review Digest (TCRD):** optional digest proving which translation contexts were reviewed for a route class.
- **Original-Language Recovery Digest (OLRD):** optional digest proving how the voter can return to source-language authority or the official translated/help lane.
- **Translation Ambiguity Routing Digest (TARD):** optional digest proving the current fallback posture when browser translation is not safe to treat as authoritative.

## What belongs in the public browser-translation payload

Keep the payload **small, bounded, and explicit about non-equivalence**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id`
- human `browser_translation_surface_label`
- `delivery_role_note`
- `covered_surface_refs`
- `official_source_anchors`
- `reviewed_translation_contexts[]`
- `official_translation_availability_note`
- `authority_boundary_note`
- `selected_text_translation_boundary_note`
- `auto_translate_persistence_note`
- `original_language_recovery_note`
- `high_risk_topic_routing_note`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

Do **not** publish by default:
- raw translated transcripts,
- per-user language settings,
- copied browser prompts,
- individualized translation histories,
- or shadow translated page archives that could be mistaken for official reviewed publications.

## How this fits the family map

Use `487` when the right official page is already open, but a browser-integrated translation layer can still make the answer look more official, more universal, or more complete than the office intended.

Use nearby controls when the problem is instead:
- which translated materials or oral-assistance lanes the jurisdiction officially offers (`302`),
- how a language selector or multilingual landing page represents equivalence and fallback (`377`),
- whether search can discover the right translated official page (`397`),
- whether a browser summary or page-context AI layer compresses the same page into a new answer (`486`),
- whether the browser or platform is translating generated captions over already-open official media rather than translating page text (`492`),
- or whether the voter must escalate to ordinary help or rights/safety routing (`305`, `307`).

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-translation-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-browser-translation-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
- EAC: Clearinghouse Resources on Language Access (xref: `eac_language_access_resources_page`)
- EAC: Language Access Program Checklist (source: `eac_language_access_program_checklist_pdf`)
- Google Chrome Help: Translate pages and change Chrome languages (xref: `google_chrome_help_translate_pages_page`)
- Mozilla Support: Firefox Translations (xref: `mozilla_support_firefox_translations_page`)
- Microsoft Support: Use Microsoft Translator in Microsoft Edge browser (xref: `microsoft_support_edge_translator_page`)
- Apple Support: Translate a webpage in Safari on Mac (xref: `apple_support_safari_translate_webpage_page`)
- Apple Support: Web Page Translation in Safari on Mac (same-domain tab continuity) (xref: `apple_support_safari_web_page_translation_auto_same_domain_page`)
