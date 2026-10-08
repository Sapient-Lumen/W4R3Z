# 390 — Official voter-information public APIs, data feeds, and widget-consumption discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **machine-readable public voter-information surfaces** that election offices or their partners expose to the public: JSON / API endpoints, structured data feeds, public query services used by first-party or third-party widgets, and similar machine-readable outputs that can drive maps, lookup tools, office cards, “where do I vote?” apps, or other public-facing experiences.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `308`, which governs the substantive authoritative election-calendar and key-date surface,
- `362`, which governs office-discovery ladders and routing divergence,
- `374`, which governs interactive routers and decision-path trace discipline,
- `375`, which governs on-site search/autocomplete/result ranking,
- `376`, which governs map embeds, geolocation, and directions,
- `378`, which governs file/download and embedded-viewer boundary discipline,
- `382`, which governs external search-result presentation,
- or `386`, which governs off-platform AI answer surfaces and citation handoff.

It adds one narrow rule:
**if machine-readable voter information may be queried, cached, embedded, or republished through public widgets or third-party consumers, that machine-readable layer should stay clearly subordinate to the current official page/notice/help lane, explicit about election scope and freshness, and safe when the API returns partial, stale, ambiguous, or no data.**

## Why this is a distinct surface

Current official election-administration guidance still treats online voter information as a core public responsibility. The EAC’s current **Effective Design for the Administration of Federal Elections** says election officials are responsible for creating clear, understandable, and accessible **online voter information materials**. EAC’s broader voter-help posture still routes people back to the current state/local election authority rather than to detached summaries. That matters because many modern public voter experiences are no longer just webpages: they are widget-backed lookups, public APIs, or machine-readable feeds consumed by sites and apps. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `eac_voter_faqs_page`; xref: `vote_gov_home_page`)

Primary platform documentation shows that this machine-readable layer is operationally real. Google’s current Civic Information API overview says developers can build applications that display polling places, early-vote locations, candidate data, and other election-official information. Its current developer guidelines say the API provides election information for supported elections, that data is frequently updated and may not be available for all addresses or districts, that developers must obey cache guidance, and that applications should route users to local election officials when the API lacks data. Its current `voterInfoQuery` reference says that if there is no live election the response only returns data when an election ID is specified, and that if multiple elections exist for a voter the consumer may need a second query with the election ID to ensure the correct polling location, contest, and election-official information. (xref: `google_civic_information_api_page`; xref: `google_civic_information_api_data_guidelines_page`; xref: `google_civic_information_api_voter_info_query_page`)

That is enough to justify a bounded public-surface control here.
A public webpage may look authoritative.
But if the effective answer is really coming from a cached API response or a third-party widget using that response, then the machine-readable layer is part of the public evidence surface and should be governed as such.

## Machine-readable public outputs are derivatives, not the controlling rule source

A public API or data feed MAY help first-party and third-party tools deliver official voter information.
It MUST NOT quietly become a substitute for the current official page, notice, directory entry, or direct office confirmation that the jurisdiction itself stands behind.

The machine-readable layer should do only enough to:
- expose the bounded facts the consumer needs,
- preserve election scope and source/freshness semantics,
- point back to the current official destination that controls the answer,
- and fail safely when the data is partial, ambiguous, stale, or outside the supported election window.

The goal is not to ban public APIs.
The goal is to stop a JSON response or widget result from silently acting like a timeless rulebook.

## Election scope and live-election semantics are load-bearing

Google’s current Civic Information API overview says election information is tied to an **election ID** and is intended to be accurate for that election only. The current `voterInfoQuery` reference says that if there is no live election, data only returns when an election ID is specified, and when more than one election is available the consumer may need a second query using the election ID to ensure the right polling-location, contest, and election-official answer. (xref: `google_civic_information_api_page`; xref: `google_civic_information_api_voter_info_query_page`)

