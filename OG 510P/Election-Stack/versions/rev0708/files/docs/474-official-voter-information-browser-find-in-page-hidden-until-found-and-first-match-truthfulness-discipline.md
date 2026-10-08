# 474 — Official voter-information browser find-in-page, hidden-until-found, and first-match truthfulness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that people may search inside with browser or app “Find in page” behavior** — including keyboard search such as `Ctrl+F` / `Cmd+F`, browser “Find on page”, or similar on-page keyword-refinding flows — where:

- the route is long enough that many voters will try to re-find the answer by keyword instead of by maintained section anchor,
- the decisive keyword appears several times across alert bars, navigation chrome, summaries, exceptions, FAQs, or the controlling body section,
- the first easy match can land on stale, partial, off-scope, or subordinate text that looks more authoritative than it is,
- hidden or collapsed content is assumed to be searchable/revealable even though the route has not reviewed whether that actually happens,
- or the found text becomes so decontextualized that a voter sees the matched phrase but not the heading, freshness cue, jurisdiction scope, or help lane that makes the phrase safe to act on.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `375`, which governs official site search and autocomplete,
- `442`, which governs maintained section anchors, jump links, and in-page navigation structures,
- `443`, which governs accordions, disclosures, and collapsed-answer reveal posture,
- `445`, which governs tabbed answer panels and hidden-panel continuity,
- `466`, which governs copied fragment references that fail to resolve to a real section target,
- or `473`, which governs browser-generated or search-generated highlighted-text deep links rather than ordinary manual on-page keyword search.

