# 467 — Official voter-information mutable live pages, point-in-time citation snapshots, and current-vs-citation-head discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that are likely to be cited, quoted, summarized, or handed off by search, AI answers, chatbots, hotline scripts, partner explainers, journalists, or later dispute reviewers even though the live page may continue changing over time**:
FAQ answers,
deadline pages,
hours/location pages,
status explanations,
change notices,
help articles,
and similar official routes where the current live page may be the right operational answer now but may no longer be the exact page state someone saw or cited at time `T`.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `223`, which governs hashes-first public-surface capture notes and reproducibility,
- `226`, which governs public fingerprint reports for publishable packets,
- `363`, which governs official automated voter-information assistants and answer traces,
- `365`, which governs official voter FAQ/article editions,
- `367`, which governs press releases, media advisories, and spokesperson quotes,
- `386`, which governs off-platform AI answer surfaces and citation handoff,
- `437`, which governs user-facing portable records once information leaves the live page,
- `438`, which governs whether the live URL itself is safe to keep and revisit,
- `468`, which governs the compact cross-route register that names operational heads, citation heads, and unique-head warnings across reviewed mutable lineages,
- or `201`, which governs parity snapshots across official channels.

It adds one narrow rule:
**if an official voter-information page is materially mutable yet likely to function as a citation anchor, the office should distinguish the current live operational head from the latest point-in-time citation-safe head and should not imply a unique frozen citation state when only a mutable live page exists.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications. USWDS’s current **Keep a record** guidance says successful public-service flows should preserve a record that includes the site name, URL, date, and next-step/reference context when possible. Google Search Central’s current **AI features and your website** guidance and related search-presentation guidance make clear that public-web content can be surfaced, linked, and summarized through search and AI layers before the voter reaches the official site. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `google_search_central_ai_features_page`; xref: `google_search_central_title_links_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_meta_descriptions_snippets_page`)

That is enough to justify a compact control here.
A route may pass `438`, `363`, `365`, and `386` yet still fail the public because:
- the live official page is current today, but no bounded point-in-time artifact proves what the page said when an earlier citation was made,
- an AI answer, hotline script, or media summary points to a mutable page as if it were a stable exact citation,
- the office has an operational current page but no clear citation-safe snapshot for later review,
- a reviewed preview/staging copy is confused with the actual public citation head,
- or a newer live page silently supersedes a cited earlier state without a small preserved trail linking old and new.

## Current operational head and citation head are not the same thing

This archive needs a small distinction:

For a single reviewed route, `467` is usually enough. Once a jurisdiction has several mutable route lineages or several plausible citation candidates, `468` should carry the compact cross-route register so handoff users do not have to infer head status from scattered per-route notes.


- **operational head** — the current live official page or answer state the office intends the public to use now;
- **citation head** — the latest point-in-time preserved page state or bounded capture the office is willing to treat as the exact page state for later citation, quoting, or dispute reconstruction.

Sometimes these are the same.
Often they are not.
A live page may keep changing while the latest citation-safe capture still points to yesterday’s reviewed state.

What matters is not forcing every route to freeze continuously.
What matters is not pretending that a mutable live head is automatically a uniquely reproducible citation head.

## This is not the same thing as share-safe URLs, portable records, or capture notes alone

`438` asks whether the live URL is safe to keep, copy, and revisit later.

`437` asks whether the voter can carry a useful record out of the live page.

`223` and `226` provide hashes-first capture and fingerprint machinery.

`467` asks a different question:
**when an official mutable page is used as an authoritative citation anchor, does the office distinguish the current live page from the latest point-in-time citation-safe state and preserve the relationship between them clearly enough for later review?**

If the public is arriving through a browser-generated or search-generated highlighted excerpt on the live page, `473` covers whether that quoted-text arrival is kept subordinate to the surrounding official context instead of being mistaken for the citation head itself.

A route may pass the earlier controls and still fail `467` if:
- the URL is stable but the cited live page changed materially after the citation,
- the office can reproduce a raw capture internally but does not expose whether a public citation-safe head exists,
- a printable/user-facing record exists for one person’s session but no bounded citation head exists for public review,
- or captures exist somewhere in the archive but the public-facing answer posture never says whether the current live head is already frozen, pending capture, or superseded.

## The office should not overclaim citation exactness on mutable pages

For action-changing public content, a simple but important honesty rule applies:
if the office only has a mutable live page and no current frozen snapshot/capture, it should not behave as though every citation to that live page is an exact point-in-time reference.

The bounded alternatives are straightforward:
- provide a small point-in-time snapshot or capture,
- identify the live page as the operational head and say that the current citation-safe head is pending or older,
- or route high-stakes exact-state questions to the latest signed notice, published packet, or bounded capture bundle that already exists.

