# 473 — Official voter-information text-fragment deep links, quoted-text highlights, and excerpt-anchor truthfulness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that may be reached through browser-generated, search-generated, or user-shared text-fragment deep links** — for example URLs using fragment directives such as `#:~:text=...` — where:

- a voter lands with a highlighted sentence or quoted excerpt rather than an ordinary section anchor,
- the quoted text may be easier to notice than the page’s broader official context,
- the highlighted excerpt may later drift, stop matching, or fail to scroll/highlight on some browsers,
- bookmarks or shares may propagate the quoted-text deep link even when the office did not mint it,
- or the office page cannot safely overclaim that it knows exactly which highlighted quote the visitor followed.

The concern here is not that pages can be cited or linked.
It is the narrower failure mode where a **quoted-text highlight starts to feel like a standalone official ruling** even though the controlling answer still lives in the current official page, section structure, freshness cues, and help lane around it.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `442`, which governs maintained section anchors, same-page navigation, and fragment-target continuity,
- `466`, which governs unresolved same-page target misses and fail-open refinding,
- `467`, which governs current live pages versus point-in-time citation-safe heads,
- `468`, which governs compact cross-route citation-head registers,
- or `471`, which governs office-offered Copy/Share controls,
- or `474`, which governs ordinary manual browser find-in-page / on-page keyword search rather than incoming text-fragment directives or highlighted-quote arrivals.