For election information, that means a machine-readable public surface should not pretend that one generic address lookup is enough forever.
A safe public API/feed/widget surface should keep at least these distinctions explicit:
- **which election scope** the result applies to,
- whether the answer is valid only for a **currently supported/live election**,
- whether multiple elections or overlapping windows require the user to choose a specific election,
- and where the user lands when the machine-readable layer cannot safely resolve the ambiguity by itself.

A machine-readable answer with the wrong election scope is not a small bug.
It can send the voter to the wrong site, the wrong deadline, or the wrong office.

## Cache and freshness semantics are part of the public answer

Google’s current Civic Information API developer guidelines say developers must obey any cache-control headers and, absent cache-control headers, should not cache voting-location and contest information for more than 24 hours. api.data.gov’s current agency manual says api.data.gov can act as an HTTP caching layer and that APIs must return HTTP headers to control cache duration. (xref: `google_civic_information_api_data_guidelines_page`; xref: `api_data_gov_agency_manual_page`)

That makes freshness a public-surface issue, not just a backend implementation detail.
If an election office exposes public machine-readable voter information, it should assume that:
- clients may cache it,
- intermediaries may cache it,
- widgets may display a response after the source page changed,
- and third-party developers may not understand the election-specific harm of stale data.

So the bounded rule here is simple:
- publish explicit freshness semantics,
- keep current official landing pages/help lanes visible,
- and make stale-data recovery obvious enough that a cached widget result does not quietly outrank the current official page.

## Source precedence and no-data behavior must fail safely

Google’s current developer guidelines say the API may have multiple sources for the same information, prioritizes official polling-place data over other sources, can eliminate non-official sources through an official-only mode, may sometimes return no data because of quality issues, and warns that lack of data for an address does **not** necessarily mean nobody is registered there; applications should direct users to local election officials for complete information. The same guidance also says elections auto-expire after election day, after which no data is returned for that election. (xref: `google_civic_information_api_data_guidelines_page`)

That is exactly the right posture for this archive.
A machine-readable public surface should never let **no result** masquerade as **no eligibility** or **no voting path**.
It should never let ambiguous source precedence stay hidden.
And it should never leave a user stranded when the supported-election window closed or the data is temporarily withheld for quality reasons.

So a safe API/feed/widget surface should make visible enough:
- whether the answer came from an official source path,
- whether the response is incomplete/unsupported/expired rather than negative,
- and which office/help route the user should use next.

## Parity and holdback discipline matter for public trust

Google’s current Civic Information API developer guidelines say developers should make every effort to ensure all users are met with the same experience and that holdbacks, A/B testing, or similar experiments are not allowed. (xref: `google_civic_information_api_data_guidelines_page`)

That aligns directly with the archive’s broader split-view and parity posture.
If a machine-readable public answer layer gives different users materially different answers because of experiment buckets, client-specific gating, or undeclared source selection, the office may later be unable to prove what the public answer really was.

So this surface should preserve a bounded trace of:
- the machine-readable policy version in effect,
- the election scope and freshness semantics presented to the public,
- the source-precedence mode used for the result,
- and the fallback/help route the user should have seen when the system could not safely answer.

It does **not** require retaining detailed query logs or user identifiers.
It requires only enough evidence to reconstruct the public policy state.

## Widgets, republishers, and consumer apps need authority-boundary cues

A public API or feed often does not stay on the office’s own page.
It may power:
- a first-party polling-place widget,
- an official mobile app,
- a civic-tech site,
- a newsroom lookup,
- or a map card embedded on another page.

That is why this surface should keep machine-readable outputs bounded enough that downstream consumers can still preserve:
- the issuing jurisdiction or responsible office,
- the election scope,
- freshness/current-state semantics,
- the direct official landing page,
- and the ordinary help route when the answer is incomplete or contested.

This archive does **not** need a universal schema for every civic API on earth.
It only needs a bounded rule saying that, if an office exposes or endorses a public machine-readable answer layer, that layer should carry the minimum authority/freshness/help cues required for safe downstream reuse.