The archive does **not** require a heavyweight version-control UI on every page.
It does require honest separation between live-now truth and exact-as-cited truth.

## Preview, draft, queued, or staging states are not public citation heads

A useful import from stricter publication systems is that internal release state is not the same thing as public release state.
For this archive, that means a preview URL, CMS staging copy, reviewed draft, queue entry, or published-ready artifact is **not** automatically the public citation head merely because it exists or because staff can see it.

If a route maintains internal preview or queue states, the public-facing posture should keep three truths separate:
- what the current public operational head is,
- what the latest public citation-safe head is,
- and what materials are still preview/staging/non-public and therefore not valid public citation anchors.

This keeps "we had a reviewed copy somewhere" from masquerading as "the public had a stable cited state."

## Superseding relationships should remain legible

If a mutable page changes materially, the archive should not force future readers to infer the chain by diffing captures manually.
The office should preserve a bounded statement of whether the newer live/citation head:
- supersedes,
- corrects,
- updates,
- or leaves unchanged
an earlier citation-safe head.

That can be small.
The goal is not to narrate every edit.
The goal is to stop later reviewers from guessing whether a citation drifted because the page changed, the quote was wrong, or the current live page was never the cited state in the first place.

## This is especially important for AI/chatbot/media handoff

`363`, `365`, `367`, and `386` already establish that official answers may be routed, quoted, summarized, or cited before the voter reads the whole page.
That makes mutable-page citation discipline a shared dependency rather than a niche archiving concern.

When a hotline script, official chatbot, AI overview, or media quote points to a mutable official page, the office should be able to answer:
- was that live page also the citation-safe head at the time,
- if not, which point-in-time head was,
- and how does the current live head relate to that earlier cited state?

## Preserve bounded evidence, not full web-archive exhaust

The evidence posture here is about reconstructing citation exactness without pretending every mutable page must become a giant archival bundle by default.
The archive should preserve:
- which routes are materially mutable yet likely to serve as citation anchors,
- whether each reviewed route had a current live operational head, a citation-safe head, or both,
- what bounded artifact identifies the latest citation-safe head,
- what preview/staging boundary controlled non-public copies,
- how superseding relationships between citation heads are expressed,
- and when the review last occurred.

It should **not** require publishing by default:
- full raw HTML for every change,
- internal CMS audit logs,
- private editor identities,
- giant browser-capture corpora,
- or internal queue dashboards that are not part of the public record.

## Canonical digest artifacts

Publish **small digests of live-vs-citation-head posture**, not giant archival exhaust.

- **Citation-Head Surface Digest (CHSD):** digest of the bounded operational-head / citation-head policy payload for the official route.
- **Point-in-Time Citation Snapshot Digest (PCSD):** optional digest identifying the latest public citation-safe snapshot/capture for the route.
- **Preview/Queue Boundary Digest (PQBD):** optional digest describing which preview, draft, staged, or queued states are explicitly non-public and therefore not citation heads.

## What belongs in the public citation-head payload

Keep the payload **small, route-aware, and head-status focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `citation_snapshot_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `operational_head_routes[]`
- `citation_head_status`
- `citation_head_artifacts[]`
- `live_vs_citation_head_note`
- `snapshot_generation_policy_note`
- `preview_queue_boundary_note`
- `superseding_citation_head_note`
- `quote_or_ai_citation_recovery_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- full internal CMS histories,
- private editorial diffs,
- staff-only preview URLs,
- queue dashboards or unpublished release tooling,
- or giant page-archive corpora when a bounded citation-head digest is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify which mutable official pages were likely to function as citation anchors?
- For a given route at time `T`, what was the current live operational head and was there also a citation-safe head?
- If there was no current frozen citation head, did the office avoid implying exact point-in-time citation certainty?
- Were preview, draft, staged, or queued copies kept clearly separate from the public citation head?
- When the route changed materially, was the relationship between the old and new citation-safe heads legible enough for later reconstruction?

## How this fits the family map

Mutable live pages, point-in-time citation snapshots, and current-vs-citation-head discipline is **not** a new underlying voter-question family bucket.
It is a delivery-layer and evidence-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if a mutable official page is likely to be cited as authoritative, the office should distinguish the live operational head from the latest citation-safe head and keep preview/non-public states from masquerading as public citation truth.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-citation-snapshot-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-citation-snapshot-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Keep a record (xref: `uswds_keep_a_record_page`)
- Google Search Central: AI features and your website (xref: `google_search_central_ai_features_page`)
- Google Search Central: Influencing your title links in search results (xref: `google_search_central_title_links_page`)
- Google Search Central: Site names in Google Search (xref: `google_search_central_site_names_page`)
- Google Search Central: Meta descriptions / snippets (xref: `google_search_central_meta_descriptions_snippets_page`)