It adds one narrow rule:
**if official voter information may be reached through a quoted-text deep link or browser-highlighted excerpt, the route should keep the excerpt visibly subordinate to the current official page context, fail open when the highlight is missing or unstable, and avoid treating a brittle text fragment as the sole durable official anchor.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, hierarchy, accessibility, usability, and accuracy. MDN’s current **Text fragments** guidance says text fragments link directly to specific text in a page without requiring an author-provided `id`, and that browsers usually scroll the text into view and highlight it. The same MDN guidance also says text in a document is less stable than document structure, so if the linked text changes the fragment no longer matches and the browser navigates to the top of the page. MDN’s current **URL Fragment Text Directives** guidance says fragment directives are stripped from the URL during loading so author scripts cannot directly interact with them. MDN’s current **URI fragment** reference also remains important because it says fragments are processed by the client after retrieval and are not sent to the server. The current WICG **URL Fragment Text Directives** specification further says user agents may carry a matching fragment directive into bookmarks or sharing flows while the visual indicator is still active. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_text_fragments_page`; xref: `mdn_url_fragment_text_directives_api_page`; xref: `mdn_uri_fragment_page`; xref: `wicg_url_fragment_text_directives_spec_page`)

That is enough to justify a compact control here.
A route may pass `442`, `466`, `467`, and `471` yet still fail the public because:
- the quoted sentence is highlighted, but the surrounding heading/date/jurisdiction/help context is too weak to keep the excerpt trustworthy,
- a browser or search result deep-links to text the office did not explicitly anchor and the excerpt later drifts,
- the text fragment no longer matches and the page silently opens at the top as though the exact quote had been recovered,
- a bookmark or forwarded link preserves a highlight that looks durable even though the office intended section anchors or citation-safe snapshots to be the maintained references,
- or app/server logic implies it knows which quoted excerpt was requested even though fragment directives are not directly exposed to author scripts and are not sent to the server.

## This is not the same thing as section anchors, fragment misses, citation heads, or office-offered share controls

`442` asks whether the office maintains **stable section targets and in-page navigation**.

`466` asks what happens when an expected same-page target **fails to resolve**.

`467` asks whether a mutable live page is being cited as though it were a stable **point-in-time citation head**.

`471` asks whether an office-offered **Copy/Share control** tells the truth about the artifact it hands off.

`473` asks a different question:
**when a voter arrives through a quoted-text deep link that the browser, search engine, helper, or user may have generated, does the page keep that excerpt in truthful relationship to the current official answer surface instead of letting the highlight masquerade as a standalone authoritative object?**

A route may pass the earlier controls and still fail `473` if:
- maintained heading anchors exist, but the highlighted sentence floats without enough visible official context,
- the text fragment miss posture is generic top-of-page recovery, but nothing tells the public that quoted-text highlights are brittle references rather than durable maintained anchors,
- a citation-safe head exists elsewhere, but the arriving highlighted excerpt makes the mutable live page look like the exact preserved citation object,
- or the office never offered a Share button, yet browser-generated/bookmarked highlight links still circulate as though the office vouched for them.

## Highlighted excerpts should remain subordinate to the current official page context

A quoted-text highlight can be helpful because it reduces search friction.
But on election pages, the excerpt should not outrank the page context that makes it meaningful.
A highlighted sentence about ID requirements, ballot deadlines, or cure steps may need nearby qualifiers, exceptions, dates, jurisdiction scope, or office contact lanes.

For this archive, a route should preserve enough visible context around highlighted text that a reader can still tell:
- what official page they are on,
- what section or heading the excerpt belongs to,
- whether freshness or `as_of` cues matter,
- and where the official help or replacement lane lives if the excerpt is no longer sufficient by itself.

The archive does **not** require suppressing all browser highlighting.
It does require that the highlighted quote not become the only thing a hurried voter can realistically see or trust.

## Text fragments are useful, but they are not the best durable official anchor

MDN’s current text-fragment guidance is explicit that text is less stable than document structure and that if the linked text changes the browser navigates to the top of the page. (xref: `mdn_text_fragments_page`)
That matters here because the office may want several different kinds of durable reference:

- a maintained section anchor for ordinary long-page navigation,
- a citation-safe snapshot or citation head for point-in-time exactness,
- or a share-safe canonical page URL for ordinary forwarding.

A text fragment can complement those.
It should not silently replace them as the office’s only durable public anchor when the office actually needs something more stable than a quoted phrase match.

## Do not overclaim that the page knows exactly which quote the visitor followed

MDN’s current text-fragment guidance says fragment directives are stripped from the URL during loading so author scripts cannot directly interact with them, and MDN’s URI fragment reference says fragments are not sent to the server. (xref: `mdn_text_fragments_page`; xref: `mdn_uri_fragment_page`; xref: `mdn_url_fragment_text_directives_api_page`)

For this archive, that means a route should be careful about claims such as:
- “you followed the quote about early voting hours,”
- “we know exactly which highlighted sentence you opened,”
- or “this page can prove which excerpt was shared to you”

unless the office has some separate, truthful, privacy-safe basis for making that claim.

The archive does **not** forbid contextual recovery or nearby help cues.
It does forbid pretending that server logs or ordinary page scripts can reliably see and certify the exact incoming text-fragment directive when the platform guidance says otherwise.

## Bookmarks and sharing can propagate highlighted deep links even when the office did not mint them

The current WICG specification says newly created bookmarks and share flows may include the fragment directive when a match was found and the highlight is still active. (xref: `wicg_url_fragment_text_directives_spec_page`)
That matters because the office may never expose a `Copy link to highlight` control and still find that highlighted-text deep links circulate anyway.

So for this archive:
- do not confuse browser-generated/bookmarked/share-propagated highlight links with office-issued portable records,
- do not assume `471` covers the whole problem,
- and keep the page’s recovery/help/context posture strong enough that a forwarded highlight link does not silently outrank maintained official anchors.

## Missing, unsupported, or suppressed text-fragment behavior should fail open

MDN’s current guidance says if the text fragment does not match any text in the linked document, or if the browser does not support text fragments, the whole text fragment is ignored and the top of the document is linked. MDN also notes that sites can opt out of text-fragment processing via a `Document-Policy: force-load-at-top` header, and the current WICG specification explains that this policy disables automatic scroll-on-load features. (xref: `mdn_text_fragments_page`; xref: `wicg_url_fragment_text_directives_spec_page`)

For this archive, that means a route should not let these cases masquerade as successful exact-quote recovery:
- no match because the text changed,
- unsupported browser,
- policy-driven suppression of automatic scroll/highlight,
- or any other arrival where the highlight cue is missing even though the page itself loaded.

Bounded good behavior can include:
- preserving a visible heading/section structure that helps re-find the answer,
- keeping freshness/help cues near the top of the route,
- preferring maintained section anchors or citation-safe links in office-authored durable references,
- or adding a compact public note in review artifacts that highlighted-text links are convenience pointers rather than guaranteed exact anchors.

## Preserve bounded review evidence, not per-user highlight telemetry

The evidence posture here is about reconstructing whether the office reviewed how quoted-text deep links behave on important public-answer routes.
The archive should preserve:
- which route families were reviewed for text-fragment arrival posture,
- whether highlighted excerpts remain subordinate to visible official context,
- whether maintained anchors or citation-safe references are preferred for durable official linking,
- whether no-match / unsupported / suppressed-highlight cases fail open,
- whether the office avoids overclaiming quote-level observability,
- and when the review last occurred.

It should **not** require preserving:
- exact incoming quoted strings tied to named users,
- per-user shared-link trails,
- bookmark histories,
- individualized fragment analytics,
- or giant clickstream/session-replay stores merely to prove that highlighted-text links were seen.

## Canonical digest artifacts

Publish **small digests of text-fragment posture**, not quote telemetry.

- **Text-Fragment Surface Digest (TFSD):** digest of how highlighted-text deep-link arrivals are handled on the reviewed official route family.
- **Excerpt-Context Integrity Digest (ECID):** optional digest describing how visible official context is preserved around a highlighted excerpt.
- **Highlight-Fail-Open Digest (HFOD):** optional digest describing no-match / unsupported / policy-suppressed recovery posture.

## What belongs in the public text-fragment payload

Keep the payload **small, route-aware, and quoted-link focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `text_fragment_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_text_fragment_routes[]`
- `excerpt_context_integrity_note`
- `durable_anchor_preference_note`
- `unsupported_or_no_match_recovery_note`
- `fragment_visibility_boundary_note`
- `bookmark_share_propagation_note`
- `highlight_subordination_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- per-user quoted-text logs,
- individualized bookmarks or forwarded-link trails,
- raw fragment-directive strings tied to real people,
- session replays,
- or giant analytics exports.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review how important voter-information pages behave when opened through a text-fragment deep link or highlighted-text excerpt?
- Does a highlighted sentence remain visibly subordinate to the current official page, section, freshness, and help context?
- Did the office avoid treating brittle text fragments as its only durable official anchor when section IDs, share-safe links, or citation-safe heads are more appropriate?
- When the highlight is missing, unsupported, or no longer matches, does the route fail open instead of implying exact-quote recovery?
- Did the office avoid overclaiming that it can directly observe and certify the exact incoming quote fragment?
- Did the review preserve bounded evidence without collecting per-user highlight telemetry?

## How this fits the family map

Text-fragment deep links, quoted-text highlights, and excerpt-anchor truthfulness is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if the public may reach or forward official voter information through highlighted-text deep links, the page should keep those excerpts truthful, subordinate, and recoverable rather than letting them pose as durable standalone official rulings.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-text-fragment-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-text-fragment-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- MDN: Text fragments (xref: `mdn_text_fragments_page`)
- MDN: URL Fragment Text Directives (xref: `mdn_url_fragment_text_directives_api_page`)
- MDN: URI fragment (xref: `mdn_uri_fragment_page`)
- WICG: URL Fragment Text Directives specification (xref: `wicg_url_fragment_text_directives_spec_page`)
