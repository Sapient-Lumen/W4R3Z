# 468 — Official voter-information citation-head registers, unique-head warnings, and public handoff discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information programs that maintain more than one mutable public-answer route, more than one point-in-time citation snapshot, or more than one possible candidate for “the current exact thing people should quote or hand off”**:
FAQ/article clusters,
mutable deadline pages,
hours/location pages,
status explainers,
change-notice sequences,
partner relay packets,
hotline packets,
and similar official materials where multiple live pages, snapshots, or superseding states may coexist.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `363`, which governs official automated assistants and answer traces,
- `365`, which governs official FAQ/help article editions,
- `367`, which governs press releases and spokesperson quote discipline,
- `386`, which governs off-platform AI answer-surface citation handoff,
- or `467`, which governs per-route separation between the current live operational head and the latest point-in-time citation-safe head.

It adds one narrow rule:
**if a jurisdiction has more than one mutable or superseding public-answer route that may function as a citation anchor, it should publish one tiny register that names the operational head, the citation head, and any explicit warnings that mean there is no unique citation-ready head for a reviewed lineage or surface family.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications. USWDS’s current **Keep a record** guidance says important public-service flows should preserve a record that includes the site name, URL, date, and next-step/reference context when possible. Google Search Central’s current **AI features and your website** guidance and related search-presentation guidance make clear that public-web pages may be surfaced, linked, summarized, and handed off through search and AI layers before a voter ever reads the underlying official page. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `google_search_central_ai_features_page`; xref: `google_search_central_title_links_page`; xref: `google_search_central_site_names_page`; xref: `google_search_central_meta_descriptions_snippets_page`)

That is enough to justify one compact register layer here.
A jurisdiction may already satisfy `467` route by route and still fail public handoff because:
- the office has several plausible heads across live pages, snapshots, and superseding notices but no tiny surface saying which one is operationally current,
- a hotline, partner explainer, or AI answer cites a mutable page family without a clear unique citation-safe head,
- a journalist or observer can find several preserved snapshots but cannot tell which one is the citation-ready tip,
- or the latest operational page is obvious internally while the public still has no compact warning that the unique citation head is pending, split, superseded, or ambiguous.

## Per-route head discipline is not enough once multiple lineages exist

`467` answers a per-route question:
**for this mutable official route, what is the live operational head and what is the citation-safe head?**

`468` answers the cross-route handoff question:
**across the reviewed family of mutable official routes, which heads are current, which are citation-safe, and where should a third party see a warning that no unique citation head exists?**

Without that compact register, later readers are forced to reconstruct head status by hand from scattered pages, captures, notices, or editorial memory.
This archive should not make public citation truth depend on manual lineage tracing.

## One tiny generated register is enough

The archive does **not** need a giant CMS dashboard or release-admin console.
It needs one small public register that can be regenerated whenever reviewed head state changes.

For each reviewed lineage or bounded page family, that register should make three things legible:
- **operational head** — the live page or official route the office intends the public to use now,
- **citation head** — the latest point-in-time public snapshot/capture the office is willing to treat as the exact citation-ready state,
- **warning state** — whether branch, superseding, pending-freeze, or missing-snapshot conditions mean no unique citation-safe head should be implied.

The point is not to narrate every edit.
The point is to prevent “something current exists somewhere” from masquerading as “there is one clearly identified citation-ready head.”

## Unique-head warnings should be explicit

A useful import from stricter lineage-oriented systems is that ambiguity should be surfaced as a first-class warning rather than left to interpretation.
For this archive, a citation-head register should be able to say, in bounded form, at least things like:
- `no_unique_citation_head_yet`
- `multiple_citation_heads_require_human_review`
- `operational_head_is_live_but_not_frozen_for_exact_citation`
- `preview_or_queue_state_exists_but_is_not_public`
- `older_citation_head_still_circulates_but_has_been_superseded`
- `lineage_branching_or_scope_split_requires_explicit_disambiguation`

What matters is not a fixed global warning vocabulary.
What matters is that a third party should not have to infer ambiguity from silence.

## This is a handoff surface, not an internal publishing console

