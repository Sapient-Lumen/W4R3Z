# 377 — Official voter-information language selectors, locale fallback, and machine-translation boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information language selectors, language menus, locale toggles, multilingual landing paths, selected-content-in-other-languages menus, and any machine-translation helper the public may encounter while trying to reach voting information**.

It does **not** replace the underlying language-assistance and translated-materials surface in `302`.
It does **not** replace:
- `248`, which treats accessibility, usability, and language access as an integrity property,
- `302`, which governs what translated materials and oral-assistance paths the jurisdiction claims exist,
- `305`, which governs the authoritative office/help route,
- `365`, which governs editioned FAQ/help pages,
- `375`, which governs site search and autocomplete,
- `376`, which governs map/pin/geolocation surfaces,
- or `487`, which governs browser-integrated page translation and selected-text translation **after** the official page is already open.
- `501`, which governs alternate spoken tracks such as dubbed audio or audio description **after** the official recording is already open.

It adds one narrow rule:
**if an election office expects voters to rely on a language selector or locale path to reach action-changing voting information, that selector layer should make clear whether the voter is reaching an equivalent current official translation, only selected multilingual content, or a help/oral-assistance fallback; it should avoid silent locale steering; and it should preserve a bounded trace of what language path was actually presented.**

## Why this is a distinct surface

Current official guidance is enough to justify a narrow control here.
DOJ’s current Section 203 page says covered jurisdictions that provide registration or voting notices, forms, instructions, assistance, or other election-related materials or information must provide them in the applicable minority language as well as English.
EAC’s current language-access resources page treats language access, accessibility, unwritten-language support, and operational checklists as active election-administration resources rather than side topics.
EAC’s current language-access checklist turns that into deployable expectations: identify which election materials must be translated, translate key materials, and plan oral-assistance/publicity paths where written translation is not the right fit.
EAC’s current Voting Accessibility page likewise keeps language accessibility inside the live voter-access lane.
USWDS’s current language-selector guidance then supplies the delivery-layer design rule: language selection is a distinct government-web component with consistent placement and behavior, equivalent-page expectations, explicit selected-content patterns, accessibility tests, and warnings against flags, dead ends, and automatic locale redirects. (xref: `justice_language_minority_citizens_page`; xref: `eac_language_access_resources_page`; source: `eac_language_access_program_checklist_pdf`; xref: `eac_voting_accessibility`; xref: `uswds_language_selector_component_page`; xref: `uswds_language_selector_accessibility_tests_page`; xref: `uswds_select_language_two_languages_pattern_page`; xref: `uswds_select_language_three_or_more_languages_pattern_page`; xref: `uswds_select_language_selected_content_pattern_page`)

That means the language selector is not decorative chrome.
It is often the **delivery layer** that decides whether a voter reaches the current official answer, a partial language landing page, a dead-end translation stub, or an unsupported path that should have routed them to official help.

## The selector is a delivery layer, not a language-coverage claim

A language menu MAY help people reach current official content in the language most usable to them.
It MUST NOT silently overstate what the jurisdiction has actually translated or authorized.

The controlling artifact remains the current official translated page, selected multilingual landing page, hotline/help path, or oral-assistance route that the jurisdiction actually stands behind.
So the selector layer should expose **equivalence class**, not hide it.

At minimum, the public should be able to tell whether they are reaching:
- a current official page with equivalent translated content,
- a current page that only offers selected multilingual content,
- a current official help path for oral assistance or further routing,
- or a convenience-only machine-translated view that does not itself become the authoritative rule source.

## Why locale steering and selector UX matter

Language selection behavior is not neutral.
A header toggle, menu label, browser-locale prompt, automatic redirect, or “translate this page” affordance shapes which answer the public sees first and whether they realize content coverage is partial.

USWDS’s current guidance is unusually concrete here:
- keep the selector visible and consistently placed,
- take users to an equivalent page when equivalent content exists,
- use explicit “selected content” patterns when only some multilingual material exists,
- do not create dead ends,
- do not use flags or country codes as language markers,
- and avoid auto-redirecting language based on location or browser settings because it can confuse and disorient users. (xref: `uswds_language_selector_component_page`; xref: `uswds_select_language_two_languages_pattern_page`; xref: `uswds_select_language_three_or_more_languages_pattern_page`; xref: `uswds_select_language_selected_content_pattern_page`)

