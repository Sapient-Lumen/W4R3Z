# Rev0014 audit and factor report

Rev0014 is a foundation-cleaning revision. It adds no records and enables no public pages.

The audit found that the cube was conceptually strong but mechanically uneven. The largest issues were not fatal, but they were the kind that would mislead future sessions: missing source cards for early source IDs, source-card dependency drift, missing `links` blocks in setting and perspective records, missing `review` blocks in perspective records, duplicated class tags, setting values leaking into the timeline axis, lowercase/uppercase review-packet path drift, and a record schema whose class enum no longer matched actual records.

The fixes are deliberately infrastructural rather than interpretive. No record was promoted. No private testimony was invented. No public advice surface was created.

## What was repaired

- Added missing source cards for record-referenced sources.
- Recomputed every source card's `dependent_record_ids` from record `source_packet.source_ids`.
- Added review blocks to perspective records that lacked them.
- Added links blocks to setting and perspective records that lacked them.
- Deduplicated repeated `setting_axis` and `perspective_axis` class tags.
- Normalized `ICU`/`ED` setting tags to lower-case `icu`/`ed` and removed setting tags that had leaked into `timeline_phase`.
- Renamed lower-case review-packet filenames for `DV-RP-0011` through `DV-RP-0015` to match their packet IDs.
- Replaced the obsolete `record_classes` enum in `RECORD-SCHEMA.json` with a lower_snake_case tag contract.
- Added audit/factor surfaces so future offices can see what happened.

## What remains unresolved

- The records are still public-source synthesis, not the oral witness corpus the project ultimately dreams of.
- Duplicate URL/source-ID groups exist and are ledgered but not merged.
- `record_classes` is still overloaded; `CLASS-TAXONOMY.json` explains the compatibility compromise.
- Related-record links are directional and not yet a curated public browse graph.
- No external clinical, tradition-holder, legal, trauma, child, suicide-safe, custody, disaster, funeral, or lived-witness review has occurred.

## The factoring principle

The cube now has clearer layers: telos, records, sources, review gates, axes, language/search, public prototypes, tooling, and high-gate negative space. Future sessions may refactor any soft layer, but not the hard protections around consent, source integrity, cultural sovereignty, non-voyeurism, and non-advice.