## Claims this surface should support

1. **Scope-boundary claim:** machine-readable public voter-information outputs identify the election scope or supported-election context strongly enough that a consumer cannot silently reuse the answer outside its intended election window.
2. **Freshness claim:** the public API/feed/widget layer exposes bounded freshness semantics and recovery routes so stale cache state does not quietly become the trusted answer.
3. **Source-precedence claim:** official-source preference, ambiguity, and no-data states are handled explicitly enough that absence of data is not misread as absence of eligibility or service.
4. **Parity claim:** the machine-readable public answer layer preserves materially consistent user-facing behavior rather than hidden holdbacks or undeclared split views.
5. **Trace-minimization claim:** bounded reconstruction of public API/feed/widget policy state is possible without retaining unnecessary user-level query telemetry.

## Canonical digest artifacts

Publish **digests of API/feed policy and consumer-visible answer semantics**, not raw user query logs.

- **Public API Surface Digest (PASD):** digest of the bounded public payload for an official voter-information API/feed/widget surface.
- **API Freshness and Source Policy Digest (AFSPD):** digest of freshness, cache, and official-source-precedence policy for a given public machine-readable surface.
- **Machine-Readable Fallback Recovery Digest (MRFRD):** optional digest proving what help/fallback path a user should have seen when the API/feed/widget could not safely resolve the answer at time `T`.

## What belongs in the public payload

Keep the payload **small, election-scoped, freshness-aware, and authority-boundary explicit**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `public_api_surface_label`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `authority_boundary_note`
- `machine_readable_scope_note`
- `freshness_and_cache_policy_note`
- `official_source_precedence_note`
- `no_data_does_not_mean_ineligible_note`
- `multiple_elections_resolution_note`
- `live_election_window_note`
- `consumer_widget_boundary_note`
- `fallback_recovery_policy_note`
- `api_state_classes[]`
- `api_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw user query logs,
- API keys or consumer secrets,
- detailed per-user address lookups,
- individualized analytics about which voter searched what,
- or backend debug traces that do not help reconstruct the bounded public answer policy.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which official machine-readable voter-information surfaces were intended to feed public widgets or apps at time `T`?
- Did the surface expose election scope strongly enough that a consumer could not silently reuse the result for the wrong election?
- Were freshness/cache semantics explicit enough that stale widget/API output was recoverable?
- Did no-data / ambiguous / unsupported-election states route the user safely to the current official help lane instead of implying a negative answer?
- Did the jurisdiction preserve a bounded API/feed policy trace without collecting unnecessary user-level query telemetry?

## How this fits the family map

Public APIs, data feeds, and machine-readable widget backends are **not** a new canonical voter-question family bucket.
They are a delivery and reuse layer that may sit underneath or in front of existing voter-information surfaces.

So the underlying question remains:
- where the voter should go,
- whether the voter is eligible,
- which office controls the answer,
- which deadline applies,
- or which special-case path now controls.

This document only says that, if a public machine-readable layer can answer those questions through APIs, widgets, or republished feeds, that layer should stay clearly scoped, freshness-aware, subordinate to the current official page/notice/help lane, and safe under ambiguity instead of quietly becoming the trusted rule source.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-api-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-api-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- EAC: Voter FAQs (xref: `eac_voter_faqs_page`)
- Vote.gov home / official-routing posture (xref: `vote_gov_home_page`)
- Google for Developers: Civic Information API overview (xref: `google_civic_information_api_page`)
- Google for Developers: Civic Information API developer data guidelines (xref: `google_civic_information_api_data_guidelines_page`)
- Google for Developers: Civic Information API `voterInfoQuery` reference (xref: `google_civic_information_api_voter_info_query_page`)
- api.data.gov: Agency Manual / caching API responses (xref: `api_data_gov_agency_manual_page`)