For election information, that operationally means a voter should not be pushed into a partial or stale language path without realizing it.

## Equivalent-page / selected-content / help-lane discipline

A public voter-information site should not flatten every multilingual path into “this page is available in language X.”

A small state taxonomy is enough:

1. **Equivalent current translation** — the selected language route lands on a current official page with the same or closely corresponding action-changing content.
2. **Selected multilingual content** — only certain content for this topic is available in that language, and the surface says so explicitly.
3. **Official help/oral-assistance route** — the site cannot provide equivalent written content for this path, so it directs the user to the official language-help or oral-assistance lane.
4. **Unsupported language path** — the selector cannot safely resolve the requested language for this topic and instead exposes the current official fallback.

That distinction matters because “some translated content exists somewhere” is not the same as “this action-changing page is currently available and complete in that language.”

## Machine-translation boundary discipline

The archive does **not** forbid machine translation as a convenience layer.
But if a machine-translation widget or browser-driven translated view is present, the public surface should not treat that convenience output as a hidden official rule source.

The bounded discipline is:
- machine-assisted translation should be visibly subordinate to the current official source page,
- the current official language-access/help path should remain reachable,
- the surface should not imply equivalence where none has been reviewed or published,
- and unresolved ambiguity should route the voter to the official help/oral-assistance lane instead of pretending the convenience layer settled the rule.

This is an inference from the combined official posture above:
DOJ and EAC make language access a real election-information obligation, while USWDS distinguishes between equivalent translated content and selected-content patterns.
That makes it unsafe to let a machine-only presentation silently masquerade as a fully equivalent official publication. (xref: `justice_language_minority_citizens_page`; xref: `eac_language_access_resources_page`; source: `eac_language_access_program_checklist_pdf`; xref: `uswds_select_language_two_languages_pattern_page`; xref: `uswds_select_language_three_or_more_languages_pattern_page`; xref: `uswds_select_language_selected_content_pattern_page`)

## Markup, annotation, and accessibility minimum

A multilingual election-information surface should also preserve basic machine-readable language signaling.
USWDS’s current component guidance says the language of each page should be identified with the HTML `lang` attribute, and language links in menus should identify the linked language.
USWDS’s current accessibility-test page also says implementers should test the selector in the context of their own site for Section 508 compliance rather than assuming the component alone solves accessibility. (xref: `uswds_language_selector_component_page`; xref: `uswds_language_selector_accessibility_tests_page`)

That means the selector is not finished when the menu “looks right.”
The surrounding page, translated route, keyboard behavior, and language annotations still matter.

## Bounded locale-trace minimum

The archive does **not** need indefinite logs of browser headers or per-user language histories.
But for accountability and dispute resolution, a voter-information language-selector surface should preserve a bounded **locale trace** for action-changing outputs.

At minimum, that trace should make it possible to reconstruct:
- which selector/locale policy version was in force,
- whether the language path was manually selected or automatically suggested/presented,
- which equivalence class the user was shown,
- which translated/help/fallback anchor the surface promoted,
- what language code or label the surface presented,
- and when the result state was generated.

Prefer **surface-policy versions, equivalence-class labels, selected-language identifiers, promoted-anchor identifiers, and timestamps** over indefinite retention of raw `Accept-Language` headers, geolocation guesses, or cross-session language profiles.

## Privacy and minimization floor

Language-selector layers can quietly become fingerprinting or profiling surfaces if they retain raw browser-locale, IP-geography, or long-lived preference data without a clear need.

So the selector should default to minimization:
- do not retain raw `Accept-Language` headers longer than the published policy requires,
- do not combine browser-language hints with voter-record data absent a separately disclosed authority,
- do not geolocate users merely to guess language when a visible manual selector exists,
- and do not treat language preference trails as a shadow case-management system.