It adds one narrow rule:
**if an official voter-information route is long enough that ordinary people will realistically use browser find-in-page to re-find the answer, the route should keep first realistic matches truthful, keep keyword hits subordinate to the current official page context, and avoid relying on hidden-state magic as the only way decisive text becomes findable.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes hierarchy, structure, clarity, accessibility, usability, and accuracy. MDN’s current HTML `hidden` guidance matters because hidden content is not presented to the user, while the special `hidden="until-found"` state is treated differently: the content remains accessible to browser find-in-page or fragment navigation, and when a match occurs the browser fires `beforematch`, removes the `hidden` attribute, and scrolls to the element. MDN’s current `beforematch` guidance matters because it makes the trigger explicit: the browser may reveal hidden-until-found content because the user found it through find-in-page or fragment navigation. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_hidden_global_attribute_page`; xref: `mdn_beforematch_event_page`)

That is enough to justify a compact control here.
A route may pass anchors, disclosures, tabs, and stale-link recovery yet still fail the public because:
- a voter searches `ID`, `drop box`, `signature`, or `deadline` and the first visible hit lands in banner chrome or an exception note rather than the controlling section,
- a keyword match appears in a stale summary, old warning, or secondary navigation item before the main answer,
- a maintainer assumes hidden or collapsed content will be revealed by browser search when only some hiding patterns were actually reviewed for that behavior,
- or the matched phrase is visible but the voter cannot tell whether it belongs to the current jurisdiction, current election phase, or current official rule.

## This is not the same thing as anchors, disclosures, tabs, or quoted-text deep links

`442` asks whether the office provides maintained section anchors and in-page navigation that remain stable and legible over time.

`443` asks whether collapsed disclosures and accordions reveal the controlling answer without guesswork.

`445` asks whether tabbed interfaces keep the answer-bearing panel discoverable and continuously reachable.

`473` asks whether browser-generated or search-generated highlighted-text deep links are subordinate to the surrounding official context.

`474` asks a different question:
**when a person manually searches within the current official page by keyword, do the easiest matches still tell the truth about where the controlling answer lives and what context makes it safe?**

A route may pass the earlier controls and still fail `474` if:
- maintained anchors exist, yet the public still uses find-in-page and the first match lands on a misleading summary or duplicate phrase,
- disclosures or tabs are technically operable, yet browser search lands on vague labels or noncontrolling snippets before the real answer,
- a quoted-text deep link posture is sound, yet ordinary manual find-in-page still leaves the voter staring at a decontextualized keyword match,
- or the route technically contains the right words while repeated chrome makes browser search feel like a scavenger hunt.

## First realistic matches are part of the answer-delivery surface

For long official pages, the first realistic browser-search hit is not just a browser convenience.
It becomes part of the public answer path.
A hurried voter may search for:
- `registration deadline`
- `photo ID`
- `drop box`
- `signature cure`
- `student`
- `military`
- `provisional`

and then act from the first match they see.

That means the route should review whether common action-changing terms first land on:
- the governing section,
- a clearly subordinate summary that points immediately to the governing section,
- or a misleading side surface such as a banner, footer, expired warning, generic FAQ label, or off-scope exception.

The archive does **not** require perfect keyword-engineering for every possible query.
It does require the office not to ignore the obvious high-stakes terms that voters predictably use to re-find the answer on long pages.

## Duplicate keyword matches in chrome can quietly outrank the real answer

A long route can be current and well maintained while still failing this surface because decisive words appear repeatedly in places that are not the controlling answer:
- repeated site navigation,
- sticky alerts,
- “related content” cards,
- summary boxes,
- footer help text,
- stale archived notices still visible on the page,
- or exception paragraphs that only govern a minority case.

For `474`, the question is not “does the word appear somewhere?”
It is:
**does ordinary on-page keyword search help the voter re-find the controlling section, or does it first amplify surrounding chrome and secondary language that looks easier to trust than it should?**

A route does not need to eliminate every duplicate word.
It should keep high-stakes keywords from being dominated by misleading or context-poor early matches.

## Hidden-until-found is a bounded convenience, not a blanket promise

MDN’s current `hidden` guidance is useful because it separates ordinary hidden content from the special `hidden="until-found"` state. Ordinary hidden content is not presented to the user. Hidden-until-found content may be revealed by browser find-in-page or fragment navigation, and the browser fires `beforematch` before removing the hidden attribute and scrolling to the element. (xref: `mdn_hidden_global_attribute_page`; xref: `mdn_beforematch_event_page`)

For this archive, that means:
- hidden-until-found can be a useful convenience,
- but the office should not assume every collapsed, hidden, injected, or offscreen answer region will become visible through browser search,
- and the route should not make hidden-until-found behavior the only realistic way a voter can reveal decisive official text.

If the controlling answer matters enough to change what the voter does next, there should still be an ordinary visible path to that answer even when browser search reveal behavior is absent, inconsistent, or simply not the path the voter takes.

## A found phrase should stay subordinate to heading, freshness, scope, and help context

Browser find-in-page often highlights only a phrase or a short local snippet.
That makes surrounding context load-bearing.
A matched `deadline` or `ID required` phrase can be misleading if the voter cannot also tell:
- which page or section they are in,
- whether the match belongs to the current election phase,
- whether the phrase is a summary, exception, or superseded notice,
- what jurisdiction or voter class the text applies to,
- and where the current help lane lives if the match alone is not enough.

The archive does **not** require browser search to turn into a custom in-page search application.
It does require that the page remain context-rich enough that a highlighted keyword hit does not quietly impersonate the whole official answer.

## Browser search should fail open when the first hit is not the controlling answer

The office cannot fully control browser find-in-page UX.
But it can control whether the page fails open.
Bounded good behavior can include:
- clear headings near the real answer,
- summary text that honestly points deeper instead of pretending to be the full rule,
- visible freshness or `as_of` cues where time sensitivity matters,
- explicit exception labels so minority-case text does not read like the default rule,
- and an ordinary help/contact lane that stays visible when a keyword hit alone is not enough.

What fails `474` is not “the browser had a search box.”
What fails `474` is leaving the voter with a highlighted phrase that appears actionable while the surrounding route provides too little context to tell whether that phrase really controls.

## Preserve bounded findability evidence, not user search logs

The evidence posture here is about reconstructing whether important routes were reviewed for manual on-page keyword search.
The archive should preserve:
- which route families were reviewed for browser find-in-page posture,
- which high-stakes keywords or keyword classes were tested,
- whether first realistic matches landed on controlling sections, subordinate summaries, or misleading secondary text,
- whether hidden-until-found behavior was intentionally relied upon anywhere,
- whether heading/freshness/help context remained visible around matched phrases,
- and when the review last occurred.

It should **not** require preserving:
- individualized browser search strings tied to named people,
- per-user find-in-page telemetry,
- keypress logs,
- session replay archives,
- or giant analytics stores merely to prove that people searched within a page.

## Canonical digest artifacts

Publish **small digests of manual on-page keyword-find posture**, not user search exhaust.

- **Find-in-Page Surface Digest (FPSD):** digest of how important official routes behave under ordinary browser find-in-page use.
- **First-Match Integrity Digest (FMID):** optional digest describing whether high-stakes keywords first land on the controlling section, an honest subordinate summary, or misleading secondary text.
- **Hidden-Reveal Review Digest (HRRD):** optional digest describing where hidden-until-found behavior is reviewed and where ordinary visible reveal paths still control.

## What belongs in the public browser-find payload

Keep the payload **small, route-aware, and keyword-refinding focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `find_in_page_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_find_routes[]`
- `high_stakes_keyword_classes[]`
- `first_match_integrity_note`
- `duplicate_match_boundary_note`
- `hidden_until_found_boundary_note`
- `context_preservation_note`
- `help_or_heading_refind_note`
- `unsupported_or_nonreveal_recovery_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized search strings,
- per-user find telemetry,
- keypress capture,
- full session-replay artifacts,
- or giant analytics exports that are not needed for bounded public-answer reconstruction.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether important voter-information routes remain trustworthy when a voter uses browser find-in-page to re-find an answer by keyword?
- For high-stakes terms, did the first realistic matches land on the controlling section, an honest subordinate summary, or misleading secondary text?
- Did the office avoid relying on hidden-state magic as the only practical way decisive text becomes findable?
- When a matched phrase appears, does enough heading/freshness/scope/help context remain visible to keep the phrase subordinate to the full official answer?
- Did the archive preserve bounded review evidence without collecting individualized search logs or replay exhaust?

## How this fits the family map

Browser find-in-page, hidden-until-found, and first-match truthfulness is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if voters will realistically use ordinary browser keyword search inside a long official page, the route should keep those keyword hits truthful, contextual, and fail-open rather than letting a decontextualized first match silently pose as the official answer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-find-in-page-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-find-in-page-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- MDN: HTML `hidden` global attribute (xref: `mdn_hidden_global_attribute_page`)
- MDN: `beforematch` event (xref: `mdn_beforematch_event_page`)
