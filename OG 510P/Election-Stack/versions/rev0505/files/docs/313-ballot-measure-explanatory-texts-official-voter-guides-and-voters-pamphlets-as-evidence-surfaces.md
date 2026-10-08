# 313. Ballot-measure explanatory texts, official voter guides, and voters’ pamphlets as evidence surfaces

**Track:** Shared / Public surfaces

This document treats the **public answer surface for “what does this ballot measure mean, where is the authoritative guide or pamphlet, which explanatory materials were officially attached to it, and what changed?”** as an **evidence surface**.
The goal is not to preserve campaign speech, petition-signature workflows, legislative drafting records, or every page of every guide inside this archive. The goal is to make six things hard to fake after the fact:

1. **Which official guide / pamphlet / measure-information surface the jurisdiction identified as authoritative** for election scope `E`,
2. **Which explanatory components the public surface said accompanied each measure**,
3. **Whether the guide was general, regional, or voter-customized in scope**, and what caveats were published,
4. **When explanatory text, fiscal-impact text, arguments, translations, or guide editions changed**,
5. **Whether draft public-display materials and final published materials were clearly distinguished**, and
6. **Whether official channels stayed consistent, accessible, translated where required, and explicit about superseding corrections**.

It composes with:
- `docs/186-incident-communications-as-evidence.md`
- `docs/195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`
- `docs/199-official-surface-security-snapshots.md`
- `docs/200-publicnotice-feeds-and-mirror-index.md`
- `docs/201-public-surface-parity-snapshots.md`
- `docs/203-official-channel-directory-as-evidence.md`
- `docs/205-cache-and-freshness-controls-for-public-surfaces.md`
- `docs/217-claim-cards-and-traceability-minspec.md`
- `docs/223-public-surface-capture-notes-and-reproducibility.md`
- `docs/248-accessibility-usability-and-language-access-as-integrity.md`
- `docs/293-ballot-style-lookups-and-sample-ballots-as-evidence-surfaces.md`
- `docs/302-language-assistance-translated-materials-and-change-notices-as-evidence-surfaces.md`
- `docs/308-election-calendars-key-dates-and-change-notices-as-evidence-surfaces.md`
- `docs/310-voter-facing-public-answer-surfaces-family-map-and-promotion-rules.md`
- `docs/312-runoff-and-special-election-participation-district-scope-and-change-notices-as-evidence-surfaces.md`

## Why this exists (bounded)

Official election authorities already publish a distinct public surface for **measure explanation and guide material**, not just a bare sample ballot. California’s current **Voter Information Guides** page says that for each measure on the ballot, the state guide contains an impartial analysis, potential taxpayer-cost analysis, arguments for and against, the text and a summary, and other information. California’s current **Public Display – Official Voter Information Guide** page separately says draft ballot materials for the June 2, 2026 Primary Election are made available in PDF for public inspection before printing. Oregon’s current **File a Statement / Argument in the Voters’ Pamphlet** page says the State Voters’ Pamphlet contains candidates, ballot measures, political parties, and election-process details, and specifically includes measure arguments, fiscal impact statements, explanatory statements, and legislative arguments; it also says portions of the pamphlet are translated into the most commonly spoken languages in Oregon for an abbreviated online version. Washington’s current **Proposed Ballot Measure Information** page says it will update with ballot titles, explanatory statements, fiscal impact statements, and public investment impact disclosures, with official certification later posted and measure information then appearing in the online voters’ guide before the printed pamphlet is delivered. Washington’s current **2025 General Election Voters’ Guide** page also says the guide can be customized through VoteWA, provides translated PDF editions, audio, and video formats, and warns that the statewide pamphlet may show candidates or measures that do not appear on a given voter’s ballot because precinct scope still controls the voter-specific answer. (source: `california_voter_information_guides_page`, `california_public_display_official_voter_information_guide_page`, `oregon_file_statement_argument_voters_pamphlet_page`, `washington_proposed_ballot_measure_information_page`, `washington_2025_general_election_voters_guide_page`)

That makes this a real public-answer surface with its own correction semantics. `docs/293` answers **what appears on the voter’s ballot style or sample ballot**. This document answers **what explanatory guide material, statement package, fiscal-impact text, or official pamphlet accompanied a measure, in what edition, and under what scope caveats**. A jurisdiction can have an accurate sample ballot while the public explanatory guide is stale, mistranslated, silently swapped, or inconsistent across print, PDF, dynamic guide, and audio/video formats. The dispute surface is therefore different.

This document stays intentionally bounded. It is **not** a claim that election offices should publish the full text of every guide inside this archive. It is a claim that the jurisdiction should be able to prove which official guide edition, explanatory bundle, and correction chain controlled the public answer at time `T`.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Authoritative guide-surface claim:** for election scope `E`, the jurisdiction identified one authoritative public path for official guide / pamphlet / explanatory-material publication and one authoritative help path.
2. **Edition claim:** each guide or pamphlet edition identifies its scope, effective window, and whether it is draft-for-public-display, final, or superseded.
3. **Measure-component claim:** for each measure, the public surface states which official explanatory components exist (for example full text, summary, explanatory statement, fiscal impact statement, arguments for/against, rebuttals, plain-language label, or equivalent local/state-specific components).
4. **Scope/customization claim:** the public surface states whether it is statewide, regional, countywide, precinct-sensitive, or voter-customized, and warns when the guide may include material not present on a particular voter’s ballot.
5. **Change-log claim:** changes to explanatory text, component availability, translations, audio/video assets, or edition status are published as explicit superseding events rather than silent edits.
6. **Parity/accessibility claim:** website, printable PDF, mailed or public-distribution guide, translated edition, accessible format, online customized guide, and signed notices converge on the same effective public state.