A citation-head register is for the public and semi-public handoff lanes that sit around the page itself:
partner explainers,
hotline packets,
media quoting,
AI-assisted summaries,
search-result clickthrough,
observer review,
and later dispute reconstruction.

So the register should stay small and handoff-friendly.
It is **not** the place to publish:
- full internal CMS histories,
- unpublished release tooling,
- editor rosters,
- private preview URLs,
- or giant capture inventories.

It should only expose enough to answer:
- what the office says is operationally current,
- what the office says is citation-safe,
- whether a unique citation head exists,
- and what warning or recovery note applies when it does not.

## Warning-bearing registers are especially important for quoted and summarized pages

`363`, `365`, `367`, `386`, and `467` already assume official material may be summarized, quoted, translated, clipped, screenshotted, or surfaced by search and AI before someone reads the whole official page.
That means a citation-head register is not a records-management luxury.
It is a compact anti-overclaim surface for the surrounding handoff ecosystem.

When a journalist, partner organization, hotline operator, or AI answer surface asks “what exactly should we cite right now?”, the office should be able to answer with something smaller and more truthful than “probably the latest page we remember updating.”

## Preserve bounded evidence, not lineage archaeology

The evidence posture here is about reconstructing head status and ambiguity with a compact public artifact.
The archive should preserve:
- which mutable route families or lineages are included in the register,
- which route is the operational head for each,
- which artifact is the citation head for each,
- whether the citation head is unique,
- what warning codes or notes block unique-head certainty,
- what superseding relationship applies,
- and when the register was last reviewed.

It should **not** require publishing by default:
- full snapshot corpora,
- raw internal queue state,
- internal editorial reasoning threads,
- or private lineage-management infrastructure.

## Canonical digest artifacts

Publish **small digests of head-register posture**, not archival exhaust.

- **Citation-Head Register Digest (CHRD):** digest of the bounded register naming reviewed lineages, operational heads, citation heads, and warning posture.
- **Citation-Head Warning Digest (CHWD):** optional digest over the current active ambiguity/warning set for reviewed lineages.
- **Superseding-Head Register Delta Digest (SHRDD):** optional digest when the register changes because a newer citation head supersedes an older one.

## What belongs in the public citation-head-register payload

Keep the payload **small, lineage-aware, and warning-bearing**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `citation_head_register_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `register_scope_note`
- `reviewed_lineages[]`
- `register_warning_codes[]`
- `public_handoff_note`
- `warning_recovery_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Recommended per-lineage fields inside `reviewed_lineages[]`:
- `lineage_id`
- `surface_family_ref`
- `operational_head_ref`
- `citation_head_ref`
- `citation_head_uniqueness`
- `warning_codes[]`
- `superseding_note`
- `latest_reviewed_at`

Do **not** publish by default:
- private preview/staging URLs,
- internal queue identifiers,
- full snapshot inventories,
- private editorial comments,
- or giant lineage graphs when a compact reviewed head register is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, partner, or court should be able to answer:
- Which mutable official route or bounded lineage was operationally current at time `T`?
- Which point-in-time artifact, if any, was the citation-safe head at time `T`?
- Was there exactly one unique citation head, or did the office publish a warning that exact citation certainty was blocked?
- Were preview, queue, staged, or other non-public states kept out of the public head register?
- When an older citation head was superseded, did the register show the relationship clearly enough that handoff users did not have to infer it from scattered pages?

## How this fits the family map

Citation-head registers and unique-head warnings are **not** a new underlying voter-question family bucket.
They are a delivery-layer and evidence-layer control over mutable official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, when multiple mutable or superseding official-answer states exist, the office should publish one tiny register that says which head is operationally current, which head is citation-safe, and when no unique citation-ready head should be implied.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-citation-head-register-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-citation-head-register-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Keep a record (xref: `uswds_keep_a_record_page`)
- Google Search Central: AI features and your website (xref: `google_search_central_ai_features_page`)
- Google Search Central: Influencing your title links in search results (xref: `google_search_central_title_links_page`)
- Google Search Central: Site names in Google Search (xref: `google_search_central_site_names_page`)
- Google Search Central: Meta descriptions / snippets (xref: `google_search_central_meta_descriptions_snippets_page`)