The selector should help a voter reach official content; it should not become a silent profiling layer.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official selector-surface claim:** the office identified one or more public language-selection or multilingual-routing surfaces as official for scope `E`.
2. **Equivalence-class claim:** each language path is presented as equivalent translation, selected-content route, help/oral-assistance route, or unsupported path rather than as vague “translation availability.”
3. **Equivalent-page claim:** when equivalent current content exists, the selector routes to the corresponding current page instead of a generic or stale landing page.
4. **No-silent-steering claim:** automatic locale suggestion or presentment does not silently replace visible manual language choice.
5. **Machine-boundary claim:** convenience translation layers do not silently become authoritative rule sources.
6. **Locale-trace claim:** action-changing outputs are reconstructible through bounded policy-version, language-choice, equivalence-class, anchor, and timestamp evidence.
7. **Privacy-minimization claim:** browser-language, location, and preference data are not retained or linked longer than the published policy requires.
8. **Superseding claim:** material selector behavior or language-route changes produce an explicit update state rather than silent drift.

## Canonical digest artifacts

Publish **digests of the language-selection surface and state**, not raw user preference logs.

- **Language Selector Surface Digest (LSSD):** digest of the bounded public language-selector payload for a scope.
- **Language Route Policy Digest (LRPD):** digest of the current equivalence/fallback/steering policy for multilingual public routes.
- **Locale Path Snapshot Digest (LPSD):** optional digest proving what bounded language-path state the selector would have shown for a documented topic/language pair at time `T`.

## What belongs in the public language-selector payload

Keep the payload **small, action-relevant, and clear about equivalence boundaries**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `language_surface_label`
- `language_entrypoints[]`
- `selector_modalities[]`
- `supported_language_routes[]`
- `official_language_access_uri`
- `official_help_uri` / `official_help_phone`
- `equivalence_policy_note`
- `selected_content_policy_note`
- `machine_translation_boundary_note`
- `auto_redirect_policy_note`
- `markup_accessibility_note`
- `locale_trace_policy`
- `privacy_minimization_note`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw `Accept-Language` headers,
- IP-derived locale guesses,
- per-user language-preference histories,
- internal translation QA notes,
- draft translations,
- or copied legal analysis that is not needed for the public answer surface.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official language selector or multilingual route surface was in force at time `T`?
- Did the selector present the route as equivalent translation, selected content, help/oral-assistance, or unsupported?
- When equivalent translated content existed, did the selector reach the corresponding current page?
- Did the surface create dead ends, hide partial translation coverage, or silently auto-redirect users into a different language path?
- If a machine-translation helper was present, was the current official source/help path still visible?
- Could a third party reconstruct the bounded language-path state without full browser-fingerprint logs?

## How this fits the family map

A language selector is **not** a new canonical voter-question family bucket.
It is a delivery layer that sits in front of the public-answer families already modeled in `292–343`.

So the family question remains:
- `302` states which languages, translated materials, and oral-assistance paths exist,
- `305` states which office/help route is authoritative,
- `365` governs the editioned FAQ/help pages the selector may point toward,
- `375` governs search if users search inside the selected language path,
- `376` governs maps if users locate a site after changing language,
- and the special-case family docs still determine the substantive answer.

This document only says that, if an office uses language selectors or multilingual routing as a public delivery layer, that layer should remain explicit about equivalence, current-state-aware, bounded, and later-reconstructible instead of silently acting as a rule-making surface.

If the harder question is instead what happens when the **already-open** official page is browser-translated or selected-text-translated in place, use `487` rather than stretching this selector/locale-routing surface beyond its boundary.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-language-selector-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-language-selector-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- DOJ: Language Minority Citizens / Section 203 overview (xref: `justice_language_minority_citizens_page`)
- EAC: Clearinghouse Resources on Language Access (xref: `eac_language_access_resources_page`)
- EAC: Language Access Program Checklist (source: `eac_language_access_program_checklist_pdf`)
- EAC: Voting Accessibility (xref: `eac_voting_accessibility`)
- USWDS: Language selector component (xref: `uswds_language_selector_component_page`)
- USWDS: Language selector accessibility tests (xref: `uswds_language_selector_accessibility_tests_page`)
- USWDS: Select a language — two languages (xref: `uswds_select_language_two_languages_pattern_page`)
- USWDS: Select a language — three or more languages (xref: `uswds_select_language_three_or_more_languages_pattern_page`)
- USWDS: Select a language — selected multilingual content (xref: `uswds_select_language_selected_content_pattern_page`)