## Canonical digest artifacts

Publish **digests of the public explanatory-guide surface**, not full copied pamphlets by default.

- **Measure Guide Surface Digest (MGSD):** digest of the authoritative guide / pamphlet / measure-information payload for an election scope.
- **Measure Entry Digest (MED):** per-measure digest binding the authoritative set of explanatory-component pointers for that measure.
- **Measure Guide Change Notice Digest (MGCND):** per-event digest for superseding changes to explanatory text, fiscal-impact references, arguments, translations, edition status, or scope caveats.
- **Measure Guide Public Display Snapshot (MGPDS):** optional digest binding a draft public-display package to a declared publication window before final printing.
- **Measure Guide Parity Snapshot (MGPS):** optional snapshot binding the effective public state across print/PDF/web/customized/audio/video channels.
- **Measure Guide Help Path Digest (MGHPD):** optional digest of the authoritative help path when a voter cannot determine which measure materials govern their ballot scope.

## What belongs in the public guide / pamphlet payload

Keep the payload **small, pointer-heavy, and edition-aware**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `guide_kind` (`official_voter_guide`, `state_voters_pamphlet`, `local_voters_pamphlet`, `official_measure_information_page`)
- `authoritative_guide_uri`
- optional `authoritative_measure_info_uri`
- `authoritative_help_uri` and/or `authoritative_help_phone`
- `coverage_scope_note`
- `effective_from` and optional `effective_until`
- `edition_status` (`draft_public_display`, `final`, `superseded`)
- `freshness_note`
- `last_verified_at`
- supersedes / superseded-by pointers
- pointer to the latest signed correction or maintenance notice

Recommended guide-format fields:
- `distribution_channels`
- `language_set`
- accessibility-format indicators
- optional `customized_lookup_uri`
- optional `archive_uri`
- optional `draft_display_uri`

Recommended per-measure fields:
- stable `measure_id`
- `display_label`
- `ballot_scope_note`
- optional `ballot_title_uri`
- optional `summary_uri`
- optional `full_text_uri`
- optional `explanatory_statement_uri`
- optional `fiscal_impact_uri`
- optional `arguments_for_uri`
- optional `arguments_against_uri`
- optional `rebuttals_uri`
- optional `translation_refs`
- optional `detail_surface_ref`
- bounded `plain_language`

Do **not** publish by default:
- full copied guide text inside this archive when stable pointers and digests suffice
- campaign-finance truth claims or factual adjudication of arguments-for/against content
- petition signatures, drafting workpapers, or sponsor contact details unless another surface explicitly owns them
- voter-specific ballot history or individualized precinct-assignment data
- mutable third-party “voter guide” material that the jurisdiction did not adopt as official

## Scope semantics, customization, and anti-retcon rules

Guide surfaces need to fail **loudly** when the public explanation changes or when scope is ambiguous.

Rules:
- Draft public-display materials SHOULD be distinguishable from final guide editions.
- A change to explanatory statement text, fiscal-impact text, ballot-title wording, translation availability, or guide scope caveat SHOULD produce a new change notice digest.
- If a guide includes all statewide, countywide, or regional measures while a given voter receives only a subset, the guide surface SHOULD say so plainly and point to the authoritative ballot-style / voter-specific lookup rather than pretending the guide itself is a precise per-voter ballot answer.
- If the dynamic online guide, printable PDF, mailed pamphlet, audio file, translated edition, or video guide diverges from the rest of the official surface, publish a parity snapshot (`201`) and a signed correction notice.
- Silent PDF swaps, silent dynamic-guide rewrites, or quiet replacement of explanatory statements after controversy SHOULD be treated as governance failures.
- Where a proposed-measure page exists before final certification, it SHOULD identify that pre-certification status rather than implying the measure is already on every voter’s ballot.
- If a runoff, special election, district split, or local edition changes which measures are in scope, the guide surface SHOULD point to `293`, `308`, and `312` as needed instead of swallowing those boundaries.

## Accessibility, translation, and public reach

Guide surfaces often appear in several formats at once: dynamic online guide, printable PDF, mailed pamphlet, translated editions, audio, and video.

Minimum publishable facts:
- which guide or pamphlet edition is authoritative right now,
- which measures it covers and under what scope caveat,
- which explanatory components exist for each measure,
- which translations and accessible formats cover the answer surface,
- which voter-specific lookup should be used when the guide is broader than the voter’s actual ballot,
- which signed notice superseded the prior explanation.

A jurisdiction does not get to count a generic statewide PDF as the whole answer if the actual voter-facing path depends on customized lookup, translation access, or accessible-format parity.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Was there one authoritative public guide / pamphlet / measure-information surface at time `T`?
- Can we reconstruct which explanatory components were officially attached to a measure at that time?
- Did the public surface say whether it was draft, final, general, regional, or voter-customized in scope?
- Were translations and accessible formats materially equivalent to the main guide surface?
- Did print/PDF/web/customized/audio/video channels converge on the same effective public state?
- Were changes explicit and timestamped, or silently edited away?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/ballot-measure-guide-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/ballot-measure-guide-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- California Secretary of State: Voter Information Guides (source: `california_voter_information_guides_page`)
- California Secretary of State: Public Display — Official Voter Information Guide (source: `california_public_display_official_voter_information_guide_page`)
- Oregon Secretary of State: File a Statement / Argument in the Voters’ Pamphlet (source: `oregon_file_statement_argument_voters_pamphlet_page`)
- Washington Secretary of State: Proposed Ballot Measure Information (source: `washington_proposed_ballot_measure_information_page`)
- Washington Secretary of State: 2025 General Election Voters’ Guide (source: `washington_2025_general_election_voters_guide_page`)
